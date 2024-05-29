"""
Created on 2024-05-15

@author: brassbeat
"""
import attrs
import pandas as pd

from ls_analysis.data.livesplit_data import LivesplitData
from ls_analysis.data.enums import IndexCategory
from ls_analysis.distributions.enums import DistributionColumn


@attrs.define
class WeightedEmpiricalDistribution:
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
        """
        segment_data is expected to be a simple table,
            with attempts as index and segments as column names

        returned dataframe index:
            Layer "attempt"
            Layer "segment"
        returned dataframe columns:
            Layer "statistic"
                "segment_time"
                "node_weight"
                "prior_cumulative_weight"
        """
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

        sorted_segments[DistributionColumn.PRIOR_CUMULATIVE_WEIGHT] = (
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
        sorted_segments[DistributionColumn.PRIOR_CUMULATIVE_WEIGHT] /= total_weights

        return cls(sorted_segments)

    @property
    def segment_count(self) -> int:
        return self.distribution.index.get_level_values(IndexCategory.SEGMENT).nunique()

    def get_quantile_times(self, quantiles: pd.Series | float) -> pd.DataFrame:
        node_is_lower = (
            self.distribution[
                DistributionColumn.PRIOR_CUMULATIVE_WEIGHT
            ]
            .le(
                quantiles
            )
        )
        segments = (
            self.distribution[DistributionColumn.SEGMENT_TIME]
            .loc[node_is_lower]
            .groupby(by="segment", sort=False, )
            .last()
        )
        return pd.DataFrame(
            data={
                DistributionColumn.QUANTILE: quantiles,
                DistributionColumn.SEGMENT_TIME: segments
            }
        )
