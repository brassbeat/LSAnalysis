"""
Created on 2024-05-25

@author: brassbeat
"""
import pandas as pd
import scipy.stats as scipy_stats

from ls_analysis.data.core import LivesplitData
from ls_analysis.statistics.core.latest_n import get_latest_n


def apply_brunner_munzel_segments_naive(
        left: LivesplitData,
        right: LivesplitData,
        sample_sizes: tuple[int, int]
):
    left_samples = get_latest_n(left, sample_sizes[0]).map(pd.Timedelta.total_seconds)
    right_samples = get_latest_n(right, sample_sizes[1]).map(pd.Timedelta.total_seconds)

    segment_count = left_samples.columns.size

    w, p_value = scipy_stats.brunnermunzel(
        x=left_samples.to_numpy(),
        y=right_samples.to_numpy(),
        axis=0,
    )

    return pd.DataFrame(
        {
            "w": w,
            "p_value": p_value
        },
        index=range(1, segment_count + 1),
    )
