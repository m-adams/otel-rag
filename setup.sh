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

# List of example files and their corresponding real filenames
declare -A files=(
    ["example.corpus_description.txt"]="corpus_description.txt"
    ["example.env"]=".env"
    ["example.query_template.json"]="query_template.json"
)

# Copy example files to their real filenames if they don't exist
for example_file in "${!files[@]}"; do
    real_file="${files[$example_file]}"
    if [ ! -f "$real_file" ] && [ -f "$example_file" ]; then
        cp "$example_file" "$real_file"
        echo "Copied $example_file to $real_file"
    fi
done