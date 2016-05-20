"""Modul for Indicators widget.

This widget should contain all filters needed to help the user find and select
any indicator.
"""


from PyQt4 import QtGui

import wbpy

from orangecontrib.wbd.widgets import filter_table_widget
from orangecontrib.wbd.widgets import benchmark


class IndicatorsWidget(filter_table_widget.HideWidgetWrapper):
    """Widget for filtering and selecting indicators."""

    TITLE_TEMPLATE = "Indicator: {}"
    MAX_TITLE_CHARS = 50

    def __init__(self):
        super().__init__()

        self.api = wbpy.IndicatorAPI()
        layout = QtGui.QGridLayout()

        with benchmark.Benchmark("fetching indicator data"):
            data = self.api.get_indicator_list(common_only=False)

        self.indicators = filter_table_widget.FilterTableWidget(data=data)
        layout.addWidget(self.indicators)
        self.setLayout(layout)

        self.indicators.table_widget.on("selection_changed",
                                        self.selection_changed)

    def selection_changed(self, selected_ids):
        """Callback function for selected indicators.

        This function sets the title of the current widget to display the
        selected indicator.

        Args:
            selected_ids (list of str): List of selected indicator ids. This
                list should always contain just one indicator. If more
                indicators are given, only the first one will be used.
        """
        if selected_ids:
            self.set_title(selected_ids[0])
        else:
            self.set_title()