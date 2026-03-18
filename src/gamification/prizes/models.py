"""Prize Beanie Document."""
from typing import Literal, Optional

from beanie import Document


class Prize(Document):
    class_id: str
    title: str
    description: str = ""
    prize_type: Literal["online", "physical"] = "online"
    image_url: Optional[str] = None
    point_cost: int = 0
    visible: bool = True
    created_by: str  # teacher user_id

    class Settings:
        name = "prizes"
