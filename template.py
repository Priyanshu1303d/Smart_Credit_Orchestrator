import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] : %(message)s")

project_name = "Smart_Credit_Orchestrator"

files_to_create = [
    ".env",
    ".env.example",
    "requirements.txt",
    "README.md",
    "main.py",
    "streamlit/ui/app.py",
    ".gitignore",
    "Dockerfile",

    "src/__init__.py",

    f"src/{project_name}/api/__init__.py",
    f"src/{project_name}/api/routes.py",
    f"src/{project_name}/api/models.py",

    f"src/{project_name}/graph/__init__.py",
    f"src/{project_name}/graph/state.py",
    f"src/{project_name}/graph/nodes.py",
    f"src/{project_name}/graph/edges.py",
    f"src/{project_name}/graph/workflow.py",

    f"src/{project_name}/services/__init__.py",
    f"src/{project_name}/services/llm_service.py",
    f"src/{project_name}/services/email_service.py",
    f"src/{project_name}/services/escalation_service.py",
    f"src/{project_name}/services/validation_service.py",
    f"src/{project_name}/services/audit_service.py",

    f"src/{project_name}/models/__init__.py",
    f"src/{project_name}/models/invoice.py",
    f"src/{project_name}/models/email_log.py",
    f"src/{project_name}/models/response_models.py",

    f"src/{project_name}/prompts/__init__.py",
    f"src/{project_name}/prompts/stage1.py",
    f"src/{project_name}/prompts/stage2.py",
    f"src/{project_name}/prompts/stage3.py",
    f"src/{project_name}/prompts/stage4.py",

    f"src/{project_name}/database/__init__.py",

    f"src/{project_name}/utils/__init__.py",
    f"src/{project_name}/utils/logger.py",
    f"src/{project_name}/utils/helpers.py",
    f"src/{project_name}/utils/security.py",

    "data/sample_invoices.csv",
    "data/generated_logs.json",

    "notebooks/.gitkeep",
    "tests/__init__.py",
    "tests/test_escalation.py",
    "tests/test_validation.py",
    "screenshots/.gitkeep",
]

for filepath in files_to_create:
    filepath = Path(filepath)
    folder = filepath.parent

    if folder != Path(""):
        os.makedirs(folder, exist_ok=True)
        logging.info(f"Created folder: {folder}")

    if not filepath.exists():
        filepath.touch()
        logging.info(f"Created file: {filepath}")
    else:
        logging.info(f"File exists: {filepath}")
