#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e
# Export OTEL environment variables from .env file
if [ -f .env ]; then
    # Export variables that start with OTEL, ignoring lines that are comments or empty
    export $(grep -v '^#' .env | grep 'OTEL' | xargs)
else
    echo ".env file not found!"
    exit 1
fi

# Verify that essential environment variables are set
: "${OTEL_RESOURCE_ATTRIBUTES:?Need to set OTEL_RESOURCE_ATTRIBUTES in .env}"
: "${OTEL_EXPORTER_OTLP_ENDPOINT:?Need to set OTEL_EXPORTER_OTLP_ENDPOINT in .env}"
: "${OTEL_EXPORTER_OTLP_HEADERS:?Need to set OTEL_EXPORTER_OTLP_HEADERS in .env}"


echo "Starting the application with OpenTelemetry instrumentation..."

# Run the application with OpenTelemetry instrumentation
opentelemetry-instrument python main.py
