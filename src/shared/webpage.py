"""Shared WebPage singleton for Jinja2 template rendering."""
from pathlib import Path

from fastapi_webpage import WebPage

_templates_dir = Path(__file__).parents[1] / "templates"

webpage = WebPage(template_directory=str(_templates_dir))
