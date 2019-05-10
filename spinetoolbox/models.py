######################################################################################################################
# Copyright (C) 2017 - 2018 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Classes for handling models in PySide2's model/view framework.
Note: These are Spine Toolbox internal data models.

:authors: P. Savolainen (VTT), M. Marin (KTH), P. Vennström (VTT)
:date:   23.1.2018
"""

import logging
import os
import json
from PySide2.QtCore import Qt, Slot, QModelIndex, QAbstractListModel, QAbstractTableModel, \
    QSortFilterProxyModel, QAbstractItemModel
from PySide2.QtGui import QStandardItem, QStandardItemModel, QBrush, QFont, QIcon, QGuiApplication
from PySide2.QtWidgets import QMessageBox
from config import INVALID_CHARS, TOOL_OUTPUT_DIR
from helpers import rename_dir, busy_effect, format_string_list, strip_json_data
from spinedb_api import SpineDBAPIError


class ProjectItemModel(QAbstractItemModel):
    """Class to store project items, e.g. Data Stores, Data Connections, Tools, Views.

    Attributes:
        toolbox (ToolboxUI): QMainWindow instance
        root (ProjectItem): Root item for the project item tree
    """
    def __init__(self, toolbox, root):
        """Class constructor."""
        super().__init__()
        self._toolbox = toolbox
        self._root = root

    def root(self):
        """Returns root project item."""
        return self._root

    def rowCount(self, parent=QModelIndex()):
        """Reimplemented rowCount method.

        Args:
            parent (QModelIndex): Index of parent item whose children are counted.

        Returns:
            int: Number of children of given parent
        """
        if not parent.isValid():  # Number of category items (children of root)
            return self.root().child_count()
        elif parent.internalPointer().is_category:  # Number of project items in the category
            return parent.internalPointer().child_count()
        else:
            return 0

    def columnCount(self, parent=QModelIndex()):
        """Returns model column count."""
        return 1

    def flags(self, index):
        """Returns flags for the item at given index

        Args:
            index (QModelIndex): Flags of item at this index.
        """
        if not index.internalPointer().is_category:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def parent(self, index=QModelIndex()):
        """Returns index of the parent of given index.

        Args:
            index (QModelIndex): Index of item whose parent is returned

        Returns:
            QModelIndex: Index of parent item
        """
        item = self.project_item(index)
        parent_item = item.parent()
        if not parent_item:
            return QModelIndex()
        if parent_item == self.root():
            return QModelIndex()
        # logging.debug("parent_item: {0}".format(parent_item.name))
        return self.createIndex(parent_item.row(), 0, parent_item)

    def index(self, row, column, parent=QModelIndex()):
        """Returns index of item with given row, column, and parent.

        Args:
            row (int): Item row
            column (int): Item column
            parent (QModelIndex): Parent item index

        Returns:
            QModelIndex: Item index
        """
        if row < 0 or row >= self.rowCount(parent):
            return QModelIndex()
        if column < 0 or column >= self.columnCount(parent):
            return QModelIndex()
        parent_item = self.project_item(parent)
        child = parent_item.child(row)
        if not child:
            return QModelIndex()
        else:
            return self.createIndex(row, column, child)

    def data(self, index, role=None):
        """Returns data in the given index according to requested role.

        Args:
            index (QModelIndex): Index to query
            role (int): Role to return

        Returns:
            Data depending on role.
        """
        if not index.isValid():
            return None
        project_item = index.internalPointer()
        if role == Qt.DisplayRole:
            return project_item.name
        else:
            return None

    def project_item(self, index):
        """Returns project item at given index.

        Args:
            index (QModelIndex): Index of project item

        Returns:
            ProjectItem: Item at given index or root project item if index is not valid
        """
        if not index.isValid():
            return self.root()
        return index.internalPointer()

    def find_category(self, category_name):
        """Returns the index of the given category name.

        Args:
            category_name (str): Name of category item to find

        Returns:
             QModelIndex of a category item or None if it was not found
        """
        category_names = [category.name for category in self.root().children()]
        # logging.debug("Category names:{0}".format(category_names))
        try:
            row = category_names.index(category_name)
        except ValueError:
            logging.error("Category name %s not found in %s", category_name, category_names)
            return None
        return self.index(row, 0, QModelIndex())

    def find_item(self, name):
        """Returns the QModelIndex of the project item with the given name

        Args:
            name (str): The searched project item (long) name

        Returns:
            QModelIndex of a project item with the given name or None if not found
        """
        for category in self.root().children():
            # logging.debug("Looking for {0} in category {1}".format(name, category.name))
            category_index = self.find_category(category.name)
            start_index = self.index(0, 0, category_index)
            matching_index = self.match(start_index, Qt.DisplayRole, name,
                                        1, Qt.MatchFixedString | Qt.MatchRecursive)
            if not matching_index:
                pass  # no match in this category
            elif len(matching_index) == 1:
                # logging.debug("Found item:{0}".format(matching_index[0].internalPointer().name))
                return matching_index[0]
        return None

    def insert_item(self, item, parent=QModelIndex()):
        """Add new item to model. Fails if parent_item is not a category item or root item.
        Inserts new item as the last item.

        Args:
            item (ProjectItem): Project item to add to model
            parent (QModelIndex): Parent project item

        Returns:
            True if successful, False otherwise
        """
        parent_item = self.project_item(parent)
        row = self.rowCount(parent)  # parent.child_count()
        # logging.debug("Inserting item on row:{0} under parent:{1}".format(row, parent_item.name))
        self.beginInsertRows(parent, row, row)
        retval = parent_item.add_child(item)
        self.endInsertRows()
        return retval

    def remove_item(self, item, parent=QModelIndex()):
        """Remove item from model.

        Args:
            item (ProjectItem): Project item to remove
            parent (QModelIndex): Parent of item that is to be removed

        Returns:
            bool: True if item removed successfully, False if item removing failed
        """
        parent_item = self.project_item(parent)
        row = item.row()
        self.beginRemoveRows(parent, row, row)
        retval = parent_item.remove_child(row)
        self.endRemoveRows()
        return retval

    def setData(self, index, value, role=Qt.EditRole):
        # TODO: Test this. Should this emit dataChanged signal at some point?
        """Change name of item in index to value.
        # TODO: If the item is a Data Store the reference sqlite path must be updated.

        Args:
            index (QModelIndex): Item index
            value (str): New name
            role (int): Item data role to set

        Returns:
            Boolean value depending on whether the new name is accepted.
        """
        if not role == Qt.EditRole:
            return super().setData(index, value, role)
        item = index.internalPointer()
        old_name = item.name
        if value.strip() == '' or value == old_name:
            return False
        # Check that new name is legal
        if any(True for x in value if x in INVALID_CHARS):
            msg = "<b>{0}</b> contains invalid characters.".format(value)
            # noinspection PyTypeChecker, PyArgumentList, PyCallByClass
            QMessageBox.information(self._toolbox, "Invalid characters", msg)
            return False
        # Check if project item with the same name already exists
        if self.find_item(value):
            msg = "Project item <b>{0}</b> already exists".format(value)
            # noinspection PyTypeChecker, PyArgumentList, PyCallByClass
            QMessageBox.information(self._toolbox, "Invalid name", msg)
            return False
        # Check that no existing project item short name matches the new item's short name.
        # This is to prevent two project items from using the same folder.
        new_short_name = value.lower().replace(' ', '_')
        if self._toolbox.project_item_model.short_name_reserved(new_short_name):
            msg = "Project item using directory <b>{0}</b> already exists".format(new_short_name)
            # noinspection PyTypeChecker, PyArgumentList, PyCallByClass
            QMessageBox.information(self._toolbox, "Invalid name", msg)
            return False
        # Get old data dir which will be renamed
        try:
            old_data_dir = item.data_dir  # Full path
        except AttributeError:
            logging.error("Item does not have a data_dir. "
                          "Make sure that class %s creates one.", item.item_type)
            return False
        # Get project path from the old data dir path
        project_path = os.path.split(old_data_dir)[0]
        # Make path for new data dir
        new_data_dir = os.path.join(project_path, new_short_name)
        # Rename item project directory
        if not rename_dir(self._toolbox, old_data_dir, new_data_dir):
            return False
        # Rename project item
        item.set_name(value)
        # Update project item directory variable
        item.data_dir = new_data_dir
        # If item is a Data Connection the QFileSystemWatcher path must be updated
        if item.item_type == "Data Connection":
            item.data_dir_watcher.removePaths(item.data_dir_watcher.directories())
            item.data_dir_watcher.addPath(item.data_dir)
        # If item is a Tool, also output_dir must be updated
        elif item.item_type == "Tool":
            item.output_dir = os.path.join(item.data_dir, TOOL_OUTPUT_DIR)
        # If item is a Data Store and an SQLite path is set, give the user a notice that this must be updated manually
        elif item.item_type == "Data Store":
            if not self._toolbox.ui.lineEdit_SQLite_file.text().strip() == "":
                self._toolbox.msg_warning.emit("Note: Path to SQLite file may need updating.")
        # Update name label in tab
        item.update_name_label()
        # Update name item of the QGraphicsItem
        item.get_icon().update_name_item(value)
        # Change old item names in connection model headers to the new name
        header_index = self._toolbox.connection_model.find_index_in_header(old_name)
        self._toolbox.connection_model.setHeaderData(header_index, Qt.Horizontal, value)
        self._toolbox.connection_model.setHeaderData(header_index, Qt.Vertical, value)
        # Force save project
        self._toolbox.save_project()
        self._toolbox.msg_success.emit("Project item <b>{0}</b> renamed to <b>{1}</b>".format(old_name, value))
        return True

    def items(self, category_name=None):
        """Returns a list of items in model according to category name. If no category name given,
        returns all project items in a list.

        Args:
            category_name (str): Item category. Data Connections, Data Stores, Tools or Views permitted.

        Returns:
            :obj:'list' of :obj:'ProjectItem': Depending on category_name argument, returns all items or only
            items according to category. An empty list is returned if there are no items in the given category
            or if an unknown category name was given.
        """
        if not category_name:
            items = list()
            for category in self.root().children():
                items += category.children()
            return items
        else:
            category_item = self.find_category(category_name)
            if not category_item:
                logging.error("Category item '%s' not found", category_name)
                return list()
            return category_item.internalPointer().children()

    def n_items(self):
        """Return the number of all project items in the model excluding category items and root."""
        return len(self.items())

    def return_item_names(self):
        """Returns the names of all items in a list."""
        return [item.name for item in self.items()]

    def new_item_index(self, category):
        """Get index where a new item is appended according to category. This is needed for
        appending the connection model.

        Args:
            category (str): Display Role of the parent

        Returns:
            Number of items according to category
        """
        n_data_stores = self.rowCount(self.find_category("Data Stores"))
        n_data_connections = self.rowCount(self.find_category("Data Connections"))
        n_tools = self.rowCount(self.find_category("Tools"))
        if category == "Data Stores":
            # Return number of data stores
            return n_data_stores - 1
        elif category == "Data Connections":
            # Return number of data stores + data connections - 1
            return n_data_stores + n_data_connections - 1
        elif category == "Tools":
            # Return number of data stores + data connections + tools - 1
            return n_data_stores + n_data_connections + n_tools - 1
        elif category == "Views":
            # Return total number of items - 1
            return self.n_items() - 1
        else:
            logging.error("Unknown category: %s", category)
            return 0

    def short_name_reserved(self, short_name):
        """Check if folder name derived from the name of the given item is in use.

        Args:
            short_name (str): Item short name

        Returns:
            bool: True if short name is taken, False if it is available.
        """
        project_items = self.items()
        for item in project_items:
            if item.short_name == short_name:
                return True
        return False


class ToolTemplateModel(QAbstractListModel):
    """Class to store tools that are available in a project e.g. GAMS or Julia models."""
    def __init__(self, toolbox=None):
        super().__init__()
        self._tools = list()
        self._toolbox = toolbox

    def rowCount(self, parent=None, *args, **kwargs):
        """Must be reimplemented when subclassing. Returns
        the number of Tools in the model.

        Args:
            parent (QModelIndex): Not used (because this is a list)

        Returns:
            Number of rows (available tools) in the model
        """
        return len(self._tools)

    def data(self, index, role=None):
        """Must be reimplemented when subclassing.

        Args:
            index (QModelIndex): Requested index
            role (int): Data role

        Returns:
            Data according to requested role
        """
        if not index.isValid() or self.rowCount() == 0:
            return None
        row = index.row()
        if role == Qt.DisplayRole:
            toolname = self._tools[row].name
            return toolname
        elif role == Qt.ToolTipRole:
            if row >= self.rowCount():
                return ""
            else:
                return self._tools[row].def_file_path

    def flags(self, index):
        """Returns enabled flags for the given index.

        Args:
            index (QModelIndex): Index of Tool
        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def insertRow(self, tool, row=None, parent=QModelIndex(), *args, **kwargs):
        """Insert row (tool) into model.

        Args:
            tool (Tool): Tool added to the model
            row (str): Row to insert tool to
            parent (QModelIndex): Parent of child (not used)

        Returns:
            Void
        """
        if not row:
            row = self.rowCount()
        self.beginInsertRows(parent, row, row)
        self._tools.insert(row, tool)
        self.endInsertRows()

    def removeRow(self, row, parent=QModelIndex(), *args, **kwargs):
        """Remove row (tool) from model.

        Args:
            row (int): Row to remove the tool from
            parent (QModelIndex): Parent of tool on row (not used)

        Returns:
            Boolean variable
        """
        if row < 0 or row > self.rowCount():
            # logging.error("Invalid row number")
            return False
        self.beginRemoveRows(parent, row, row)
        self._tools.pop(row)
        self.endRemoveRows()
        return True

    def update_tool_template(self, tool, row):
        """Update tool template.

        Args:
            tool (ToolTemplate): new tool, to replace the old one
            row (int): Position of the tool to be updated

        Returns:
            Boolean value depending on the result of the operation
        """
        try:
            self._tools[row] = tool
            return True
        except IndexError:
            return False

    def tool_template(self, row):
        """Returns tool template on given row.

        Args:
            row (int): Row of tool template

        Returns:
            ToolTemplate from tool template list or None if given row is zero
        """
        return self._tools[row]

    def find_tool_template(self, name):
        """Returns tool template with the given name.

        Args:
            name (str): Name of tool template to find
        """
        for template in self._tools:
            if name.lower() == template.name.lower():
                return template
        return None

    def tool_template_row(self, name):
        """Returns the row on which the given template is located or -1 if it is not found."""
        for i in range(len(self._tools)):
            if name == self._tools[i].name:
                return i
        return -1

    def tool_template_index(self, name):
        """Returns the QModelIndex on which a tool template with
        the given name is located or invalid index if it is not found."""
        row = self.tool_template_row(name)
        if row == -1:
            return QModelIndex()
        return self.createIndex(row, 0)


