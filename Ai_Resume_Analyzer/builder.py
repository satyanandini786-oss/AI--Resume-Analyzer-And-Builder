"""
builder.py
Handles turning form input (collected in app.py) into a saved .docx resume,
dispatching to the chosen template in templates/.
"""

import os
from datetime import datetime

from templates import modern, professional

TEMPLATE_MAP = {
    "Modern": modern.build_resume,
    "Professional": professional.build_resume,
}


def build_resume(data: dict, template_name: str = "Modern", output_dir: str = "generated") -> str:
    """
    Build a resume docx using the selected template and save it into output_dir.
    Returns the path to the generated file.
    """
    if template_name not in TEMPLATE_MAP:
        raise ValueError(f"Unknown template '{template_name}'. Choose from {list(TEMPLATE_MAP)}")

    os.makedirs(output_dir, exist_ok=True)

    safe_name = (data.get("name") or "resume").strip().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{template_name}_{timestamp}.docx"
    output_path = os.path.join(output_dir, filename)

    build_fn = TEMPLATE_MAP[template_name]
    return build_fn(data, output_path)


def parse_comma_list(text: str) -> list:
    """Helper: turn a comma-separated string into a clean list."""
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]