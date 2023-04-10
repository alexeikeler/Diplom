from PyQt5 import QtWidgets
from typing import Iterable, Dict


def config_table(
    table: QtWidgets.QTableWidget,
    rows: int,
    cols: int,
    columns: Iterable,
    areas_to_stretch: Dict[int, QtWidgets.QHeaderView.ResizeMode],
    enable_column_sort: bool,
) -> None:

    table.setRowCount(rows)
    table.setColumnCount(cols)
    table.setHorizontalHeaderLabels(columns)
    table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
    table.setSortingEnabled(enable_column_sort)

    table.resizeRowsToContents()

    header = table.horizontalHeader()
    for area, mode in areas_to_stretch.items():
        header.setSectionResizeMode(area, mode)

    table.resizeRowsToContents()