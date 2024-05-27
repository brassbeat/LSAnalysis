"""
Created on 2024-05-25

@author: brassbeat
"""

import pandas as pd

from ls_analysis.data.core import LivesplitData


def get_latest_n(data: LivesplitData, n: int) -> pd.DataFrame:
    def get_latest_n_of_series(s: pd.Series):
        return (
            s
            .dropna()
            .tail(n)
            .reset_index(drop=True)
        )

    return (
        data
        .segment_data
        .apply(
            func=get_latest_n_of_series
        )
    )