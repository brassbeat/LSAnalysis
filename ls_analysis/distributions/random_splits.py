"""
Created on 2024/05/24

@author: brassbeat
"""
import random

import pandas as pd

from ls_analysis.data.enums import IndexCategory
from ls_analysis.distributions.enums import DistributionColumn
from ls_analysis.distributions.protocols import SegmentDistribution


def draw_quantile_segments(distribution: pd.DataFrame, quantiles: pd.Series) -> pd.Series:
    """
    distribution dataframe index:
        Layer "attempt"
        Layer "segment"
    distribution dataframe columns:
        Layer "statistic"
            "segment_time"
            "node_weight"
            "prior_cumulative_weight"
    """
    compared_values = distribution.merge(
        quantiles,
        how="left",
        left_index=True,
        right_index=True,
    )

    quantiles_name = quantiles.name
    node_is_lower = (
        compared_values[DistributionColumn.PRIOR_CUMULATIVE_WEIGHT] <=
        compared_values[quantiles_name]
    )

    return (
        compared_values[DistributionColumn.SEGMENT_TIME]
        .loc[node_is_lower]
        .groupby(by="segment", sort=False,)
        .last()
    )


def roll_random_segments(
        distribution: SegmentDistribution,
        difficulty: float,
        seed: float = None
) -> pd.DataFrame:

    if seed:
        random.seed(seed)

    dropped_tail_size = 0.05 * difficulty
    segment_count = distribution.segment_count

    rolled_quantiles = (
        pd.Series(
            data=0.5,
            index=pd.Index(
                data=range(1, segment_count+1),
                dtype="int64",
                name=IndexCategory.SEGMENT,
            ),
            name="quantile",
        ).map(lambda _: random.random())
        .pow(difficulty)
        .mul(1 - dropped_tail_size)
    )
    return distribution.get_quantile_times(rolled_quantiles)
