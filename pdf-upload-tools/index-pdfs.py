
import os
import base64
import dotenv
from elasticsearch import Elasticsearch
from art import text2art
import sys
import argparse
import json
from tqdm import tqdm

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

# Set up argument parser
parser = argparse.ArgumentParser(description="Index PDFs to Elasticsearch")
parser.add_argument("-y", "--yes", action="store_true", help="Automatically answer yes to all prompts",default=True)
args = parser.parse_args()

# Function to get user input
def get_user_input(prompt):
    if args.yes:
        print(f"{prompt} y")
        return "y"
    else:
        return input(prompt)


allowed_extensions = [".pdf"]  # Add or remove file extensions as needed
# Establish connection to Elasticsearch


def main():
    """
    Index PDF files in a directory to Elasticsearch.
    """
    # Establish connection to Elasticsearch
    es = Elasticsearch(hosts=[ELASTICSEARCH_HOST], api_key=ELASTICSEARCH_API_KEY,timeout=60)

    # Print a nice ascii welcome message using the art lib

    print(text2art("Index PDFs"))


    if es.ping():
        print("Connected to Elasticsearch") 
    else:
        print("Could not connect to Elasticsearch")
        print("Please check your onfigiration details in config/.env")
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

    # Create an index in Elasticsearch
    index = ELASTICSEARCH_INDEX
    pipeline = "pdf-pipeline"  # Name of the ingest pipeline

    all_pipelines = es.ingest.get_pipeline().body.keys()
    # Check to see if the pipeline exists
    if pipeline not in  all_pipelines:
        print("Creating ingest pipeline")
        # Load the pipeline body from file
        with open("pdf-upload-tools/default_pdf_pipeline.json", "r") as file:
            pipeline_body = file.read()
        # Create the pipeline if it doesn't exist
        es.ingest.put_pipeline(
            id=pipeline,
            body=pipeline_body
        )
    else:
        print("Pipeline already exists")

    # Ask the user if they want to use semantic_text which will chunk and vectorise the text. Otherwise all the text will be in a single field
    semantic_text_input = get_user_input("Would you like to use semantic text (recommended)? (y/n) [default: y]: ") or "y"

    if semantic_text_input.lower() == "y":
        # Check that the version is 8.15.0 or later
        #extract the major, minor and patch numbers from the version string
        if not (es_major_version >=8 and es_minor_version >= 15):
            print("Semantic text requires Elasticsearch 8.15.0 or later")
            print("Exiting...")
            exit()

        use_semantic_text = True

        # Check if the index exists
        if es.indices.exists(index=index):
            replace_index_input = get_user_input(f"The index '{index}' already exists. Do you want to replace it? (y/n) [default: n]: ") or "n"
            if replace_index_input.lower() == "y":
                # Delete the existing index
                es.indices.delete(index=index)
                print(f"Deleted index '{index}'")

        # Load the index mapping from file
        with open("pdf-upload-tools/default_samantic_pdf_mapping.json", "r") as file:
            index_mapping = file.read()
            index_mapping = json.loads(index_mapping)

        # Walk the index_mapping JSON object to find any key equal to inference_id
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

        update_field_in_object(index_mapping, "inference_id", elser_endpoint_name)

        # Create the index with the mapping
        es.indices.create(index=index, mappings=index_mapping)
        print(f"Created index '{index}' with the provided mapping")


        use_default_input = get_user_input("Would you like to use the default ELSER inference model? (y/n) [default: y]: ") or "y"
        
        # Check what inference endpoints are available
        inference_resp = es.inference.get().body["endpoints"]

        inference_ids = [endpoint["inference_id"] for endpoint in inference_resp]

        if use_default_input.lower() == "y":
            use_default=True

            if elser_endpoint_name not in inference_ids:
                print("Creating the ELSER inference endpoint")
                resp = es.inference.put(
                    task_type="sparse_embedding",
                    inference_id=elser_endpoint_name,
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
            use_default=False
            # Delete the fefault pipeline from the inference endpoints array if it exists
            if elser_endpoint_name in inference_ids:
                inference_ids.remove(elser_endpoint_name)
            # Print the available inference endoints and ask the user to select one
            print("Available inference endpoints:")
                    
            print(f"-1: Create new custom inference endpoint")
            for idx, endpoint in enumerate(inference_endpoints):
                print(f"{idx}: {endpoint}")

            selected_index = int(input("Please select an inference endpoint by index number: "))
            if selected_index == -1:
                print("This script doesn't currently support creating custom inference endpoints")
                print("Head overt to the Elastic documentation to learn how to create custom inference endpoints")
                print("https://www.elastic.co/guide/en/elasticsearch/reference/current/put-inference-api.html")
                exit()
            else:
                inference_pipeline_id = inference_endpoints[selected_index]




    print("Indexing PDF files...")
    # Get the total number of PDF files to process
    total_files = sum(len([file for file in files if any(file.endswith(ext) for ext in allowed_extensions)]) for _, _, files in os.walk(directory))

    # Initialize the progress bar
    progress_bar = tqdm(total=total_files, desc="Indexing PDFs", unit="file")
    docs_indexed=0
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
                index_doc_response = es.index(index=index, pipeline=pipeline, body=document,timeout="30s")
                # Update the progress bar
                progress_bar.update(1)
    
    # Close the progress bar
    progress_bar.close()
    print(f"Indexing completed. {docs_indexed} documents indexed successfully.")

if __name__ == "__main__":
    main()