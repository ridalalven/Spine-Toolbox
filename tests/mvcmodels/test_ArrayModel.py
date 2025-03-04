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
Unit tests for the ArrayModel class.

:author: A. Soininen (VTT)
:date:   9.4.2020
"""
import unittest
from PySide2.QtCore import Qt
from spinedb_api import Array
from spinetoolbox.mvcmodels.array_model import ArrayModel


class TestArrayModel(unittest.TestCase):
    def test_columnCount(self):
        model = ArrayModel()
        self.assertEqual(model.columnCount(), 1)
        model.reset(Array([3, 5, 1]))
        self.assertEqual(model.columnCount(), 1)

    def test_row_count_with_empty_array_is_still_one(self):
        model = ArrayModel()
        self.assertEqual(model.rowCount(), 1)

    def test_data_for_first_row_returns_none_with_empty_array(self):
        model = ArrayModel()
        roles = [Qt.DisplayRole, Qt.ToolTip]
        index = model.index(0, 0)
        self.assertTrue(index.isValid())
        for role in roles:
            self.assertIsNone(model.data(index, role))

    def test_data_in_edit_role_for_first_row_returns_default_float_with_empty_array(self):
        model = ArrayModel()
        index = model.index(0, 0)
        self.assertTrue(index.isValid())
        self.assertEqual(model.data(index, Qt.EditRole), 0.0)

    def test_insertRows_when_empty_array(self):
        model = ArrayModel()
        self.assertTrue(model.insertRows(0, 2))
        self.assertEqual(model.rowCount(), 3)
        expected_data = [0.0, 0.0, None]
        for row, expected in enumerate(expected_data):
            index = model.index(row, 0)
            self.assertEqual(index.data(), expected)

    def test_removeRows_when_empty_array(self):
        model = ArrayModel()
        self.assertFalse(model.removeRows(0, 1))

    def test_removeRows_remove_all_rows(self):
        model = ArrayModel()
        model.reset(Array([5.0, 3.0, 7.0]))
        self.assertTrue(model.removeRows(0, 3))
        self.assertEqual(model.rowCount(), 1)
        index = model.index(0, 0)
        self.assertIsNone(index.data())

    def test_batch_set_data(self):
        model = ArrayModel()
        model.reset(Array([5.0]))
        model.batch_set_data([model.index(0, 0)], ["2.3"])
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.index(0, 0).data(), 2.3)

    def test_batch_set_data_on_last_row_extends_table(self):
        model = ArrayModel()
        model.reset(Array([5.0]))
        model.batch_set_data([model.index(1, 0)], ["2.3"])
        self.assertEqual(model.rowCount(), 3)
        self.assertEqual(model.index(0, 0).data(), 5.0)

    def test_set_array_type_converts_existing_data(self):
        model = ArrayModel()
        model.reset(Array([5.0]))
        model.set_array_type(str)
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.index(0, 0).data(), "5.0")

    def test_setData(self):
        model = ArrayModel()
        model.reset(Array([5.0]))
        self.assertTrue(model.setData(model.index(0, 0), 2.3))
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.index(0, 0).data(), 2.3)

    def test_setData_on_last_row_extends_array(self):
        model = ArrayModel()
        model.reset(Array([5.0]))
        self.assertTrue(model.setData(model.index(1, 0), 2.3))
        self.assertEqual(model.rowCount(), 3)
        self.assertEqual(model.index(0, 0).data(), 5.0)
        self.assertEqual(model.index(1, 0).data(), 2.3)


if __name__ == '__main__':
    unittest.main()
