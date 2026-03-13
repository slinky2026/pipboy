from dataclasses import dataclass, field
from typing import List


@dataclass #dataclass removes lines of bullshit basically
class Vitals:
    hp: int = 90
    hp_max: int = 100
    ap: int = 60
    ap_max: int = 100
    rad: int = 5  # 0-100


@dataclass
class Item:
    name: str
    category: str  # "WEAPONS", "APPAREL", "AID", "MISC"
    value: int = 0
    weight: float = 0.0
    description: str = ""


@dataclass
class AppState:
    vitals: Vitals = field(default_factory=Vitals)
    inventory: List[Item] = field(default_factory=lambda: [
        Item("10mm Pistol", "WEAPONS", value=50, weight=3.5, description="Standard sidearm."),
        Item("Hunting Rifle", "WEAPONS", value=120, weight=9.2, description="Bolt-action rifle."),
        Item("Leather Chestpiece", "APPAREL", value=75, weight=8.0, description="Light armor."),
        Item("Stimpak", "AID", value=25, weight=0.1, description="Restores HP."),
        Item("RadAway", "AID", value=40, weight=0.1, description="Removes radiation."),
        Item("Bobby Pin", "MISC", value=1, weight=0.0, description="Lockpicking tool."),
    ])