class ConnectionModel(QAbstractTableModel):
    """Table model for storing connections between items."""

    def __init__(self, toolbox=None):
        super().__init__()
        self._toolbox = toolbox  # QMainWindow
        self.connections = []
        self.header = list()

    def flags(self, index):
        """Returns flags for table items."""
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount(self, *args, **kwargs):
        """Number of rows in the model. This should be the same as the number of items in the project."""
        return len(self.connections)

    def columnCount(self, *args, **kwargs):
        """Number of columns in the model. This should be the same as the number of items in the project."""
        try:
            n = len(self.connections[0])
        except IndexError:
            return 0
        return n

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Returns header data according to given role."""
        if role == Qt.DisplayRole:
            try:
                h = self.header[section]
            except IndexError:
                return None
            return h
        else:
            return None

    def setHeaderData(self, section, orientation, value, role=Qt.EditRole):
        """Sets the data for the given role and section in the header
        with the specified orientation to the value supplied.
        """
        if not role == Qt.EditRole:
            return super().setHeaderData(section, orientation, value, role)
        if orientation in [Qt.Horizontal, Qt.Vertical]:
            try:
                self.header[section] = value
                self.headerDataChanged.emit(orientation, section, section)
                return True
            except IndexError:
                return False
        return False

    def data(self, index, role):
        """Returns the data stored under the given role for the item referred to by the index.
        DisplayRole is a string "False" or "True" depending on if a Link is present.

        Args:
            index (QModelIndex): Index of item
            role (int): Data role

        Returns:
            Item data for given role.
        """
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            if not self.connections[index.row()][index.column()]:
                return "False"  # If there is no Link return "False"
            else:
                return "True"  # If a link is present return "True"
        elif role == Qt.ToolTipRole:
            row_header = self.headerData(index.row(), Qt.Vertical, Qt.DisplayRole)
            column_header = self.headerData(index.column(), Qt.Horizontal, Qt.DisplayRole)
            if row_header == column_header:
                return row_header + " (Feedback)"
            else:
                return row_header + "->" + column_header + " - " + str(index.row()) + ":" + str(index.column())
        elif role == Qt.UserRole:
            return self.connections[index.row()][index.column()]
        else:
            return None

    def setData(self, index, value, role=Qt.EditRole):
        """Set data of single cell in table. Toggles the checkbox state at index.

        Args:
            index (QModelIndex): Index of data to edit
            value (QVariant): Value to write to index (Link instance)
            role (int): Role for editing
        """
        if not index.isValid():
            return False
        if not role == Qt.EditRole:
            return False
        self.connections[index.row()][index.column()] = value  # Should be a Link or None
        # noinspection PyUnresolvedReferences
        self.dataChanged.emit(index, index)
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        """Inserts count rows into the model before the given row.
        Items in the new row will be children of the item represented
        by the parent model index.

        Args:
            row (int): Row number where new rows are inserted
            count (int): Number of inserted rows
            parent (QModelIndex): Parent index

        Returns:
            True if rows were inserted successfully, False otherwise
        """
        if row < 0 or row > self.rowCount():
            return False
        if not count == 1:
            logging.error("Insert 1 row at a time")
            return False
        # beginInsertRows(const QModelIndex & parent, int first, int last)
        self.beginInsertRows(parent, row, row)
        new_row = list()
        if self.columnCount() == 0:
            new_row.append(None)
        else:
            new_row += self.columnCount() * [None]
        # Notice if insert index > rowCount(), new object is inserted to end
        self.connections.insert(row, new_row)
        self.endInsertRows()
        return True

    def insertColumns(self, column, count, parent=QModelIndex()):
        """Inserts count columns into the model before the given column.
        Items in the new column will be children of the item represented
        by the parent model index.

        Args:
            column (int): Column number where new columns are inserted
            count (int): Number of inserted columns
            parent (QModelIndex): Parent index

        Returns:
            True if columns were inserted successfully, False otherwise
        """
        if column < 0 or column > self.columnCount():
            return False
        if not count == 1:
            logging.error("Insert 1 column at a time")
            return False
        # beginInsertColumns(const QModelIndex & parent, int first, int last)
        self.beginInsertColumns(parent, column, column)
        if self.rowCount() == 1:
            # This is the feedback cell of a single item (cell already written in insertRows())
            pass
        else:
            for j in range(self.rowCount()):
                # Notice if insert index > rowCount(), new object is inserted to end
                self.connections[j].insert(column, None)
        self.endInsertColumns()
        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        """Removes count rows starting with the given row under parent.

        Args:
            row (int): Row number where to start removing rows
            count (int): Number of removed rows
            parent (QModelIndex): Parent index

        Returns:
            True if rows were removed successfully, False otherwise
        """
        if row < 0 or row > self.rowCount():
            return False
        if not count == 1:
            logging.error("Remove 1 row at a time")
            return False
        # beginRemoveRows(const QModelIndex & parent, int first, int last)
        self.beginRemoveRows(parent, row, row)
        self.connections.pop(row)
        self.endRemoveRows()
        return True

    def removeColumns(self, column, count, parent=QModelIndex()):
        """Removes count columns starting with the given column under parent.

        Args:
            column (int): Column number where to start removing columns
            count (int): Number of removed columns
            parent (QModelIndex): Parent index

        Returns:
            True if columns were removed successfully, False otherwise
        """
        if column < 0 or column > self.columnCount():
            return False
        if not count == 1:
            logging.error("Remove 1 column at a time")
            return False
        # beginRemoveColumns(const QModelIndex & parent, int first, int last)
        self.beginRemoveColumns(parent, column, column)
        # for loop all rows and remove the column from each
        removed_column = list()  # for testing and debugging
        removing_last_column = False
        if self.columnCount() == 1:
            removing_last_column = True
        for r in self.connections:
            removed_column.append(r.pop(column))
        if removing_last_column:
            self.connections = []
        # logging.debug("{0} removed from column:{1}".format(removed_column, column))
        self.endRemoveColumns()
        return True

    def append_item(self, name, index):
        """Embiggen connections table by a new item.

        Args:
            name (str): New item name
            index (int): Table row and column where the new item is appended

        Returns:
            True if successful, False otherwise
        """
        # item_name = item.name
        # logging.debug("Appending item {0} on row and column: {1}".format(name, index))
        # logging.debug("Appending {3}. rows:{0} columns:{1} data:\n{2}"
        #               .format(self.rowCount(), self.columnCount(), self.connections, item_name))
        self.header.insert(index, name)
        if not self.insertRows(index, 1, parent=QModelIndex()):
            return False
        if not self.insertColumns(index, 1, parent=QModelIndex()):
            return False
        # logging.debug("After append. rows:{0} columns:{1} data:\n{2}"
        #               .format(self.rowCount(), self.columnCount(), self.connections))
        return True

    def remove_item(self, name):
        """Remove project item from connections table.

        Args:
            name (str): Name of removed item

        Returns:
            True if successful, False otherwise
        """
        try:
            item_index = self.header.index(name)
        except ValueError:
            logging.error("%s not found in connection table header list", name)
            return False
        # logging.debug("Removing {3}. rows:{0} columns:{1} data:\n{2}"
        #               .format(self.rowCount(), self.columnCount(), self.connections, item_name))
        if not self.removeRows(item_index, 1, parent=QModelIndex()):
            return False
        if not self.removeColumns(item_index, 1, parent=QModelIndex()):
            return False
        self.header.remove(name)
        # logging.debug("After remove. rows:{0} columns:{1} data:\n{2}"
        #               .format(self.rowCount(), self.columnCount(), self.connections))
        return True

    def output_items(self, name):
        """Returns a list of input items for the given item."""
        item_row = self.header.index(name)  # Row or column of item in the model
        output_items = list()
        for column in range(self.columnCount()):
            a = self.connections[item_row][column]
            # logging.debug("row:{0} column:{1} is {2}".format(item_row, column, a))
            if a:
                # append the name of output item to list
                output_items.append(self.header[column])
        return output_items

    def input_items(self, name):
        """Returns a list of output items for the given item."""
        item_column = self.header.index(name)  # Row or column of item in the model
        input_items = list()
        for row in range(self.rowCount()):
            a = self.connections[row][item_column]
            # logging.debug("row:{0} column:{1} is {2}".format(row, item_column, a))
            if a:
                # append the name of input item to list
                input_items.append(self.header[row])
        return input_items

    def get_connections(self):
        """Returns the internal data structure of the model."""
        return self.connections

    def connected_links(self, name):
        """Returns a list of connected links for the given item"""
        item_row = self.header.index(name)  # Row or column of item in the model
        row = self.connections[item_row]
        column = [self.connections[i][item_row] for i in range(self.rowCount()) if i != item_row]
        links = [x for x in row if x]
        links.extend([x for x in column if x])
        return links

    def reset_model(self, connection_table):
        """Reset model. Used in replacing the current model
        with a boolean table that represents connections.
        Overwrites the current model with a True or False
        (boolean) table that is read from a project save
        file (.json). This table is updated by restore_links()
        method to add Link instances to True cells and Nones
        to False cells."""
        if not connection_table:
            return
        # logging.debug("resetting model to:\n{0}".format(connection_table))
        self.beginResetModel()
        self.connections = connection_table
        self.endResetModel()
        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount()-1, self.columnCount()-1)
        self.dataChanged.emit(top_left, bottom_right)

    def find_index_in_header(self, name):
        """Returns the row or column (row==column) of the header item with the given text (item name)."""
        return self.header.index(name)

    def link(self, row, column):
        # TODO: Modify or remove this
        """Returns Link instance stored on row and column."""
        try:
            return self.connections[row][column]
        except IndexError:
            logging.error("IndexError in link()")
            return False


class MinimalTableModel(QAbstractTableModel):
    """Table model for outlining simple tabular data.

    Attributes:
        parent (QMainWindow): the parent widget, usually an instance of TreeViewForm
    """
    def __init__(self, parent=None):
        """Initialize class"""
        super().__init__(parent)
        self._parent = parent
        self._main_data = list()  # DisplayRole and EditRole
        self.default_flags = Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        self.header = list()  # DisplayRole and EditRole
        self.aux_header = list()  # All the other roles, each entry in the list is a dict

    def clear(self):
        """Clear all data in model."""
        self.beginResetModel()
        self._main_data = list()
        self.endResetModel()

    def flags(self, index):
        """Return index flags."""
        if not index.isValid():
            return Qt.NoItemFlags
        return self.default_flags

    def rowCount(self, *args, **kwargs):
        """Number of rows in the model."""
        return len(self._main_data)

    def columnCount(self, *args, **kwargs):
        """Number of columns in the model."""
        try:
            return len(self._main_data[0])
        except IndexError:
            return len(self.header)

    def headerData(self, section, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        """Get headers."""
        if role != Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                try:
                    return self.aux_header[section][role]
                except IndexError:
                    return None
                except KeyError:
                    return None
            return None
        if orientation == Qt.Horizontal:
            try:
                return self.header[section]
            except IndexError:
                return None
        if orientation == Qt.Vertical:
            return section + 1

    def set_horizontal_header_labels(self, labels):
        """Set horizontal header labels."""
        if not labels:
            return
        self.header = labels
        self.aux_header = [{} for i in range(len(labels))]
        self.headerDataChanged.emit(Qt.Horizontal, 0, len(labels) - 1)

    def insert_horizontal_header_labels(self, section, labels):
        """Insert horizontal header labels at the given section."""
        if not labels:
            return
        for j, value in enumerate(labels):
            if section + j >= self.columnCount():
                self.header.append(value)
                self.aux_header.append({})
            else:
                self.header.insert(section + j, value)
                self.aux_header.insert(section + j, {})
        self.headerDataChanged.emit(Qt.Horizontal, section, section + len(labels) - 1)

    def horizontal_header_labels(self):
        return self.header

    def setHeaderData(self, section, orientation, value, role=Qt.EditRole):
        """Sets the data for the given role and section in the header
        with the specified orientation to the value supplied.
        """
        if role != Qt.EditRole:
            try:
                self.aux_header[section][role] = value
                self.headerDataChanged.emit(orientation, section, section)
                return True
            except IndexError:
                return False
        if orientation == Qt.Horizontal:
            try:
                self.header[section] = value
                self.headerDataChanged.emit(orientation, section, section)
                return True
            except IndexError:
                return False
        return False

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index.

        Args:
            index (QModelIndex): Index of item
            role (int): Data role

        Returns:
            Item data for given role.
        """
        if not index.isValid():
            return None
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        try:
            return self._main_data[index.row()][index.column()]
        except IndexError:
            logging.error(index)
            return None

    def row_data(self, row, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the given row.

        Args:
            row (int): Item row
            role (int): Data role

        Returns:
            Row data for given role.
        """
        if not 0 <= row < self.rowCount():
            return None
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        return self._main_data[row]

    def column_data(self, column, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the given column.

        Args:
            column (int): Item column
            role (int): Data role

        Returns:
            Column data for given role.
        """
        if not 0 <= column < self.columnCount():
            return None
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        return [self._main_data[row][column] for row in range(self.rowCount())]

    def model_data(self, role=Qt.DisplayRole):
        """Returns the data stored under the given role in the entire model.

        Args:
            role (int): Data role

        Returns:
            Model data for given role.
        """
        if role in (Qt.DisplayRole, Qt.EditRole):
            return self._main_data
        return [self.row_data(row, role) for row in range(self.rowCount())]

    def setData(self, index, value, role=Qt.EditRole):
        """Set data in model."""
        if not index.isValid():
            return False
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return False
        return self.batch_set_data([index], [value])

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes."""
        if not indexes:
            return False
        if len(indexes) != len(data):
            return False
        for k, index in enumerate(indexes):
            if not index.isValid():
                continue
            self._main_data[index.row()][index.column()] = data[k]
        # Find square envelope of indexes to emit dataChanged
        top = min(ind.row() for ind in indexes)
        bottom = max(ind.row() for ind in indexes)
        left = min(ind.column() for ind in indexes)
        right = max(ind.column() for ind in indexes)
        self.dataChanged.emit(self.index(top, left), self.index(bottom, right), [Qt.EditRole, Qt.DisplayRole])
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        """Inserts count rows into the model before the given row.
        Items in the new row will be children of the item represented
        by the parent model index.

        Args:
            row (int): Row number where new rows are inserted
            count (int): Number of inserted rows
            parent (QModelIndex): Parent index

        Returns:
            True if rows were inserted successfully, False otherwise
        """
        if row < 0 or row > self.rowCount():
            return False
        if count < 1:
            return False
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            if self.columnCount() == 0:
                new_main_row = [None]
            else:
                new_main_row = [None for j in range(self.columnCount())]
            # Notice if insert index > rowCount(), new object is inserted to end
            self._main_data.insert(row + i, new_main_row)
        self.endInsertRows()
        return True

    def insertColumns(self, column, count, parent=QModelIndex()):
        """Inserts count columns into the model before the given column.
        Items in the new column will be children of the item represented
        by the parent model index.

        Args:
            column (int): Column number where new columns are inserted
            count (int): Number of inserted columns
            parent (QModelIndex): Parent index

        Returns:
            True if columns were inserted successfully, False otherwise
        """
        if column < 0 or column > self.columnCount():
            return False
        if count < 1:
            return False
        self.beginInsertColumns(parent, column, column + count - 1)
        for j in range(count):
            for i in range(self.rowCount()):
                self._main_data[i].insert(column + j, None)
        self.endInsertColumns()
        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        """Removes count rows starting with the given row under parent.

        Args:
            row (int): Row number where to start removing rows
            count (int): Number of removed rows
            parent (QModelIndex): Parent index

        Returns:
            True if rows were removed successfully, False otherwise
        """
        if row < 0 or row + count - 1 >= self.rowCount():
            return False
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in reversed(range(row, row + count)):
            self._main_data.pop(i)
        self.endRemoveRows()
        return True

    def removeColumns(self, column, count, parent=QModelIndex()):
        """Removes count columns starting with the given column under parent.

        Args:
            column (int): Column number where to start removing columns
            count (int): Number of removed columns
            parent (QModelIndex): Parent index

        Returns:
            True if columns were removed successfully, False otherwise
        """
        if column < 0 or column >= self.columnCount():
            return False
        if not count == 1:
            logging.error("Remove 1 column at a time")
            return False
        self.beginRemoveColumns(parent, column, column)
        # for loop all rows and remove the column from each
        removing_last_column = False
        if self.columnCount() == 1:
            removing_last_column = True
        for r in self._main_data:
            r.pop(column)
        if removing_last_column:
            self._main_data = []
        # logging.debug("{0} removed from column:{1}".format(removed_column, column))
        self.endRemoveColumns()
        return True

    def reset_model(self, main_data=None, aux_data=None):
        """Reset model."""
        if main_data is None:
            main_data = list()
        self.beginResetModel()
        self._main_data = main_data
        self.endResetModel()


class EmptyRowModel(MinimalTableModel):
    """A table model with a last empty row."""
    def __init__(self, parent=None):
        """Init class."""
        super().__init__(parent)
        self.default_row = {}  # A row of default values to put in any newly inserted row
        self.force_default = False  # Whether or not default values are editable
        self.dataChanged.connect(self._handle_data_changed)
        self.rowsRemoved.connect(self._handle_rows_removed)
        self.rowsInserted.connect(self._handle_rows_inserted)
        self.columnsInserted.connect(self._handle_columns_inserted)

    def flags(self, index):
        """Return default flags except if forcing defaults."""
        if not index.isValid():
            return Qt.NoItemFlags
        if self.force_default:
            try:
                name = self.header[index.column()]
                if name in self.default_row:
                    return self.default_flags & ~Qt.ItemIsEditable
            except IndexError:
                pass
        return self.default_flags

    def set_default_row(self, **kwargs):
        """Set default row data."""
        self.default_row = kwargs

    def clear(self):
        super().clear()
        self.insertRows(self.rowCount(), 1, QModelIndex())

    def reset_model(self, data):
        super().reset_model(data)
        self.insertRows(self.rowCount(), 1, QModelIndex())

    @Slot("QModelIndex", "QModelIndex", "QVector", name="_handle_data_changed")
    def _handle_data_changed(self, top_left, bottom_right, roles=None):
        """Insert a new last empty row in case the previous one has been filled
        with any data other than the defaults."""
        if roles is None:
            roles = list()
        if roles and Qt.EditRole not in roles:
            return
        last_row = self.rowCount() - 1
        for column in range(self.columnCount()):
            try:
                name = self.header[column]
            except IndexError:
                name = None
            data = self._main_data[last_row][column]
            default = self.default_row.get(name)
            if not data and not default:
                continue
            if data != default:
                self.insertRows(self.rowCount(), 1)
                break

    @Slot("QModelIndex", "int", "int", name="_handle_rows_removed")
    def _handle_rows_removed(self, parent, first, last):
        """Insert a new empty row in case it's been removed."""
        last_row = self.rowCount()
        if last_row in range(first, last + 1):
            self.insertRows(self.rowCount(), 1)

    @Slot("QModelIndex", "int", "int", name="_handle_rows_inserted")
    def _handle_rows_inserted(self, parent, first, last):
        """Handle rowsInserted signal."""
        self.set_rows_to_default(first, last)

    def set_rows_to_default(self, first, last):
        """Set default data in newly inserted rows."""
        left = None
        right = None
        for column in range(self.columnCount()):
            try:
                name = self.header[column]
            except IndexError:
                name = None
            default = self.default_row.get(name)
            if left is None:
                left = column
            right = column
            for row in range(first, last + 1):
                self._main_data[row][column] = default
        if left is None:
            return
        top_left = self.index(first, left)
        bottom_right = self.index(last, right)
        self.dataChanged.emit(top_left, bottom_right)

    @Slot("QModelIndex", "int", "int", name="_handle_columns_inserted")
    def _handle_columns_inserted(self, parent, first, last):
        """Set default data in newly inserted columns."""
        left = None
        right = None
        for column in range(first, last + 1):
            try:
                name = self.header[column]
            except IndexError:
                continue
            default = self.default_row.get(name)
            if left is None:
                left = column
            right = column
            for row in range(self.rowCount()):
                self._main_data[row][column] = default
        if left is None:
            return
        top_left = self.index(0, left)
        bottom_right = self.index(self.rowCount() - 1, right)
        self.dataChanged.emit(top_left, bottom_right)


class ObjectClassListModel(QStandardItemModel):
    """A class to list object classes in the GraphViewForm."""
    def __init__(self, graph_view_form):
        """Initialize class"""
        super().__init__(graph_view_form)
        self._graph_view_form = graph_view_form
        self.db_map = graph_view_form.db_map
        self.add_more_index = None

    def populate_list(self):
        """Populate model."""
        self.clear()
        object_class_list = [x for x in self.db_map.object_class_list()]
        for object_class in object_class_list:
            object_class_item = QStandardItem(object_class.name)
            data = {"type": "object_class"}
            data.update(object_class._asdict())
            object_class_item.setData(data, Qt.UserRole + 1)
            object_class_item.setData(object_class.name, Qt.ToolTipRole)
            self.appendRow(object_class_item)
        add_more_item = QStandardItem()
        add_more_item.setData("Add more...", Qt.DisplayRole)
        self.appendRow(add_more_item)
        self.add_more_index = self.indexFromItem(add_more_item)

    def add_object_class(self, object_class):
        """Add object class item to model."""
        object_class_item = QStandardItem(object_class.name)
        data = {"type": "object_class", **object_class._asdict()}
        object_class_item.setData(data, Qt.UserRole + 1)
        object_class_item.setData(object_class.name, Qt.ToolTipRole)
        for i in range(self.rowCount()):
            visited_index = self.index(i, 0)
            visited_display_order = visited_index.data(Qt.UserRole + 1)['display_order']
            if visited_display_order >= object_class.display_order:
                self.insertRow(i, object_class_item)
                return
        self.insertRow(self.rowCount() - 1, object_class_item)

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index."""
        if role == Qt.DecorationRole and index.data(Qt.UserRole + 1):
            return self._graph_view_form.icon_mngr.object_icon(index.data(Qt.UserRole + 1)["name"])
        return super().data(index, role)


class RelationshipClassListModel(QStandardItemModel):
    """A class to list relationship classes in the GraphViewForm."""
    def __init__(self, graph_view_form):
        """Initialize class"""
        super().__init__(graph_view_form)
        self._graph_view_form = graph_view_form
        self.db_map = graph_view_form.db_map
        self.add_more_index = None

    def populate_list(self):
        """Populate model."""
        self.clear()
        relationship_class_list = [x for x in self.db_map.wide_relationship_class_list()]
        for relationship_class in relationship_class_list:
            relationship_class_item = QStandardItem(relationship_class.name)
            data = {"type": "relationship_class"}
            data.update(relationship_class._asdict())
            relationship_class_item.setData(data, Qt.UserRole + 1)
            relationship_class_item.setData(relationship_class.name, Qt.ToolTipRole)
            self.appendRow(relationship_class_item)
        add_more_item = QStandardItem()
        add_more_item.setData("Add more...", Qt.DisplayRole)
        self.appendRow(add_more_item)
        self.add_more_index = self.indexFromItem(add_more_item)

    def add_relationship_class(self, relationship_class):
        """Add relationship class."""
        relationship_class_item = QStandardItem(relationship_class.name)
        data = {"type": "relationship_class", **relationship_class._asdict()}
        relationship_class_item.setData(data, Qt.UserRole + 1)
        relationship_class_item.setData(relationship_class.name, Qt.ToolTipRole)
        self.insertRow(self.rowCount() - 1, relationship_class_item)

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index."""
        if role == Qt.DecorationRole and index.data(Qt.UserRole + 1):
            return self._graph_view_form.icon_mngr.relationship_icon(
                index.data(Qt.UserRole + 1)["object_class_name_list"]
            )
        return super().data(index, role)


class RelationshipTreeModel(QStandardItemModel):
    """A class to display Spine data structure in a treeview
    with relationship classes at the outer level.
    """
    def __init__(self, tree_view_form):
        """Initialize class"""
        super().__init__(tree_view_form)
        self._tree_view_form = tree_view_form
        self.db_map = tree_view_form.db_map
        self.root_item = None
        self.bold_font = QFont()
        self.bold_font.setBold(True)
        self._fetched_relationship_class_id = set()

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index."""
        if role == Qt.ForegroundRole:
            item_type = index.data(Qt.UserRole)
            if item_type.endswith('class') and not self.hasChildren(index):
                return QBrush(Qt.gray)
        if role == Qt.DecorationRole:
            item_type = index.data(Qt.UserRole)
            if item_type == 'relationship_class':
                return self._tree_view_form.icon_mngr.relationship_icon(
                    index.data(Qt.UserRole + 1)["object_class_name_list"]
                )
            if item_type == 'relationship':
                return self._tree_view_form.icon_mngr.relationship_icon(
                    index.parent().data(Qt.UserRole + 1)["object_class_name_list"]
                )
        return super().data(index, role)

    def hasChildren(self, parent):
        """Return True if not fetched, so the user can try and expand it."""
        if not parent.isValid():
            return super().hasChildren(parent)
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return super().hasChildren(parent)
        if parent_type == 'relationship_class':
            relationship_class_id = parent.data(Qt.UserRole + 1)['id']
            if relationship_class_id in self._fetched_relationship_class_id:
                return super().hasChildren(parent)
            return True
        elif parent_type == 'relationship':
            return False
        return super().hasChildren(parent)

    def canFetchMore(self, parent):
        """Return True if not fetched."""
        if not parent.isValid():
            return True
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return True
        if parent_type == 'relationship_class':
            parent_id = parent.data(Qt.UserRole + 1)['id']
            return parent_id not in self._fetched_relationship_class_id
        if parent_type == 'relationship':
            return False

    @busy_effect
    def fetchMore(self, parent):
        """Build the deeper level of the tree"""
        if not parent.isValid():
            return False
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return False
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'relationship_class':
            relationship_class_item = self.itemFromIndex(parent)
            relationship_class = parent.data(Qt.UserRole + 1)
            relationship_list = self.db_map.wide_relationship_list(class_id=relationship_class['id'])
            self.add_relationships_to_class(relationship_list, relationship_class_item)
            self._fetched_relationship_class_id.add(relationship_class['id'])
        self.dataChanged.emit(parent, parent)

    def build_tree(self, database):
        """Build the first level of the tree"""
        self.clear()
        self._fetched_relationship_class_id = set()
        self.root_item = QStandardItem(database)
        self.root_item.setData('root', Qt.UserRole)
        icon = QIcon(":/symbols/Spine_symbol.png")
        self.root_item.setData(icon, Qt.DecorationRole)
        self.add_relationship_classes(self.db_map.wide_relationship_class_list().all())
        self.appendRow(self.root_item)

    def new_relationship_class_item(self, wide_relationship_class):
        """Returns new relationship class item."""
        relationship_class_item = QStandardItem(wide_relationship_class.name)
        relationship_class_item.setData(wide_relationship_class._asdict(), Qt.UserRole + 1)
        relationship_class_item.setData('relationship_class', Qt.UserRole)
        relationship_class_item.setData(wide_relationship_class.object_class_name_list, Qt.ToolTipRole)
        relationship_class_item.setData(self.bold_font, Qt.FontRole)
        return relationship_class_item

    def new_relationship_item(self, wide_relationship, icon):
        """Returns new relationship item."""
        relationship_item = QStandardItem(wide_relationship.object_name_list)
        relationship_item.setData(icon, Qt.DecorationRole)
        relationship_item.setData(wide_relationship._asdict(), Qt.UserRole + 1)
        relationship_item.setData('relationship', Qt.UserRole)
        return relationship_item

    def add_relationship_classes(self, relationship_classes):
        """Add relationship class items to the model."""
        relationship_class_item_list = list()
        for relationship_class in relationship_classes:
            relationship_class_item = self.new_relationship_class_item(relationship_class)
            relationship_class_item_list.append(relationship_class_item)
        self.root_item.appendRows(relationship_class_item_list)

    def add_relationships_to_class(self, relationship_list, relationship_class_item):
        """Add relationship class items to the model."""
        icon = relationship_class_item.data(Qt.DecorationRole)
        relationship_item_list = list()
        for relationship in relationship_list:
            relationship_item = self.new_relationship_item(relationship, icon)
            relationship_item_list.append(relationship_item)
        relationship_class_item.appendRows(relationship_item_list)

    def add_relationships(self, relationships):
        """Add relationship items to the model."""
        relationship_dict = {}
        for relationship in relationships:
            relationship_dict.setdefault(relationship.class_id, list()).append(relationship)
        # Sweep first level and check if there's something to append
        for i in range(self.root_item.rowCount()):
            relationship_class_item = self.root_item.child(i)
            relationship_class_id = relationship_class_item.data(Qt.UserRole + 1)['id']
            try:
                relationship_list = relationship_dict[relationship_class_id]
            except KeyError:
                continue
            # If not fetched, fetch it and continue
            relationship_class_index = self.indexFromItem(relationship_class_item)
            if self.canFetchMore(relationship_class_index):
                self.fetchMore(relationship_class_index)  # NOTE: this also adds the new items, which are now in the db
                continue
            # Already fetched, add new items manually
            self.add_relationships_to_class(relationship_list, relationship_class_item)

    def update_relationship_classes(self, updated_items):
        """Update relationship classes in the model."""
        updated_items_dict = {x.id: x for x in updated_items}
        for i in range(self.root_item.rowCount()):
            visited_item = self.root_item.child(i)
            visited_id = visited_item.data(Qt.UserRole + 1)['id']
            updated_item = updated_items_dict.pop(visited_id, None)
            if not updated_item:
                continue
            visited_item.setData(updated_item._asdict(), Qt.UserRole + 1)
            visited_item.setText(updated_item.name)

    def update_relationships(self, updated_items):
        """Update relationships in the model."""
        updated_items_dict = {x.id: x for x in updated_items}
        for i in range(self.root_item.rowCount()):
            relationship_class_item = self.root_item.child(i)
            for j in range(relationship_class_item.rowCount()):
                visited_item = relationship_class_item.child(j)
                visited_id = visited_item.data(Qt.UserRole + 1)['id']
                updated_item = updated_items_dict.pop(visited_id, None)
                if not updated_item:
                    continue
                visited_item.setData(updated_item._asdict(), Qt.UserRole + 1)
                visited_item.setText(updated_item.object_name_list)

    def remove_items(self, removed_type, removed_ids):
        """Remove all matched items and their 'childs'."""
        # TODO: try and remove all rows at once, if possible
        if not removed_ids:
            return
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        for visited_item in reversed(items):
            visited_type = visited_item.data(Qt.UserRole)
            visited = visited_item.data(Qt.UserRole + 1)
            if visited_type == 'root':
                continue
            # Get visited id
            visited_id = visited['id']
            visited_index = self.indexFromItem(visited_item)
            if visited_type == removed_type and visited_id in removed_ids:
                self.removeRows(visited_index.row(), 1, visited_index.parent())
            # When removing an object class, also remove 'child' relationship classes
            if removed_type == 'object_class' and visited_type == 'relationship_class':
                object_class_id_list = visited['object_class_id_list']
                if any([id in [int(x) for x in object_class_id_list.split(',')] for id in removed_ids]):
                    self.removeRows(visited_index.row(), 1, visited_index.parent())
            # When removing an object, also remove 'child' relationships
            if removed_type == 'object' and visited_type == 'relationship':
                object_id_list = visited['object_id_list']
                if any([id in [int(x) for x in object_id_list.split(',')] for id in removed_ids]):
                    self.removeRows(visited_index.row(), 1, visited_index.parent())


class ObjectTreeModel(QStandardItemModel):
    """A class to display Spine data structure in a treeview
    with object classes at the outer level.
    ."""

    def __init__(self, tree_view_form):
        """Initialize class"""
        super().__init__(tree_view_form)
        self._tree_view_form = tree_view_form
        self.db_map = tree_view_form.db_map
        self.root_item = None
        self.bold_font = QFont()
        self.bold_font.setBold(True)
        self.is_flat = False
        self._fetched = {
            "object_class": set(),
            "object": set(),
            "relationship_class": set()
        }

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index."""
        if role == Qt.ForegroundRole:
            item_type = index.data(Qt.UserRole)
            if item_type.endswith('class') and not self.hasChildren(index):
                return QBrush(Qt.gray)
        elif role == Qt.DecorationRole:
            item_type = index.data(Qt.UserRole)
            if item_type == 'object_class':
                return self._tree_view_form.icon_mngr.object_icon(index.data(Qt.DisplayRole))
            if item_type == 'object':
                return self._tree_view_form.icon_mngr.object_icon(index.parent().data(Qt.DisplayRole))
            if item_type == 'relationship_class':
                return self._tree_view_form.icon_mngr.relationship_icon(
                    index.data(Qt.UserRole + 1)["object_class_name_list"]
                )
            if item_type == 'relationship':
                return self._tree_view_form.icon_mngr.relationship_icon(
                    index.parent().data(Qt.UserRole + 1)["object_class_name_list"]
                )
        return super().data(index, role)

    def backward_sweep(self, index, call=None):
        """Sweep the tree from the given index towards the root, and apply `call` on each."""
        current = index
        while True:
            if call:
                call(current)
            # Try and visit parent
            next_ = current.parent()
            if not next_.isValid():
                break
            current = next_
            continue

    def forward_sweep(self, index, call=None):
        """Sweep the tree from the given index towards the leaves, and apply `call` on each."""
        if call:
            call(index)
        if not self.hasChildren(index):
            return
        current = index
        back_to_parent = False  # True if moving back to the parent index
        while True:
            if call:
                call(current)
            if not back_to_parent:
                # Try and visit first child
                next_ = self.index(0, 0, current)
                if next_.isValid():
                    back_to_parent = False
                    current = next_
                    continue
            # Try and visit next sibling
            next_ = current.sibling(current.row() + 1, 0)
            if next_.isValid():
                back_to_parent = False
                current = next_
                continue
            # Go back to parent
            next_ = self.parent(current)
            if next_ != index:
                back_to_parent = True
                current = next_
                continue
            break

    def hasChildren(self, parent):
        """Return True if not fetched, so the user can try and expand it."""
        if not parent.isValid():
            return super().hasChildren(parent)
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return super().hasChildren(parent)
        if parent_type == 'object_class':
            object_class_id = parent.data(Qt.UserRole + 1)['id']
            if object_class_id in self._fetched['object_class']:
                return super().hasChildren(parent)
            return True
        elif parent_type == 'object':
            if self.is_flat:
                # The flat model doesn't go beyond the 'object' level
                return False
            object_id = parent.data(Qt.UserRole + 1)['id']
            object_class_id = parent.data(Qt.UserRole + 1)['class_id']
            if object_id in self._fetched['object']:
                return super().hasChildren(parent)
            return True
        elif parent_type == 'relationship_class':
            if self.is_flat:
                # The flat model doesn't go beyond the 'object' level
                return False
            object_id = parent.parent().data(Qt.UserRole + 1)['id']
            relationship_class_id = parent.data(Qt.UserRole + 1)['id']
            if (object_id, relationship_class_id) in self._fetched['relationship_class']:
                return super().hasChildren(parent)
            return True
        elif parent_type == 'relationship':
            return False
        return super().hasChildren(parent)

    def canFetchMore(self, parent):
        """Return True if not fetched."""
        if not parent.isValid():
            return True
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return True
        if parent_type in ('object_class', 'object'):
            parent_id = parent.data(Qt.UserRole + 1)['id']
            return parent_id not in self._fetched[parent_type]
        if parent_type == 'relationship_class':
            object_id = parent.parent().data(Qt.UserRole + 1)['id']
            relationship_class_id = parent.data(Qt.UserRole + 1)['id']
            return (object_id, relationship_class_id) not in self._fetched[parent_type]
        if parent_type == 'relationship':
            return False

    @busy_effect
    def fetchMore(self, parent):
        """Build the deeper level of the tree"""
        if not parent.isValid():
            return False
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'root':
            return False
        parent_type = parent.data(Qt.UserRole)
        if parent_type == 'object_class':
            object_class_item = self.itemFromIndex(parent)
            object_class = parent.data(Qt.UserRole + 1)
            object_icon = parent.data(Qt.DecorationRole)
            object_list = self.db_map.object_list(class_id=object_class['id'])
            object_item_list = list()
            for object_ in object_list:
                object_item = QStandardItem(object_.name)
                object_item.setData('object', Qt.UserRole)
                object_item.setData(object_._asdict(), Qt.UserRole + 1)
                object_item.setData(object_.description, Qt.ToolTipRole)
                object_item.setData(object_icon, Qt.DecorationRole)
                object_item_list.append(object_item)
            object_class_item.appendRows(object_item_list)
            self._fetched['object_class'].add(object_class['id'])
        elif parent_type == 'object':
            object_item = self.itemFromIndex(parent)
            object_ = parent.data(Qt.UserRole + 1)
            relationship_class_list = self.db_map.wide_relationship_class_list(object_class_id=object_['class_id'])
            relationship_class_item_list = list()
            for relationship_class in relationship_class_list:
                relationship_class_item = QStandardItem(relationship_class.name)
                relationship_class_item.setData('relationship_class', Qt.UserRole)
                relationship_class_item.setData(relationship_class._asdict(), Qt.UserRole + 1)
                relationship_class_item.setData(relationship_class.object_class_name_list, Qt.ToolTipRole)
                relationship_class_item.setData(self.bold_font, Qt.FontRole)
                relationship_class_item_list.append(relationship_class_item)
            object_item.appendRows(relationship_class_item_list)
            self._fetched['object'].add(object_['id'])
        elif parent_type == 'relationship_class':
            relationship_class_item = self.itemFromIndex(parent)
            relationship_class = parent.data(Qt.UserRole + 1)
            object_ = parent.parent().data(Qt.UserRole + 1)
            relationship_list = self.db_map.wide_relationship_list(
                class_id=relationship_class['id'],
                object_id=object_['id']
                )
            relationship_item_list = list()
            for relationship in relationship_list:
                relationship_item = QStandardItem(relationship.object_name_list)
                relationship_item.setData('relationship', Qt.UserRole)
                relationship_item.setData(relationship._asdict(), Qt.UserRole + 1)
                relationship_item_list.append(relationship_item)
            relationship_class_item.appendRows(relationship_item_list)
            self._fetched['relationship_class'].add((object_['id'], relationship_class['id']))
        self.dataChanged.emit(parent, parent)

    def build_tree(self, database, flat=False):
        """Build the first level of the tree"""
        self.clear()
        self._fetched = {
            "object_class": set(),
            "object": set(),
            "relationship_class": set()
        }
        self.root_item = QStandardItem(database)
        self.root_item.setData('root', Qt.UserRole)
        icon = QIcon(":/symbols/Spine_symbol.png")
        self.root_item.setData(icon, Qt.DecorationRole)
        object_class_item_list = list()
        for object_class in self.db_map.object_class_list():
            object_class_item = QStandardItem(object_class.name)
            object_class_item.setData('object_class', Qt.UserRole)
            object_class_item.setData(object_class._asdict(), Qt.UserRole + 1)
            object_class_item.setData(object_class.description, Qt.ToolTipRole)
            object_class_item.setData(self.bold_font, Qt.FontRole)
            object_class_item_list.append(object_class_item)
        self.root_item.appendRows(object_class_item_list)
        self.appendRow(self.root_item)

    def new_object_class_item(self, object_class):
        """Returns new object class item."""
        object_class_item = QStandardItem(object_class.name)
        object_class_item.setData('object_class', Qt.UserRole)
        object_class_item.setData(object_class._asdict(), Qt.UserRole + 1)
        object_class_item.setData(object_class.description, Qt.ToolTipRole)
        object_class_item.setData(self.bold_font, Qt.FontRole)
        return object_class_item

    def new_object_item(self, object_):
        """Returns new object item."""
        object_item = QStandardItem(object_.name)
        object_item.setData('object', Qt.UserRole)
        object_item.setData(object_._asdict(), Qt.UserRole + 1)
        object_item.setData(object_.description, Qt.ToolTipRole)
        return object_item

    def new_relationship_class_item(self, wide_relationship_class, object_):
        """Returns new relationship class item."""
        relationship_class_item = QStandardItem(wide_relationship_class.name)
        relationship_class_item.setData(wide_relationship_class._asdict(), Qt.UserRole + 1)
        relationship_class_item.setData('relationship_class', Qt.UserRole)
        relationship_class_item.setData(wide_relationship_class.object_class_name_list, Qt.ToolTipRole)
        relationship_class_item.setData(self.bold_font, Qt.FontRole)
        return relationship_class_item

    def new_relationship_item(self, wide_relationship):
        """Returns new relationship item."""
        relationship_item = QStandardItem(wide_relationship.object_name_list)
        relationship_item.setData('relationship', Qt.UserRole)
        relationship_item.setData(wide_relationship._asdict(), Qt.UserRole + 1)
        return relationship_item

    def add_object_classes(self, object_classes):
        """Add object class items to the model."""
        for object_class in object_classes:
            object_class_item = self.new_object_class_item(object_class)
            for i in range(self.root_item.rowCount()):
                visited_object_class_item = self.root_item.child(i)
                visited_object_class = visited_object_class_item.data(Qt.UserRole + 1)
                if visited_object_class['display_order'] >= object_class.display_order:
                    self.root_item.insertRow(i, QStandardItem())
                    self.root_item.setChild(i, 0, object_class_item)
                    break
            else:
                self.root_item.appendRow(object_class_item)

    def add_objects(self, objects):
        """Add object items to the model."""
        object_dict = {}
        for object_ in objects:
            object_dict.setdefault(object_.class_id, list()).append(object_)
        # Sweep first level and check if there's something to append
        for i in range(self.root_item.rowCount()):
            object_class_item = self.root_item.child(i)
            object_class_id = object_class_item.data(Qt.UserRole + 1)['id']
            try:
                object_list = object_dict[object_class_id]
            except KeyError:
                continue
            # If not fetched, fetch it and continue
            object_class_index = self.indexFromItem(object_class_item)
            if self.canFetchMore(object_class_index):
                self.fetchMore(object_class_index)  # NOTE: this also adds the new items, which are now in the db
                continue
            # Already fetched, add new items manually
            object_item_list = list()
            for object_ in object_list:
                object_item = self.new_object_item(object_)
                icon = object_class_item.data(Qt.DecorationRole)
                object_item.setData(icon, Qt.DecorationRole)
                object_item_list.append(object_item)
            object_class_item.appendRows(object_item_list)

    def add_relationship_classes(self, relationship_classes):
        """Add relationship class items to model."""
        relationship_class_dict = {}
        for relationship_class in relationship_classes:
            relationship_class_dict.setdefault(
                relationship_class.object_class_id_list,
                list()
            ).append(relationship_class)
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if not visited_type == 'object':
                continue
            visited_object = visited_item.data(Qt.UserRole + 1)
            visited_object_class_id = visited_object['class_id']
            relationship_class_list = list()
            for object_class_id_list, relationship_classes in relationship_class_dict.items():
                if visited_object_class_id in [int(x) for x in object_class_id_list.split(',')]:
                    relationship_class_list.extend(relationship_classes)
            if not relationship_class_list:
                continue
            # If not fetched, fetch it and continue
            visited_index = self.indexFromItem(visited_item)
            if self.canFetchMore(visited_index):
                self.fetchMore(visited_index)  # NOTE: this also adds the new items, which are now in the db
                continue
            # Already fetched, add new items manually
            relationship_class_item_list = list()
            for relationship_class in relationship_class_list:
                relationship_class_item = self.new_relationship_class_item(relationship_class, visited_object)
                relationship_class_item_list.append(relationship_class_item)
            visited_item.appendRows(relationship_class_item_list)

    def add_relationships(self, relationships):
        """Add relationship items to model."""
        relationship_dict = {}
        for relationship in relationships:
            relationship_dict.setdefault(relationship.class_id, list()).append(relationship)
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if not visited_type == 'relationship_class':
                continue
            visited_relationship_class_id = visited_item.data(Qt.UserRole + 1)['id']
            try:
                relationship_list = relationship_dict[visited_relationship_class_id]
            except KeyError:
                continue
            # If not fetched, fetch it and continue
            visited_index = self.indexFromItem(visited_item)
            if self.canFetchMore(visited_index):
                self.fetchMore(visited_index)  # NOTE: this also adds the new items, which are now in the db
                continue
            # Already fetched, add new items manually
            relationship_item_list = list()
            visited_object_id = visited_item.parent().data(Qt.UserRole + 1)['id']
            for relationship in relationship_list:
                object_id_list = relationship.object_id_list
                if visited_object_id not in [int(x) for x in object_id_list.split(',')]:
                    continue
                relationship_item = self.new_relationship_item(relationship)
                icon = visited_item.data(Qt.DecorationRole)
                relationship_item.setData(icon, Qt.DecorationRole)
                relationship_item_list.append(relationship_item)
            visited_item.appendRows(relationship_item_list)

    def update_object_classes(self, updated_items):
        """Update object classes in the model."""
        updated_items_dict = {x.id: x for x in updated_items}
        for i in range(self.root_item.rowCount()):
            visited_item = self.root_item.child(i)
            visited_id = visited_item.data(Qt.UserRole + 1)['id']
            updated_item = updated_items_dict.pop(visited_id, None)
            if not updated_item:
                continue
            visited_item.setData(updated_item._asdict(), Qt.UserRole + 1)
            visited_item.setData(updated_item.name, Qt.DisplayRole)

    def update_objects(self, updated_items):
        """Update object in the model.
        This of course means updating the object name in relationship items.
        """
        items = self.findItems("*", Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        updated_items_dict = {x.id: x for x in updated_items}
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if visited_type == 'object':
                visited_id = visited_item.data(Qt.UserRole + 1)['id']
                try:
                    updated_item = updated_items_dict[visited_id]
                    visited_item.setData(updated_item._asdict(), Qt.UserRole + 1)
                    visited_item.setText(updated_item.name)
                except KeyError:
                    continue
            elif visited_type == 'relationship':
                relationship = visited_item.data(Qt.UserRole + 1)
                object_id_list = [int(x) for x in relationship['object_id_list'].split(",")]
                object_name_list = relationship['object_name_list'].split(",")
                found = False
                for i, id in enumerate(object_id_list):
                    try:
                        updated_item = updated_items_dict[id]
                        object_name_list[i] = updated_item.name
                        found = True
                    except KeyError:
                        continue
                if found:
                    str_object_name_list = ",".join(object_name_list)
                    relationship['object_name_list'] = str_object_name_list
                    visited_item.setText(str_object_name_list)
                    visited_item.setData(relationship, Qt.UserRole + 1)

    def update_relationship_classes(self, updated_items):
        """Update relationship classes in the model."""
        items = self.findItems("*", Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        updated_items_dict = {x.id: x for x in updated_items}
        for visited_item in items:
            visited_type = visited_item.data(Qt.UserRole)
            if visited_type != 'relationship_class':
                continue
            visited_id = visited_item.data(Qt.UserRole + 1)['id']
            try:
                updated_item = updated_items_dict[visited_id]
                visited_item.setData(updated_item._asdict(), Qt.UserRole + 1)
                visited_item.setText(updated_item.name)
            except KeyError:
                continue

    def update_relationships(self, updated_items):
        """Update relationships in the model.
        Move rows if the objects in the relationship change."""
        items = self.findItems("*", Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        updated_items_dict = {x.id: x for x in updated_items}
        relationships_to_add = set()
        for visited_item in reversed(items):
            visited_type = visited_item.data(Qt.UserRole)
            if visited_type != "relationship":
                continue
            visited_id = visited_item.data(Qt.UserRole + 1)['id']
            try:
                updated_item = updated_items_dict[visited_id]
            except KeyError:
                continue
            # Handle changes in object path
            visited_object_id_list = visited_item.data(Qt.UserRole + 1)['object_id_list']
            updated_object_id_list = updated_item.object_id_list
            if visited_object_id_list != updated_object_id_list:
                visited_index = self.indexFromItem(visited_item)
                self.removeRows(visited_index.row(), 1, visited_index.parent())
                relationships_to_add.add(updated_item)
            else:
                visited_item.setText(updated_item.object_name_list)
                visited_item.setData(updated_item._asdict(), Qt.UserRole + 1)
        self.add_relationships(relationships_to_add)

    def remove_items(self, removed_type, removed_ids):
        """Remove all matched items and their 'childs'."""
        # TODO: try and remove all rows at once, if possible
        if not removed_ids:
            return
        items = self.findItems('*', Qt.MatchWildcard | Qt.MatchRecursive, column=0)
        for visited_item in reversed(items):
            visited_type = visited_item.data(Qt.UserRole)
            visited = visited_item.data(Qt.UserRole + 1)
            if visited_type == 'root':
                continue
            # Get visited id
            visited_id = visited['id']
            visited_index = self.indexFromItem(visited_item)
            if visited_type == removed_type and visited_id in removed_ids:
                self.removeRows(visited_index.row(), 1, visited_index.parent())
            # When removing an object class, also remove 'child' relationship classes
            if removed_type == 'object_class' and visited_type == 'relationship_class':
                object_class_id_list = visited['object_class_id_list']
                if any([id in [int(x) for x in object_class_id_list.split(',')] for id in removed_ids]):
                    self.removeRows(visited_index.row(), 1, visited_index.parent())
            # When removing an object, also remove 'child' relationships
            if removed_type == 'object' and visited_type == 'relationship':
                object_id_list = visited['object_id_list']
                if any([id in [int(x) for x in object_id_list.split(',')] for id in removed_ids]):
                    self.removeRows(visited_index.row(), 1, visited_index.parent())

    def next_relationship_index(self, index):
        """Find and return next ocurrence of relationship item."""
        if index.data(Qt.UserRole) != 'relationship':
            return None
        object_name_list = index.data(Qt.DisplayRole)
        class_id = index.data(Qt.UserRole + 1)["class_id"]
        items = [item for item in self.findItems(object_name_list, Qt.MatchExactly | Qt.MatchRecursive, column=0)
                 if item.data(Qt.UserRole + 1)["class_id"] == class_id]
        position = None
        for i, item in enumerate(items):
            if index == self.indexFromItem(item):
                position = i
                break
        if position is None:
            return None
        position = (position + 1) % len(items)
        return self.indexFromItem(items[position])


class SubParameterModel(MinimalTableModel):
    """A parameter model which corresponds to a slice of the entire table.
    The idea is to combine several of these into one big model.
    Allows specifying set of columns that are non-editable (e.g., object_class_name)
    TODO: how column insertion/removal impacts fixed_columns?
    """
    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self.gray_brush = QGuiApplication.palette().button()
        self.error_log = []
        self.updated_count = 0

    def flags(self, index):
        """Make fixed indexes non-editable."""
        flags = super().flags(index)
        if index.column() in self._parent.fixed_columns:
            return flags & ~Qt.ItemIsEditable
        return flags

    def data(self, index, role=Qt.DisplayRole):
        """Paint background of fixed indexes gray."""
        if role != Qt.BackgroundRole:
            return super().data(index, role)
        if index.column() in self._parent.fixed_columns:
            return self.gray_brush
        return super().data(index, role)

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes.
        Try and update data in the database first,
        and if successful set data in the model.
        Subclasses need to implement `update_items_in_db`.
        """
        self.error_log = []
        self.updated_count = 0
        if not indexes:
            return False
        if len(indexes) != len(data):
            return False
        items_to_update = self.items_to_update(indexes, data)
        upd_ids = self.update_items_in_db(items_to_update)
        header = self._parent.horizontal_header_labels()
        id_column = header.index('id')
        for k, index in enumerate(indexes):
            if self._main_data[index.row()][id_column] not in upd_ids:
                continue
            self._main_data[index.row()][index.column()] = data[k]
        return True

    def items_to_update(self, indexes, data):
        """A list of items (dict) to update in the database. Reimplement in subclasses."""
        return []

    def update_items_in_db(self, items_to_update):
        """A list of ids of items updated in the database. Reimplement in subclasses."""
        return []


class SubParameterValueModel(SubParameterModel):
    """A parameter model which corresponds to a slice of an entire parameter value table.
    The idea is to combine several of these into one big model.
    """
    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def items_to_update(self, indexes, data):
        """A list of items (dict) for updating in the database."""
        items_to_update = dict()
        header = self._parent.horizontal_header_labels()
        id_column = header.index('id')
        for k, index in enumerate(indexes):
            index_data = index.data(Qt.EditRole)
            if not data[k] or str(data[k]).isspace():
                data[k] = None
            if data[k] == index_data:
                continue
            if str(data[k]) == str(index_data):
                continue
            row = index.row()
            id_ = index.sibling(row, id_column).data(Qt.EditRole)
            if not id_:
                continue
            field_name = header[index.column()]
            item = {"id": id_, field_name: data[k]}
            items_to_update.setdefault(id_, dict()).update(item)
        return list(items_to_update.values())

    @busy_effect
    def update_items_in_db(self, items_to_update):
        """Try and update parameter values in database."""
        if not items_to_update:
            return []
        try:
            upd_items, error_log = self._parent.db_map.update_parameter_values(*items_to_update)
            self.updated_count += upd_items.count()
            self.error_log += error_log
            return [x.id for x in upd_items]
        except SpineDBAPIError as e:
            self.error_log.append(e.msg)
            return []

    def data(self, index, role=Qt.DisplayRole):
        """Limit the display of json array data."""
        if role == Qt.ToolTipRole and self._parent.header[index.column()] == 'value':
            return strip_json_data(super().data(index, Qt.DisplayRole), 512)
        if role == Qt.DisplayRole and self._parent.header[index.column()] == 'value':
            return strip_json_data(super().data(index, Qt.DisplayRole), 16)
        return super().data(index, role)


class SubParameterDefinitionModel(SubParameterModel):
    """A parameter model which corresponds to a slice of an entire parameter definition table.
    The idea is to combine several of these into one big model.
    """
    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def items_to_update(self, indexes, data):
        """A list of items (dict) for updating in the database."""
        items_to_update = dict()
        header = self._parent.horizontal_header_labels()
        id_column = header.index('id')
        value_list_id_column = header.index('value_list_id')
        parameter_tag_id_list_column = header.index('parameter_tag_id_list')
        parameter_value_list_dict = {x.name: x.id for x in self._parent.db_map.wide_parameter_value_list_list()}
        parameter_tag_dict = {x.tag: x.id for x in self._parent.db_map.parameter_tag_list()}
        new_indexes = []
        new_data = []
        for k, index in enumerate(indexes):
            index_data = index.data(Qt.EditRole)
            if str(data[k]) == str(index_data):
                continue
            if not data[k] and not index_data:
                continue
            if str(data[k]).isspace():
                data[k] = None
            row = index.row()
            id_ = index.sibling(row, id_column).data(Qt.EditRole)
            if not id_:
                continue
            field_name = header[index.column()]
            item = {"id": id_}
            # Handle changes in parameter tag list: update tag id list accordingly
            if field_name == "parameter_tag_list":
                split_parameter_tag_list = data[k].split(",") if data[k] else []
                try:
                    parameter_tag_id_list = ",".join(str(parameter_tag_dict[x]) for x in split_parameter_tag_list)
                    new_indexes.append(index.sibling(row, parameter_tag_id_list_column))
                    new_data.append(parameter_tag_id_list)
                    item.update({'parameter_tag_id_list': parameter_tag_id_list})
                except KeyError as e:
                    self.error_log.append("Invalid parameter tag '{}'.".format(e))
            # Handle changes in value_list name: update value_list id accordingly
            elif field_name == "value_list_name":
                value_list_name = data[k]
                try:
                    value_list_id = parameter_value_list_dict[value_list_name]
                    new_indexes.append(index.sibling(row, value_list_id_column))
                    new_data.append(value_list_id)
                    item.update({'parameter_value_list_id': value_list_id})
                except KeyError:
                    self.error_log.append("Invalid value list '{}'.".format(value_list_name))
            elif field_name == "parameter_name":
                item.update({"name": data[k]})
            else:
                item.update({field_name: data[k]})
            items_to_update.setdefault(id_, dict()).update(item)
        indexes.extend(new_indexes)
        data.extend(new_data)
        return list(items_to_update.values())

    @busy_effect
    def update_items_in_db(self, items_to_update):
        """Try and update parameter definitions in database."""
        if not items_to_update:
            return []
        try:
            tag_dict = dict()
            for item in items_to_update:
                parameter_tag_id_list = item.pop("parameter_tag_id_list", None)
                if parameter_tag_id_list is None:
                    continue
                tag_dict[item["id"]] = parameter_tag_id_list
            upd_def_tag_list, def_tag_error_log = self._parent.db_map.set_parameter_definition_tags(tag_dict)
            upd_params, param_error_log = self._parent.db_map.update_parameters(*items_to_update)
            self.updated_count += len(upd_def_tag_list) + upd_params.count()
            self.error_log += def_tag_error_log + param_error_log
            return [x.parameter_definition_id for x in upd_def_tag_list] + [x.id for x in upd_params]
        except SpineDBAPIError as e:
            self.error_log.append(e.msg)
            return []

    def data(self, index, role=Qt.DisplayRole):
        """Limit the display of json array data."""
        if role == Qt.ToolTipRole and self._parent.header[index.column()] == 'default_value':
            return strip_json_data(super().data(index, Qt.DisplayRole), 512)
        if role == Qt.DisplayRole and self._parent.header[index.column()] == 'default_value':
            return strip_json_data(super().data(index, Qt.DisplayRole), 16)
        return super().data(index, role)


class EmptyParameterModel(EmptyRowModel):
    """An empty parameter model.
    It implements `bath_set_data` for all 'EmptyParameter' models.
    """
    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent
        self.error_log = []
        self.added_rows = []

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes.
        Set data in model first, then check if the database needs to be updated as well.
        Extend set of indexes as additional data is set (for emitting dataChanged at the end).
        Subclasses need to implement `items_to_add` and `add_items_to_db`."""
        self.error_log = []
        self.added_rows = []
        if not super().batch_set_data(indexes, data):
            return False
        items_to_add = self.items_to_add(indexes)
        self.add_items_to_db(items_to_add)
        return True


class EmptyParameterValueModel(EmptyParameterModel):
    """An empty parameter value model.
    Implements `add_items_to_db` for both EmptyObjectParameterValueModel
    and EmptyRelationshipParameterValueModel.
    """
    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    @busy_effect
    def add_items_to_db(self, items_to_add):
        """Add parameter values to database.
        """
        if not items_to_add:
            return
        try:
            items = list(items_to_add.values())
            parameter_values, error_log = self._parent.db_map.add_parameter_values(*items)
            self.added_rows = list(items_to_add.keys())
            id_column = self._parent.horizontal_header_labels().index('id')
            for i, parameter_value in enumerate(parameter_values):
                self._main_data[self.added_rows[i]][id_column] = parameter_value.id
            self.error_log.extend(error_log)
        except SpineDBAPIError as e:
            self.error_log.append(e.msg)


class EmptyObjectParameterValueModel(EmptyParameterValueModel):
    """An empty object parameter value model.
    Implements `items_to_add`.
    """
    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def items_to_add(self, indexes):
        """A dictionary of rows (int) to items (dict) to add to the db.
        Extend set of indexes as additional data is set."""
        items_to_add = dict()
        # Get column numbers
        header = self._parent.horizontal_header_labels()
        object_class_id_column = header.index('object_class_id')
        object_class_name_column = header.index('object_class_name')
        object_id_column = header.index('object_id')
        object_name_column = header.index('object_name')
        parameter_id_column = header.index('parameter_id')
        parameter_name_column = header.index('parameter_name')
        # Query db and build ad-hoc dicts
        object_class_list = self._parent.db_map.object_class_list().all()
        object_class_dict = {x.name: x.id for x in object_class_list}
        object_class_name_dict = {x.id: x.name for x in object_class_list}
        object_dict = {x.name: {'id': x.id, 'class_id': x.class_id} for x in self._parent.db_map.object_list()}
        parameter_dict = {}
        for x in self._parent.db_map.object_parameter_list():
            parameter_dict.setdefault(x.parameter_name, {}).update(
                {x.object_class_id: {'id': x.id, 'object_class_id': x.object_class_id}})
        unique_rows = {ind.row() for ind in indexes}
        for row in unique_rows:
            object_class_name = self.index(row, object_class_name_column).data(Qt.DisplayRole)
            object_name = self.index(row, object_name_column).data(Qt.DisplayRole)
            parameter_name = self.index(row, parameter_name_column).data(Qt.DisplayRole)
            object_class_id = None
            object_ = None
            parameter = None
            if object_class_name:
                try:
                    object_class_id = object_class_dict[object_class_name]
                    self._main_data[row][object_class_id_column] = object_class_id
                except KeyError:
                    self.error_log.append("Invalid object class '{}'".format(object_class_name))
            if object_name:
                try:
                    object_ = object_dict[object_name]
                    self._main_data[row][object_id_column] = object_['id']
                except KeyError:
                    self.error_log.append("Invalid object '{}'".format(object_name))
            if parameter_name:
                try:
                    dup_parameters = parameter_dict[parameter_name]
                    if len(dup_parameters) == 1:
                        parameter = list(dup_parameters.values())[0]
                    elif object_class_id in dup_parameters:
                        parameter = dup_parameters[object_class_id]
                    if parameter is not None:
                        self._main_data[row][parameter_id_column] = parameter['id']
                except KeyError:
                    self.error_log.append("Invalid parameter '{}'".format(parameter_name))
            if object_class_id is None:
                if object_ is not None:
                    object_class_id = object_['class_id']
                    object_class_name = object_class_name_dict[object_class_id]
                    self._main_data[row][object_class_id_column] = object_class_id
                    self._main_data[row][object_class_name_column] = object_class_name
                    indexes.append(self.index(row, object_class_name_column))
                elif parameter is not None:
                    object_class_id = parameter['object_class_id']
                    object_class_name = object_class_name_dict[object_class_id]
                    self._main_data[row][object_class_id_column] = object_class_id
                    self._main_data[row][object_class_name_column] = object_class_name
                    indexes.append(self.index(row, object_class_name_column))
            if object_ is None or parameter is None:
                continue
            item = {
                "object_id": object_['id'],
                "parameter_id": parameter['id']
            }
            for column in range(parameter_name_column + 1, self.columnCount()):
                item[header[column]] = self.index(row, column).data(Qt.DisplayRole)
            items_to_add[row] = item
        return items_to_add


class EmptyRelationshipParameterValueModel(EmptyParameterValueModel):
    """An empty relationship parameter value model.
    Reimplements alsmot all methods from the super class EmptyParameterModel.
    """
    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes. A little different from the base class implementation,
        since here we need to manage creating relationships on the fly.
        """
        self.error_log = []
        self.added_rows = []
        if not indexes:
            return False
        if len(indexes) != len(data):
            return False
        for k, index in enumerate(indexes):
            self._main_data[index.row()][index.column()] = data[k]
        relationships_on_the_fly = self.relationships_on_the_fly(indexes)
        items_to_add = self.items_to_add(indexes, relationships_on_the_fly)
        self.add_items_to_db(items_to_add)
        # Find square envelope of indexes to emit dataChanged
        top = min(ind.row() for ind in indexes)
        bottom = max(ind.row() for ind in indexes)
        left = min(ind.column() for ind in indexes)
        right = max(ind.column() for ind in indexes)
        self.dataChanged.emit(self.index(top, left), self.index(bottom, right))
        return True

    def relationships_on_the_fly(self, indexes):
        """A dict of row (int) to relationship item (KeyedTuple),
        which can be either retrieved or added on the fly.
        Extend set of indexes as additional data is set.
        """
        relationships_on_the_fly = dict()
        relationships_to_add = dict()
        # Get column numbers
        header = self._parent.horizontal_header_labels()
        relationship_class_id_column = header.index('relationship_class_id')
        relationship_class_name_column = header.index('relationship_class_name')
        object_class_id_list_column = header.index('object_class_id_list')
        object_class_name_list_column = header.index('object_class_name_list')
        object_id_list_column = header.index('object_id_list')
        object_name_list_column = header.index('object_name_list')
        parameter_id_column = header.index('parameter_id')
        parameter_name_column = header.index('parameter_name')
        # Query db and build ad-hoc dicts
        relationship_class_dict = {
            x.name: {
                "id": x.id,
                "object_class_id_list": x.object_class_id_list,
                "object_class_name_list": x.object_class_name_list
            } for x in self._parent.db_map.wide_relationship_class_list()}
        relationship_class_name_dict = {x.id: x.name for x in self._parent.db_map.wide_relationship_class_list()}
        parameter_dict = {}
        for x in self._parent.db_map.relationship_parameter_list():
            parameter_dict.setdefault(x.parameter_name, {}).update(
                {x.relationship_class_id: {'id': x.id, 'relationship_class_id': x.relationship_class_id}})
        relationship_dict = {
            (x.class_id, x.object_id_list): x.id for x in self._parent.db_map.wide_relationship_list()}
        object_dict = {x.name: x.id for x in self._parent.db_map.object_list()}
        unique_rows = {ind.row() for ind in indexes}
        for row in unique_rows:
            relationship_class_name = self.index(row, relationship_class_name_column).data(Qt.DisplayRole)
            parameter_name = self.index(row, parameter_name_column).data(Qt.DisplayRole)
            object_name_list = self.index(row, object_name_list_column).data(Qt.DisplayRole)
            relationship_class_id = None
            object_id_list = None
            parameter = None
            if relationship_class_name:
                try:
                    relationship_class = relationship_class_dict[relationship_class_name]
                    relationship_class_id = relationship_class['id']
                    object_class_id_list = relationship_class['object_class_id_list']
                    object_class_name_list = relationship_class['object_class_name_list']
                    self._main_data[row][relationship_class_id_column] = relationship_class_id
                    self._main_data[row][object_class_id_list_column] = object_class_id_list
                    self._main_data[row][object_class_name_list_column] = object_class_name_list
                    indexes.append(self.index(row, object_class_name_list_column))
                except KeyError:
                    self.error_log.append("Invalid relationship class '{}'".format(relationship_class_name))
            if object_name_list:
                try:
                    object_id_list = [object_dict[x] for x in object_name_list.split(",")]
                    join_object_id_list = ",".join(str(x) for x in object_id_list)
                    self._main_data[row][object_id_list_column] = join_object_id_list
                except KeyError as e:
                    self.error_log.append("Invalid object '{}'".format(e))
            if parameter_name:
                try:
                    dup_parameters = parameter_dict[parameter_name]
                    if len(dup_parameters) == 1:
                        parameter = list(dup_parameters.values())[0]
                    elif relationship_class_id in dup_parameters:
                        parameter = dup_parameters[relationship_class_id]
                    if parameter is not None:
                        self._main_data[row][parameter_id_column] = parameter['id']
                except KeyError:
                    self.error_log.append("Invalid parameter '{}'".format(parameter_name))
            if relationship_class_id is None and parameter is not None:
                relationship_class_id = parameter['relationship_class_id']
                relationship_class_name = relationship_class_name_dict[relationship_class_id]
                relationship_class = relationship_class_dict[relationship_class_name]
                object_class_id_list = relationship_class['object_class_id_list']
                object_class_name_list = relationship_class['object_class_name_list']
                self._main_data[row][relationship_class_id_column] = relationship_class_id
                self._main_data[row][relationship_class_name_column] = relationship_class_name
                self._main_data[row][object_class_id_list_column] = object_class_id_list
                self._main_data[row][object_class_name_list_column] = object_class_name_list
                indexes.append(self.index(row, relationship_class_name_column))
                indexes.append(self.index(row, object_class_name_list_column))
            if relationship_class_id is None or object_id_list is None:
                continue
            try:
                relationship_id = relationship_dict[relationship_class_id, join_object_id_list]
                relationships_on_the_fly[row] = relationship_id
            except KeyError:
                relationship_name = relationship_class_name + "_" + object_name_list.replace(",", "__")
                relationship = {
                    "name": relationship_name,
                    "object_id_list": object_id_list,
                    "class_id": relationship_class_id
                }
                relationships_to_add[row] = relationship
        new_relationships = self.add_relationships(relationships_to_add)
        if new_relationships:
            relationships_on_the_fly.update(new_relationships)
        return relationships_on_the_fly

    def add_relationships(self, relationships_to_add):
        """Add relationships to database on the fly and return them."""
        if not relationships_to_add:
            return {}
        try:
            items = list(relationships_to_add.values())
            rows = list(relationships_to_add.keys())
            relationships, error_log = self._parent.db_map.add_wide_relationships(*items)
            self._parent._tree_view_form.object_tree_model.add_relationships(relationships)
            self.error_log.extend(error_log)
            return dict(zip(rows, [x.id for x in relationships]))
        except SpineDBAPIError as e:
            self.error_log.append(e.msg)
            return {}

    def items_to_add(self, indexes, relationships_on_the_fly):
        """A dictionary of rows (int) to items (dict) to add to the db.
        Extend set of indexes as additional data is set."""
        items_to_add = dict()
        # Get column numbers
        header = self._parent.horizontal_header_labels()
        relationship_id_column = header.index('relationship_id')
        parameter_id_column = header.index('parameter_id')
        parameter_name_column = header.index('parameter_name')
        # Query db and build ad-hoc dicts
        for row in {ind.row() for ind in indexes}:
            parameter_id = self.index(row, parameter_id_column).data(Qt.DisplayRole)
            if parameter_id is None:
                continue
            try:
                relationship_id = relationships_on_the_fly[row]
                self._main_data[row][relationship_id_column] = relationship_id
            except KeyError:
                continue
            item = {
                "relationship_id": relationship_id,
                "parameter_id": parameter_id
            }
            for column in range(parameter_name_column + 1, self.columnCount()):
                item[header[column]] = self.index(row, column).data(Qt.DisplayRole)
            items_to_add[row] = item
        return items_to_add


class EmptyParameterDefinitionModel(EmptyParameterModel):
    """An empty parameter definition model."""
    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    @busy_effect
    def add_items_to_db(self, items_to_add):
        """Add parameter definitions to database.
        """
        if not items_to_add:
            return
        try:
            items = list(items_to_add.values())
            name_tag_dict = dict()
            for item in items:
                parameter_tag_id_list = item.pop("parameter_tag_id_list", None)
                if parameter_tag_id_list is None:
                    continue
                name_tag_dict[item["name"]] = parameter_tag_id_list
            parameters, error_log = self._parent.db_map.add_parameters(*items)
            self.added_rows = list(items_to_add.keys())
            self.error_log.extend(error_log)
            id_column = self._parent.horizontal_header_labels().index('id')
            tag_dict = dict()
            for i, parameter in enumerate(parameters):
                if parameter.name in name_tag_dict:
                    tag_dict[parameter.id] = name_tag_dict[parameter.name]
                self._main_data[self.added_rows[i]][id_column] = parameter.id
            upd_def_tag_list, def_tag_error_log = self._parent.db_map.set_parameter_definition_tags(tag_dict)
            self.error_log.extend(def_tag_error_log)
        except SpineDBAPIError as e:
            self.error_log.append(e.msg)


class EmptyObjectParameterDefinitionModel(EmptyParameterDefinitionModel):
    """An empty object parameter definition model."""
    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def items_to_add(self, indexes):
        """Return a dictionary of rows (int) to items (dict) to add to the db."""
        items_to_add = dict()
        # Get column numbers
        header = self._parent.horizontal_header_labels()
        object_class_id_column = header.index('object_class_id')
        object_class_name_column = header.index('object_class_name')
        parameter_name_column = header.index('parameter_name')
        parameter_tag_list_column = header.index('parameter_tag_list')
        parameter_tag_id_list_column = header.index('parameter_tag_id_list')
        value_list_id_column = header.index('value_list_id')
        value_list_name_column = header.index('value_list_name')
        # Query db and build ad-hoc dicts
        object_class_dict = {x.name: x.id for x in self._parent.db_map.object_class_list()}
        parameter_tag_dict = {x.tag: x.id for x in self._parent.db_map.parameter_tag_list()}
        parameter_value_list_dict = {x.name: x.id for x in self._parent.db_map.wide_parameter_value_list_list()}
        for row in {ind.row() for ind in indexes}:
            object_class_name = self.index(row, object_class_name_column).data(Qt.DisplayRole)
            parameter_name = self.index(row, parameter_name_column).data(Qt.DisplayRole)
            parameter_tag_list = self.index(row, parameter_tag_list_column).data(Qt.DisplayRole)
            value_list_name = self.index(row, value_list_name_column).data(Qt.DisplayRole)
            object_class_id = None
            if object_class_name:
                try:
                    object_class_id = object_class_dict[object_class_name]
                    self._main_data[row][object_class_id_column] = object_class_id
                except KeyError:
                    self.error_log.append("Invalid object class '{}'".format(object_class_name))
            if parameter_tag_list:
                try:
                    split_parameter_tag_list = parameter_tag_list.split(",")
                    parameter_tag_id_list = ",".join(str(parameter_tag_dict[x]) for x in split_parameter_tag_list)
                    self._main_data[row][parameter_tag_id_list_column] = parameter_tag_id_list
                except KeyError as e:
                    self.error_log.append("Invalid parameter tag '{}'".format(e))
            if value_list_name:
                try:
                    value_list_id = parameter_value_list_dict[value_list_name]
                    self._main_data[row][value_list_id_column] = value_list_id
                except KeyError:
                    self.error_log.append("Invalid value list '{}'".format(value_list_name))
            if not parameter_name or object_class_id is None:
                continue
            item = {
                "object_class_id": object_class_id,
                "name": parameter_name
            }
            for column in range(parameter_name_column + 1, self.columnCount()):
                item[header[column]] = self.index(row, column).data(Qt.DisplayRole)
            items_to_add[row] = item
        return items_to_add


class EmptyRelationshipParameterDefinitionModel(EmptyParameterDefinitionModel):
    """An empty relationship parameter definition model."""
    def __init__(self, parent):
        """Initialize class."""
        super().__init__(parent)
        self._parent = parent

    def items_to_add(self, indexes):
        """Return a dictionary of rows (int) to items (dict) to add to the db.
        Extend set of indexes as additional data is set."""
        items_to_add = dict()
        # Get column numbers
        header = self._parent.horizontal_header_labels()
        relationship_class_id_column = header.index('relationship_class_id')
        relationship_class_name_column = header.index('relationship_class_name')
        object_class_id_list_column = header.index('object_class_id_list')
        object_class_name_list_column = header.index('object_class_name_list')
        parameter_name_column = header.index('parameter_name')
        parameter_tag_list_column = header.index('parameter_tag_list')
        parameter_tag_id_list_column = header.index('parameter_tag_id_list')
        value_list_id_column = header.index('value_list_id')
        value_list_name_column = header.index('value_list_name')
        # Query db and build ad-hoc dicts
        relationship_class_dict = {
            x.name: {
                'id': x.id,
                'object_class_id_list': x.object_class_id_list,
                'object_class_name_list': x.object_class_name_list
            } for x in self._parent.db_map.wide_relationship_class_list()}
        parameter_tag_dict = {x.tag: x.id for x in self._parent.db_map.parameter_tag_list()}
        parameter_value_list_dict = {x.name: x.id for x in self._parent.db_map.wide_parameter_value_list_list()}
        unique_rows = {ind.row() for ind in indexes}
        for row in unique_rows:
            relationship_class_name = self.index(row, relationship_class_name_column).data(Qt.DisplayRole)
            object_class_name_list = self.index(row, object_class_name_list_column).data(Qt.DisplayRole)
            parameter_name = self.index(row, parameter_name_column).data(Qt.DisplayRole)
            parameter_tag_list = self.index(row, parameter_tag_list_column).data(Qt.DisplayRole)
            value_list_name = self.index(row, value_list_name_column).data(Qt.DisplayRole)
            relationship_class_id = None
            if relationship_class_name:
                try:
                    relationship_class = relationship_class_dict[relationship_class_name]
                    relationship_class_id = relationship_class['id']
                    object_class_id_list = relationship_class['object_class_id_list']
                    object_class_name_list = relationship_class['object_class_name_list']
                    self._main_data[row][relationship_class_id_column] = relationship_class_id
                    self._main_data[row][object_class_id_list_column] = object_class_id_list
                    self._main_data[row][object_class_name_list_column] = object_class_name_list
                    indexes.append(self.index(row, object_class_name_list_column))
                except KeyError:
                    self.error_log.append("Invalid relationship class '{}'".format(relationship_class_name))
            if parameter_tag_list:
                try:
                    split_parameter_tag_list = parameter_tag_list.split(",")
                    parameter_tag_id_list = ",".join(str(parameter_tag_dict[x]) for x in split_parameter_tag_list)
                    self._main_data[row][parameter_tag_id_list_column] = parameter_tag_id_list
                except KeyError as e:
                    self.error_log.append("Invalid tag '{}'".format(e))
            if value_list_name:
                try:
                    value_list_id = parameter_value_list_dict[value_list_name]
                    self._main_data[row][value_list_id_column] = value_list_id
                except KeyError:
                    self.error_log.append("Invalid value list '{}'".format(value_list_name))
            if not parameter_name or relationship_class_id is None:
                continue
            item = {
                "relationship_class_id": relationship_class_id,
                "name": parameter_name
            }
            for column in range(parameter_name_column + 1, self.columnCount()):
                item[header[column]] = self.index(row, column).data(Qt.DisplayRole)
            items_to_add[row] = item
        return items_to_add


class ObjectParameterModel(MinimalTableModel):
    """A model that concatenates several 'sub' object parameter models,
    one per object class.
    """
    def __init__(self, tree_view_form=None):
        """Init class."""
        super().__init__(tree_view_form)
        self._tree_view_form = tree_view_form
        self.db_map = tree_view_form.db_map
        self.sub_models = {}
        self.empty_row_model = None
        self.fixed_columns = list()
        self.filtered_out = dict()
        self.italic_font = QFont()
        self.italic_font.setItalic(True)

    def flags(self, index):
        """Return flags for given index.
        Depending on the index's row we will land on a specific model.
        Models whose object class id is not selected are skipped.
        """
        row = index.row()
        column = index.column()
        selected_object_class_ids = self._tree_view_form.all_selected_object_class_ids()
        for object_class_id, model in self.sub_models.items():
            if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                continue
            if row < model.rowCount():
                return model.index(row, column).flags()
            row -= model.rowCount()
        return self.empty_row_model.index(row, column).flags()

    def data(self, index, role=Qt.DisplayRole):
        """Return data for given index and role.
        Depending on the index's row we will land on a specific model.
        Models whose object class id is not selected are skipped.
        """
        row = index.row()
        column = index.column()
        selected_object_class_ids = self._tree_view_form.all_selected_object_class_ids()
        for object_class_id, model in self.sub_models.items():
            if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                continue
            if row < model.rowCount():
                if role == Qt.DecorationRole and column == self.object_class_name_column:
                    object_class_name = model.index(row, column).data(Qt.DisplayRole)
                    return self._tree_view_form.icon_mngr.object_icon(object_class_name)
                return model.index(row, column).data(role)
            row -= model.rowCount()
        if role == Qt.DecorationRole and column == self.object_class_name_column:
            object_class_name = self.empty_row_model.index(row, column).data(Qt.DisplayRole)
            return self._tree_view_form.icon_mngr.object_icon(object_class_name)
        return self.empty_row_model.index(row, column).data(role)

    def rowCount(self, parent=QModelIndex()):
        """Return the sum of rows in all models.
        Skip models whose object class id is not selected.
        """
        count = 0
        selected_object_class_ids = self._tree_view_form.all_selected_object_class_ids()
        for object_class_id, model in self.sub_models.items():
            if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                continue
            count += model.rowCount()
        count += self.empty_row_model.rowCount()
        return count

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes.
        Distribute indexes and data among the different submodels
        and call batch_set_data on each of them."""
        if not indexes:
            return False
        if len(indexes) != len(data):
            return False
        model_indexes = {}
        model_data = {}
        selected_object_class_ids = self._tree_view_form.all_selected_object_class_ids()
        for k, index in enumerate(indexes):
            if not index.isValid():
                continue
            row = index.row()
            column = index.column()
            for object_class_id, model in self.sub_models.items():
                if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                    continue
                if row < model.rowCount():
                    model_indexes.setdefault(model, list()).append(model.index(row, column))
                    model_data.setdefault(model, list()).append(data[k])
                    break
                row -= model.rowCount()
            else:
                model = self.empty_row_model
                model_indexes.setdefault(model, list()).append(model.index(row, column))
                model_data.setdefault(model, list()).append(data[k])
        updated_count = 0
        update_error_log = []
        for model in self.sub_models.values():
            model.batch_set_data(model_indexes.get(model, list()), model_data.get(model, list()))
            updated_count += model.sourceModel().updated_count
            update_error_log += model.sourceModel().error_log
        model = self.empty_row_model
        model.batch_set_data(model_indexes.get(model, list()), model_data.get(model, list()))
        add_error_log = model.error_log
        added_rows = model.added_rows
        # Find square envelope of indexes to emit dataChanged
        top = min(ind.row() for ind in indexes)
        bottom = max(ind.row() for ind in indexes)
        left = min(ind.column() for ind in indexes)
        right = max(ind.column() for ind in indexes)
        self.dataChanged.emit(self.index(top, left), self.index(bottom, right))
        if added_rows:
            self.move_rows_to_sub_models(added_rows)
            self._tree_view_form.commit_available.emit(True)
            self._tree_view_form.msg.emit("Successfully added entries.")
        if updated_count:
            self._tree_view_form.commit_available.emit(True)
            self._tree_view_form.msg.emit("Successfully updated entries.")
        error_log = add_error_log + update_error_log
        if error_log:
            msg = format_string_list(error_log)
            self._tree_view_form.msg_error.emit(msg)
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        """Find the right sub-model (or the empty model) and call insertRows on it."""
        selected_object_class_ids = self._tree_view_form.all_selected_object_class_ids()
        for object_class_id, model in self.sub_models.items():
            if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                continue
            if row < model.rowCount():
                return model.insertRows(row, count)
            row -= model.rowCount()
        return self.empty_row_model.insertRows(row, count)

    def removeRows(self, row, count, parent=QModelIndex()):
        """Find the right sub-models (or empty model) and call removeRows on them."""
        if row < 0 or row + count - 1 >= self.rowCount():
            return False
        self.beginRemoveRows(parent, row, row + count - 1)
        selected_object_class_ids = self._tree_view_form.all_selected_object_class_ids()
        model_row_sets = dict()
        for i in range(row, row + count):
            for object_class_id, model in self.sub_models.items():
                if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                    continue
                if i < model.rowCount():
                    model_row_sets.setdefault(model, set()).add(i)
                    break
                i -= model.rowCount()
            else:
                model_row_sets.setdefault(self.empty_row_model, set()).add(i)
        for model in self.sub_models.values():
            try:
                row_set = model_row_sets[model]
                min_row = min(row_set)
                max_row = max(row_set)
                model.removeRows(min_row, max_row - min_row + 1)
            except KeyError:
                pass
        try:
            row_set = model_row_sets[self.empty_row_model]
            min_row = min(row_set)
            max_row = max(row_set)
            self.empty_row_model.removeRows(min_row, max_row - min_row + 1)
        except KeyError:
            pass
        self.endRemoveRows()
        return True

    @Slot("QModelIndex", "int", "int", name="_handle_empty_rows_inserted")
    def _handle_empty_rows_inserted(self, parent, first, last):
        offset = self.rowCount() - self.empty_row_model.rowCount()
        self.rowsInserted.emit(QModelIndex(), offset + first, offset + last)

    def invalidate_filter(self):
        """Invalidate filter."""
        self.layoutAboutToBeChanged.emit()
        for model in self.sub_models.values():
            model.invalidateFilter()
        self.layoutChanged.emit()

    @busy_effect
    def auto_filter_values(self, column):
        """Return values to populate the auto filter of given column.
        Each 'row' in the returned value consists of:
        1) The 'checked' state, True if the value *hasn't* been filtered out
        2) The value itself (an object name, a parameter name, a numerical value...)
        3) A set of object class ids where the value is found.
        """
        values = dict()
        selected_object_class_ids = self._tree_view_form.all_selected_object_class_ids()
        for object_class_id, model in self.sub_models.items():
            if selected_object_class_ids and object_class_id not in selected_object_class_ids:
                continue
            data = model.sourceModel()._main_data
            row_count = model.sourceModel().rowCount()
            for i in range(row_count):
                if not model.main_filter_accepts_row(i, None):
                    continue
                if not model.auto_filter_accepts_row(i, None, ignored_columns=[column]):
                    continue
                values.setdefault(data[i][column], set()).add(object_class_id)
        filtered_out = self.filtered_out.get(column, [])
        return [[val not in filtered_out, val, obj_cls_id_set] for val, obj_cls_id_set in values.items()]

    def set_filtered_out_values(self, column, values):
        """Set values that need to be filtered out."""
        filtered_out = [val for obj_cls_id, values in values.items() for val in values]
        self.filtered_out[column] = filtered_out
        for object_class_id, model in self.sub_models.items():
            model.set_filtered_out_values(column, values.get(object_class_id, {}))
        if filtered_out:
            self.setHeaderData(column, Qt.Horizontal, self.italic_font, Qt.FontRole)
        else:
            self.setHeaderData(column, Qt.Horizontal, None, Qt.FontRole)

    def clear_filtered_out_values(self):
        """Clear the set of values that need to be filtered out."""
        for column in self.filtered_out:
            self.setHeaderData(column, Qt.Horizontal, None, Qt.FontRole)
        self.filtered_out = dict()

    def rename_object_classes(self, object_classes):
        """Rename object classes in model."""
        object_class_name_column = self.header.index("object_class_name")
        object_class_id_name = {x.id: x.name for x in object_classes}
        for object_class_id, model in self.sub_models.items():
            if object_class_id in object_class_id_name:
                object_class_name = object_class_id_name[object_class_id]
            else:
                continue
            for row_data in model.sourceModel()._main_data:
                row_data[object_class_name_column] = object_class_name

    def rename_parameter_tags(self, parameter_tags):
        """Rename parameter tags in model."""
        parameter_tag_list_column = self.header.index("parameter_tag_list")
        parameter_tag_id_list_column = self.header.index("parameter_tag_id_list")
        parameter_tag_dict = {x.id: x.tag for x in parameter_tags}
        for model in self.sub_models.values():
            for row_data in model.sourceModel()._main_data:
                parameter_tag_id_list = row_data[parameter_tag_id_list_column]
                parameter_tag_list = row_data[parameter_tag_list_column]
                if not parameter_tag_id_list:
                    continue
                split_parameter_tag_id_list = [int(x) for x in parameter_tag_id_list.split(",")]
                split_parameter_tag_list = parameter_tag_list.split(",")
                found = False
                for k, tag_id in enumerate(split_parameter_tag_id_list):
                    if tag_id in parameter_tag_dict:
                        new_tag = parameter_tag_dict[tag_id]
                        split_parameter_tag_list[k] = new_tag
                        found = True
                if not found:
                    continue
                row_data[parameter_tag_list_column] = ",".join(split_parameter_tag_list)

    def remove_object_classes(self, object_classes):
        """Remove object classes from model."""
        self.layoutAboutToBeChanged.emit()
        for object_class in object_classes:
            self.sub_models.pop(object_class['id'], None)
        self.layoutChanged.emit()

    def remove_parameter_tags(self, parameter_tag_ids):
        """Remove parameter tags from model."""
        parameter_tag_list_column = self.header.index("parameter_tag_list")
        parameter_tag_id_list_column = self.header.index("parameter_tag_id_list")
        for model in self.sub_models.values():
            for row_data in model.sourceModel()._main_data:
                parameter_tag_id_list = row_data[parameter_tag_id_list_column]
                parameter_tag_list = row_data[parameter_tag_list_column]
                if not parameter_tag_id_list:
                    continue
                split_parameter_tag_id_list = [int(x) for x in parameter_tag_id_list.split(",")]
                split_parameter_tag_list = parameter_tag_list.split(",")
                found = False
                for k, tag_id in enumerate(split_parameter_tag_id_list):
                    if tag_id in parameter_tag_ids:
                        del split_parameter_tag_list[k]
                        found = True
                if not found:
                    continue
                row_data[parameter_tag_list_column] = ",".join(split_parameter_tag_list)


class ObjectParameterValueModel(ObjectParameterModel):
    """A model that concatenates several 'sub' object parameter value models,
    one per object class.
    """
    def __init__(self, tree_view_form=None):
        """Init class."""
        super().__init__(tree_view_form)
        self.empty_row_model = EmptyObjectParameterValueModel(self)
        self.empty_row_model.rowsInserted.connect(self._handle_empty_rows_inserted)

    def reset_model(self):
        """Reset model data. Each sub-model is filled with parameter value data
        for a different object class."""
        self.beginResetModel()
        header = self.db_map.object_parameter_value_fields()
        data = self.db_map.object_parameter_value_list()
        self.fixed_columns = [header.index(x) for x in ('object_class_name', 'object_name', 'parameter_name')]
        self.object_class_name_column = header.index('object_class_name')
        parameter_definition_id_column = header.index('parameter_id')
        object_id_column = header.index('object_id')
        self.set_horizontal_header_labels(header)
        data_dict = {}
        for parameter_value in data:
            object_class_id = parameter_value.object_class_id
            data_dict.setdefault(object_class_id, list()).append(parameter_value)
        for object_class_id, data in data_dict.items():
            source_model = SubParameterValueModel(self)
            source_model.reset_model([list(x) for x in data])
            model = self.sub_models[object_class_id] = ObjectParameterValueFilterProxyModel(
                self, parameter_definition_id_column, object_id_column)
            model.setSourceModel(source_model)
        self.empty_row_model.set_horizontal_header_labels(header)
        self.empty_row_model.clear()
        self.endResetModel()

    def update_filter(self):
        """Update filter."""
        self.layoutAboutToBeChanged.emit()
        selected_parameter_definition_ids = self._tree_view_form.selected_obj_parameter_definition_ids
        selected_object_ids = self._tree_view_form.selected_object_ids
        for object_class_id, model in self.sub_models.items():
            parameter_definition_ids = selected_parameter_definition_ids.get(object_class_id, {})
            object_ids = selected_object_ids.get(object_class_id, {})
            model.update_filter(parameter_definition_ids, object_ids)
            model.clear_filtered_out_values()
        self.clear_filtered_out_values()
        self.layoutChanged.emit()

    def rename_objects(self, objects):
        """Rename objects in model."""
        object_id_column = self.header.index("object_id")
        object_name_column = self.header.index("object_name")
        object_dict = {}
        for object_ in objects:
            object_dict.setdefault(object_.class_id, {}).update({object_.id: object_.name})
        for object_class_id, object_id_name in object_dict.items():
            if object_class_id in self.sub_models:
                model = self.sub_models[object_class_id]
            else:
                continue
            source_model = model.sourceModel()
            for row_data in source_model._main_data:
                object_id = row_data[object_id_column]
                if object_id in object_id_name:
                    row_data[object_name_column] = object_id_name[object_id]

    def rename_parameter(self, parameter_id, object_class_id, new_name):
        """Rename single parameter in model."""
        if object_class_id in self.sub_models:
            model = self.sub_models[object_class_id]
        else:
            return
        parameter_id_column = self.header.index("parameter_id")
        parameter_name_column = self.header.index("parameter_name")
        for row_data in model.sourceModel()._main_data:
            if row_data[parameter_id_column] == parameter_id:
                row_data[parameter_name_column] = new_name

    def remove_objects(self, objects):
        """Remove objects from model."""
        object_id_column = self.header.index("object_id")
        object_dict = {}
        for object_ in objects:
            object_dict.setdefault(object_['class_id'], set()).add(object_['id'])
        for object_class_id, object_ids in object_dict.items():
            if object_class_id in self.sub_models:
                model = self.sub_models[object_class_id]
            else:
                continue
            source_model = model.sourceModel()
            for row in reversed(range(source_model.rowCount())):
                object_id = source_model._main_data[row][object_id_column]
                if object_id in object_ids:
                    source_model.removeRows(row, 1)

    def remove_parameters(self, parameter_dict):
        """Remove parameters from model."""
        parameter_id_column = self.header.index("parameter_id")
        for object_class_id, parameter_ids in parameter_dict.items():
            if object_class_id in self.sub_models:
                model = self.sub_models[object_class_id]
            else:
                continue
            source_model = model.sourceModel()
            for row in reversed(range(source_model.rowCount())):
                parameter_id = source_model._main_data[row][parameter_id_column]
                if parameter_id in parameter_ids:
                    source_model.removeRows(row, 1)

    def move_rows_to_sub_models(self, rows):
        """Move rows from empty row model to the appropriate sub_model.
        Called when the empty row model succesfully inserts new data in the db.
        """
        object_class_id_column = self.header.index("object_class_id")
        parameter_definition_id_column = self.header.index('parameter_id')
        object_id_column = self.header.index("object_id")
        model_data_dict = {}
        for row in rows:
            row_data = self.empty_row_model._main_data[row]
            object_class_id = row_data[object_class_id_column]
            model_data_dict.setdefault(object_class_id, list()).append(row_data)
        for object_class_id, data in model_data_dict.items():
            if object_class_id in self.sub_models:
                model = self.sub_models[object_class_id]
                source_model = model.sourceModel()
                row_count = source_model.rowCount()
                source_model.insertRows(row_count, len(data))
                source_model._main_data[row_count:row_count + len(data)] = data
            else:
                source_model = SubParameterValueModel(self)
                source_model.reset_model(data)
                model = self.sub_models[object_class_id] = ObjectParameterValueFilterProxyModel(
                    self, parameter_definition_id_column, object_id_column)
                model.setSourceModel(source_model)
        for row in reversed(rows):
            self.empty_row_model.removeRows(row, 1)
        self.invalidate_filter()


class ObjectParameterDefinitionModel(ObjectParameterModel):
    """A model that concatenates several object parameter definition models
    (one per object class) vertically.
    """
    def __init__(self, tree_view_form=None):
        """Init class."""
        super().__init__(tree_view_form)
        self.empty_row_model = EmptyObjectParameterDefinitionModel(self)
        self.empty_row_model.rowsInserted.connect(self._handle_empty_rows_inserted)

    def reset_model(self):
        """Reset model data. Each sub-model is filled with parameter definition data
        for a different object class."""
        self.beginResetModel()
        header = self.db_map.object_parameter_fields()
        data = self.db_map.object_parameter_list()
        self.fixed_columns = [header.index('object_class_name')]
        self.object_class_name_column = header.index('object_class_name')
        parameter_definition_id_column = header.index('id')
        self.set_horizontal_header_labels(header)
        data_dict = {}
        for parameter_definition in data:
            object_class_id = parameter_definition.object_class_id
            data_dict.setdefault(object_class_id, list()).append(parameter_definition)
        for object_class_id, data in data_dict.items():
            source_model = SubParameterDefinitionModel(self)
            source_model.reset_model([list(x) for x in data])
            model = self.sub_models[object_class_id] = ObjectParameterDefinitionFilterProxyModel(
                self, parameter_definition_id_column)
            model.setSourceModel(source_model)
        self.empty_row_model.set_horizontal_header_labels(header)
        self.empty_row_model.clear()
        self.endResetModel()

    def update_filter(self):
        """Update filter."""
        self.layoutAboutToBeChanged.emit()
        selected_parameter_definition_ids = self._tree_view_form.selected_obj_parameter_definition_ids
        for object_class_id, model in self.sub_models.items():
            model.update_filter(selected_parameter_definition_ids.get(object_class_id, {}))
            model.clear_filtered_out_values()
        self.clear_filtered_out_values()
        self.layoutChanged.emit()

    def move_rows_to_sub_models(self, rows):
        """Move rows from empty row model to the appropriate sub_model.
        Called when the empty row model succesfully inserts new data in the db.
        """
        object_class_id_column = self.header.index("object_class_id")
        parameter_definition_id_column = self.header.index('id')
        model_data_dict = {}
        for row in rows:
            row_data = self.empty_row_model._main_data[row]
            object_class_id = row_data[object_class_id_column]
            model_data_dict.setdefault(object_class_id, list()).append(row_data)
        for object_class_id, data in model_data_dict.items():
            if object_class_id in self.sub_models:
                model = self.sub_models[object_class_id]
                source_model = model.sourceModel()
                row_count = source_model.rowCount()
                source_model.insertRows(row_count, len(data))
                source_model._main_data[row_count:row_count + len(data)] = data
            else:
                source_model = SubParameterDefinitionModel(self)
                source_model.reset_model(data)
                model = self.sub_models[object_class_id] = ObjectParameterDefinitionFilterProxyModel(
                    self, parameter_definition_id_column)
                model.setSourceModel(source_model)
        for row in reversed(rows):
            self.empty_row_model.removeRows(row, 1)
        self.invalidate_filter()

    def clear_parameter_value_lists(self, value_list_ids):
        """Clear parameter value_lists from model."""
        value_list_id_column = self.header.index("value_list_id")
        value_list_name_column = self.header.index("value_list_name")
        for model in self.sub_models.values():
            for row_data in model.sourceModel()._main_data:
                value_list_id = row_data[value_list_id_column]
                if value_list_id in value_list_ids:
                    row_data[value_list_id_column] = None
                    row_data[value_list_name_column] = None
        self.dataChanged.emit(
            self.index(0, value_list_name_column), self.index(self.rowCount() - 1, value_list_name_column), [Qt.DisplayRole])

    def rename_parameter_value_lists(self, value_lists):
        """Rename parameter value_lists in model."""
        value_list_id_column = self.header.index("value_list_id")
        value_list_name_column = self.header.index("value_list_name")
        value_list_dict = {x.id: x.name for x in value_lists}
        for model in self.sub_models.values():
            for row_data in model.sourceModel()._main_data:
                value_list_id = row_data[value_list_id_column]
                if value_list_id in value_list_dict:
                    row_data[value_list_name_column] = value_list_dict[value_list_id]
        self.dataChanged.emit(
            self.index(0, value_list_name_column), self.index(self.rowCount() - 1, value_list_name_column), [Qt.DisplayRole])


class RelationshipParameterModel(MinimalTableModel):
    """A model that combines several relationship parameter models
    (one per relationship class), one on top of the other.
    """
    def __init__(self, tree_view_form=None):
        """Init class."""
        super().__init__(tree_view_form)
        self._tree_view_form = tree_view_form
        self.db_map = tree_view_form.db_map
        self.sub_models = {}
        self.object_class_id_lists = {}
        self.empty_row_model = EmptyRowModel(self)
        self.fixed_columns = list()
        self.filtered_out = dict()
        self.italic_font = QFont()
        self.italic_font.setItalic(True)

    def add_object_class_id_lists(self, wide_relationship_class_list):
        """Populate a dictionary of object class id lists per relationship class."""
        self.object_class_id_lists.update({
            x.id: [int(x) for x in x.object_class_id_list.split(",")] for x in wide_relationship_class_list})

    def flags(self, index):
        """Return flags for given index.
        Depending on the index's row we will land on a specific model.
        Models whose relationship class id is not selected are skipped.
        Models whose object class id list doesn't intersect the selected ones are also skipped.
        """
        row = index.row()
        column = index.column()
        selected_object_class_ids = self._tree_view_form.selected_object_class_ids
        selected_relationship_class_ids = self._tree_view_form.all_selected_relationship_class_ids()
        for relationship_class_id, model in self.sub_models.items():
            if selected_object_class_ids:
                object_class_id_list = self.object_class_id_lists[relationship_class_id]
                if not selected_object_class_ids.intersection(object_class_id_list):
                    continue
            if selected_relationship_class_ids:
                if relationship_class_id not in selected_relationship_class_ids:
                    continue
            if row < model.rowCount():
                return model.index(row, column).flags()
            row -= model.rowCount()
        return self.empty_row_model.index(row, column).flags()

    def data(self, index, role=Qt.DisplayRole):
        """Return data for given index and role.
        Depending on the index's row we will land on a specific model.
        Models whose relationship class id is not selected are skipped.
        Models whose object class id list doesn't intersect the selected ones are also skipped.
        """
        row = index.row()
        column = index.column()
        selected_object_class_ids = self._tree_view_form.selected_object_class_ids
        selected_relationship_class_ids = self._tree_view_form.all_selected_relationship_class_ids()
        for relationship_class_id, model in self.sub_models.items():
            if selected_object_class_ids:
                object_class_id_list = self.object_class_id_lists[relationship_class_id]
                if not selected_object_class_ids.intersection(object_class_id_list):
                    continue
            if selected_relationship_class_ids:
                if relationship_class_id not in selected_relationship_class_ids:
                    continue
            if row < model.rowCount():
                if role == Qt.DecorationRole and column == self.relationship_class_name_column:
                    object_class_name_list = model.index(row, self.object_class_name_list_column).\
                        data(Qt.DisplayRole)
                    return self._tree_view_form.icon_mngr.relationship_icon(object_class_name_list)
                return model.index(row, column).data(role)
            row -= model.rowCount()
        if role == Qt.DecorationRole and column == self.relationship_class_name_column:
            object_class_name_list = self.empty_row_model.index(row, self.object_class_name_list_column).\
                data(Qt.DisplayRole)
            return self._tree_view_form.icon_mngr.relationship_icon(object_class_name_list)
        return self.empty_row_model.index(row, column).data(role)

    def rowCount(self, parent=QModelIndex()):
        """Return the sum of rows in all models.
        Models whose relationship class id is not selected are skipped.
        Models whose object class id list doesn't intersect the selected ones are also skipped.
        """
        count = 0
        selected_object_class_ids = self._tree_view_form.selected_object_class_ids
        selected_relationship_class_ids = self._tree_view_form.all_selected_relationship_class_ids()
        for relationship_class_id, model in self.sub_models.items():
            if selected_object_class_ids:
                object_class_id_list = self.object_class_id_lists[relationship_class_id]
                if not selected_object_class_ids.intersection(object_class_id_list):
                    continue
            if selected_relationship_class_ids:
                if relationship_class_id not in selected_relationship_class_ids:
                    continue
            count += model.rowCount()
        count += self.empty_row_model.rowCount()
        return count

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes.
        Distribute indexes and data among the different submodels
        and call batch_set_data on each of them."""
        if not indexes:
            return False
        if len(indexes) != len(data):
            return False
        model_indexes = {}
        model_data = {}
        selected_object_class_ids = self._tree_view_form.selected_object_class_ids
        selected_relationship_class_ids = self._tree_view_form.all_selected_relationship_class_ids()
        for k, index in enumerate(indexes):
            if not index.isValid():
                continue
            row = index.row()
            column = index.column()
            for relationship_class_id, model in self.sub_models.items():
                if selected_object_class_ids:
                    object_class_id_list = self.object_class_id_lists[relationship_class_id]
                    if not selected_object_class_ids.intersection(object_class_id_list):
                        continue
                if selected_relationship_class_ids:
                    if relationship_class_id not in selected_relationship_class_ids:
                        continue
                if row < model.rowCount():
                    model_indexes.setdefault(model, list()).append(model.index(row, column))
                    model_data.setdefault(model, list()).append(data[k])
                    break
                row -= model.rowCount()
            else:
                model = self.empty_row_model
                model_indexes.setdefault(model, list()).append(model.index(row, column))
                model_data.setdefault(model, list()).append(data[k])
        updated_count = 0
        update_error_log = []
        for model in self.sub_models.values():
            model.batch_set_data(model_indexes.get(model, list()), model_data.get(model, list()))
            updated_count += model.sourceModel().updated_count
            update_error_log += model.sourceModel().error_log
        model = self.empty_row_model
        model.batch_set_data(model_indexes.get(model, list()), model_data.get(model, list()))
        add_error_log = model.error_log
        added_rows = model.added_rows
        # Find square envelope of indexes to emit dataChanged
        top = min(ind.row() for ind in indexes)
        bottom = max(ind.row() for ind in indexes)
        left = min(ind.column() for ind in indexes)
        right = max(ind.column() for ind in indexes)
        self.dataChanged.emit(self.index(top, left), self.index(bottom, right))
        if added_rows:
            self.move_rows_to_sub_models(added_rows)
            self._tree_view_form.commit_available.emit(True)
            self._tree_view_form.msg.emit("Successfully added entries.")
        if updated_count:
            self._tree_view_form.commit_available.emit(True)
            self._tree_view_form.msg.emit("Successfully updated entries.")
        error_log = add_error_log + update_error_log
        if error_log:
            msg = format_string_list(error_log)
            self._tree_view_form.msg_error.emit(msg)
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        """Find the right sub-model (or the empty model) and call insertRows on it."""
        selected_object_class_ids = self._tree_view_form.selected_object_class_ids
        selected_relationship_class_ids = self._tree_view_form.all_selected_relationship_class_ids()
        for relationship_class_id, model in self.sub_models.items():
            if selected_object_class_ids:
                object_class_id_list = self.object_class_id_lists[relationship_class_id]
                if not selected_object_class_ids.intersection(object_class_id_list):
                    continue
            if selected_relationship_class_ids:
                if relationship_class_id not in selected_relationship_class_ids:
                    continue
            if row < model.rowCount():
                return model.insertRows(row, count)
            row -= model.rowCount()
        return self.empty_row_model.insertRows(row, count)

    def removeRows(self, row, count, parent=QModelIndex()):
        """Find the right sub-models (or empty model) and call removeRows on them."""
        if row < 0 or row + count - 1 >= self.rowCount():
            return False
        self.beginRemoveRows(parent, row, row + count - 1)
        selected_object_class_ids = self._tree_view_form.selected_object_class_ids
        selected_relationship_class_ids = self._tree_view_form.all_selected_relationship_class_ids()
        model_row_sets = {}
        for i in range(row, row + count):
            for relationship_class_id, model in self.sub_models.items():
                if selected_object_class_ids:
                    object_class_id_list = self.object_class_id_lists[relationship_class_id]
                    if not selected_object_class_ids.intersection(object_class_id_list):
                        continue
                if selected_relationship_class_ids:
                    if relationship_class_id not in selected_relationship_class_ids:
                        continue
                if i < model.rowCount():
                    model_row_sets.setdefault(model, set()).add(i)
                    break
                i -= model.rowCount()
            else:
                model_row_sets.setdefault(self.empty_row_model, set()).add(i)
        for model in self.sub_models.values():
            try:
                row_set = model_row_sets[model]
                min_row = min(row_set)
                max_row = max(row_set)
                model.removeRows(min_row, max_row - min_row + 1)
            except KeyError:
                pass
        try:
            row_set = model_row_sets[self.empty_row_model]
            min_row = min(row_set)
            max_row = max(row_set)
            self.empty_row_model.removeRows(min_row, max_row - min_row + 1)
        except KeyError:
            pass
        self.endRemoveRows()
        return True

    @Slot("QModelIndex", "int", "int", name="_handle_empty_rows_inserted")
    def _handle_empty_rows_inserted(self, parent, first, last):
        offset = self.rowCount() - self.empty_row_model.rowCount()
        self.rowsInserted.emit(QModelIndex(), offset + first, offset + last)

    def invalidate_filter(self):
        """Invalidate filter."""
        self.layoutAboutToBeChanged.emit()
        for model in self.sub_models.values():
            model.invalidateFilter()
        self.layoutChanged.emit()

    @busy_effect
    def auto_filter_values(self, column):
        """Return values to populate the auto filter of given column.
        Each 'row' in the returned value consists of:
        1) The 'checked' state, True if the value *hasn't* been filtered out
        2) The value itself (an object name, a parameter name, a numerical value...)
        3) A set of relationship class ids where the value is found.
        """
        values = dict()
        selected_object_class_ids = self._tree_view_form.selected_object_class_ids
        selected_relationship_class_ids = self._tree_view_form.all_selected_relationship_class_ids()
        for relationship_class_id, model in self.sub_models.items():
            if selected_object_class_ids:
                object_class_id_list = self.object_class_id_lists[relationship_class_id]
                if not selected_object_class_ids.intersection(object_class_id_list):
                    continue
            if selected_relationship_class_ids:
                if relationship_class_id not in selected_relationship_class_ids:
                    continue
            data = model.sourceModel()._main_data
            row_count = model.sourceModel().rowCount()
            for i in range(row_count):
                if not model.main_filter_accepts_row(i, None):
                    continue
                if not model.auto_filter_accepts_row(i, None, ignored_columns=[column]):
                    continue
                values.setdefault(data[i][column], set()).add(relationship_class_id)
        filtered_out = self.filtered_out.get(column, [])
        return [[val not in filtered_out, val, rel_cls_id_set] for val, rel_cls_id_set in values.items()]

    def set_filtered_out_values(self, column, values):
        """Set values that need to be filtered out."""
        filtered_out = [val for rel_cls_id, values in values.items() for val in values]
        self.filtered_out[column] = filtered_out
        for relationship_class_id, model in self.sub_models.items():
            model.set_filtered_out_values(column, values.get(relationship_class_id, {}))
        if filtered_out:
            self.setHeaderData(column, Qt.Horizontal, self.italic_font, Qt.FontRole)
        else:
            self.setHeaderData(column, Qt.Horizontal, None, Qt.FontRole)

    def clear_filtered_out_values(self):
        """Clear the set of filtered out values."""
        for column in self.filtered_out:
            self.setHeaderData(column, Qt.Horizontal, None, Qt.FontRole)
        self.filtered_out = dict()

    def rename_object_classes(self, object_classes):
        """Rename object classes in model."""
        object_class_name_list_column = self.header.index("object_class_name_list")
        object_class_id_name = {x.id: x.name for x in object_classes}
        for relationship_class_id, model in self.sub_models.items():
            object_class_id_list = self.object_class_id_lists[relationship_class_id]
            new_object_class_name_dict = {}
            for k, object_class_id in enumerate(object_class_id_list):
                if object_class_id in object_class_id_name:
                    object_class_name = object_class_id_name[object_class_id]
                    new_object_class_name_dict.update({k: object_class_name})
            if not new_object_class_name_dict:
                continue
            for row_data in model.sourceModel()._main_data:
                object_class_name_list = row_data[object_class_name_list_column].split(',')
                object_class_name_dict = {i: name for i, name in enumerate(object_class_name_list)}
                object_class_name_dict.update(new_object_class_name_dict)
                new_object_class_name_list = ",".\
                    join([object_class_name_dict[i] for i in range(len(object_class_name_dict))])
                row_data[object_class_name_list_column] = new_object_class_name_list

    def rename_relationship_classes(self, relationship_classes):
        """Rename relationship classes in model."""
        relationship_class_name_column = self.header.index("relationship_class_name")
        relationship_class_id_name = {x.id: x.name for x in relationship_classes}
        for relationship_class_id, model in self.sub_models.items():
            if relationship_class_id in relationship_class_id_name:
                relationship_class_name = relationship_class_id_name[relationship_class_id]
            else:
                continue
            for row_data in model.sourceModel()._main_data:
                row_data[relationship_class_name_column] = relationship_class_name

    def rename_parameter_tags(self, parameter_tags):
        """Rename parameter tags in model."""
        parameter_tag_list_column = self.header.index("parameter_tag_list")
        parameter_tag_id_list_column = self.header.index("parameter_tag_id_list")
        parameter_tag_dict = {x.id: x.tag for x in parameter_tags}
        for model in self.sub_models.values():
            for row_data in model.sourceModel()._main_data:
                parameter_tag_id_list = row_data[parameter_tag_id_list_column]
                parameter_tag_list = row_data[parameter_tag_list_column]
                if not parameter_tag_id_list:
                    continue
                split_parameter_tag_id_list = [int(x) for x in parameter_tag_id_list.split(",")]
                split_parameter_tag_list = parameter_tag_list.split(",")
                found = False
                for k, tag_id in enumerate(split_parameter_tag_id_list):
                    if tag_id in parameter_tag_dict:
                        new_tag = parameter_tag_dict[tag_id]
                        split_parameter_tag_list[k] = new_tag
                        found = True
                if not found:
                    continue
                row_data[parameter_tag_list_column] = ",".join(split_parameter_tag_list)

    def remove_object_classes(self, object_classes):
        """Remove object classes from model."""
        self.layoutAboutToBeChanged.emit()
        object_class_ids = {x['id'] for x in object_classes}
        for relationship_class_id, object_class_id_list in self.object_class_id_lists.items():
            if object_class_ids.intersection(object_class_id_list):
                self.sub_models.pop(relationship_class_id, None)
        self.layoutChanged.emit()

    def remove_relationship_classes(self, relationship_classes):
        """Remove relationship classes from model."""
        self.layoutAboutToBeChanged.emit()
        for relationship_class in relationship_classes:
            self.sub_models.pop(relationship_class['id'], None)
        self.layoutChanged.emit()

    def remove_parameter_tags(self, parameter_tag_ids):
        """Remove parameter tags from model."""
        parameter_tag_list_column = self.header.index("parameter_tag_list")
        parameter_tag_id_list_column = self.header.index("parameter_tag_id_list")
        for model in self.sub_models.values():
            for row_data in model.sourceModel()._main_data:
                parameter_tag_id_list = row_data[parameter_tag_id_list_column]
                parameter_tag_list = row_data[parameter_tag_list_column]
                if not parameter_tag_id_list:
                    continue
                split_parameter_tag_id_list = [int(x) for x in parameter_tag_id_list.split(",")]
                split_parameter_tag_list = parameter_tag_list.split(",")
                found = False
                for k, tag_id in enumerate(split_parameter_tag_id_list):
                    if tag_id in parameter_tag_ids:
                        del split_parameter_tag_list[k]
                        found = True
                if not found:
                    continue
                row_data[parameter_tag_list_column] = ",".join(split_parameter_tag_list)


class RelationshipParameterValueModel(RelationshipParameterModel):
    """A model that combines several relationship parameter value models
    (one per relationship class), one on top of the other.
    """
    def __init__(self, tree_view_form=None):
        """Init class."""
        super().__init__(tree_view_form)
        self.empty_row_model = EmptyRelationshipParameterValueModel(self)
        self.empty_row_model.rowsInserted.connect(self._handle_empty_rows_inserted)

    def reset_model(self):
        """Reset model data. Each sub-model is filled with parameter value data
        for a different relationship class."""
        self.beginResetModel()
        self.add_object_class_id_lists(self.db_map.wide_relationship_class_list())
        header = self.db_map.relationship_parameter_value_fields()
        data = self.db_map.relationship_parameter_value_list()
        self.fixed_columns = [
            header.index(x) for x in ('relationship_class_name', 'object_name_list', 'parameter_name')]
        self.relationship_class_name_column = header.index('relationship_class_name')
        self.object_class_name_list_column = header.index('object_class_name_list')
        parameter_definition_id_column = header.index('parameter_id')
        object_id_list_column = header.index('object_id_list')
        self.set_horizontal_header_labels(header)
        data_dict = {}
        for parameter_value in data:
            relationship_class_id = parameter_value.relationship_class_id
            data_dict.setdefault(relationship_class_id, list()).append(parameter_value)
        for relationship_class_id, data in data_dict.items():
            source_model = SubParameterValueModel(self)
            source_model.reset_model([list(x) for x in data])
            model = self.sub_models[relationship_class_id] = RelationshipParameterValueFilterProxyModel(
                self, parameter_definition_id_column, object_id_list_column)
            model.setSourceModel(source_model)
        self.empty_row_model.set_horizontal_header_labels(header)
        self.empty_row_model.clear()
        self.endResetModel()

    def update_filter(self):
        """Update filter."""
        self.layoutAboutToBeChanged.emit()
        selected_parameter_definition_ids = self._tree_view_form.selected_rel_parameter_definition_ids
        selected_object_ids = self._tree_view_form.selected_object_ids
        selected_object_id_lists = self._tree_view_form.selected_object_id_lists
        for relationship_class_id, model in self.sub_models.items():
            parameter_definition_ids = selected_parameter_definition_ids.get(relationship_class_id, {})
            object_class_id_list = self.object_class_id_lists[relationship_class_id]
            object_ids = set(y for x in object_class_id_list for y in selected_object_ids.get(x, {}))
            object_id_lists = selected_object_id_lists.get(relationship_class_id, {})
            model.update_filter(parameter_definition_ids, object_ids, object_id_lists)
            model.clear_filtered_out_values()
        self.clear_filtered_out_values()
        self.layoutChanged.emit()

    def move_rows_to_sub_models(self, rows):
        """Move rows from empty row model to the appropriate sub_model.
        Called when the empty row model succesfully inserts new data in the db.
        """
        relationship_class_id_column = self.header.index("relationship_class_id")
        parameter_definition_id_column = self.header.index('parameter_id')
        object_id_list_column = self.header.index('object_id_list')
        model_data_dict = {}
        for row in rows:
            row_data = self.empty_row_model._main_data[row]
            relationship_class_id = row_data[relationship_class_id_column]
            model_data_dict.setdefault(relationship_class_id, list()).append(row_data)
        for relationship_class_id, data in model_data_dict.items():
            try:
                model = self.sub_models[relationship_class_id]
                source_model = model.sourceModel()
                row_count = source_model.rowCount()
                source_model.insertRows(row_count, len(data))
                source_model._main_data[row_count:row_count + len(data)] = data
            except KeyError:
                source_model = SubParameterValueModel(self)
                source_model.reset_model(data)
                model = RelationshipParameterValueFilterProxyModel(
                    self, parameter_definition_id_column, object_id_list_column)
                model.setSourceModel(source_model)
                self.sub_models[relationship_class_id] = model
        for row in reversed(rows):
            self.empty_row_model.removeRows(row, 1)
        self.invalidate_filter()

    def rename_objects(self, objects):
        """Rename objects in model."""
        object_id_list_column = self.header.index("object_id_list")
        object_name_list_column = self.header.index("object_name_list")
        object_id_name = {x.id: x.name for x in objects}
        for model in self.sub_models.values():
            for row_data in model.sourceModel()._main_data:
                object_id_list = [int(x) for x in row_data[object_id_list_column].split(',')]
                object_name_list = row_data[object_name_list_column].split(',')
                for i, object_id in enumerate(object_id_list):
                    if object_id in object_id_name:
                        object_name_list[i] = object_id_name[object_id]
                row_data[object_name_list_column] = ",".join(object_name_list)

    def remove_objects(self, objects):
        """Remove objects from model."""
        object_id_list_column = self.header.index("object_id_list")
        object_ids = {x['id'] for x in objects}
        for model in self.sub_models.values():
            source_model = model.sourceModel()
            for row in reversed(range(source_model.rowCount())):
                object_id_list = source_model._main_data[row][object_id_list_column]
                if object_ids.intersection(int(x) for x in object_id_list.split(',')):
                    source_model.removeRows(row, 1)

    def remove_relationships(self, relationships):
        """Remove relationships from model."""
        relationship_id_column = self.header.index("relationship_id")
        relationship_dict = {}
        for relationship in relationships:
            relationship_dict.setdefault(relationship['class_id'], set()).add(relationship['id'])
        for relationship_class_id, relationship_ids in relationship_dict.items():
            if relationship_class_id in self.sub_models:
                model = self.sub_models[relationship_class_id]
            else:
                continue
            source_model = model.sourceModel()
            for row in reversed(range(source_model.rowCount())):
                relationship_id = source_model._main_data[row][relationship_id_column]
                if relationship_id in relationship_ids:
                    source_model.removeRows(row, 1)

    def rename_parameter(self, parameter_id, relationship_class_id, new_name):
        """Rename single parameter in model."""
        if relationship_class_id in self.sub_models:
            model = self.sub_models[relationship_class_id]
        else:
            return
        parameter_id_column = self.header.index("parameter_id")
        parameter_name_column = self.header.index("parameter_name")
        for row_data in model.sourceModel()._main_data:
            if row_data[parameter_id_column] == parameter_id:
                row_data[parameter_name_column] = new_name

    def remove_parameters(self, parameter_dict):
        """Remove parameters from model."""
        parameter_id_column = self.header.index("parameter_id")
        for relationship_class_id, parameter_ids in parameter_dict.items():
            if relationship_class_id in self.sub_models:
                model = self.sub_models[relationship_class_id]
            else:
                continue
            source_model = model.sourceModel()
            for row in reversed(range(source_model.rowCount())):
                parameter_id = source_model._main_data[row][parameter_id_column]
                if parameter_id in parameter_ids:
                    source_model.removeRows(row, 1)


class RelationshipParameterDefinitionModel(RelationshipParameterModel):
    """A model that combines several relationship parameter definition models
    (one per relationship class), one on top of the other.
    """
    def __init__(self, tree_view_form=None):
        """Init class."""
        super().__init__(tree_view_form)
        self.empty_row_model = EmptyRelationshipParameterDefinitionModel(self)
        self.empty_row_model.rowsInserted.connect(self._handle_empty_rows_inserted)

    def reset_model(self):
        """Reset model data. Each sub-model is filled with parameter definition data
        for a different relationship class."""
        self.beginResetModel()
        self.add_object_class_id_lists(self.db_map.wide_relationship_class_list())
        header = self.db_map.relationship_parameter_fields()
        data = self.db_map.relationship_parameter_list()
        self.fixed_columns = [header.index(x) for x in ('relationship_class_name', 'object_class_name_list')]
        self.relationship_class_name_column = header.index('relationship_class_name')
        self.object_class_name_list_column = header.index('object_class_name_list')
        parameter_definition_id_column = header.index('id')
        self.set_horizontal_header_labels(header)
        data_dict = {}
        for parameter_definition in data:
            relationship_class_id = parameter_definition.relationship_class_id
            data_dict.setdefault(relationship_class_id, list()).append(parameter_definition)
        for relationship_class_id, data in data_dict.items():
            source_model = SubParameterDefinitionModel(self)
            source_model.reset_model([list(x) for x in data])
            model = self.sub_models[relationship_class_id] = RelationshipParameterDefinitionFilterProxyModel(
                self, parameter_definition_id_column)
            model.setSourceModel(source_model)
        self.empty_row_model.set_horizontal_header_labels(header)
        self.empty_row_model.clear()
        self.endResetModel()

    def update_filter(self):
        """Update filter."""
        self.layoutAboutToBeChanged.emit()
        selected_parameter_definition_ids = self._tree_view_form.selected_rel_parameter_definition_ids
        for relationship_class_id, model in self.sub_models.items():
            parameter_definition_ids = selected_parameter_definition_ids.get(relationship_class_id, {})
            model.update_filter(parameter_definition_ids)
            model.clear_filtered_out_values()
        self.clear_filtered_out_values()
        self.layoutChanged.emit()

    def move_rows_to_sub_models(self, rows):
        """Move rows from empty row model to the appropriate sub_model.
        Called when the empty row model succesfully inserts new data in the db.
        """
        relationship_class_id_column = self.header.index("relationship_class_id")
        parameter_definition_id_column = self.header.index('id')
        model_data_dict = {}
        for row in rows:
            row_data = self.empty_row_model._main_data[row]
            relationship_class_id = row_data[relationship_class_id_column]
            model_data_dict.setdefault(relationship_class_id, list()).append(row_data)
        for relationship_class_id, data in model_data_dict.items():
            try:
                model = self.sub_models[relationship_class_id]
                source_model = model.sourceModel()
                row_count = source_model.rowCount()
                source_model.insertRows(row_count, len(data))
                source_model._main_data[row_count:row_count + len(data)] = data
            except KeyError:
                source_model = SubParameterDefinitionModel(self)
                source_model.reset_model(data)
                model = RelationshipParameterDefinitionFilterProxyModel(self, parameter_definition_id_column)
                model.setSourceModel(source_model)
                self.sub_models[relationship_class_id] = model
        for row in reversed(rows):
            self.empty_row_model.removeRows(row, 1)
        self.invalidate_filter()

    def clear_parameter_value_lists(self, value_list_ids):
        """Clear parameter value_lists from model."""
        value_list_id_column = self.header.index("value_list_id")
        value_list_name_column = self.header.index("value_list_name")
        for model in self.sub_models.values():
            for row_data in model.sourceModel()._main_data:
                value_list_id = row_data[value_list_id_column]
                if value_list_id in value_list_ids:
                    row_data[value_list_id_column] = None
                    row_data[value_list_name_column] = None
        self.dataChanged.emit(
            self.index(0, value_list_name_column), self.index(self.rowCount() - 1, value_list_name_column), [Qt.DisplayRole])

    def rename_parameter_value_lists(self, value_lists):
        """Rename parameter value_lists in model."""
        value_list_id_column = self.header.index("value_list_id")
        value_list_name_column = self.header.index("value_list_name")
        parameter_value_list_dict = {x.id: x.name for x in value_lists}
        for model in self.sub_models.values():
            for row_data in model.sourceModel()._main_data:
                value_list_id = row_data[value_list_id_column]
                if value_list_id in parameter_value_list_dict:
                    row_data[value_list_name_column] = parameter_value_list_dict[value_list_id]
        self.dataChanged.emit(
            self.index(0, value_list_name_column), self.index(self.rowCount() - 1, value_list_name_column), [Qt.DisplayRole])


class ObjectParameterDefinitionFilterProxyModel(QSortFilterProxyModel):
    """A filter proxy model for object parameter models."""
    def __init__(self, parent, parameter_definition_id_column):
        """Init class."""
        super().__init__(parent)
        self.parameter_definition_ids = set()
        self.parameter_definition_id_column = parameter_definition_id_column
        self.filtered_out = dict()

    def update_filter(self, parameter_definition_ids):
        """Update filter."""
        if parameter_definition_ids == self.parameter_definition_ids:
            return
        self.parameter_definition_ids = parameter_definition_ids
        self.invalidateFilter()

    def set_filtered_out_values(self, column, values):
        """Set values that need to be filtered out."""
        if values == self.filtered_out.get(column, {}):
            return
        self.filtered_out[column] = values
        self.invalidateFilter()

    def clear_filtered_out_values(self):
        """Clear the filtered out values."""
        if not self.filtered_out:
            return
        self.filtered_out = dict()
        self.invalidateFilter()

    def auto_filter_accepts_row(self, source_row, source_parent, ignored_columns=None):
        """Accept or reject row."""
        if ignored_columns is None:
            ignored_columns = []
        for column, values in self.filtered_out.items():
            if column in ignored_columns:
                continue
            if self.sourceModel()._main_data[source_row][column] in values:
                return False
        return True

    def main_filter_accepts_row(self, source_row, source_parent):
        """Accept or reject row."""
        if self.parameter_definition_ids:
            parameter_definition_id = self.sourceModel()._main_data[source_row][self.parameter_definition_id_column]
            return parameter_definition_id in self.parameter_definition_ids
        return True

    def filterAcceptsRow(self, source_row, source_parent):
        """Accept or reject row."""
        if not self.main_filter_accepts_row(source_row, source_parent):
            return False
        if not self.auto_filter_accepts_row(source_row, source_parent):
            return False
        return True

    def batch_set_data(self, indexes, data):
        source_indexes = [self.mapToSource(x) for x in indexes]
        return self.sourceModel().batch_set_data(source_indexes, data)


class ObjectParameterValueFilterProxyModel(ObjectParameterDefinitionFilterProxyModel):
    """A filter proxy model for object parameter value models."""
    def __init__(self, parent, parameter_definition_id_column, object_id_column):
        """Init class."""
        super().__init__(parent, parameter_definition_id_column)
        self.object_ids = set()
        self.object_id_column = object_id_column

    def update_filter(self, parameter_definition_ids, object_ids):
        """Update filter."""
        if parameter_definition_ids == self.parameter_definition_ids and object_ids == self.object_ids:
            return
        self.parameter_definition_ids = parameter_definition_ids
        self.object_ids = object_ids
        self.invalidateFilter()

    def main_filter_accepts_row(self, source_row, source_parent):
        """Accept or reject row."""
        if not super().main_filter_accepts_row(source_row, source_parent):
            return False
        if self.object_ids:
            return self.sourceModel()._main_data[source_row][self.object_id_column] in self.object_ids
        return True


class RelationshipParameterDefinitionFilterProxyModel(QSortFilterProxyModel):
    """A filter proxy model for relationship parameter definition models."""
    def __init__(self, parent, parameter_definition_id_column):
        """Init class."""
        super().__init__(parent)
        self.parameter_definition_ids = set()
        self.parameter_definition_id_column = parameter_definition_id_column
        self.filtered_out = dict()

    def update_filter(self, parameter_definition_ids):
        """Update filter."""
        if parameter_definition_ids == self.parameter_definition_ids:
            return
        self.parameter_definition_ids = parameter_definition_ids
        self.invalidateFilter()

    def set_filtered_out_values(self, column, values):
        """Set values that need to be filtered out."""
        if values == self.filtered_out.get(column, {}):
            return
        self.filtered_out[column] = values
        self.invalidateFilter()

    def clear_filtered_out_values(self):
        """Clear the set of values that need to be filtered out."""
        if not self.filtered_out:
            return
        self.filtered_out = dict()
        self.invalidateFilter()

    def auto_filter_accepts_row(self, source_row, source_parent, ignored_columns=None):
        """Accept or reject row."""
        if ignored_columns is None:
            ignoredColumns = list()
        for column, values in self.filtered_out.items():
            if column in ignored_columns:
                continue
            if self.sourceModel()._main_data[source_row][column] in values:
                return False
        return True

    def main_filter_accepts_row(self, source_row, source_parent):
        """Accept or reject row."""
        if self.parameter_definition_ids:
            parameter_definition_id = self.sourceModel()._main_data[source_row][self.parameter_definition_id_column]
            return parameter_definition_id in self.parameter_definition_ids
        return True

    def filterAcceptsRow(self, source_row, source_parent):
        """Accept or reject row."""
        if not self.main_filter_accepts_row(source_row, source_parent):
            return False
        if not self.auto_filter_accepts_row(source_row, source_parent):
            return False
        return True

    def batch_set_data(self, indexes, data):
        source_indexes = [self.mapToSource(x) for x in indexes]
        return self.sourceModel().batch_set_data(source_indexes, data)


class RelationshipParameterValueFilterProxyModel(RelationshipParameterDefinitionFilterProxyModel):
    """A filter proxy model for relationship parameter value models."""
    def __init__(self, parent, parameter_definition_id_column, object_id_list_column):
        """Init class."""
        super().__init__(parent, parameter_definition_id_column)
        self.object_ids = dict()
        self.object_id_lists = set()
        self.object_id_list_column = object_id_list_column

    def update_filter(self, parameter_definition_ids, object_ids, object_id_lists):
        """Update filter."""
        if parameter_definition_ids == self.parameter_definition_ids \
                and object_ids == self.object_ids and object_id_lists == self.object_id_lists:
            return
        self.parameter_definition_ids = parameter_definition_ids
        self.object_ids = object_ids
        self.object_id_lists = object_id_lists
        self.invalidateFilter()

    def main_filter_accepts_row(self, source_row, source_parent):
        """Accept or reject row."""
        if not super().main_filter_accepts_row(source_row, source_parent):
            return False
        object_id_list = self.sourceModel()._main_data[source_row][self.object_id_list_column]
        if self.object_id_lists:
            return object_id_list in self.object_id_lists
        if self.object_ids:
            return len(self.object_ids.intersection(int(x) for x in object_id_list.split(","))) > 0
        return True


class TreeNode:
    """A helper class to use as the internalPointer of indexes in ParameterValueListModel.

    Attributes
        parent (TreeNode): the parent node
        row (int): the row, needed in ParameterValueListModel.parent()
        text (str, NoneType): the text to show
        id (int, NoneType): the id from the db table
    """
    def __init__(self, parent, row, text=None, id=None):
        self.parent = parent
        self.row = row
        self.child_nodes = list()
        self.text = text
        self.id = id


class ParameterValueListModel(QAbstractItemModel):
    """A class to display parameter value list data in a treeview."""

    def __init__(self, tree_view_form):
        """Initialize class"""
        super().__init__(tree_view_form)
        self._tree_view_form = tree_view_form
        self.db_map = tree_view_form.db_map
        self.bold_font = QFont()
        self.bold_font.setBold(True)
        gray_color = QGuiApplication.palette().text().color()
        gray_color.setAlpha(128)
        self.gray_brush = QBrush(gray_color)
        self.empty_list = "Type new list name here..."
        self.empty_value = "Type new list value here..."
        self._root_nodes = list()
        self.dataChanged.connect(self._handle_data_changed)

    def build_tree(self):
        """Initialize the internal data structure of TreeNode instances."""
        self.beginResetModel()
        self._root_nodes = list()
        i = 0
        for wide_value_list in self.db_map.wide_parameter_value_list_list():
            root_node = TreeNode(None, i, text=wide_value_list.name, id=wide_value_list.id)
            i += 1
            self._root_nodes.append(root_node)
            j = 0
            for value in wide_value_list.value_list.split(","):
                child_node = TreeNode(root_node, j, text=value)
                j += 1
                root_node.child_nodes.append(child_node)
            root_node.child_nodes.append(TreeNode(root_node, j, text=self.empty_value))
        self._root_nodes.append(TreeNode(None, i, text=self.empty_list))
        self.endResetModel()

    def index(self, row, column, parent=QModelIndex()):
        """Returns the index of the item in the model specified by the given row, column and parent index.
        Toplevel indexes get their pointer from the `_root_nodes` attribute;
        whereas inner indexes get their pointer from the `child_nodes` attribute of the parent node.
        """
        if not parent.isValid():
            return self.createIndex(row, column, self._root_nodes[row])
        parent_node = parent.internalPointer()
        return self.createIndex(row, column, parent_node.child_nodes[row])

    def parent(self, index):
        """Returns the parent of the model item with the given index.
        Use the internal pointer to retrieve the parent node and use it
        to create the parent index.
        """
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        if node.parent is None:
            return QModelIndex()
        return self.createIndex(node.parent.row, 0, node.parent)

    def rowCount(self, parent=QModelIndex()):
        """Returns the number of rows under the given parent.
        Get it from the lenght of the appropriate list.
        """
        if not parent.isValid():
            return len(self._root_nodes)
        node = parent.internalPointer()
        return len(node.child_nodes)

    def columnCount(self, parent=QModelIndex()):
        """Returns the number of columns under the given parent. Always 1.
        """
        return 1

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index.
        Bold toplevel items. Get the DisplayRole from the `text` attribute of the internal pointer.
        """
        if not index.isValid():
            return None
        if role == Qt.FontRole:
            if not index.parent().isValid():
                return self.bold_font
            return None
        if role == Qt.ForegroundRole:
            if index.row() == self.rowCount(index.parent()) - 1:
                return self.gray_brush
            return None
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        node = index.internalPointer()
        return node.text

    def flags(self, index):
        """Returns the item flags for the given index.
        """
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role=Qt.EditRole):
        """Sets the role data for the item at index to value.
        Returns True if successful; otherwise returns False.
        Basically just update the `text` attribute of the internal pointer.
        """
        if not index.isValid():
            return False
        if role != Qt.EditRole:
            return False
        node = index.internalPointer()
        if value == node.text:
            return False
        node.text = value
        self.dataChanged.emit(index, index, [role])
        return True

    def appendRows(self, count, parent=QModelIndex()):
        """Append count rows into the model.
        Items in the new row will be children of the item represented by the parent model index.
        """
        row = self.rowCount(parent)
        self.beginInsertRows(parent, row, row + count -1)
        if not parent.isValid():
            self._root_nodes.append(TreeNode(None, row, text=self.empty_list))
        else:
            root_node = parent.internalPointer()
            root_node.child_nodes.append(TreeNode(root_node, row, text=self.empty_value))
        self.endInsertRows()

    @Slot("QModelIndex", "QModelIndex", "QVector", name="_handle_data_changed")
    def _handle_data_changed(self, top_left, bottom_right, roles=None):
        """Called when data in the model changes.
        """
        if roles is None:
            roles = list()
        if Qt.EditRole not in roles:
            return
        parent = self.parent(top_left)
        if parent != self.parent(bottom_right):
            return
        self.append_empty_rows(bottom_right, parent)
        to_add, to_update = self.items_to_add_and_update(top_left.row(), bottom_right.row(), parent)
        self._tree_view_form.add_parameter_value_lists(*to_add)
        self._tree_view_form.update_parameter_value_lists(*to_update)

    def append_empty_rows(self, index, parent):
        """Append emtpy rows if index is the last children, so the user can continue editing the model.
        The argument `parent` is given for convenience.
        """
        if self.rowCount(parent) == index.row() + 1:
            self.appendRows(1, parent)
            if not parent.isValid():
                self.appendRows(1, index)

    def items_to_add_and_update(self, first, last, parent):
        """Return list of items to add and update in the db.
        """
        to_add = list()
        to_update = list()
        if not parent.isValid():
            # The changes correspond to list *names*.
            # We need to check them all
            for row in range(first, last + 1):
                index = self.index(row, 0, parent)
                node = index.internalPointer()
                id = node.id
                name = node.text
                if id:
                    # Update
                    to_update.append(dict(id=id, name=name))
                else:
                    # Add
                    value_list = [
                        self.index(i, 0, index).internalPointer().text
                        for i in range(self.rowCount(index) - 1)
                    ]
                    if value_list:
                        to_add.append(dict(parent=index, name=name, value_list=value_list))
        else:
            # The changes correspond to list *values*, so it's enough to check the parent
            value_list = [
                self.index(i, 0, parent).internalPointer().text
                for i in range(self.rowCount(parent) - 1)
            ]
            id = parent.internalPointer().id
            if id:
                # Update
                to_update.append(dict(id=id, value_list=value_list))
            else:
                # Add
                name = parent.internalPointer().text
                to_add.append(dict(parent=parent, name=name, value_list=value_list))
        return to_add, to_update

    def batch_set_data(self, indexes, values):
        """Set edit role for indexes to values in batch."""
        # NOTE: Not in use at the moment
        parented_rows = dict()
        for index, value in zip(indexes, values):
            index.internalPointer().text = value
            parent = self.parent(index)
            parented_rows.setdefault(parent, list()).append(index.row())
        # Emit dataChanged parent-wise
        for parent, rows in parented_rows.items():
            top_left = self.index(min(rows), 0, parent)
            bottom_right = self.index(max(rows), 0, parent)
            self.dataChanged.emit(top_left, bottom_right, [Qt.EditRole])

    def removeRow(self, row, parent=QModelIndex()):
        """Remove row under parent, but never the last row (which is the empty one)"""
        if row == self.rowCount(parent) - 1:
            return
        self.beginRemoveRows(parent, row, row)
        if not parent.isValid():
            # Row is at the top level
            self._root_nodes.pop(row)
            # Update row attribute of tail items. This is awful but we need it.
            for r in range(row, len(self._root_nodes)):
                node = self._root_nodes[r]
                node.row = r
        else:
            # Row is at the low level
            parent_node = parent.internalPointer()
            child_nodes = parent_node.child_nodes
            child_nodes.pop(row)
            # We don't need to update the row attribute of the childs, since they're not used.
        self.endRemoveRows()


