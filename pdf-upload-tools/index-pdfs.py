


import os
import base64
import dotenv
from elasticsearch import Elasticsearch
from art import text2art
import sys
import argparse
import json
from tqdm import tqdm
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
dotenv.load_dotenv( override=True,dotenv_path="config/.env")
# Set variables
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX")
# What directory would you like to index?
directory = "pdfs"
elser_endpoint_name = "pdf-elser"
allowed_extensions = [".pdf"]  # Add or remove file extensions as needed
pipeline = "pdf-pipeline"  # Name of the ingest pipeline

# We are going to use optional arguments which will allow us to automatically answer yes to all prompts
# This speeds up devolpment of the default route
parser = argparse.ArgumentParser(description="Index PDFs to Elasticsearch")
parser.add_argument("-y", "--yes", action="store_true", help="Automatically answer yes to all prompts",default=True) # Set fefault to true for now
args = parser.parse_args()


def main():
    """
    Index PDF files in a directory to Elasticsearch.
    """
     # Print a nice ascii welcome message using the art lib
    print(text2art("Index PDFs"))

    # Establish connection to Elasticsearch
    es , elasticsearch_info = connect_to_elasticsearch(ELASTICSEARCH_HOST, ELASTICSEARCH_API_KEY)

   # Check if the cluster can use semantic text. Must be version 8.15 or later 
    semantic_eligible = can_use_semantic_text(elasticsearch_info["es_major_version"],elasticsearch_info["es_minor_version"],elasticsearch_info["es_license"])

    if semantic_eligible:
        # Check if the user is ok with default ELSER or if they want to use an existing inference endppoint
        use_elser_input = get_user_input("Would you like to use the default ELSER inference model? (y/n) [default: y]: ") or "y"

        if use_elser_input.lower() == "y":
            # Create the inference endpoint if it doesn't already exist
            create_elser_inference_endpoint(es, elser_endpoint_name)
            # Test the inference endpoint
            if not test_interence_endpoint(es, elser_endpoint_name):
                print("Inference endpoint still not available Exiting...")
                exit()
        else:
            # Choose an existing inference endpoint
            inference_pipeline_id = choose_inference_endpoint(es)
        mapping = create_semantic_mapping(inference_pipeline_id)
    else:
        # Load the index mapping from file
        with open("pdf-upload-tools/default_bm25_pdf_mapping.json", "r") as file:
            mapping = json.load(file)

    
    create_index_with_mapping(es, mapping, ELASTICSEARCH_INDEX)

    # Load the pipeline body from file
    with open("pdf-upload-tools/default_pdf_pipeline.json", "r") as file:
        pipeline_body = file.read()
    create_pipeline(es, pipeline, pipeline_body)

    index_pdfs(directory, allowed_extensions, es, ELASTICSEARCH_INDEX, pipeline)

    print("Indexing completed.")

# Function to get user input
def get_user_input(prompt):
    if args.yes:
        print(f"{prompt} y")
        return "y"
    else:
        return input(prompt)


def index_pdfs(directory, allowed_extensions, es, index, pipeline, use_semantic_text=False, use_default=False):
    """
    Index PDF files in a directory to Elasticsearch.
    """
    # Get the total number of PDF files to process
    total_files = sum(len([file for file in files if any(file.endswith(ext) for ext in allowed_extensions)]) for _, _, files in os.walk(directory))

    # Initialize the progress bar
    progress_bar = tqdm(total=total_files, desc="Indexing PDFs", unit="file")

    # Recurse the directory and process PDF files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in allowed_extensions):
                file_path = os.path.join(root, file)
                print(f"Indexing {file_path}...")

                # Base64 encode the file
                with open(file_path, "rb") as f:
                    encoded_file = base64.b64encode(f.read()).decode("utf-8")

                # Create JSON document to index in Elasticsearch
                document = {
                    "file_name": file,
                    "data": encoded_file
                }

                # Index the document in Elasticsearch
                es.index(index=index, pipeline=pipeline, body=document)

                # Update the progress bar
                progress_bar.update(1)

    # Close the progress bar
    progress_bar.close()
    print("Indexing completed.")


def create_index_with_mapping(es, mapping, index):
    """
    Create an index in Elasticsearch with a given mapping.
    """
    # Check if the index exists
    if es.indices.exists(index=index):
        replace_index_input = get_user_input(f"The index '{index}' already exists. Do you want to replace it? (y/n) [default: n]: ") or "n"
        if replace_index_input.lower() == "y":
            # Delete the existing index
            es.indices.delete(index=index)
            print(f"Deleted index '{index}'")

    # Create the index with the mapping
    es.indices.create(index=index, mappings=mapping)
    print(f"Created index '{index}' with the provided mapping")


