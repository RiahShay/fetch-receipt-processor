
# Receipt Processor

## Overview
This project implements a web service to process retail receipts and calculate reward points based on specific rules. It provides two main API endpoints: one to process a receipt and generate a unique ID, and another to retrieve the points associated with that receipt ID. The points are awarded based on rules like the retailer name length, purchase totals, number of items, and time of purchase. The solution is designed to use in-memory data storage, and no persistence is required.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Docker](#docker)
- [Improvements](#improvements)

## Installation

### Prerequisites
Make sure you have Python 3.8 or later installed. If not, continue to [Docker](#docker) section for container run instructions

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/RiahShay/fetch-receipt-processor.git
   cd fetch-receipt-processor
   ```

2. Set up a virtual environment (optional but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Provide basic instructions on how to use the project. This may include examples of how to run scripts, start services, or interact with the software.

For example:

1. Run the main script:

   ```bash
   PYTHONPATH=./app uvicorn app.main:app --port 8080 --reload
   ```

2. Access the web service at:

   ```
   http://localhost:8080
   ```

## File Structure

```plaintext
fetch-receipt-processor/
│
├── app/                        # Source code files
│   ├── main.py                 # Entry point of the application
│   ├── receipt_processor.py    # Helper functions
│   └── ...                     # Other source code files
│
├── tests/                # Unit tests
│   ├── test_main.py     # Test for helper functions
│   └── ...               # Other test files
│
├── Dockerfile            # Dockerfile to build the project container
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── .gitignore            # Git ignore file
```

## Docker

### Build the Docker Image

To build the Docker image, make sure you're in the root directory of the project (where the `Dockerfile` is located), and then run:

```bash
docker build -t receipt-processor .
```

This command will build the Docker image using the `Dockerfile` and tag it as `receipt-processor`.

### Run the Docker Container

Once the image is built, you can run the container with the following command:

```bash
docker run -d --name receipt-processor-container -p 8080:8080 receipt-processor
```

This will run the application in the background, exposing it on port `8080`. Adjust the port as necessary depending on your application's configuration.


## Testing

### Running Tests

We use `pytest` for testing. To run the tests, make sure you have the dependencies installed and run the following from the root directory:

```bash
pytest
```

### Writing Tests

Tests are located in the `tests/` directory. Each module should have a corresponding test file in this directory.


### Improvements
Improvements
1. Idempotency for Repeated Requests
I added payload hashing to handle repeated requests with the same receipt. If the same request comes in again, it’s ignored to prevent duplicate processing.

2. User/Error Safeguard for Repeated Requests
To avoid processing the same request multiple times (by the user or system), I added a safeguard. It checks for duplicate requests based on the payload hash and prevents redundancy.

3. Local and Docker Dev Setup
I made sure the app works both locally and in Docker. This means you can easily switch between environments without issues, with the app automatically handling file paths and imports for both setups.

4. Logging for Debugging
I set up logging to track key events, errors, and request data. This helps with debugging and understanding the app’s behavior in development and production.