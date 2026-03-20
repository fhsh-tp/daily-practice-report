"""Shared WebPage singleton for Jinja2 template rendering."""
from pathlib import Path

from fastapi_webpage import WebPage
from shared.gravatar import gravatar_url

_templates_dir = Path(__file__).parents[1] / "templates"

webpage = WebPage(template_directory=str(_templates_dir))
webpage._template.env.filters["gravatar_url"] = gravatar_url
