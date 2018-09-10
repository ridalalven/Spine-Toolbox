#############################################################################
# Copyright (C) 2017 - 2018 VTT Technical Research Centre of Finland
#
# This file is part of Spine Toolbox.
#
# Spine Toolbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################

"""
Classes for custom context menus and pop-up menus.

:author: Pekka Savolainen <pekka.t.savolainen@vtt.fi>
:date:   9.1.2018
"""

import logging
from PySide2.QtWidgets import QMenu
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt


class CustomContextMenu(QMenu):
    """Context menu master class for several context menus.

    Attributes:
        parent (QWidget): Parent for menu widget (ToolboxUI)
        index (QModelIndex): Index of item that requested the context-menu
    """
    def __init__(self, parent, index):
        """Constructor."""
        super().__init__(parent=parent)
        self._parent = parent
        self.index = index
        self.option = "None"

    def add_action(self, text, icon=QIcon(), enabled=True):
        """Adds an action to the context menu.

        Args:
            text (str): Text description of the action
            icon (QIcon): Icon for menu item
            enabled (bool): Is action enabled?
        """
        action = self.addAction(icon, text)
        action.setEnabled(enabled)
        action.triggered.connect(lambda: self.set_action(text))

    def set_action(self, option):
        """Sets the action which was clicked.

        Args:
            option (str): string with the text description of the action
        """
        self.option = option

    def get_action(self):
        """Returns the clicked action, a string with a description."""
        return self.option


class ProjectItemContextMenu(CustomContextMenu):
    """Context menu for project items both in the QTreeView and in the QGraphicsView.

    Attributes:
        parent (QWidget): Parent for menu widget (ToolboxUI)
        position (QPoint): Position on screen
        index (QModelIndex): Index of item that requested the context-menu
    """
    def __init__(self, parent, position, index):
        """Class constructor."""
        super().__init__(parent, index)
        if not index.isValid():
            # If no item at index
            return
        if not index.parent().isValid():
            # If index is at a category item
            return
        d = index.data(Qt.UserRole)
        if d.item_type == "Data Connection":
            self.add_action("Open directory...")
        elif d.item_type == "Data Store":
            self.add_action("Open directory...")
        elif d.item_type == "Tool":
            self.add_action("Execute")
            self.add_action("Results...")
            if d.get_icon().wheel.isVisible():
                self.add_action("Stop")
            else:
                self.add_action("Stop", enabled=False)
            self.addSeparator()
            if not d.tool_template():
                enabled = False
            else:
                enabled = True
            self.add_action("Edit Tool template", enabled=enabled)
            self.add_action("Open main program file", enabled=enabled)
        elif d.item_type == "View":
            pass
        else:
            logging.error("Unknown item type:{0}".format(d.item_type))
            return
        self.addSeparator()
        self.add_action("Rename")
        self.add_action("Remove Item")
        self.exec_(position)


class LinkContextMenu(CustomContextMenu):
    """Context menu class for connection links.

    Attributes:
        parent (QWidget): Parent for menu widget (ToolboxUI)
        position (QPoint): Position on screen
        index (QModelIndex): Index of item that requested the context-menu
        parallel_link (Link(QGraphicsPathItem)): Link that is parallel to the one that requested the menu
    """
    def __init__(self, parent, position, index, parallel_link=None):
        """Class constructor."""
        super().__init__(parent, index)
        if not index.isValid():
            return
        self.add_action("Remove Connection")
        if parallel_link:
            self.add_action("Send to bottom")
        self.exec_(position)


class ToolTemplateContextMenu(CustomContextMenu):
    """Context menu class for Tool templates.

    Attributes:
        parent (QWidget): Parent for menu widget (ToolboxUI)
        position (QPoint): Position on screen
        index (QModelIndex): Index of item that requested the context-menu
    """

    def __init__(self, parent, position, index):
        """Class constructor."""
        super().__init__(parent, index)
        if not index.isValid():
            # If no item at index
            return
        if index.row() == 0:
            # Don't show menu when clicking on No tool
            return
        self.add_action("Edit Tool template")
        self.add_action("Remove Tool template")
        self.addSeparator()
        self.add_action("Open main program file")
        self.add_action("Open definition file")
        self.exec_(position)


