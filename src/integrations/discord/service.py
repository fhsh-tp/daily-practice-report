"""Discord Webhook integration service."""
import logging

import httpx

logger = logging.getLogger(__name__)

_EMBED_COLOR = 0x7C3AED  # brand purple
_MAX_DESC = 200


async def send_task_embed(
    webhook_url: str,
    task_name: str,
    description: str,
    date: str | None,
) -> None:
    """Send a task assignment embed to a Discord Webhook URL.

    Errors are logged and swallowed — callers must not depend on this succeeding.
    """
    desc = description[:_MAX_DESC] + "..." if len(description) > _MAX_DESC else description

    fields = []
    if date:
        fields.append({"name": "日期", "value": date, "inline": True})

    payload = {
        "embeds": [
            {
                "title": task_name,
                "description": desc,
                "color": _EMBED_COLOR,
                "fields": fields,
                "footer": {"text": "每日訓練提交系統"},
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(webhook_url, json=payload)
            resp.raise_for_status()
    except Exception as exc:
        logger.error("Discord Webhook send failed: %s", exc)
