"""Module contains countries and regions tree widget."""

import logging

import simple_wbd
from PyQt4 import QtGui
from PyQt4 import QtCore
import collections

logger = logging.getLogger(__name__)


class CountryTreeWidget(QtGui.QTreeWidget):
    """Display a list of countries and their codes.

    The aggregates list was taken from:
        https://datahelpdesk.worldbank.org/knowledgebase/articles/898614-api-aggregates-regions-and-income-levels
    Groups were taken from:
        https://datahelpdesk.worldbank.org/knowledgebase/articles/906519
    """

    _data_structure = [
        ("Aggregates", [
            ("Income Levels", [
                "LIC",  # "Low income"
                "MIC",  # "Middle income",
                "LMC",  # "Lower middle income",
                "UMC",  # "Upper middle income",
                "HIC",  # "High income",
            ]),
            ("Regions", [
                "EAS",  # "East Asia & Pacific (all income levels)",
                "ECS",  # "Europe & Central Asia (all income levels)",
                "LCN",  # "Latin America & Caribbean (all income levels)",
                "MEA",  # "Middle East & North Africa (all income levels)",
                "NAC",  # "North America",
                "SAS",  # "South Asia",
                "SSF",  # "Sub-Saharan Africa (all income levels)",
            ]),
            ("Other", [
                "WLD",  # "World",
                "AFR",  # "Africa",
                "ARB",  # "Arab World",
                ("Low & middle income", [
                    "LMY",  # "All low and middle income regions",
                    "EAP",  # "East Asia & Pacific (developing only)",
                    "ECA",  # "Europe & Central Asia (developing only)",
                    "LAC",  # "Latin America & Caribbean (developing only)",
                    "MNA",  # "Middle East & North Africa (developing only)",
                    "SSA",  # "Sub-Saharan Africa (developing only)",
                ]),
                "EMU",  # other high income areas don't exist anymore
                # ("High income", [
                #     "EMU",  # "Euro area",
                #     "OEC",  # "High income: OECD",
                #     "NOC",  # "High income: nonOECD",
                # ]),
                "CEB",  # "Central Europe and the Baltics",
                "EUU",  # "European Union",
                "FCS",  # "Fragile and conflict affected situations",
                "HPC",  # "Heavily indebted poor countries (HIPC)",
                "IBD",  # "IBRD only",
                "IBT",  # "IDA & IBRD total",
                "IDB",  # "IDA blend",
                "IDX",  # "IDA only",
                "IDA",  # "IDA total",
                "LDC",  # "Least developed countries: UN classification",
                "OED",  # "OECD members",
                ("Small states", [
                    "SST",  # "All small states",
                    "CSS",  # "Caribbean small states",
                    "PSS",  # "Pacific island small states",
                    "OSS",  # "Other small states",
                ]),
            ]),
        ]),
        ("Countries", []),
    ]
    RENAME_MAP = {
        "SST": "All small states",
        "EMU": "High Income Euro area",
    }

    def __init__(self, parent, selection_list):
        super().__init__(parent)
        self._selection_list = selection_list
        self._busy = False
        self._api = simple_wbd.IndicatorAPI()
        self._init_view()
        self._init_data()
        self._init_listeners()

    def _init_data(self):
        self._set_data()

    def _init_listeners(self):
        self.itemChanged.connect(self.selection_changed)
        self.itemCollapsed.connect(self._item_collapsed)
        self.itemExpanded.connect(self._item_expanded)

    def _item_expanded(self, item):
        self._selection_list[("collapsed", item.key)] = False

    def _item_collapsed(self, item):
        self._selection_list[("collapsed", item.key)] = True

    def _init_view(self):
        self.setHeaderLabels(["Regions and countries", "Code"])
        self.setRootIsDecorated(True)

    def selection_changed(self, item, column):
        if self._busy:
            return
        self._selection_list[item.key] = item.checkState(0)

    def _fill_values(self, data, parent=None):
        if not parent:
            parent = self

        tristate = QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate
        defaults = self._selection_list
        for key, value in data.items():
            name = self.RENAME_MAP.get(key, value.get("name", key))
            display_key = "" if name == key else key

            item = QtGui.QTreeWidgetItem(parent, [name, display_key])
            item.setFlags(item.flags() | tristate)
            item.key = value if isinstance(value, str) else key

            defaults[item.key] = defaults.get(item.key, QtCore.Qt.Checked)
            item.setCheckState(0, defaults[item.key])
            if isinstance(value, collections.OrderedDict):
                self._fill_values(value, item)

    def _collapse_items(self, root=None):
        """Collapse items that were marked as collapsed in previous sessions.

        Args:
            root: Item whose children we want to check and collapse. If none is
                set, root item is chosen and we iterate through all top level
                items.
        """
        if root is None:
            root = self.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            if not item.childCount():
                continue
            if self._selection_list.get(("collapsed", item.key)):
                item.setExpanded(False)
            self._collapse_items(item)

    def _set_data(self):
        self._busy = True
        self.clear()
        from orangecontrib.wbd import countries

        self._country_dict = countries.get_countries_regions_dict()
        self._fill_values(self._country_dict)

        self.expandAll()
        self._collapse_items()

        for i in range(self.columnCount()):
            self.resizeColumnToContents(i)
        self._busy = False
