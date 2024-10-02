# Chat-based RAG Chat Bot with OpenTelemetry Instrumentation

This project is a simple chat-based Retrieval-Augmented Generation (RAG) chat bot designed to let people learn about adding simple instrumentation to the application using OpenTelemetry to Elastic.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Instrumentation](#instrumentation)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This chat bot leverages Retrieval-Augmented Generation to provide more accurate and contextually relevant responses. It is instrumented with OpenTelemetry to send telemetry data to Elastic, allowing for better monitoring and observability.
Observability is extremely important in RAG architectures for a number of reasons:
- The retrieval process can be slow and expensive, so it's important to monitor performance and costs.
- The generation process can be complex and error-prone, so it's important to monitor the quality of the responses.
- The chat bot itself can be a critical part of a larger system, so it's important to monitor its availability and reliability.
- Auditability and compliance are also important, so it's important to monitor who is using the chat bot and what they are using it for.
- Regression testing and continuous integration are also important, so it's important to monitor the performance of the chat bot over time.

## Features

- Chat-based interface
- Retrieval-Augmented Generation for improved responses
- OpenTelemetry instrumentation
- Integration with Elastic for telemetry data

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/m-adams/otel-rag.git
    cd otel-rag
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
    In VS Code cmd+p to launch the command pallet and select Python: Create virtual environment

3. Check the shell scripts are executable:
    ```sh
    chmod +x ./*.sh
    ```

4. Setup the environment using the script:
    ```sh
    ./setup.sh
    ```
    
5. Set up environment variables:
    ```sh
    cp .example-env .env
    # Edit .env to include your specific configuration
    ```


## Usage

1. Start the application:
    ```sh
    ./start-app.sh
    ```

2. Interact with the chat bot through the provided interface.

## Lab Instructions
To walk through the lab to instrument the application with OpenTelemetry, see the [LAB_INSTRUCTIONS.md](LAB_INSTRUCTIONS.md) file.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.


## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.