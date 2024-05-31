# -*- coding: utf-8 -*-
"""
Created on 2024/05/30

@author: brassbeat
"""
import attrs
from matplotlib import pyplot as plt
from scipy import stats

from statistics.core.censored_segment import CensoredSegment


@attrs.define
class KaplanMeierCurve:
    data: CensoredSegment
    name: str

    @property
    def _plot_kwargs(self) -> dict:
        return {
            "label": self.name
        }

    @property
    def cdf(self):
        scipy_data = self.data.get_scipy_censored_data()
        return stats.ecdf(scipy_data).cdf

    def plot(self, ax: plt.Axes, **kwargs):
        full_kwargs = kwargs | self._plot_kwargs
        self.cdf.plot(ax, **full_kwargs)
