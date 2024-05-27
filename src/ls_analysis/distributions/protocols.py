# -*- coding: utf-8 -*-
"""
Created on 2023/05/18

@author: brassbeat
"""
import pandas as pd

from typing import Protocol


class SegmentDistribution(Protocol):
    @property
    def segment_count(self) -> int:
        ...

    def get_quantile_times(self, quantiles: pd.Series | float) -> pd.Series:
        ...
