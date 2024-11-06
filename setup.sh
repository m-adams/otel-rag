#!/bin/bash

# Navigate to the directory containing the script
cd "$(dirname "$0")"


# We have seen some compatibility issues with the latest version of python
# Stop and give a warning message if the python version is not between 3.4 and 3.11 inclusive
if ! python -c 'import sys; exit(0) if sys.version_info >= (3, 4) and sys.version_info < (3, 12) else exit(1)'; then
    echo "Only tested on 3.11 and there have been compatibility issues with the latest version of python."
    echo "Strong reccomend using python 3.11 or before."
    echo "do you want to continue? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Continuing with the installation..."
    else
        echo "Exiting..."
        exit 1
    fi
    
fi

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


cp -rn ./example-config/.* ./example-config/* ./config/