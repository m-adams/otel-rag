#!/bin/bash

# Navigate to the directory containing the script
cd "$(dirname "$0")"

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    echo "requirements.txt not found!"
    exit 1
fi

# Install dependencies from requirements.txt
pip install -r requirements.txt

echo "Dependencies installed successfully."

echo "Installing OpenTelemetry instrumentation packages..."

# Install OpenTelemetry instrumentation packages based on installed libraries
opentelemetry-bootstrap --action=install

# Elasticsearch is now natively supported so this causes a warning message
pip uninstall -y opentelemetry-instrumentation-elasticsearch

# Check and copy example.corpus_description.txt to corpus_description.txt
if [ ! -f corpus_description.txt ] && [ -f example.corpus_description.txt ]; then
    cp example.corpus_description.txt corpus_description.txt
    echo "Copied example.corpus_description.txt to corpus_description.txt"
fi

# Check and copy example.env to .env
if [ ! -f .env ] && [ -f example.env ]; then
    cp example.env .env
    echo "Copied example.env to .env"
fi

# Check and copy example.query_template.json to query_template.json
if [ ! -f query_template.json ] && [ -f example.query_template.json ]; then
    cp example.query_template.json query_template.json
    echo "Copied example.query_template.json to query_template.json"
fi