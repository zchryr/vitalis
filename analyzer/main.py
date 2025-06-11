from fastapi import FastAPI, HTTPException, UploadFile, File
from .models.schemas import AnalysisRequest, Policy
from .services import dependency_extractor, package_info, repo_health
from .services.repo_health import GITHUB_TOKEN, GITLAB_TOKEN

# Initialize FastAPI app
app = FastAPI()

@app.post("/v1/analyze")
def analyze(request: AnalysisRequest):
    """
    Analyze the provided manifest content to extract dependencies, fetch package info, and check repository health.
    Args:
        request (AnalysisRequest): The analysis request containing manifest content, type, and policy.
    Returns:
        dict: Results for each dependency including package info and health check.
    """
    # 1. Extract dependencies from manifest content
    manifest_type = request.manifest_type.lower()
    content = request.manifest_content

    # Map manifest types to their respective extractor functions
    extractor_map = {
        'requirements.txt': dependency_extractor.extract_requirements_txt_from_content,
        'package.json': dependency_extractor.extract_package_json_from_content,
        'pyproject.toml': dependency_extractor.extract_pyproject_toml_from_content,
        'environment.yml': dependency_extractor.extract_environment_yml_from_content,
        'poetry.lock': dependency_extractor.extract_poetry_lock_from_content
    }

    if manifest_type not in extractor_map:
        # Raise error if manifest type is not supported
        raise HTTPException(status_code=400, detail=f"Unsupported manifest type: {manifest_type}")

    # Extract dependencies using the appropriate extractor
    dependencies = extractor_map[manifest_type](content)
    results = []

    for dep in dependencies:
        # 2. Get package info and repo URL
        if dep.source in ['pypi', 'poetry', 'poetry.lock', 'pip', 'conda']:
            # For 'conda' and 'pip', treat as PyPI package if possible
            info = package_info.get_library_info(dep.name)
            if not info:
                # For conda, clarify it may be a conda-only or system package
                if dep.source == 'conda':
                    results.append({
                        "dependency": dep.name,
                        "error": True,
                        "message": f"Could not fetch info for {dep.name} from PyPI. This may be a conda-only or system package."
                    })
                else:
                    results.append({
                        "dependency": dep.name,
                        "error": True,
                        "message": f"Could not fetch info for {dep.name} from PyPI"
                    })
                continue
            package_info_data = info.get("info", {})
            repo_url, platform, org, repo = package_info.extract_repo_info(package_info_data)
        elif dep.source == 'npm':
            info = package_info.get_npm_info(dep.name)
            if not info:
                results.append({
                    "dependency": dep.name,
                    "error": True,
                    "message": f"Could not fetch info for {dep.name} from npmjs.org"
                })
                continue
            repo_url, platform, org, repo = package_info.extract_npm_repo_info(info)
        else:
            results.append({
                "dependency": dep.name,
                "error": True,
                "message": f"Unsupported dependency source: {dep.source}"
            })
            continue

        # 3. If repo URL found, check health
        if platform in ["github", "gitlab"] and org and repo:
            # Check health for supported platforms
            if platform == "github":
                health = repo_health.check_github_health(org, repo, request.policy, token=GITHUB_TOKEN)
            elif platform == "gitlab":
                health = repo_health.check_gitlab_health(org, repo, request.policy, token=GITLAB_TOKEN)
            results.append({
                "dependency": dep.name,
                "package_info": {
                    "summary": package_info_data.get("summary") if dep.source != 'npm' else info.get("description"),
                    "repository_url": repo_url,
                    "repository_platform": platform,
                    "repository_org": org,
                    "repository_name": repo,
                    "latest_version": package_info_data.get("version") if dep.source != 'npm' else info.get("dist-tags", {}).get("latest"),
                    "created_date": package_info.get_latest_version_release_date(info) if dep.source != 'npm' else info.get("time", {}).get(info.get("dist-tags", {}).get("latest"))
                },
                "health": health.dict()
            })
        else:
            # If no supported repo URL, return package info without health
            results.append({
                "dependency": dep.name,
                "package_info": {
                    "summary": package_info_data.get("summary") if dep.source != 'npm' else info.get("description"),
                    "repository_url": repo_url,
                    "repository_platform": platform,
                    "repository_org": org,
                    "repository_name": repo,
                    "latest_version": package_info_data.get("version") if dep.source != 'npm' else info.get("dist-tags", {}).get("latest"),
                    "created_date": package_info.get_latest_version_release_date(info) if dep.source != 'npm' else info.get("time", {}).get(info.get("dist-tags", {}).get("latest"))
                },
                "health": None,
                "message": "No supported repository URL found for health check."
            })
    return {"results": results}

@app.post("/v1/analyze/file")
def post_file(file: UploadFile = File(...)):
    """
    Analyze a manifest file uploaded by the user. Infers manifest type from filename and delegates to analyze().
    Args:
        file (UploadFile): The uploaded manifest file.
    Returns:
        dict: Analysis results for the uploaded file.
    """
    # Infer manifest type from filename
    filename = file.filename.lower()
    manifest_type_map = {
        "requirements.txt": "requirements.txt",
        "package.json": "package.json",
        "pyproject.toml": "pyproject.toml",
        "environment.yml": "environment.yml",
        "environment.yaml": "environment.yml",
        "poetry.lock": "poetry.lock"
    }

    manifest_type = None
    for ext, type_name in manifest_type_map.items():
        if filename.endswith(ext):
            manifest_type = type_name
            break

    if not manifest_type:
        # Raise error if manifest type cannot be inferred
        raise HTTPException(status_code=400, detail=f"Could not infer manifest type from filename: {filename}")

    # Read file content and create default policy
    content = file.file.read().decode("utf-8")
    policy = Policy()
    request = AnalysisRequest(manifest_content=content, manifest_type=manifest_type, policy=policy)
    return analyze(request)