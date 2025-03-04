######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Unit tests for ArrayTableView class.

:author: A. Soininen (VTT)
:date:   25.3.2021
"""

import csv
from io import StringIO
import unittest
from PySide2.QtCore import QItemSelectionModel
from PySide2.QtWidgets import QApplication
from spinedb_api import Array
from spinetoolbox.mvcmodels.array_model import ArrayModel
from spinetoolbox.widgets.custom_qtableview import ArrayTableView


class TestArrayTableView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._original_clip = QApplication.clipboard().text()

    def tearDown(self):
        QApplication.clipboard().setText(self._original_clip)

    def test_copy_without_selection_returns_false(self):
        model = ArrayModel()
        table_view = ArrayTableView()
        table_view.setModel(model)
        self.assertFalse(table_view.copy())

    def test_copy_single_non_numeric_cell(self):
        model = ArrayModel()
        table_view = ArrayTableView()
        table_view.setModel(model)
        model.reset(Array(["a"]))
        index = model.index(0, 0)
        table_view.selectionModel().select(index, QItemSelectionModel.Select)
        self.assertTrue(table_view.copy())
        clip = StringIO(QApplication.clipboard().text())
        array = [row for row in csv.reader(clip)]
        self.assertEqual(array, [["a"]])

    def test_copy_single_numeric_cell(self):
        model = ArrayModel()
        table_view = ArrayTableView()
        table_view.setModel(model)
        model.reset(Array([5.5]))
        index = model.index(0, 0)
        table_view.selectionModel().select(index, QItemSelectionModel.Select)
        self.assertTrue(table_view.copy())
        clip = StringIO(QApplication.clipboard().text())
        array = [row for row in csv.reader(clip)]
        self.assertEqual(array, [["5.5"]])

    def test_paste_non_numeric_to_empty_table(self):
        model = ArrayModel()
        model.set_array_type(str)
        table_view = ArrayTableView()
        table_view.setModel(model)
        index = model.index(0, 0)
        table_view.selectionModel().select(index, QItemSelectionModel.Select)
        self._write_to_clipboard([["a"]])
        self.assertTrue(table_view.paste())
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.array(), Array(["a"]))

    def test_paste_numeric_to_empty_table(self):
        model = ArrayModel()
        table_view = ArrayTableView()
        table_view.setModel(model)
        index = model.index(0, 0)
        table_view.selectionModel().select(index, QItemSelectionModel.Select)
        self._write_to_clipboard([[2.3]])
        self.assertTrue(table_view.paste())
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.array(), Array([2.3]))

    def test_paste_multiple_rows_to_single_row_selection(self):
        model = ArrayModel()
        model.reset(Array([5.5]))
        table_view = ArrayTableView()
        table_view.setModel(model)
        index = model.index(0, 0)
        table_view.selectionModel().select(index, QItemSelectionModel.Select)
        self._write_to_clipboard([[2.3], [-2.3]])
        self.assertTrue(table_view.paste())
        self.assertEqual(model.rowCount(), 3)
        self.assertEqual(model.array(), Array([2.3, -2.3]))

    def test_paste_only_what_fits_selection(self):
        model = ArrayModel()
        model.reset(Array([5.5, -5.5]))
        table_view = ArrayTableView()
        table_view.setModel(model)
        for row in (0, 1):
            table_view.selectionModel().select(model.index(row, 0), QItemSelectionModel.Select)
        self._write_to_clipboard([[2.3], [-2.3], [23.0]])
        self.assertTrue(table_view.paste())
        self.assertEqual(model.rowCount(), 3)
        self.assertEqual(model.array(), Array([2.3, -2.3]))

    @staticmethod
    def _write_to_clipboard(data):
        with StringIO() as out_string:
            writer = csv.writer(out_string)
            writer.writerows(data)
            clip = out_string.getvalue()
        QApplication.clipboard().setText(clip)


if __name__ == "__main__":
    unittest.main()
