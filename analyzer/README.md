# Analyzer

A unified FastAPI service for end-to-end package and repository health analysis. The analyzer provides a single orchestrator endpoint that takes a dependency manifest (e.g., requirements.txt, package.json) and returns a comprehensive health report for all dependencies, including package metadata and repository health metrics.

## Features
- Supports Python (PyPI), JavaScript (npm), and more
- Parses requirements.txt, package.json, pyproject.toml, environment.yml, poetry.lock
- Fetches package metadata and repository URLs
- Performs health checks on GitHub and GitLab repositories
- Configurable health policy (inactivity threshold, require license/readme, etc.)
- Docker and CI/CD ready

## API Endpoints

### `POST /v1/analyze`

Analyze a manifest and return a health report for all dependencies.

#### Request Body
```json
{
  "manifest_content": "<contents of your manifest file>",
  "manifest_type": "requirements.txt | package.json | pyproject.toml | environment.yml | poetry.lock",
  "policy": {
    "max_inactive_days": 365,
    "require_license": true,
    "require_readme": true
  }
}
```
- `manifest_content`: The raw text of your dependency manifest
- `manifest_type`: The type of manifest (required)
- `policy`: (Optional) Health policy configuration

#### Response
Returns a list of results, one per dependency, with package info and repository health metrics.

## Examples

### Python (requirements.txt)
```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_content": "requests\nfastapi\npytest",
    "manifest_type": "requirements.txt"
  }'
```

### Node.js (package.json)
```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_content": "{\"dependencies\":{\"express\":\"^4.18.2\",\"lodash\":\"^4.17.21\"}}",
    "manifest_type": "package.json"
  }'
```

### Python (pyproject.toml)
```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_content": "[tool.poetry.dependencies]\npython = \"^3.10\"\nrequests = \"^2.28.1\"",
    "manifest_type": "pyproject.toml"
  }'
```

### Conda (environment.yml)
```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_content": "name: myenv\ndependencies:\n  - python=3.10\n  - numpy\n  - pandas",
    "manifest_type": "environment.yml"
  }'
```

### Poetry (poetry.lock)
```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_content": "[[package]]\nname = \"requests\"\nversion = \"2.28.1\"",
    "manifest_type": "poetry.lock"
  }'
```

### With Custom Policy
```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_content": "requests\nfastapi",
    "manifest_type": "requirements.txt",
    "policy": {
      "max_inactive_days": 180,
      "require_license": false,
      "require_readme": true
    }
  }'
```

### `POST /v1/analyze/file`

### Using a Manifest File as Input
```bash
curl -X POST http://127.0.0.1:8000/v1/analyze/file \
  -H "Content-Type: multipart/form-data" \
  -F "file=@requirements.txt"
```

## Configuration

For repository health checks, set your GitHub and GitLab tokens in a `.env` file in the project root:
```
GITHUB_TOKEN=your_github_token
GITLAB_TOKEN=your_gitlab_token
```

## Running with Docker Compose

From the project root:
```bash
docker-compose up --build
```
The analyzer API will be available at http://localhost:8000

## Development
- Python 3.12+
- Install dependencies: `pip install -r requirements.txt`
- Run locally: `uvicorn app:app --reload --host 0.0.0.0 --port 8000`
- Run tests: `pytest`