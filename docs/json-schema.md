# JSON Schema Documentation

This document describes the JSON output format for the Vitalis CLI when using `--format json`.

## Usage

```bash
vitalis extract requirements.txt --format json
```

## Schema Overview

The JSON output varies depending on whether the full analyzer service is available or if the CLI falls back to basic extraction.

## Full Analysis Output (Analyzer Service Available)

When the analyzer service is available, the output follows this schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "dependencies": {
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
          },
          "health": {
            "type": "object",
            "properties": {
              "is_healthy": {
                "type": "boolean",
                "description": "Overall health status"
              },
              "repository_url": {
                "type": ["string", "null"],
                "description": "Repository URL"
              },
              "platform": {
                "type": ["string", "null"],
                "description": "Platform (e.g., 'github', 'gitlab')"
              },
              "owner": {
                "type": ["string", "null"],
                "description": "Repository owner/organization"
              },
              "repo_name": {
                "type": ["string", "null"],
                "description": "Repository name"
              },
              "last_activity": {
                "type": ["string", "null"],
                "description": "ISO 8601 timestamp of last activity"
              },
              "days_since_last_activity": {
                "type": ["integer", "null"],
                "description": "Days since last repository activity"
              },
              "open_issues_count": {
                "type": ["integer", "null"],
                "description": "Number of open issues"
              },
              "stars_count": {
                "type": ["integer", "null"],
                "description": "Number of repository stars"
              },
              "forks_count": {
                "type": ["integer", "null"],
                "description": "Number of repository forks"
              },
              "has_readme": {
                "type": "boolean",
                "description": "Whether repository has README"
              },
              "has_license": {
                "type": "boolean",
                "description": "Whether repository has LICENSE"
              },
              "warnings": {
                "type": "array",
                "items": {
                  "type": "string"
                },
                "description": "Health check warnings"
              },
              "errors": {
                "type": "array",
                "items": {
                  "type": "string"
                },
                "description": "Health check errors"
              }
            },
            "required": ["is_healthy", "has_readme", "has_license", "warnings", "errors"]
          }
        },
        "required": ["name"]
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "total_dependencies": {
          "type": "integer",
          "description": "Total number of dependencies analyzed"
        },
        "healthy_count": {
          "type": "integer",
          "description": "Number of healthy dependencies"
        },
        "unhealthy_count": {
          "type": "integer",
          "description": "Number of dependencies with health issues"
        }
      },
      "required": ["total_dependencies", "healthy_count", "unhealthy_count"]
    },
    "policy": {
      "type": "object",
      "properties": {
        "max_inactive_days": {
          "type": "integer",
          "description": "Maximum days of inactivity before flagging as unhealthy"
        },
        "require_license": {
          "type": "boolean",
          "description": "Whether LICENSE file is required"
        },
        "require_readme": {
          "type": "boolean",
          "description": "Whether README file is required"
        }
      },
      "required": ["max_inactive_days", "require_license", "require_readme"]
    }
  },
  "required": ["dependencies"]
}
```

## Fallback Output (Basic Extraction)

When the analyzer service is unavailable, the output is simplified:

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

### Full Analysis Example

```json
{
  "dependencies": [
    {
      "name": "requests",
      "version": "2.25.0",
      "source": "pypi",
      "raw": "requests==2.25.0",
      "health": {
        "is_healthy": true,
        "repository_url": "https://github.com/psf/requests",
        "platform": "github",
        "owner": "psf",
        "repo_name": "requests",
        "last_activity": "2023-12-01T10:30:00Z",
        "days_since_last_activity": 45,
        "open_issues_count": 123,
        "stars_count": 45000,
        "forks_count": 8500,
        "has_readme": true,
        "has_license": true,
        "warnings": [],
        "errors": []
      }
    }
  ],
  "summary": {
    "total_dependencies": 1,
    "healthy_count": 1,
    "unhealthy_count": 0
  },
  "policy": {
    "max_inactive_days": 365,
    "require_license": true,
    "require_readme": true
  }
}
```

### Fallback Example

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
vitalis extract requirements.txt --format json | jq '.summary.unhealthy_count'

# Check for health issues
if vitalis extract requirements.txt --format json | jq -e '.summary.unhealthy_count > 0' > /dev/null; then
  echo "Health issues detected"
  exit 1
fi
```