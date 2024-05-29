"""
Created on 2024-05-25

@author: brassbeat
"""
from typing import TextIO, Literal, Self

import attrs
import pandas as pd

from ls_analysis.data.enums import AttemptStat, IndexCategory
from ls_analysis.data.import_lss import import_lss


@attrs.define
class LivesplitData:
    """
    Index of returned dataframe:
        'attempt': Attempt id, usually just 1, 2, ...

    Columns of underlying dataframe hold a 2-layer MultiIndex:
        Layer 'statistic':
            'start_of_attempt'

            'end_of_attempt'

            'run_time'

            'attempt_time'

            'cumulative_playtime'

            'last_split'

            'reset_at'

            'segment_time'

            'split_time'

        Layer 'segment': either integer corresponding to segment index or NaN for columns relating
                to the whole attempt
    """
    data: pd.DataFrame = attrs.field()

    @classmethod
    def from_lss(cls, f: TextIO, timing_method: Literal["RealTime", "GameTime"] = "RealTime") -> Self:
        return cls(
            data=import_lss(f, timing_method)
        )

    @property
    def segment_data(self) -> pd.DataFrame:
        return self.data[AttemptStat.SEGMENT_TIME]

    def to_csv(self, f: TextIO | str) -> None:
        self.data.to_csv(f)

    @classmethod
    def from_csv(cls, f: TextIO | str) -> Self:
        data = pd.read_csv(
            filepath_or_buffer=f,
            header=[0, 1]
        )
        return cls(data)

    @property
    def _column_is_full_attempt_statistic(self):
        return (
            self.data
            .columns
            .get_level_values(level=IndexCategory.SEGMENT)
            < 0
        )

    @property
    def full_run_stats(self) -> pd.DataFrame:
        return (
            self.data
            .loc[:, self._column_is_full_attempt_statistic]
        )

    @property
    def segment_stats(self) -> pd.DataFrame:
        return (
            self.data
            .loc[:, ~self._column_is_full_attempt_statistic]
        )
