# -*- coding: utf-8 -*-
"""
Created on 2024/05/31

@author: brassbeat
"""
import attrs
import pandas as pd
from scipy import stats

from data.enums import IndexCategory, AttemptStat
from data.livesplit_data import LivesplitData


@attrs.define
class CensoredSegment:
    _data: pd.DataFrame = attrs.field()

    def get_full_times(self) -> pd.Series:
        return (
            self._data["time"]
            .map(pd.Timedelta.total_seconds)
            .loc[~self._data["is_censored"]]
        )

    def get_reset_times(self) -> pd.Series:
        completion_times = self._data["time"].loc[~self._data["is_censored"]]
        is_at_least_best_completion = self._data["time"] >= completion_times.min()
        is_at_most_worst_completion = self._data["time"] <= completion_times.max()
        return (
            self._data["time"]
            .where(is_at_most_worst_completion, completion_times.max() + pd.Timedelta(seconds=1))
            .map(pd.Timedelta.total_seconds)
            .loc[self._data["is_censored"] & is_at_least_best_completion]
        )

    @classmethod
    def from_livesplit_data(cls, data: LivesplitData, segment: int, cutoff: pd.Timestamp | None):
        cutoff = cutoff or pd.Timestamp.fromordinal(1)

        included_attempts: pd.Series = (
            data.full_run_stats
            .droplevel(IndexCategory.SEGMENT, axis="columns")
            [AttemptStat.START_OF_ATTEMPT]
            >= cutoff
        )

        used_data = (
            data.segment_stats
            .loc[
                included_attempts,
                pd.IndexSlice[
                    [AttemptStat.SEGMENT_TIME, AttemptStat.RESET_TIME],
                    segment
                ]
            ]
            .rename(
                columns={
                    AttemptStat.SEGMENT_TIME: False,
                    AttemptStat.RESET_TIME: True,
                    segment: "time"
                }
            )
            .rename_axis(columns={IndexCategory.STATISTIC: "is_censored"})
            .stack(level="is_censored", future_stack=True)
            .reset_index(level="is_censored")
            .dropna(how="any")
            .sort_values(by="time")
        )

        return cls(used_data)

    def get_time_bounds(self) -> tuple[pd.Timedelta, pd.Timedelta]:
        ...

    def get_scipy_censored_data(self) -> stats.CensoredData:
        return stats.CensoredData(
            uncensored=self.get_full_times(),
            right=self.get_reset_times(),
        )
