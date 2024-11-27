# main.py

############################################
# Introduction
############################################

"""
This application is a chat-based assistant that interacts with users through the command line.
It leverages Azure OpenAI for generating responses and OpenTelemetry for tracing and logging.
The application performs the following high-level tasks:

1. **Configuration and Setup**:
    - Loads environment variables from a `.env` file.
    - Sets up OpenTelemetry for tracing.
    - Configures logging.
    - Initializes the Azure OpenAI client.

2. **Function Loading**:
    - Dynamically loads functions from the `llm_functions` module.
    - Stores function definitions and their corresponding implementations.

3. **Chat Interaction**:
    - Maintains a conversation history.
    - Handles user input and generates responses using Azure OpenAI.
    - Supports function calls within the chat, dynamically invoking the appropriate functions.

4. **User Management**:
    - Prompts the user for their name and saves it in a pickle file for future sessions.
    - Greets returning users and maintains a personalized experience.

5. **Main Loop**:
    - Continuously prompts the user for input until they choose to exit.
    - Processes each input, generates a response, and prints it in a formatted manner.

The main functions in the application are:
- `print_pretty_response(response)`: Formats and prints the assistant's response.
- `chat(user_input)`: Handles the interaction with the user, including sending input to Azure OpenAI and processing the response.
- `main()`: Sets up the argument parser, configures logging, handles user interaction, and manages the main chat loop.
"""

############################################
# Standard Import Libraries
############################################
import os
import logging
import json
import argparse
import pprint
from dotenv import load_dotenv
from openai import AzureOpenAI
import openai

############################################
# OpenTelemetry setup
############################################
from opentelemetry import trace
# Init tracer
tracer = trace.get_tracer_provider().get_tracer(__name__)
# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger()

############################################
# Import functions we can expose to the LLM
############################################
import llm_functions
from pkgutil import iter_modules
import pickle
import art

# Every file in the foler is loaded as a seperate function.
# The function name is the same as the file name
function_definitions = []
function_functions = {}
for submodule in iter_modules(getattr(llm_functions,"__path__")):
        if submodule.ispkg:
            pass
        else:
            mod= __import__(f"llm_functions.{submodule.name}",fromlist=["llm_functions"])
            definition = getattr(mod,"definition")
            function_definitions.append(definition)
            name = submodule.name
            function = getattr(mod,submodule.name)
            function_functions[name] = function


############################################
# Load the configuration from the .env file
############################################
load_dotenv(dotenv_path="./config/.env", override=True)

ASSISTANT_NAME = os.getenv("ASSISTANT_NAME")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")  # e.g., "2023-05-15"
CONTEXT_FIELDS = os.getenv("CONTEXT_FIELDS", "content")  # Default to 'content' if not set


############################################
# Azure OpenAI setup
############################################
############################################
if OPENAI_API_KEY:
    logger.info("Using OpenAI")
    AZURE_OPENAI_DEPLOYMENT_NAME = OPENAI_MODEL
    if OPENAI_BASE_URL:
        client = openai.Client(api_key=OPENAI_API_KEY)
        client.base_url = OPENAI_BASE_URL
    else:
        client = openai.Client(api_key=OPENAI_API_KEY)
else:
    logger.info("Using Azure OpenAI")
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
        api_key=AZURE_OPENAI_API_KEY
    )


############################################
# Chat application global variables
############################################
user_name = None
messages = []
# Initialise the message list
with open("./config/system_prompt.txt", "r") as file:
    system_prompt = file.read().strip()
messages.append({
    "role": "system",
    "content": system_prompt
})


def print_pretty_response(response):
    """
    Print the response in a pretty format.

    Args:
        response (str): The response to print.

    Returns:
        None
    """
    global messages
    messages.append({
        "role": "assistant",
        "content": response
    })
    print(f"{ASSISTANT_NAME}: {response}")
    print("-"*50)


