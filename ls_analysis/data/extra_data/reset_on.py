import pandas as pd

from ls_analysis.data.enums import AttemptStat


def get_segment_reset_on(attempt_data: pd.DataFrame, segment_data: pd.DataFrame) -> pd.Series:
    total_segments = len(segment_data.loc[:, AttemptStat.SEGMENT_TIME].columns)
    return (
        segment_data
        [AttemptStat.SPLIT_TIME]
        .map(pd.Timedelta.total_seconds)
        .where(pd.DataFrame.isna, 1)
        .bfill(axis="columns")
        .sum(axis="columns")
        .add(
            pd.Series(
                data=1,
                index=attempt_data.index
            ),
            fill_value=0,
        )
        .where(lambda s: s <= total_segments, pd.NA)
        .convert_dtypes()
    )
