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
Contains logic for the fixed step time series editor widget.

:author: A. Soininen (VTT)
:date:   14.6.2019
"""
import locale
from numbers import Number
import numpy
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from spinedb_api import Array, from_database, ParameterValueFormatError, SpineDBAPIError
from .indexed_value_table_model import EXPANSE_COLOR


class ArrayModel(QAbstractTableModel):
    """
    Model for the Array parameter_value type.

    Even if the array is empty this model's rowCount() will still return 1.
    This is to show an empty row in the table view.
    """

    def __init__(self):
        super().__init__()
        self._data = list()
        self._data_type = float

    def array(self):
        """Returns the array modeled by this model."""
        return Array(self._data, self._data_type)

    def batch_set_data(self, indexes, values):
        """Sets data at multiple indexes at once.

        Args:
            indexes (list of QModelIndex): indexes to set
            values (list of str): values corresponding to the indexes
        """
        if not indexes:
            return
        top_row = indexes[0].row()
        bottom_row = top_row
        indexes, values = self._convert_to_data_type(indexes, values)
        if not indexes:
            return
        for index, value in zip(indexes, values):
            row = index.row()
            top_row = min(top_row, row)
            bottom_row = max(bottom_row, row)
            if row == len(self._data):
                self.insertRow(len(self._data))
            self._data[row] = value
        top_left = self.index(top_row, 0)
        bottom_right = self.index(bottom_row, 0)
        self.dataChanged.emit(top_left, bottom_right, [Qt.BackgroundRole, Qt.DisplayRole, Qt.ToolTipRole])

    def columnCount(self, parent=QModelIndex()):
        """Returns 1."""
        return 1

    def _convert_to_data_type(self, indexes, values):
        """
        Converts values from string to current data type filtering failed conversions.

        Args:
            indexes (list of QModelIndex): indexes
            values (list of str): values to convert

        Returns:
            tuple: indexes and converted values
        """
        filtered = list()
        converted = list()
        if self._data_type == float:
            for index, value in zip(indexes, values):
                if value is None:
                    converted.append(numpy.nan)
                    filtered.append(index)
                    continue
                try:
                    number = locale.atof(value)
                    converted.append(number)
                    filtered.append(index)
                except ValueError:
                    pass
        elif self._data_type == str:
            for index, value in zip(indexes, values):
                converted.append(str(value) if value is not None else "")
                filtered.append(index)
        else:
            for index, value in zip(indexes, values):
                try:
                    data = self._data_type(value)
                    converted.append(data)
                    filtered.append(index)
                    continue
                except SpineDBAPIError:
                    pass
                try:
                    data = from_database(value)
                    if isinstance(data, self._data_type):
                        converted.append(data)
                        filtered.append(index)
                except ParameterValueFormatError:
                    pass
        return filtered, converted

    def data(self, index, role=Qt.DisplayRole):
        """Returns model's data for given role."""
        if not index.isValid():
            return None
        row = index.row()
        if role == Qt.DisplayRole:
            if row == len(self._data):
                return None
            element = self._data[row]
            if isinstance(element, (float, str)):
                return element
            return str(element)
        if role == Qt.EditRole:
            if row == len(self._data):
                return self._data_type()
            return self._data[row]
        if role == Qt.ToolTipRole:
            if row == len(self._data):
                return None
            element = self._data[row]
            return str(element)
        if role == Qt.BackgroundRole:
            if row == len(self._data):
                return EXPANSE_COLOR
            return None
        return None

    def flags(self, index):
        """Returns table cell's flags."""
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Returns header data."""
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Vertical:
            return section + 1
        return "Value"

    def insertRows(self, row, count, parent=QModelIndex()):
        """Inserts rows to the array."""
        self.beginInsertRows(parent, row, row + count - 1)
        self._data = self._data[:row] + [self._data_type() for _ in range(count)] + self._data[row:]
        self.endInsertRows()
        return True

    def is_expanse_row(self, row):
        """
        Returns True if row is the expanse row.

        Args:
            row (int): a row

        Returns:
            bool: True is row is expanse row, False otherwise
        """
        return row == len(self._data)

    def removeRows(self, row, count, parent=QModelIndex()):
        """Removes rows from the array."""
        # Some special handling is needed if the array becomes empty after the operation.
        if not self._data:
            return False
        if row == 0:
            if len(self._data) == 1:
                self._data.clear()
                self.dataChanged.emit(
                    self.index(0, 0), self.index(0, 0), [Qt.DisplayRole, Qt.ToolTipRole, Qt.BackgroundRole]
                )
                return False
        first_row = row if count < len(self._data) else 1
        self.beginRemoveRows(parent, first_row, row + count - 1)
        self._data = self._data[:row] + self._data[row + count :]
        self.endRemoveRows()
        if not self._data:
            self.dataChanged.emit(
                self.index(0, 0), self.index(0, 0), [Qt.DisplayRole, Qt.ToolTipRole, Qt.BackgroundRole]
            )
        return True

    def reset(self, value):
        """
        Resets the model to a new array.

        Args:
            value (Array): a new array to model
        """
        self.beginResetModel()
        self._data = list(value.values)
        self._data_type = value.value_type
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        """
        Returns the length of the array.

        Note: returns 1 even if the array is empty.
        """
        return len(self._data) + 1

    def set_array_type(self, new_type):
        """Changes the data type of array's elements.

        Args:
            new_type (Type): new element type
        """
        if new_type == self._data_type:
            return
        self.beginResetModel()
        try:
            self._data = [new_type(x) for x in self._data]
        except (ParameterValueFormatError, TypeError, ValueError):
            self._data = len(self._data) * [new_type()]
        self._data_type = new_type
        self.endResetModel()

    def setData(self, index, value, role=Qt.EditRole):
        """Sets the value at given index."""
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            if isinstance(value, (str, Number)):
                try:
                    value = self._data_type(value)
                except ValueError:
                    return False
            row = index.row()
            if row == len(self._data):
                self.insertRow(row)
            self._data[row] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.ToolTipRole, Qt.BackgroundRole])
            return True
        return False
