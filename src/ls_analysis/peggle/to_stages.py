# -*- coding: utf-8 -*-
"""
Created on 2022/01/27

@author: brassbeat
"""
import itertools as it

import pandas as pd

from ls_analysis.data.core import LivesplitData
from ls_analysis.data.enums import AttemptStat, IndexCategory
from ls_analysis.data.import_lss import remake_livesplit_data


def _get_stage_segment_data(segment_data: pd.DataFrame):
    stage_splits: pd.DataFrame = (
        segment_data
        .loc[:, [AttemptStat.SPLIT_TIME]]
        .iloc[:, 4::5]
        .rename(columns=lambda n: n // 5, level=IndexCategory.SEGMENT)
    )

    stage_segments = (
        stage_splits
        .sub(
            # previous split times
            stage_splits
            .shift(
                periods=1,
                axis="columns",
                fill_value=pd.Timedelta(seconds=0)
            )
        )
        .rename(columns={AttemptStat.SPLIT_TIME: AttemptStat.SEGMENT_TIME})
    )
    return pd.concat(
        [
            stage_segments,
            stage_splits,
        ],
        axis="columns",
    )


def convert_levels_to_stages(data: LivesplitData) -> LivesplitData:
    stage_segments = (
        data.segment_stats
        .pipe(_get_stage_segment_data)
    )
    new_data = remake_livesplit_data(
        attempt_data=data.full_run_stats,
        segment_data=stage_segments
    )
    return LivesplitData(new_data)




def main():
    pass


if __name__ == "__main__":
    main()
