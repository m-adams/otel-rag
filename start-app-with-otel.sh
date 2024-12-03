#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Check if .env file exists
if [ ! -f config/.env ]; then
    echo ".env file not found!"
    exit 1
fi
# Export all variables from the .env file
set -o allexport
source ./config/.env
set +o allexport



# Verify that essential environment variables are set and exported
if [ -z "${OTEL_RESOURCE_ATTRIBUTES+x}" ]; then
    echo "OTEL_RESOURCE_ATTRIBUTES is not set or exported in the environment!"
    exit 1
fi

if [ -z "${OTEL_EXPORTER_OTLP_ENDPOINT+x}" ]; then
    echo "OTEL_EXPORTER_OTLP_ENDPOINT is not set or exported in the environment!"
    exit 1
fi

if [ -z "${OTEL_EXPORTER_OTLP_HEADERS+x}" ]; then
    echo "OTEL_EXPORTER_OTLP_HEADERS is not set or exported in the environment!"
    exit 1
fi

# Run the application with OpenTelemetry instrumentation
opentelemetry-instrument python main.py
