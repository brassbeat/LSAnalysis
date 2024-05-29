import pandas as pd

from ls_analysis.data.enums import AttemptStat


def _pad_segment_data(segment_data: pd.DataFrame, attempt_data: pd.DataFrame) -> pd.DataFrame:
    return (
        segment_data

        .add(
            pd.DataFrame(
                data=pd.Timedelta(seconds=0),
                index=attempt_data.index,
                columns=segment_data.columns,
            ),
        )
    )


def _delete_merged_splits(segment_data: pd.DataFrame) -> pd.DataFrame:
    segment_data[AttemptStat.SEGMENT_TIME] = (
        segment_data[AttemptStat.SEGMENT_TIME]
        .mask(
            (
                segment_data[AttemptStat.SEGMENT_TIME]
                .isna()
                .shift(
                    periods=1,
                    axis="columns",
                    fill_value=False
                )
            ),
            pd.NaT
        )
    )
    return segment_data


def clean_up_segments(attempt_data: pd.DataFrame, segment_data: pd.DataFrame) -> pd.DataFrame:
    return (
        segment_data
        .pipe(_pad_segment_data, attempt_data)
        .pipe(_delete_merged_splits)
    )
