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
Contains a class for storing project items.

:authors: P. Savolainen (VTT)
:date:   23.1.2018
"""
import logging
from copy import copy
from PySide2.QtCore import Qt, QModelIndex, QAbstractItemModel
from PySide2.QtGui import QIcon, QFont


class ProjectItemModel(QAbstractItemModel):
    def __init__(self, root, parent=None):
        """Class to store project tree items and ultimately project items in a tree structure.

        Args:
            root (RootProjectTreeItem): Root item for the project item tree
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._root = root

    def root(self):
        """Returns the root item."""
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
        return parent.internalPointer().child_count()

    def columnCount(self, parent=QModelIndex()):
        """Returns model column count which is always 1."""
        return 1

    def flags(self, index):
        """Returns flags for the item at given index

        Args:
            index (QModelIndex): Flags of item at this index.
        """
        return index.internalPointer().flags()

    def parent(self, index=QModelIndex()):
        """Returns index of the parent of given index.

        Args:
            index (QModelIndex): Index of item whose parent is returned

        Returns:
            QModelIndex: Index of parent item
        """
        item = self.item(index)
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
        parent_item = self.item(parent)
        child = parent_item.child(row)
        if not child:
            return QModelIndex()
        return self.createIndex(row, column, child)

    def data(self, index, role=None):
        """Returns data in the given index according to requested role.

        Args:
            index (QModelIndex): Index to query
            role (int): Role to return

        Returns:
            object: Data depending on role.
        """
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            return item.name
        if role == Qt.DecorationRole:
            if not hasattr(item, "project_item"):
                # item is a CategoryProjectTreeItem or root
                return None
            # item is a LeafProjectTreeItem
            icon_path = item.project_item.get_icon().icon_file
            return QIcon(icon_path)
        if role == Qt.FontRole:
            if not hasattr(item, "project_item"):
                bold_font = QFont()
                bold_font.setBold(True)
                return bold_font
        return None

    def item(self, index):
        """Returns item at given index.

        Args:
            index (QModelIndex): Index of item

        Returns:
            RootProjectTreeItem, CategoryProjectTreeItem or LeafProjectTreeItem: Item at given index or root project
                item if index is not valid
        """
        if not index.isValid():
            return self.root()
        return index.internalPointer()

    def find_category(self, category_name):
        """Returns the index of the given category name.

        Args:
            category_name (str): Name of category item to find

        Returns:
             QModelIndex: index of a category item or None if it was not found
        """
        category_names = [category.name for category in self.root().children()]
        try:
            row = category_names.index(category_name)
        except ValueError:
            logging.error("Category name %s not found in %s", category_name, category_names)
            return None
        return self.index(row, 0, QModelIndex())

    def find_item(self, name):
        """Returns the QModelIndex of the leaf item with the given name

        Args:
            name (str): The searched project item (long) name

        Returns:
            QModelIndex: Index of a project item with the given name or None if not found
        """
        for category in self.root().children():
            category_index = self.find_category(category.name)
            start_index = self.index(0, 0, category_index)
            matching_index = self.match(start_index, Qt.DisplayRole, name, 1, Qt.MatchFixedString | Qt.MatchRecursive)
            if not matching_index:
                pass  # no match in this category
            elif len(matching_index) == 1:
                return matching_index[0]
        return None

    def get_item(self, name):
        """Returns leaf item with given name or None if it doesn't exist.

        Args:
            name (str): Project item name

        Returns:
            LeafProjectTreeItem, NoneType
        """
        ind = self.find_item(name)
        if ind is None:
            return None
        return self.item(ind)

    def category_of_item(self, name):
        """Returns the category item of the category that contains project item with given name

        Args:
            name (str): Project item name

        Returns:
            category item or None if the category was not found
        """
        for category in self.root().children():
            for item in category.children():
                if name == item.name:
                    return category
        return None

    def insert_item(self, item, parent=QModelIndex()):
        """Adds a new item to model. Fails if given parent is not
        a category item nor a leaf item. New item is inserted as
        the last item of its branch.

        Args:
            item (CategoryProjectTreeItem or LeafProjectTreeItem): Project item to add to model
            parent (QModelIndex): Parent project item

        Returns:
            bool: True if successful, False otherwise
        """
        parent_item = self.item(parent)
        row = self.rowCount(parent)  # parent.child_count()
        self.beginInsertRows(parent, row, row)
        retval = parent_item.add_child(item)
        self.endInsertRows()
        return retval

    def remove_item(self, item, parent=QModelIndex()):
        """Removes item from project.

        Args:
            item (BaseProjectTreeItem): Project item to remove
            parent (QModelIndex): Parent of item that is to be removed

        Returns:
            bool: True if item removed successfully, False if item removing failed
        """
        parent_item = self.item(parent)
        row = item.row()
        self.beginRemoveRows(parent, row, row)
        parent_item.remove_child(row)
        self.endRemoveRows()

    def set_leaf_item_name(self, index, name):
        """Changes the name of the leaf item at given index.

        Args:
            index (QModelIndex): Tree item index
            name (str): New project item name
        """
        item = index.internalPointer()
        item.set_name(name)
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def items(self, category_name=None):
        """Returns a list of leaf items in model according to category name. If no category name given,
        returns all leaf items in a list.

        Args:
            category_name (str): Item category. Data Connections, Data Stores, Importers, Exporters, Tools or Views
                permitted.

        Returns:
            :obj:'list' of :obj:'LeafProjectTreeItem': Depending on category_name argument, returns all items or only
            items according to category. An empty list is returned if there are no items in the given category
            or if an unknown category name was given.
        """
        if not category_name:
            items = list()
            for category in self.root().children():
                items += category.children()
            return items
        category_index = self.find_category(category_name)
        if not category_index:
            logging.error("Category item '%s' not found", category_name)
            return list()
        return category_index.internalPointer().children()

    def n_items(self):
        """Returns the number of all items in the model excluding category items and root.

        Returns:
            int: Number of items
        """
        return len(self.items())

    def item_names(self):
        """Returns all leaf item names in a list.

        Returns:
            obj:'list' of obj:'str': Item names
        """
        return [item.name for item in self.items()]

    def items_per_category(self):
        """Returns a dict mapping category indexes to a list of items in that category.

        Returns:
            dict(QModelIndex,list(LeafProjectTreeItem))
        """
        category_inds = [self.index(row, 0) for row in range(self.rowCount())]
        return {ind: copy(ind.internalPointer().children()) for ind in category_inds}

    def short_name_reserved(self, short_name):
        """Checks if the directory name derived from the name of the given item is in use.

        Args:
            short_name (str): Item short name

        Returns:
            bool: True if short name is taken, False if it is available.
        """
        return short_name in set(item.short_name for item in self.items())

    def leaf_indexes(self):
        """Yields leaf indexes."""
        for row in range(self.rowCount()):
            category_index = self.index(row, 0)
            for inner_row in range(self.rowCount(category_index)):
                yield self.index(inner_row, 0, category_index)

    def remove_leaves(self):
        self.beginResetModel()
        for row in range(self.rowCount()):
            category_index = self.index(row, 0)
            category_index.internalPointer().children().clear()
        self.endResetModel()