def create_pipeline(es, pipeline, pipeline_body):
    """
    Create an ingest pipeline in Elasticsearch.
    """
    
    # Check to see if the pipeline exists
    if pipeline not in es.ingest.get_pipeline().body.keys():
        print("Creating ingest pipeline")
        # Create the pipeline if it doesn't exist
        es.ingest.put_pipeline(
            id=pipeline,
            body=pipeline_body
        )
    else:
        print("Pipeline already exists")
    
def create_elser_inference_endpoint(es, inference_id,):
    """
    Create an inference endpoint in Elasticsearch.
    """
    # Check to see if the inference endpoint exists
    if inference_id not in es.inference.get().body["endpoints"]:
        print(f"Creating inference endpoint '{inference_id}'")
        # Create the inference endpoint if it doesn't exist
        es.inference.put(
            task_type="sparse_embedding",
            inference_id=inference_id,
            inference_config={
                "service": "elasticsearch",
                "service_settings": {
                    "num_allocations": 1,
                    "num_threads": 2,
                    "model_id": ".elser_model_2_linux-x86_64"
                }
            }
        )
    else:
        print(f"Inference endpoint '{inference_id}' already exists")

def connect_to_elasticsearch(host, api_key):
    """
    Connect to Elasticsearch.
    """
    # Establish connection to Elasticsearch
    es = Elasticsearch(hosts=[host], api_key=api_key,timeout=60)

    if es.ping():
        print("Connected to Elasticsearch") 
    else:
        print("Could not connect to Elasticsearch")
        print("Please check your configuration details in config/.env")
        print("Exiting...")
        exit()
    # Get Elasticsearch version
    es_info = es.info()
    es_version = es_info["version"]["number"]
    es_version = es_version.split("-")[0] # Helps in case of snapshot builds etc
    es_version=es_version.strip()
    es_major_version = int(es_version.split(".")[0])
    es_minor_version = int(es_version.split(".")[1])
    es_license = es.license.get().body["license"]["type"]

    elasticsearch_info = {"es_version": es_version, "es_major_version": es_major_version, "es_minor_version": es_minor_version, "es_license": es_license}

    return es, elasticsearch_info

def can_use_semantic_text(es_major_version, es_minor_version,es_license):
    """
    Check if the cluster can use semantic text.
    """
    if not (es_major_version >=8 and es_minor_version >= 15):
        print("Semantic text requires Elasticsearch 8.15.0 or later")
        return False
    else:
        if es_license not in ["platium","enterprise","trial"]:
            print("Semantic text requires a platinum or higher license")
            print("You can start a trial to try all features in Kibana Stack Management or using the API https://www.elastic.co/guide/en/elasticsearch/reference/current/start-trial.html")
            return False
    return True

def test_interence_endpoint(es, inference_id):
    """
    Test an inference endpoint in Elasticsearch.
    """
    # Test the inference endpoint
    test_data = {
        "data": "This is a test document"
    }
    max_retries = 60  # Retry for up to 5 minutes (60 retries with 5 seconds interval)
    retry_interval = 5  # Retry every 5 seconds

    for attempt in range(max_retries):
        try:
            response = es.inference.post(inference_id=inference_id, body=test_data)
            print(response)
            break  # Exit the loop if the request is successful
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                print("Max retries reached. Inference endpoint is not deployed yet.")
                return False
            
def choose_inference_endpoint(es):
    """
    Choose an inference endpoint in Elasticsearch.
    """
    # Get the available inference endpoints
    inference_resp = es.inference.get().body["endpoints"]
    inference_endpoints = [endpoint["inference_id"] for endpoint in inference_resp]

    # Print the available inference endpoints and ask the user to select one
    print("Available inference endpoints:")
    for idx, endpoint in enumerate(inference_endpoints):
        print(f"{idx}: {endpoint}")

    selected_index = int(input("Please select an inference endpoint by index number: "))
    inference_pipeline_id = inference_endpoints[selected_index]

    return inference_pipeline_id

def update_field_in_object(obj,key_to_update,new_value):
            if isinstance(obj, dict):
                for key, value in obj.items():
                        if key == key_to_update:
                            obj[key] = new_value
                        else:
                            if isinstance(value, dict):
                                update_field_in_object(value,key_to_update,new_value)
            elif isinstance(obj, list):
                for item in obj:
                    update_field_in_object(item,key_to_update,new_value)

def create_semantic_mapping(inference_id):
    """
    Create a mapping for indexing PDFs with semantic text.
    """
    # Load the index mapping from file
    with open("pdf-upload-tools/default_samantic_pdf_mapping.json", "r") as file:
        index_mapping = file.read()
        index_mapping = json.loads(index_mapping)
    
    update_field_in_object(index_mapping, "inference_id", inference_id)
    return index_mapping

if __name__ == "__main__":
    main()


