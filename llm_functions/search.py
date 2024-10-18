# Add the parent directory to the path
import sys
import json
import os
from elasticsearch import Elasticsearch
import logging
sys.path.append("..")


# Get the logger from the main module
logger = logging.getLogger()


# Load the corpus description
with open("./config/corpus_description.txt", "r") as file:
    corpus_description = file.read().strip()

description ="The function searches an elasticsearch index to help provide accurate and up to date information to the user and returns the contents of the most relevant documents. The description of the corpus is: "+ corpus_description

definition = {
    "name": "search",
    "description": description,
    "parameters": {
        "type": "object",
        "properties": {
        "query_text": {
            "type": "string",
            "description": "The query text to search for. This should be an expansive set of keywords to find the best document, for example including synonymns"
        }
        },
        "required": ["query_text"]
    }
}
def load_query_template():
    """
    Load the Elasticsearch query template from a JSON file.
    """
    with open("./config/query_template.json", "r") as file:
        template = json.load(file)
    return template

def search(query_text):
    """
    Search the Elasticsearch corpus using the user's query.
    """
    # Environment variables
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
    ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
    ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX")
    CONTEXT_FIELDS = os.getenv("CONTEXT_FIELDS", "content").split(",")  # Default to 'content' if not set

    # Initialize Elasticsearch client
    es = Elasticsearch(
        ELASTICSEARCH_HOST,
        api_key=ELASTICSEARCH_API_KEY
    )

    try:
        # Load the query template
        query_template = load_query_template()

        # Replace the placeholder with the actual query
        query_template_str = json.dumps(query_template)
        query_template_str = query_template_str.replace("{query}", query_text)
        query_template = json.loads(query_template_str)

        # Perform the search
        search_results = es.search(index=ELASTICSEARCH_INDEX, body=query_template)


        # Extract relevant information from search results
        if search_results and search_results.get('hits', {}).get('hits'):
            hit = search_results['hits']['hits'][0]
            document = hit.get('_source', {})
            document_id = hit.get('_id', 'Unknown')

            result={"type":"search-result","id":document_id}

            # We need to test for inner_hits. If we find one we will just take the content in the hit
            # Inner hits are used by semantic_text which chunks the document
            if "inner_hits" in hit.keys():
                inner_hit = hit["inner_hits"][ELASTICSEARCH_INDEX+".content"]["hits"]["hits"][0]
                document = inner_hit.get('_source', {})
                # By default it uses "text" as the key for the content
                if "text" in document.keys():
                    result["text"]=document["text"]
                else:
                    logger.warning(f"Field 'text' is missing in the inner_hit.")
            else: 
            #    Build context from specified fields
                context_parts = []
                for field in CONTEXT_FIELDS:
                    value = document.get(field)
                    if value:
                        result[field]=value
                        context_parts.append(f"{field}: {value}")
                    else:
                        logger.warning(f"Field '{field}' is missing in the document.")
    except Exception as e:
        logger.error(f"An error occurred during the search: {e}")
        result = "An error occurred during the search. Please try again later."
    return result
