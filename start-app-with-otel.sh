#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Check if .env file exists
if [ ! -f config/.env ]; then
    echo ".env file not found!"
    exit 1
fi

# Loop through each line in the .env file
while IFS= read -r line; do
    # Strip leading and trailing whitespace from the line
    line=$(echo "$line" | xargs)
    if [[ -n "$line" && ! "$line" =~ ^# ]]; then
        # Extract KEY and VALUE from the line
        KEY=$(echo "$line" | cut -d '=' -f 1)
        VALUE=$(echo "$line" | cut -d '=' -f 2-)
        if [[ "$KEY" == *OTEL* ]]; then
            VALUE=$(echo "$VALUE" | sed 's/^"//;s/"$//')
            VALUE="$VALUE"
            export "$KEY=$VALUE"
        fi  fi
done < config/.env

# Verify that essential environment variables are set
: "${OTEL_RESOURCE_ATTRIBUTES:?Need to set OTEL_RESOURCE_ATTRIBUTES in .env}"
: "${OTEL_EXPORTER_OTLP_ENDPOINT:?Need to set OTEL_EXPORTER_OTLP_ENDPOINT in .env}"
: "${OTEL_EXPORTER_OTLP_HEADERS:?Need to set OTEL_EXPORTER_OTLP_HEADERS in .env}"

echo "Starting the application with OpenTelemetry instrumentation..."

# Run the application with OpenTelemetry instrumentation
opentelemetry-instrument python main.py