class JSONArrayModel(EmptyRowModel):
    """A model of JSON array data, used by TreeViewForm.

    Attributes:
        parent (JSONEditor): the parent widget
        stride (int): The number of elements to fetch
    """
    def __init__(self, parent, stride=256):
        """Initialize class"""
        super().__init__(parent)
        self._json_data = []
        self._stride = stride
        self.set_horizontal_header_labels("json")

    def reset_model(self, json_data):
        """Store JSON array into a list.
        Initialize `stride` rows.
        """
        try:
            self._json_data = json.loads(json_data)
        except (TypeError, json.JSONDecodeError):
            self._json_data = []
        if not isinstance(self._json_data, list):
            self._json_data = []
        data = []
        for i in range(self._stride):
            try:
                data.append([json.dumps(self._json_data.pop(0))])
            except IndexError:
                break
        super().reset_model(data)

    def canFetchMore(self, parent):
        return len(self._json_data) > 0

    def fetchMore(self, parent):
        """Pop data from the _json_data attribute and add it to the model."""
        data = list()
        count = 0
        for i in range(self._stride):
            try:
                data.append(json.dumps(self._json_data.pop(0)))
                count += 1
            except IndexError:
                break
        last_data_row = self.rowCount() - 1
        self.insertRows(last_data_row, count)
        indexes = [self.index(last_data_row + i, 0) for i in range(count)]
        self.batch_set_data(indexes, data)

    def json_data(self):
        """Return data into JSON array."""
        last_data_row = self.rowCount() - 1
        new_json_data = [json.loads(self._main_data[i][0]) for i in range(last_data_row)]
        new_json_data.extend(self._json_data)  # Whatever remains unfetched
        if not new_json_data:
            return None
        return json.dumps(new_json_data)


