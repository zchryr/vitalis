# Vitalis

A CLI tool for extracting and analyzing dependency manifests across multiple programming languages and package managers.

## Quick Start

```bash
pipx install vitalis
vitalis health
```

## Overview

This repository provides functionality for analyzing and monitoring package health across different programming languages and package managers. The analyzer service offers a seamless workflow from dependency manifest parsing to repository health analysis.

## Repository Structure

- `analyzer/`: The unified FastAPI service for package and repository health analysis
  - Single orchestrator endpoint for manifest-to-health-report workflow
  - Supports Python (PyPI), JavaScript (npm), and more
  - Integrates dependency extraction, package info, and repo health checks
  - Docker deployment and CI/CD support

- `extractor/`: Standalone Python tooling and GitHub Action for extracting dependencies from manifests
- `example-projects/`: Example projects in different languages for testing and demonstration

## Purpose

This repository aims to provide tools and services for:
1. Analyzing package health across different programming languages
2. Monitoring package repositories and their metadata
3. Providing insights into package dependencies and their relationships
4. Supporting development teams in making informed decisions about package usage
5. Evaluating repository health through activity metrics and documentation presence
6. Identifying potential maintenance issues through inactivity tracking

## Installation

### Production

```bash
pipx install vitalis
```

### Alternative (if pipx installed via pip)

```bash
python -m pipx install vitalis
```

### From Test PyPI

```bash
pipx install --index-url https://test.pypi.org/simple/ vitalis
```

### From Source

```bash
git clone https://github.com/zchryr/vitalis.git
cd vitalis
pip install -e .
```

## CLI Usage

The `vitalis` CLI provides commands for extracting dependencies from manifest files:

```bash
# Check CLI health
vitalis health

# Extract dependencies from a manifest file
vitalis extract requirements.txt
vitalis extract package.json
vitalis extract pyproject.toml

# Specify manifest type explicitly
vitalis extract myfile.txt --manifest-type requirements.txt
```

### Supported Manifest Types

- `requirements.txt` (Python pip)
- `pyproject.toml` (Python Poetry/setuptools)
- `poetry.lock` (Python Poetry)
- `package.json` (Node.js npm)
- `environment.yml` (Conda)

## Getting Started

### Analyzer API

The main service is now located in `analyzer`. It exposes a single orchestrator endpoint:

#### `POST /v1/analyze`

**Request Body:**
```json
{
  "manifest_content": "<string: contents of requirements.txt, package.json, etc.>",
  "manifest_type": "requirements.txt | package.json | pyproject.toml | environment.yml | poetry.lock",
  "policy": {
    "max_inactive_days": 365,
    "require_license": true,
    "require_readme": true
  }
}
```

- `manifest_content`: The raw text of your dependency manifest.
- `manifest_type`: The type of manifest (e.g., `requirements.txt`, `package.json`).
- `policy`: (Optional) Health policy configuration.

**Response:**
Returns a comprehensive health analysis for each dependency, including package metadata and repository health metrics.

## Development

The repository uses Python for the main API service and includes example projects in various languages. Development dependencies and setup instructions can be found in the respective component directories.

## Example Usage

You can use the `/v1/analyze` endpoint to analyze any supported manifest. Example with `curl`:

```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_content": "requests\nfastapi\npytest",
    "manifest_type": "requirements.txt"
  }'
```

## Authentication

For repository health checks, set your GitHub and GitLab tokens in a `.env` file in the project root:
```
GITHUB_TOKEN=your_github_token
GITLAB_TOKEN=your_gitlab_token
```

The analyzer service will load these automatically.
