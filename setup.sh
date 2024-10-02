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

# Elasticsearch is now natively supported so this causes a conflict
pip uninstall -y opentelemetry-instrumentation-elasticsearch