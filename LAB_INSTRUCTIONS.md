
# Self-Paced Tutorial

## Prerequisites
- An Elastic cluster with data to search
- APM server running for your Elastic cluster
- An OpenAI model running in Azure

## Initial Configuration
1. **Generate an API key in Elastic**: This key should have permissions to search your documents.
2. **Note down the APM server Endpoint and Otel Headers**: These can be found in Kibana.
3. **Note down the Azure API key for the OpenAI model**.
4. **Configure your environment variables**: Set these in the `.env` file.
5. **Configure the `corpus_description.txt` file**: Provide a description of the documents you want to search.
6. **Modify the `query_template.json` file**: Adjust this file to search your documents. You might want to prototype this using the Playground in Kibana.

## Familiarization
1. **Open `start-app.sh`**: Set the log level to `ERROR` to disable most logs.
2. **Run the `start-app.sh` script**: This will start the application.
3. **Interact with the chatbot**: Have a few conversations, maybe ask "What can you do?"
4. **Review `main.py`**: Understand the structure of the code and how it works. The main logic is in the `chat` function.

## Instrumentation
1. **Open `start-app.sh`**: Set the log level to `INFO` to enable most logs.
2. **Run the `start-app.sh` script**: This will start the application.
3. **Interact with the chatbot**: Have a few conversations, including a question that will search Elastic.
4. **Observe the logs**: Notice both the logs in `main` as well as the libraries being printed to the console along with the chat messages.
5. **Configure OpenTelemetry**: Set it up to send logs to Elastic.
6. **Review `start-app-with-otel.sh`**: See how the OTEL environment variables are set and how auto instrumentation is used to send logs and traces to Elastic.
7. **Run the `start-app-with-otel.sh` script**: This will start the application.
8. **Interact with the chatbot**: Have a few conversations, including a question that will search Elastic.
9. **Check Kibana**: Go to the APM section to see traces and logs from the chatbot.

## Optimization of APM
1. **Improve the trace**: Manually specify some spans. Look through the important parts of the code to find the commented span definitions.
2. **Uncomment the span definitions**: Run the `start-app-with-otel.sh` script to start the application (don't forget to comment the `if True:` block which handles indent changes in the code).
3. **Interact with the chatbot**: Have a few conversations, including a question that will search Elastic.
4. **Check Kibana**: Go to the APM section to see the spans you defined in the code.
5. **Install OpenTelemetry Instrumentation for OpenAI**: Run `pip install opentelemetry-instrumentation-openai` to add OpenTelemetry support for OpenAI API calls.
6. **Check the improved trace**: Run the `start-app-with-otel.sh` script to start the application. Generate some traffic and then check the waterfall for your improved trace to see the details of the OpenAI API call.

## Audit Logging
1. **Enhance audit logging**: Improve the existing simple audit log by adding more information.
2. **Run the `start-app-with-otel.sh` script**: This will start the application.
3. **Interact with the chatbot**: Have a few conversations, including a question that will search Elastic.
4. **Check Kibana**: You should see the audit log messages in the Transaction section, but you can also find them under the `logs-apm.app.<your app name>` data stream.

## Dashboard
1. **Create a dashboard in Kibana**: Show the logs and traces from the chatbot.
2. **Make the dashboard impactful**: Combine information from the traces and logs.
3. **Share the dashboard**: Share it with the rest of the team.