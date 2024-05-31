import enum
import itertools
from collections.abc import Iterator
from enum import StrEnum, Enum

import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm


class SplitsType(Enum):
    LEVELS = enum.auto()
    STAGES = enum.auto()


class StageName(StrEnum):
    BJORN = "Bjorn"
    JIMMY = "Jimmy"
    KAT_TUT = "Kat Tut"
    SPLORK = "Splork"
    CLAUDE = "Claude"
    RENFIELD = "Renfield"
    TULA = "Tula"
    WARREN = "Warren"
    CINDERBOTTOM = "Cinderbottom"
    HU = "Hu"
    MARINA = "Marina"
    MASTER = "Master"

    @property
    def color(self) -> str:
        return _STAGE_COLORS[self]


class PeggleEdition(StrEnum):
    DELUXE = enum.auto()
    NIGHTS = enum.auto()
    EXTREME = enum.auto()
    WOW = enum.auto()

    @property
    def stages(self) -> list[StageName]:
        return _STAGE_ORDERS[self]

    @property
    def level_names(self) -> list[str]:
        return _LEVEL_NAMES[self]

    @property
    def level_codes(self) -> list[str]:
        codes_by_stage: Iterator[list[str]] = map(
            lambda stage: [f"{stage[0]}-{level}" for level in range(1, 6)],
            enumerate(self.stages, start=1)
        )
        return list(itertools.chain.from_iterable(codes_by_stage))

    @property
    def colors(self) -> ListedColormap:
        return ListedColormap([stage.color for stage in self.stages])

    @property
    def level_norm(self) -> BoundaryNorm:
        stage_count = len(self.stages)
        return BoundaryNorm(np.linspace(0.5, 5*stage_count+0.5, num=stage_count+1), stage_count)

    @property
    def stage_norm(self) -> BoundaryNorm:
        stage_count = len(self.stages)
        return BoundaryNorm(np.linspace(0.5, stage_count+0.5, num=stage_count+1), stage_count)


_STAGE_ORDERS = {
        PeggleEdition.DELUXE:  [
                StageName.BJORN,
                StageName.JIMMY,
                StageName.KAT_TUT,
                StageName.SPLORK,
                StageName.CLAUDE,
                StageName.RENFIELD,
                StageName.TULA,
                StageName.WARREN,
                StageName.CINDERBOTTOM,
                StageName.HU,
                StageName.MASTER,
        ],
        PeggleEdition.NIGHTS:  [
                StageName.BJORN,
                StageName.JIMMY,
                StageName.RENFIELD,
                StageName.KAT_TUT,
                StageName.SPLORK,
                StageName.CLAUDE,
                StageName.TULA,
                StageName.CINDERBOTTOM,
                StageName.WARREN,
                StageName.HU,
                StageName.MARINA,
                StageName.MASTER,
        ],
        PeggleEdition.EXTREME: [
                StageName.BJORN,
                StageName.BJORN,
        ],
        PeggleEdition.WOW:     [
                StageName.BJORN,
                StageName.SPLORK,
        ],
}

_LEVEL_NAMES = {
    PeggleEdition.DELUXE: [
        "Peggleland",
        "Slip and Slide",
        "Bjorn's Gazebo",
        "Das Bucket",
        "Snow Day",
        "Birdy's Crib",
        "Buffalo Wings",
        "Skate Park",
        "Spiral of Doom",
        "Mr. Peepers",
        "Scarab Crunch",
        "Infinite Cheese",
        "Ra Deal",
        "Croco-gator Pit",
        "The Fever Level",
        "The Amoeban",
        "The Last Flower",
        "We Come In Peace",
        "Maid in Space",
        "Getting the Spare",
        "Pearl Clam",
        "Insane Aquarium",
        "Tasty Waves",
        "Our Favorite Eel",
        "Love Story",
        "Waves",
        "Spiderweb",
        "Blockers",
        "Baseball",
        "Vermin",
        "Holland Oats",
        "I Heart Flowers",
        "Workin From Home",
        "Tula's Ride",
        "70 and Sunny",
        "Win a Monkey",
        "Dog Pinball",
        "Spin Again",
        "Roll 'em",
        "Five of a Kind",
        "The Love Moat",
        "Doom With a View",
        "Rhombi",
        "9 Luft Balloons",
        "Twisted Sisters",
        "Spin Cycle",
        "The Dude Abides",
        "When Pigs Fly",
        "Yang, Yin",
        "Zen Frog",
        "Paw Reader",
        "End of Time",
        "Billions & Billions",
        "Don't Panic",
        "Beyond Reason",
    ]
}

_STAGE_COLORS = {
        StageName.BJORN: "dodgerblue",
        StageName.JIMMY: "olivedrab",
        StageName.KAT_TUT: "chocolate",
        StageName.SPLORK: "blueviolet",
        StageName.CLAUDE: "mediumaquamarine",
        StageName.RENFIELD: "sienna",
        StageName.TULA: "hotpink",
        StageName.WARREN: "firebrick",
        StageName.CINDERBOTTOM: "sandybrown",
        StageName.HU: "slategrey",
        StageName.MASTER: "gold",
        StageName.MARINA: "darkturquoise",
}
