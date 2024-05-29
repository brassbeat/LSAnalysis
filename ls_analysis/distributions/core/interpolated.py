# -*- coding: utf-8 -*-
"""
Created on 2024-05-15

@author: brassbeat
"""

import attrs
import pandas as pd

from data.livesplit_data import LivesplitData
from distributions.enums import DistributionColumn
from ls_analysis.data.enums import IndexCategory


@attrs.define
class InterpolatedDistribution:
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
    distribution: pd.DataFrame = attrs.field()

    @classmethod
    def from_weight_func(
        cls,
        data: LivesplitData,
        weight_func,
        *args,
        **kwargs,
    ):
        segment_data = data.segment_data
        weight_data = segment_data.apply(weight_func, args=args, **kwargs)
        combined_data = pd.concat(
            [
                segment_data.rename(
                    columns=lambda idx: (idx, DistributionColumn.SEGMENT_TIME)
                ),
                weight_data.rename(
                    columns=lambda idx: (idx, DistributionColumn.NODE_WEIGHT)
                ),
            ],
            axis=1,
        )

        combined_data.columns = pd.MultiIndex.from_tuples(
            combined_data.columns,
            names=[
                IndexCategory.SEGMENT,
                IndexCategory.STATISTIC,
            ]
        )

        long_data: pd.DataFrame = (
            combined_data
            .stack(level=IndexCategory.SEGMENT, future_stack=True)
            .dropna()
        )

        sorted_segments = (
            long_data
            .sort_values(
                by=[
                    IndexCategory.SEGMENT,
                    DistributionColumn.SEGMENT_TIME
                ]
            )
        )

        # drop weight of worst segments
        sorted_segments[DistributionColumn.NODE_WEIGHT] = (
            sorted_segments[DistributionColumn.NODE_WEIGHT]
            .groupby(by=IndexCategory.SEGMENT)
            .shift(1)
            .groupby(by=IndexCategory.SEGMENT)
            .shift(-1, fill_value=0)
        )

        sorted_segments[DistributionColumn.QUANTILE] = (
            sorted_segments[DistributionColumn.NODE_WEIGHT]
            .groupby(by=IndexCategory.SEGMENT)
            .shift(1, fill_value=0)
            .groupby(by=IndexCategory.SEGMENT)
            .cumsum()
        )

        # normalize weight of each segment block
        total_weights: pd.Series = (
            sorted_segments[DistributionColumn.NODE_WEIGHT]
            .rename("total_weight")
            .groupby(by=IndexCategory.SEGMENT)
            .sum()
        )

        sorted_segments[DistributionColumn.NODE_WEIGHT] /= total_weights
        sorted_segments[DistributionColumn.QUANTILE] /= total_weights

        return cls(sorted_segments)

    @property
    def segment_count(self) -> int:
        return self.distribution.index.get_level_values(IndexCategory.SEGMENT).nunique()

    def get_quantile_times(self, quantiles: pd.Series | float) -> pd.DataFrame:
        # get bounding quantile nodes for each segment
        node_is_higher = (
            self.distribution
            [DistributionColumn.QUANTILE]
            .gt(quantiles)
        )  # strict inequality, so no nodes found when quantiles == 1

        lower_nodes: pd.DataFrame = (
            self.distribution
            .loc[~node_is_higher, :]
            .groupby(level=IndexCategory.SEGMENT, sort=False)
            .last()
        )

        upper_nodes: pd.DataFrame = (
            self.distribution
            .loc[node_is_higher, :]
            .groupby(level=IndexCategory.SEGMENT, sort=False)
            .first()
        )  # contains missing rows for quantiles == 1

        # do the linear interpolation
        wanted_interval_length = (
            quantiles
            - lower_nodes[DistributionColumn.QUANTILE]
        )
        wanted_interval_proportions = (
            wanted_interval_length
            / lower_nodes[DistributionColumn.NODE_WEIGHT]
        )
        interval_value_sizes = (
            (
                upper_nodes[DistributionColumn.SEGMENT_TIME]
                - lower_nodes[DistributionColumn.SEGMENT_TIME]
            )
            .fillna(pd.Timedelta(seconds=0))
        )

        interpolation_time_steps = wanted_interval_proportions * interval_value_sizes

        interpolated_times = (
            lower_nodes[DistributionColumn.SEGMENT_TIME]
            + interpolation_time_steps
        )

        return pd.DataFrame(
            data={
                DistributionColumn.QUANTILE: quantiles,
                DistributionColumn.SEGMENT_TIME: interpolated_times
            }
        )


def main():
    pass


if __name__ == "__main__":
    main()
