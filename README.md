# Patch Management Service (pmgmt-service)

> [!WARNING]
> This tool and its companion, pmgmt-agent, have been (almost) entirely vibe coded. Barely anything in either of these repos has been reviewed by a professional software developer. Do not rely on this for anything even remotely resembling production use.
> This is a hobby project. Vibe coding this does not constitute an endorsement of Ai tools.

A web-based service for collecting and displaying package update information from multiple hosts.

## Features

- API endpoint for receiving update data from pmgmt-agent instances
- Authentication using API keys
- SQLite database for storing update information
- Web dashboard for viewing update status across hosts
- Host and API key management
- Docker support for easy deployment

## Installation

### Standard Installation

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

### Docker Installation

The service can be easily deployed using Docker:

```bash
# Clone the repository
git clone https://github.com/your-org/pmgmt-service.git
cd pmgmt-service

# Build and start the container
docker-compose up -d
```

## Configuration

The service is configured using environment variables:

- `PMGMT_PORT`: Port to run the service on (default: 3716)
- `PMGMT_DB_PATH`: Path to the SQLite database file (default: `pmgmt.db`)
- `PMGMT_USERNAME`: Username for dashboard login
- `PMGMT_PASSWORD`: Password for dashboard login

## Usage

### Running Locally

```bash
# Set required environment variables
export PMGMT_USERNAME=admin
export PMGMT_PASSWORD=secure_password

# Run the service
pmgmt-service
```

### Running with Docker

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

When using Docker, you can modify the environment variables in the `docker-compose.yaml` file.

The service will be available at:
- Dashboard: http://localhost:3716/
- API: http://localhost:3716/api/updates

## Docker Customization

You can customize the Docker deployment by modifying the `docker-compose.yaml` file:

```yaml
version: '3.8'

services:
  pmgmt-service:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3716:3716"  # Change the host port if needed (format: "host:container")
    volumes:
      - pmgmt-data:/data  # Persistent volume for the database
    environment:
      - PMGMT_PORT=3716
      - PMGMT_DB_PATH=/data/pmgmt.db
      - PMGMT_USERNAME=admin  # Change this!
      - PMGMT_PASSWORD=changeme  # Change this!
    restart: unless-stopped

volumes:
  pmgmt-data:
```