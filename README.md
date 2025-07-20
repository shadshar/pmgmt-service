# Patch Management Service (pmgmt-service)

A web-based service for collecting and displaying package update information from multiple hosts.

## Features

- API endpoint for receiving update data from pmgmt-agent instances
- Authentication using API keys
- SQLite database for storing update information
- Web dashboard for viewing update status across hosts
- Host and API key management

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/pmgmt-service.git
cd pmgmt-service

# Set up Python environment with pyenv
pyenv install 3.10.0  # or your preferred version
pyenv local 3.10.0

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

## Configuration

The service is configured using environment variables:

- `PMGMT_PORT`: Port to run the service on (default: 3716)
- `PMGMT_DB_PATH`: Path to the SQLite database file (default: `pmgmt.db`)
- `PMGMT_USERNAME`: Username for dashboard login
- `PMGMT_PASSWORD`: Password for dashboard login

## Usage

```bash
# Set required environment variables
export PMGMT_USERNAME=admin
export PMGMT_PASSWORD=secure_password

# Run the service
pmgmt-service
```

The service will be available at:
- Dashboard: http://localhost:3716/
- API: http://localhost:3716/api/updates