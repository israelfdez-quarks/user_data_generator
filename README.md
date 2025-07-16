# Users Data Generator

A Python application that retrieves and processes user data from multiple sources, including:

- Higyrus API.
- BeClever
- ??

## Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) (An extremely fast Python package and project manager)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd users-data-generator
   ```

2. Install the package and its dependencies:
   ```bash
   uv sync
   ```

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root with the
following variables:

```
HIGYRUS_API_URL=https://api-url/
HIGYRUS_API_USER=user
HIGYRUS_API_PASSWORD=passwd

BECLEVER_DB_CONN_STR=DSN=some-ds-name

AL2SYNC_DB_CONN_STR=DSN=some-other-ds-name
```

Replace the values with actual credentials.

## Usage

### Using the Makefile

The project includes a Makefile to simplify common operations:

```bash
# Initialize a new virtual environment with uv
make init

# Install dependencies using uv (runs 'uv sync')
make deps

# Run the main.py script using uv
make run

# Remove virtual environment and generated files
make clean

# Show help message with available targets
make help
```

### Running the Application Manually

If you prefer not to use the Makefile, you can run the application directly:

```bash
uv run main.py
```

This will retrieve information from all available data sources, combine their data, and save the result to a CSV file.