def chat(user_input):
    """
    Chat with the user.

    This function handles the interaction with the user by taking their input,
    sending it to the Azure OpenAI service, and processing the response. It 
    maintains a conversation history, manages function calls, and logs the 
    interactions for auditing purposes.

    The function performs the following steps:
    1. Appends the user's input to the messages list.
    2. Enters a loop to process the user's input until a valid response is received.
    3. Sends the user's input to the Azure OpenAI service and waits for a response.
    4. Checks if the response requires a function call.
        - If a function call is required, it extracts the function name and arguments,
          calls the function, and appends the result to the messages list.
        - If no function call is required, it processes the response as a normal reply.
    5. Logs the interaction and the response for auditing purposes.
    6. Returns the response to the user.

    Args:
        user_input (str): The input provided by the user.

    Returns:
        str: The response generated by the Azure OpenAI service.
    """
    global messages
    global logger
    messages.append({
        "role": "user",
        "content": user_input
    })

    user_reply = False
    while user_reply == False:
        reference_doc_id = None
        # manual opentelemetry span creation
        with tracer.start_as_current_span("call_llm"):
            response = client.chat.completions.create(
                                model=AZURE_OPENAI_DEPLOYMENT_NAME,
                                messages=messages,
                                stream=False,
                                functions= function_definitions
                        )
        choice = response.choices[0]
        if choice.finish_reason == "function_call":
            function_call = choice.message.function_call
            function_name = function_call.name
            function_args = function_call.arguments
            if isinstance(function_args, str):
                function_args = json.loads(function_args)
            print_pretty_response(f"Calling {function_name} with arguments: {function_args}")

            logger.info(f"Calling function {function_name} with arguments: {function_args}")
            # We will add a manual span with the name of the function being called
            # this way we can track the time spent in each function


            ############################
            # LAB: Improve tracing
            ############################
            # Hint: Add a manual span for each function call
            #with tracer.start_as_current_span(function_name):
            if True: # this is a placeholder for the manual span comment this if you uncomment the trace line
                function = function_functions[function_name]
                response = function(**function_args)
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": json.dumps(function_args),
                    },
                }
            )
            messages.append(
                {
                    "role": "function", 
                    "name": function_name, 
                    "content": f'{{"result": {str(response)} }}'}
            )
            if isinstance(response, dict) and "type" in response and response["type"] == "search-result":
                # HINT: *cough* audit log *cough*
                reference_doc_id = response["id"]
        else:
            user_reply = True
            user_response = choice.message.content

            ############################
            # LAB: Audit log
            ############################
            # Hint: Log the user's input and the response for auditing purposes
            # Look at what is available to log and create a rich audit log

            # Let's print out the response datastructure so we can see what info we might want to add to the audit log.
            # Uncomment these lines to see the datastructure
            #print("Response datastructure:")
            #print(response.model_dump_json(indent=3))

            audit_message = f'User {user_name} asked {user_input}'
            audit_context = {}
            audit_context['reply'] = response
            audit_context['query'] = user_input
            audit_context['doc_references'] = []

            logger.info(audit_message,extra=audit_context)

            ############################
            # LAB: Add events to the trace
            ############################
            # Another way to pass etra information is to us events on the span
            # This is very similar to writing a log but is specific to otel
            # Add a span event for the user interaction
            current_span = trace.get_current_span()
            current_span.add_event(
                "User interaction",
                {
                    "user_name": user_name,
                    "user_input": user_input,
                    "response": user_response,
                    "reference_doc_id": []
                }
            )

            if response == None:
                print("Something went wrong")
                print(choice)
                response = "Something went wrong"
    return user_response


def main():
    """
    This function sets up the argument parser, configures logging, and handles user interaction
    for a chat application. It performs the following steps:
    1. Parses command-line arguments to set the logging level.
    2. Configures the logging level based on the parsed arguments.
    3. Prints an ASCII art introduction using the configured assistant name.
    4. Attempts to load the user's name from a pickle file. If the name is not found, prompts the user
       to enter their name and saves it to the pickle file.
    5. Greets the user and asks how it can assist them.
    6. Enters a loop to handle user input:
       - If the user types 'exit' or 'quit', the chat ends.
       - Otherwise, it generates a response using the chat function and prints it.
    Note:
    - The function uses global variables: `user_name`.
    - The function assumes the existence of certain external modules and variables such as `argparse`, 
      `logging`, `art`, `ASSISTANT_NAME`, `pickle`, `print_pretty_response`, `tracer`, `trace`, and `chat`.
    Raises:
    - SystemExit: If the argument parsing fails.
    """
    
    
    global user_name

    # We want the user to be able to easily vary the logging level
    parser = argparse.ArgumentParser(description="A sample Python script.")
    parser.add_argument('--log-level', type=str, default='INFO', help='Set the logging level')
    args = parser.parse_args()
    log_level = args.log_level
    print(f"Log level set to: {log_level}")
    logging.getLogger().setLevel(log_level)


    ############################
    # Start the chat application
    ############################
    logger.info("Starting the chat application")
    # Print a nice introduction using the configured assistant name
    ascii_art = art.text2art(ASSISTANT_NAME)
    print(ascii_art)

    # We are going to save the users name in a pickle file
    # Define the path to the pickle file
    memory_file = "memory.pkl"
    global user_name
    # Try to load the user's name from the pickle file
    try:
        with open(memory_file, "rb") as f:
            memory = pickle.load(f)
            user_name = memory.get("user_name")
            logger.info(f"Loaded user name: {user_name}")
    except (FileNotFoundError, EOFError):
        memory = {}
        user_name = None

    # If the user's name is not found, ask for it and store it in the pickle file
    if not user_name:
        user_name = input("What's your name? ")
        memory["user_name"] = user_name
        with open(memory_file, "wb") as f:
            logger.info(f"Saved user name: {user_name}")
            pickle.dump(memory, f)
        print_pretty_response(f"Nice to meet you, {user_name}!")
    else:
        print_pretty_response(f"Welcome back, {user_name}!")

    # Print a helpful message to the user
    print_pretty_response(f"How can I assist you today? (Type 'exit' or 'quit' to end the chat./\nIf you aren't sure what to ask me just ask 'What can you do?' or 'Is it raining where I am?')")

    ############################
    # Main chat loop
    ############################
    while True:
        user_input = input("You: > ")
        print("-"*50)
        if user_input.lower() in ["exit", "quit"]:
            logger.info("User ended the chat")
            print_pretty_response("Goodbye!")
            break
        else:
            # Generate a response using Azure OpenAI
            #assistant_response = generate_response(context)
            with tracer.start_as_current_span("handle_chat"):
                current_span = trace.get_current_span()
                current_span.add_event("This is a span event")
                assistant_response = chat(user_input)
                print_pretty_response(assistant_response)


if __name__ == "__main__":
    
    main()
