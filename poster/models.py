from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Listing:
    team: str
    year: str
    brand: str
    size: str
    price: float
    photos: list[Path]
    player: str | None = None
    type: str | None = None
    condition: str = "USED_GOOD"
    best_offer: bool = True
    description: str | None = None
    custom_title: str | None = None

    def generate_title(self) -> str:
        parts = [self.team]
        if self.player:
            parts.append(self.player)
        parts.append(self.year)
        if self.type:
            parts.append(self.type)
        parts.append("Football Shirt Soccer Jersey")
        parts.append(self.brand)
        parts.append(f"size {self.size}")
        return " ".join(parts)

    @property
    def title(self) -> str:
        if self.custom_title:
            return self.custom_title
        return self.generate_title()
