import typer
import json
from pathlib import Path
from extractor.extractor.requirements_txt import extract_requirements_txt
from extractor.extractor.environment_yml import extract_environment_yml
from extractor.extractor.pyproject_toml import extract_pyproject_toml
from extractor.extractor.package_json import extract_package_json
from extractor.extractor.poetry_lock import extract_poetry_lock

app = typer.Typer(help="Vitalis - Dependency manifest extractor and analyzer")

def _print_fallback_human_readable(deps_data):
    """Print fallback extraction result in human-readable format"""
    typer.echo("📦 Basic Dependency Extraction")
    typer.echo("=" * 40)
    typer.echo(f"\nFound {len(deps_data)} dependencies:")

    for dep in deps_data:
        name = dep.get("name", "Unknown")
        version = dep.get("version", "Unknown")
        typer.echo(f"• {name} ({version})")

    typer.echo(f"\n   Note: Full analysis unavailable (analyzer service offline)")

@app.command()
def extract(
    file: Path = typer.Argument(..., help="Path to the manifest file"),
    manifest_type: str = typer.Option(None, help="Type of manifest: requirements.txt, environment.yml, pyproject.toml, package.json, poetry.lock"),
    format: str = typer.Option("human", "--format", help="Output format: human or json (default: human)")
):
    """Extract dependencies from a manifest file"""
    if not file.exists():
        typer.echo(f"File not found: {file}", err=True)
        raise typer.Exit(1)

    # Infer manifest type from file name if not provided
    if not manifest_type:
        name = file.name.lower()
        if name == 'requirements.txt':
            manifest_type = 'requirements.txt'
        elif name == 'environment.yml':
            manifest_type = 'environment.yml'
        elif name == 'pyproject.toml':
            manifest_type = 'pyproject.toml'
        elif name == 'package.json':
            manifest_type = 'package.json'
        elif name == 'poetry.lock':
            manifest_type = 'poetry.lock'
        else:
            typer.echo("Could not infer manifest type. Please specify --manifest-type.", err=True)
            raise typer.Exit(1)

    # Extract dependencies based on manifest type
    if manifest_type == 'requirements.txt':
        deps = extract_requirements_txt(str(file))
    elif manifest_type == 'environment.yml':
        deps = extract_environment_yml(str(file))
    elif manifest_type == 'pyproject.toml':
        deps = extract_pyproject_toml(str(file))
    elif manifest_type == 'package.json':
        deps = extract_package_json(str(file))
    elif manifest_type == 'poetry.lock':
        deps = extract_poetry_lock(str(file))
    else:
        typer.echo(f"Unsupported manifest type: {manifest_type}", err=True)
        raise typer.Exit(1)

    # Format output
    deps_data = [dep.__dict__ for dep in deps]
    if format == "json":
        typer.echo(json.dumps(deps_data, indent=2))
    else:
        _print_fallback_human_readable(deps_data)

@app.command()
def health():
    """Check the health of the vitalis CLI"""
    typer.echo("Vitalis CLI is healthy!")

if __name__ == "__main__":
    app()