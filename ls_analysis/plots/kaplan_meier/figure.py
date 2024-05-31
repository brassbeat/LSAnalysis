# -*- coding: utf-8 -*-
"""
Created on 2024/05/29

@author: brassbeat
"""
import attrs
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import ticker
from matplotlib import axis

from data.livesplit_data import LivesplitData
from plots.kaplan_meier.curve import KaplanMeierCurve
from statistics.core.censored_segment import CensoredSegment

_TITLE_TEMPLATE = "Recorded Segment Times for {0.name}\nin {0.game} - {0.category}"


@attrs.define
class KaplanMeierSegment:
    segment: int
    cutoff: pd.Timestamp | None

    game: str
    category: str
    name: str

    _curves: list[KaplanMeierCurve] = attrs.field(factory=list, init=False)

    fig: plt.Figure = attrs.field(init=False)
    ax: plt.Axes = attrs.field(init=False)

    @property
    def _plot_kwargs(self):
        return {

        }

    def __attrs_post_init__(self):
        self.fig, self.ax = plt.subplots()

    def draw_segment_from_data(self, full_data: LivesplitData, name: str):
        segment_data = CensoredSegment.from_livesplit_data(full_data, self.segment, self.cutoff)
        curve = KaplanMeierCurve(segment_data, name)

        self._curves.append(curve)
        curve.plot(self.ax, **self._plot_kwargs)

    def make_figure(self, filename: str):
        self.ax.set_title(
            _TITLE_TEMPLATE.format(self)
        )
        self.ax.legend()
        self._set_ticks_and_grid()

        self.fig.savefig(filename)

    @staticmethod
    def _format_seconds(seconds: float, _: float) -> str:
        today = pd.Timestamp.today().round(freq="1D")
        return "{0.minute}:{0.second:02}".format(
            (pd.Timedelta(seconds=seconds) + today)
        )

    def _set_ticks_and_grid(self):
        x_axis: axis.XAxis = self.ax.xaxis
        y_axis: axis.YAxis = self.ax.yaxis

        x_axis.set_major_locator(ticker.MultipleLocator(30))
        x_axis.set_minor_locator(ticker.MultipleLocator(5))
        x_axis.grid(visible=True, which="major", color="0.7")
        x_axis.grid(visible=True, which="minor", color="0.9")
        x_axis.set_major_formatter(self._format_seconds)
        x_axis.set_minor_formatter(self._format_seconds)
        x_axis.set_label_text("Time")
        x_axis.set_tick_params(which="minor", labelsize=8)

        y_axis.set_major_locator(ticker.MultipleLocator(0.25))
        y_axis.set_minor_locator(ticker.MultipleLocator(0.05))
        y_axis.set_label_text("Quantile")