class DatapackageResourcesModel(MinimalTableModel):
    """A model of datapackage resource data, used by SpineDatapackageWidget.

    Attributes:
        parent (SpineDatapackageWidget)
    """
    def __init__(self, parent):
        """Initialize class"""
        super().__init__(parent)

    def reset_model(self, resources):
        self.clear()
        self.set_horizontal_header_labels(["name", "source"])
        data = list()
        for resource in resources:
            name = resource.name
            source = os.path.basename(resource.source)
            data.append([name, source])
        super().reset_model(data)

    def flags(self, index):
        if index.column() == 1:
            return ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable
        return super().flags(index)


class DatapackageFieldsModel(MinimalTableModel):
    """A model of datapackage field data, used by SpineDatapackageWidget.

    Attributes:
        parent (SpineDatapackageWidget)
    """
    def __init__(self, parent):
        """Initialize class"""
        super().__init__(parent)

    def reset_model(self, schema):
        self.clear()
        self.set_horizontal_header_labels(["name", "type", "primary key?"])
        data = list()
        for field in schema.fields:
            name = field.name
            type_ = field.type
            primary_key = name in schema.primary_key
            data.append([name, type_, primary_key])
        super().reset_model(data)


class DatapackageForeignKeysModel(EmptyRowModel):
    """A model of datapackage foreign key data, used by SpineDatapackageWidget.

    Attributes:
        parent (SpineDatapackageWidget)
    """
    def __init__(self, parent):
        """Initialize class"""
        super().__init__(parent)
        self._parent = parent

    def reset_model(self, foreign_keys):
        self.clear()
        self.set_horizontal_header_labels(["fields", "reference resource", "reference fields", ""])
        data = list()
        for foreign_key in foreign_keys:
            fields = ",".join(foreign_key['fields'])
            reference_resource = foreign_key['reference']['resource']
            reference_fields = ",".join(foreign_key['reference']['fields'])
            data.append([fields, reference_resource, reference_fields, None])
        super().reset_model(data)