class ObjectTreeContextMenu(CustomContextMenu):
    """Context menu class for object tree items in Data store form.

    Attributes:
        parent (QWidget): Parent for menu widget (DataStoreForm)
        position (QPoint): Position on screen
        index (QModelIndex): Index of item that requested the context-menu
    """
    def __init__(self, parent, position, index):
        """Class constructor."""
        super().__init__(parent, index)
        if not index.isValid():
            return
        plus_object_icon = self._parent.ui.actionAdd_objects.icon()
        plus_relationship_icon = self._parent.ui.actionAdd_relationships.icon()
        plus_object_parameter_icon = self._parent.ui.actionAdd_object_parameters.icon()
        plus_relationship_parameter_icon = self._parent.ui.actionAdd_relationship_parameters.icon()
        if not index.parent().isValid():  # root item
            self.add_action("Add object classes")
        else:
            item = index.model().itemFromIndex(index)
            item_type = item.data(Qt.UserRole)
            if item_type == 'object_class':
                self.add_action("Add relationship classes", plus_relationship_icon)
                self.add_action("Add objects", plus_object_icon)
                self.addSeparator()
                self.add_action("Add parameters", plus_object_parameter_icon)
                self.addSeparator()
                self.add_action("Rename object class")
                self.addSeparator()
                self.add_action("Remove object class")
            elif item_type == 'object':
                self.add_action("Add parameter values", plus_object_parameter_icon)
                self.addSeparator()
                self.add_action("Rename object")
                self.addSeparator()
                self.add_action("Remove object")
            elif item_type == 'relationship_class':
                self.add_action("Add relationships", plus_relationship_icon)
                self.addSeparator()
                self.add_action("Add parameters", plus_relationship_parameter_icon)
                self.addSeparator()
                self.add_action("Rename relationship class")
                self.addSeparator()
                self.add_action("Remove relationship class")
            elif item_type == 'relationship':
                self.add_action("Expand next")
                self.addSeparator()
                self.add_action("Add parameter values", plus_relationship_parameter_icon)
                self.addSeparator()
                self.add_action("Rename relationship")
                self.addSeparator()
                self.add_action("Remove relationship")
        self.exec_(position)


class ParameterValueContextMenu(CustomContextMenu):
    """Context menu class for object parameter value items in Data Store.

    Attributes:
        parent (QWidget): Parent for menu widget (DataStoreForm)
        position (QPoint): Position on screen
        index (QModelIndex): Index of item that requested the context-menu
    """
    def __init__(self, parent, position, index):
        """Class constructor."""
        super().__init__(parent, index)
        if not index.isValid():
            return
        self.add_action("Remove selected")
        self.exec_(position)


class ParameterContextMenu(CustomContextMenu):
    # TODO: This is exactly the same as ParameterValueContextMenu. Remove?
    """Context menu class for object parameter items in Data Store.

    Attributes:
        parent (QWidget): Parent for menu widget (DataStoreForm)
        position (QPoint): Position on screen
        index (QModelIndex): Index of item that requested the context-menu
    """
    def __init__(self, parent, position, index):
        """Class constructor."""
        super().__init__(parent, index)
        if not index.isValid():
            return
        self.add_action("Remove selected")
        self.exec_(position)


class CustomPopupMenu(QMenu):
    """Popup menu master class for several popup menus.

    Attributes:
        parent (QWidget): Parent widget of this pop-up menu
    """
    def __init__(self, parent):
        """Class constructor."""
        super().__init__(parent=parent)
        self._parent = parent

    def add_action(self, text, slot, enabled=True):
        """Adds an action to the popup menu.

        Args:
            text (str): Text description of the action
            slot (method): Method to connect to action's triggered signal
            enabled (bool): Is action enabled?
        """
        action = self.addAction(text)
        action.setEnabled(enabled)
        action.triggered.connect(slot)


class AddToolTemplatePopupMenu(CustomPopupMenu):
    """Popup menu class for add tool template button.

    Attributes:
        parent (QWidget): parent widget (ToolboxUI)
    """
    def __init__(self, parent):
        """Class constructor."""
        super().__init__(parent)
        # Open empty Tool Template Form
        self.add_action("New", self._parent.show_tool_template_form)
        # Add an existing Tool template from file to project
        self.add_action("Add existing...", self._parent.open_tool_template)


class ToolTemplateOptionsPopupMenu(CustomPopupMenu):
    """Popup menu class for tool template options button in Tool item.

    Attributes:
        parent (QWidget): Parent widget of this menu (ToolboxUI)
        tool (Tool): Tool item that is associated with the pressed button
    """
    def __init__(self, parent, tool):
        super().__init__(parent)
        enabled = True if tool.tool_template() else False
        self.add_action("Edit Tool template", tool.edit_tool_template, enabled=enabled)
        self.add_action("Open definition file", tool.open_tool_template_file, enabled=enabled)
        self.add_action("Open main program file", tool.open_tool_main_program_file, enabled=enabled)
        self.addSeparator()
        self.add_action("New Tool template", tool.get_parent().show_tool_template_form)
        self.add_action("Add Tool template...", tool.get_parent().open_tool_template)


class AddIncludesPopupMenu(CustomPopupMenu):
    """Popup menu class for add includes button in Tool Template widget.

    Attributes:
        parent (QWidget): Parent widget (ToolTemplateWidget)
    """
    def __init__(self, parent):
        """Class constructor."""
        super().__init__(parent)
        self._parent = parent
        # Open a tool template file
        self.add_action("New file", self._parent.new_include)
        self.addSeparator()
        self.add_action("Open file", self._parent.add_includes)


class QOkMenu(QMenu):
    """An QMenu that only hides when 'Ok' action is triggered.
    It allows selecting multiple checkable options.

    Attributes:
        parent (QWidget): Parent of the QMenu
    """
    def __init__(self, parent):
        """Initialize the class."""
        super().__init__(parent)

    def mouseReleaseEvent(self, event):
        """The super implementation triggers the action and closes the menu.
        Here, we only close the menu if the action is the 'Ok' action.
        Otherwise we just trigger it.
        """
        action = self.activeAction()
        if action is None:
            super().mouseReleaseEvent(event)
            return
        if action.text() == "Ok":
            super().mouseReleaseEvent(event)
            return
        action.trigger()
