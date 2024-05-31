# -*- coding: utf-8 -*-
"""
Created on 2023/07/24

@author: brassbeat
"""
from io import StringIO

import pandas as pd

from typing import TextIO, Literal

from ls_analysis.data.clean_segments import clean_up_segments
from ls_analysis.data.enums import AttemptStat, IndexCategory
from ls_analysis.data.extra_data.reset_on import get_segment_reset_on
from ls_analysis.data.extra_data.time_on_reset import get_time_on_reset, add_reset_time_to_segment_data


def _read_segments(f: TextIO, timing_method: Literal["RealTime", "GameTime"] = "RealTime") -> pd.DataFrame:
    r"""
    Returned dataframe index:
    "attempt" Livesplit attempt id
    Returned dataframe columns:
    "last_split"
    "reset_at"
    ("SegmentTime", 1), ("SegmentTime", 2), ...
    ("SplitTime", 1), ("SplitTime", 2), ...
    """
    # get (id, segment time) pairs
    # skipped segments will still be there as NaTs
    # noinspection PyTypeChecker
    long_data = (
            pd.read_xml(
                    f,
                    xpath=".//Time",
                    converters={
                            "id": int,
                            "RealTime": pd.to_timedelta,
                            "GameTime": pd.to_timedelta,
                    },
                    parser="etree",
            )
            .loc[:, ["id", timing_method]]
            .rename(
                columns={
                    timing_method: AttemptStat.SEGMENT_TIME,
                    "id": IndexCategory.ATTEMPT
                }
            )
    )

    # get split times and segment ids
    # no need to remove NaTs
    long_data[IndexCategory.SEGMENT] = 1
    cumulative_data = (
        long_data
        .loc[long_data[IndexCategory.ATTEMPT] > 0, :]  # TODO add option to include non-positive ids
        .groupby([IndexCategory.ATTEMPT])
        .cumsum(numeric_only=False)
    )

    # pivot (id, segment time, split time, segment id) data over segment ids
    wide_data = (
        pd.concat(
            [
                long_data.loc[
                    :, [IndexCategory.ATTEMPT, AttemptStat.SEGMENT_TIME]
                ],
                cumulative_data.rename(
                    columns={AttemptStat.SEGMENT_TIME: AttemptStat.SPLIT_TIME}
                ),
            ],
            axis=1,
        )
        .convert_dtypes()
        .pivot_table(index=IndexCategory.ATTEMPT, columns=IndexCategory.SEGMENT)
        .rename_axis(
            columns=[
                IndexCategory.STATISTIC,
                IndexCategory.SEGMENT
            ]
        )
    )

    return wide_data


def _read_attempts(f: TextIO, timing_method: Literal["RealTime", "GameTime"] = "RealTime") -> pd.DataFrame:
    """
    Returned dataframe index:
    "id" Livesplit attempt id
    Returned dataframe columns:
    ("start_of_attempt", None)
    ("end_of_attempt", None)
    ("run_time", None)
    ("attempt_time", None)
    ("CumulativePlaytime", None)
    """
    # noinspection PyTypeChecker
    data: pd.DataFrame = (
        pd.read_xml(
            f,
            xpath=".//Attempt",
            converters={
                    "id":       int,
                    "started":  pd.to_datetime,
                    "ended":    pd.to_datetime,
                    "RealTime": pd.to_timedelta,
                    "GameTime": pd.to_timedelta,
            },
            parser="etree",
        )
        .drop(columns=["isStartedSynced", "isEndedSynced", "PauseTime"], errors="ignore")
        .rename(
            columns={
                "id": IndexCategory.ATTEMPT,
                timing_method: AttemptStat.RUN_TIME,
                "started": AttemptStat.START_OF_ATTEMPT,
                "ended": AttemptStat.END_OF_ATTEMPT,
            }
        )
        .set_index(IndexCategory.ATTEMPT)
    )
    data[AttemptStat.ATTEMPT_TIME] = (
        data[AttemptStat.END_OF_ATTEMPT]
        - data[AttemptStat.START_OF_ATTEMPT]
    )
    data[AttemptStat.CUMULATIVE_PLAYTIME] = (
        data[AttemptStat.ATTEMPT_TIME]
        .cumsum()
        .shift(fill_value=pd.Timedelta(0))
    )

    return (
        data
        .rename_axis(IndexCategory.STATISTIC, axis=1)
    )


def _add_extra_attempt_stats(attempt_data: pd.DataFrame, segment_data: pd.DataFrame) -> pd.DataFrame:
    attempt_data[AttemptStat.RESET_AT] = get_segment_reset_on(attempt_data, segment_data)
    attempt_data[AttemptStat.TIME_UPON_RESET] = get_time_on_reset(attempt_data, segment_data)

    return attempt_data


def _join_livesplit_data(attempt_data: pd.DataFrame, segment_data: pd.DataFrame) -> pd.DataFrame:

    attempt_data = (
        attempt_data
        .assign(**{IndexCategory.SEGMENT: -1})
        .pivot(columns=IndexCategory.SEGMENT)
    )

    data: pd.DataFrame = (
        pd.concat(
            [
                attempt_data,
                segment_data,
            ],
            axis=1
        )
    )
    return data


def remake_livesplit_data(attempt_data: pd.DataFrame, segment_data: pd.DataFrame) -> pd.DataFrame:
    attempt_data = (
        attempt_data
        .loc[:, AttemptStat.imported_attempt_stats]
        .droplevel(IndexCategory.SEGMENT, axis="columns")
        .pipe(_add_extra_attempt_stats, segment_data)
    )

    return _join_livesplit_data(attempt_data, segment_data)


def import_lss(f: TextIO, timing_method: Literal["RealTime", "GameTime"] = "RealTime") -> pd.DataFrame:
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
    raw_xml = f.read()
    xml_start = raw_xml.index("<")
    stream1 = StringIO(raw_xml[xml_start:])
    stream2 = StringIO(raw_xml[xml_start:])

    segment_data = _read_segments(stream2, timing_method)
    attempt_data = _read_attempts(stream1, timing_method)

    segment_data = clean_up_segments(attempt_data, segment_data)
    attempt_data = _add_extra_attempt_stats(attempt_data, segment_data)
    segment_data = add_reset_time_to_segment_data(segment_data, attempt_data)

    return _join_livesplit_data(attempt_data, segment_data)


def main():
    pass


if __name__ == "__main__":
    main()