class TableModel(QAbstractItemModel):
    def __init__(self, headers=None, data=None):
        super(TableModel, self).__init__()
        if headers is None:
            headers = list()
        if data is None:
            data = list()
        self._data = data
        self._headers = headers

    def parent(self, child=None):
        return QModelIndex()

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, parent)

    def set_data(self, data, headers):
        if data and len(data[0]) != len(headers):
            raise ValueError("'data[0]' must be same length as 'headers'")
        self.beginResetModel()
        self._data = data
        self._headers = headers
        self.endResetModel()
        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount(), self.columnCount())
        self.dataChanged.emit(top_left, bottom_right)

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]

    def row(self, index):
        if index.isValid():
            return self._data[index.row()]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]


class HybridTableModel(MinimalTableModel):
    """A model that concatenates two models,
    one for existing items and another one for new items.
    """
    def __init__(self, parent=None):
        """Init class."""
        super().__init__(parent)
        self._parent = parent
        self.existing_item_model = MinimalTableModel(self)
        self.new_item_model = EmptyRowModel(self)

    def flags(self, index):
        """Return flags for given index.
        Depending on the index's row we will land on one of the two models.
        """
        row = index.row()
        column = index.column()
        if row < self.existing_item_model.rowCount():
            return self.existing_item_model.index(row, column).flags()
        row -= self.existing_item_model.rowCount()
        return self.new_item_model.index(row, column).flags()

    def data(self, index, role=Qt.DisplayRole):
        """Return data for given index and role.
        Depending on the index's row we will land on one of the two models.
        """
        row = index.row()
        column = index.column()
        if row < self.existing_item_model.rowCount():
            return self.existing_item_model.index(row, column).data(role)
        row -= self.existing_item_model.rowCount()
        return self.new_item_model.index(row, column).data(role)

    def rowCount(self, parent=QModelIndex()):
        """Return the sum of rows in the two models.
        """
        return self.existing_item_model.rowCount() + self.new_item_model.rowCount()

    def batch_set_data(self, indexes, data):
        """Batch set data for indexes.
        Distribute indexes and data among the two models
        and call batch_set_data on each of them."""
        if not indexes:
            return False
        if len(indexes) != len(data):
            return False
        existing_model_indexes = []
        existing_model_data = []
        new_model_indexes = []
        new_model_data = []
        for k, index in enumerate(indexes):
            if not index.isValid():
                continue
            row = index.row()
            column = index.column()
            if row < self.existing_item_model.rowCount():
                existing_model_indexes.append(self.existing_item_model.index(row, column))
                existing_model_data.append(data[k])
            else:
                row -= self.existing_item_model.rowCount()
                new_model_indexes.append(self.new_item_model.index(row, column))
                new_model_data.append(data[k])
        self.existing_item_model.batch_set_data(existing_model_indexes, existing_model_data)
        self.new_item_model.batch_set_data(new_model_indexes, new_model_data)
        # Find square envelope of indexes to emit dataChanged
        top = min(ind.row() for ind in indexes)
        bottom = max(ind.row() for ind in indexes)
        left = min(ind.column() for ind in indexes)
        right = max(ind.column() for ind in indexes)
        self.dataChanged.emit(self.index(top, left), self.index(bottom, right))
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        """Find the right sub-model (or the empty model) and call insertRows on it."""
        if row < self.existing_item_model.rowCount():
            self.rowsInserted.emit()
            return self.existing_item_model.insertRows(row, count)
        row -= self.existing_item_model.rowCount()
        return self.new_item_model.insertRows(row, count)

    def removeRows(self, row, count, parent=QModelIndex()):
        """Find the right sub-models (or empty model) and call removeRows on them."""
        if row < 0 or row + count - 1 >= self.rowCount():
            return False
        self.beginRemoveRows(parent, row, row + count - 1)
        if row < self.existing_item_model.rowCount():
            # split count across models
            existing_count = min(count, self.existing_item_model.rowCount() - row)
            self.existing_item_model.removeRows(row, existing_count)
            new_count = count - existing_count
            if new_count > 0:
                self.new_item_model.removeRows(row, new_count)
        else:
            row -= self.existing_item_model.rowCount()
            self.new_item_model.removeRows(row, count)
        self.endRemoveRows()
        return True

    def set_horizontal_header_labels(self, labels):
        super().set_horizontal_header_labels(labels)
        self.new_item_model.set_horizontal_header_labels(labels)

    def reset_model(self, data):
        """Reset model data."""
        self.beginResetModel()
        self.existing_item_model.reset_model(data)
        self.new_item_model.clear()
        self.new_item_model.rowsInserted.connect(self._handle_new_item_model_rows_inserted)
        self.endResetModel()

    @Slot("QModelIndex", "int", "int", name="_handle_new_item_model_rows_inserted")
    def _handle_new_item_model_rows_inserted(self, parent, first, last):
        offset = self.existing_item_model.rowCount()
        self.rowsInserted.emit(QModelIndex(), offset + first, offset + last)
