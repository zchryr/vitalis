# JSON Schema Documentation

This document describes the JSON output format for the Vitalis CLI when using `--format json`.

## Usage

```bash
vitalis extract requirements.txt --format json
```

## Schema Overview

The JSON output provides a structured array of dependency information extracted from manifest files.

## JSON Output Schema

The output follows this schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Package name"
      },
      "version": {
        "type": ["string", "null"],
        "description": "Package version specifier"
      },
      "source": {
        "type": ["string", "null"],
        "description": "Package source (e.g., 'pypi', 'npm', 'conda')"
      },
      "raw": {
        "type": ["string", "null"],
        "description": "Raw entry from manifest file"
      }
    },
    "required": ["name"]
  }
}
```

## Examples

### Example Output

```json
[
  {
    "name": "requests",
    "version": "2.25.0",
    "source": "pypi",
    "raw": "requests==2.25.0"
  },
  {
    "name": "django",
    "version": "3.2.0",
    "source": "pypi",
    "raw": "django==3.2.0"
  },
  {
    "name": "numpy",
    "version": "1.21.0",
    "source": "pypi",
    "raw": "numpy==1.21.0"
  }
]
```

## Format Validation

The JSON output can be validated using standard JSON Schema validators. The schemas provided above are compatible with JSON Schema Draft 7.

## CI/CD Integration

For CI/CD systems, the JSON format enables programmatic analysis:

```bash
# Save output to file
vitalis extract requirements.txt --format json > analysis.json

# Process with jq

# Count dependencies
vitalis extract requirements.txt --format json | jq 'length'

# Filter for specific packages
vitalis extract requirements.txt --format json | jq '.[] | select(.name == "requests")'

# Get all package names
vitalis extract requirements.txt --format json | jq -r '.[].name'
```