######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains TabularViewMixin class.

:author: P. Vennström (VTT)
:date:   1.11.2018
"""

from itertools import product
from collections import namedtuple
from PySide2.QtCore import Qt, Slot
from spinedb_api import IndexedValue, Map, ParameterValueFormatError, TimeSeries
from .custom_menus import TabularViewFilterMenu, PivotTableModelMenu, PivotTableHorizontalHeaderMenu
from .tabular_view_header_widget import TabularViewHeaderWidget
from .custom_delegates import PivotTableDelegate
from ..helpers import fix_name_ambiguity, busy_effect
from ..mvcmodels.pivot_table_models import IndexId, PivotTableSortFilterProxy, PivotTableModel
from ..mvcmodels.frozen_table_model import FrozenTableModel
from ..mvcmodels.shared import EDITOR_ROLE


class TabularViewMixin:
    """Provides the pivot table and its frozen table for the DS form."""

    _PARAMETER_VALUE = "Parameter value"
    _INDEX_EXPANSION = "Indexed parameter expansion"
    _RELATIONSHIP = "Relationship"

    _PARAMETER = "parameter"
    _INDEX = "index"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # current state of ui
        self.current_class_type = None
        self.current_class_id = None
        self.current_input_type = self._PARAMETER_VALUE
        self.filter_menus = {}
        self.class_pivot_preferences = {}
        self.PivotPreferences = namedtuple("PivotPreferences", ["index", "columns", "frozen", "frozen_value"])
        self.ui.comboBox_pivot_table_input_type.addItems(
            [self._PARAMETER_VALUE, self._INDEX_EXPANSION, self._RELATIONSHIP]
        )
        self.pivot_table_proxy = PivotTableSortFilterProxy()
        self.pivot_table_model = PivotTableModel(self)
        self.pivot_table_proxy.setSourceModel(self.pivot_table_model)
        self.frozen_table_model = FrozenTableModel(self)
        self.ui.pivot_table.setModel(self.pivot_table_proxy)
        self.ui.frozen_table.setModel(self.frozen_table_model)
        self.ui.pivot_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.pivot_table.verticalHeader().setDefaultSectionSize(self.default_row_height)
        self.ui.frozen_table.verticalHeader().setDefaultSectionSize(self.default_row_height)
        self.ui.pivot_table.horizontalHeader().setResizeContentsPrecision(self.visible_rows)
        self.pivot_table_menu = PivotTableModelMenu(self)
        self._pivot_table_horizontal_header_menu = PivotTableHorizontalHeaderMenu(
            self.pivot_table_proxy, self.ui.pivot_table
        )
        self._focusable_childs.append(self.ui.pivot_table)

    def setup_delegates(self):
        """Sets delegates for tables."""
        super().setup_delegates()
        delegate = PivotTableDelegate(self)
        self.ui.pivot_table.setItemDelegate(delegate)
        delegate.parameter_value_editor_requested.connect(self.show_parameter_value_editor)
        delegate.data_committed.connect(self._set_model_data)

    def add_menu_actions(self):
        """Adds toggle view actions to View menu."""
        super().add_menu_actions()
        self.ui.menuView.addSeparator()
        self.ui.menuView.addAction(self.ui.dockWidget_pivot_table.toggleViewAction())
        self.ui.menuView.addAction(self.ui.dockWidget_frozen_table.toggleViewAction())

    def connect_signals(self):
        """Connects signals to slots."""
        super().connect_signals()
        self.ui.treeView_object.selectionModel().selectionChanged.connect(self._handle_entity_tree_selection_changed)
        self.ui.treeView_relationship.selectionModel().selectionChanged.connect(
            self._handle_entity_tree_selection_changed
        )
        self.ui.pivot_table.customContextMenuRequested.connect(self.pivot_table_menu.request_menu)
        self.ui.pivot_table.horizontalHeader().customContextMenuRequested.connect(
            self._pivot_table_horizontal_header_menu.request_menu
        )
        self.pivot_table_model.modelReset.connect(self.make_pivot_headers)
        self.ui.pivot_table.horizontalHeader().header_dropped.connect(self.handle_header_dropped)
        self.ui.pivot_table.verticalHeader().header_dropped.connect(self.handle_header_dropped)
        self.ui.frozen_table.header_dropped.connect(self.handle_header_dropped)
        self.ui.frozen_table.selectionModel().currentChanged.connect(self.change_frozen_value)
        self.ui.comboBox_pivot_table_input_type.currentTextChanged.connect(self.reload_pivot_table)
        self.ui.dockWidget_pivot_table.visibilityChanged.connect(self._handle_pivot_table_visibility_changed)
        self.ui.dockWidget_frozen_table.visibilityChanged.connect(self._handle_frozen_table_visibility_changed)
        self.ui.pivot_table.selectionModel().selectionChanged.connect(self._handle_pivot_table_selection_changed)

    def init_models(self):
        """Initializes models."""
        super().init_models()
        self.clear_pivot_table()

    @Slot("QItemSelection", "QItemSelection")
    def _handle_pivot_table_selection_changed(self, selected, deselected):
        """Accepts selection."""
        self._accept_selection(self.ui.pivot_table)

    def is_value_input_type(self):
        return self.current_input_type == self._PARAMETER_VALUE

    def is_index_expansion_input_type(self):
        return self.current_input_type == self._INDEX_EXPANSION

    @Slot("QModelIndex", object)
    def _set_model_data(self, index, value):
        self.pivot_table_proxy.setData(index, value)

    def current_object_class_id_list(self):
        if self.current_class_type == "object class":
            return [self.current_class_id]
        relationship_class = self.db_mngr.get_item(self.db_map, "relationship class", self.current_class_id)
        return [int(id_) for id_ in relationship_class["object_class_id_list"].split(",")]

    def current_object_class_name_list(self):
        if self.current_class_type == "object class":
            return [self.db_mngr.get_item(self.db_map, "object class", self.current_class_id)["name"]]
        relationship_class = self.db_mngr.get_item(self.db_map, "relationship class", self.current_class_id)
        return fix_name_ambiguity(relationship_class["object_class_name_list"].split(","))

    @staticmethod
    def _is_class_index(index, class_type):
        """Returns whether or not the given tree index is a class index.

        Args:
            index (QModelIndex): index from object or relationship tree
            class_type (str)
        Returns:
            bool
        """
        return index.column() == 0 and index.model().item_from_index(index).item_type == class_type

    @Slot(bool)
    def _handle_pivot_table_visibility_changed(self, visible):
        if visible:
            self.reload_pivot_table()
            self.reload_frozen_table()
            self.ui.dockWidget_frozen_table.setVisible(True)

    @Slot(bool)
    def _handle_frozen_table_visibility_changed(self, visible):
        if visible:
            self.ui.dockWidget_pivot_table.show()

    @Slot("QItemSelection", "QItemSelection")
    def _handle_entity_tree_selection_changed(self, selected, deselected):
        if self.ui.dockWidget_pivot_table.isVisible():
            self.reload_pivot_table()
            self.reload_frozen_table()

    def _get_entities(self, class_id=None, class_type=None):
        """Returns a list of dict items from the object or relationship tree model
        corresponding to the given class id.

        Args:
            class_id (int)
            class_type (str)

        Returns:
            list(dict)
        """
        if class_id is None:
            class_id = self.current_class_id
        if class_type is None:
            class_type = self.current_class_type
        model = {"object class": self.object_tree_model, "relationship class": self.relationship_tree_model}[class_type]
        class_item = next(model.root_item.find_children_by_id(self.db_map, class_id))
        if class_item.can_fetch_more():
            class_item.fetch_more()
            model.layoutChanged.emit()
        return [
            item.db_map_data(self.db_map) for item in class_item.find_children_by_id(self.db_map, True, reverse=False)
        ]

    def load_empty_relationship_data(self, objects_per_class=None):
        """Returns a dict containing all possible relationships in the current class.

        Args:
            objects_per_class (dict)

        Returns:
            dict: Key is object id tuple, value is None.
        """
        if objects_per_class is None:
            objects_per_class = dict()
        if self.current_class_type == "object class":
            return {}
        object_id_sets = []
        for obj_cls_id in self.current_object_class_id_list():
            objects = objects_per_class.get(obj_cls_id, None)
            if objects is None:
                objects = self._get_entities(obj_cls_id, "object class")
            id_set = {item["id"]: None for item in objects}
            object_id_sets.append(list(id_set.keys()))
        return dict.fromkeys(product(*object_id_sets))

    def load_full_relationship_data(self, relationships=None, action="add"):
        """Returns a dict of relationships in the current class.

        Returns:
            dict: Key is object id tuple, value is relationship id.
        """
        if self.current_class_type == "object class":
            return {}
        if relationships is None:
            relationships = self._get_entities()
        if action == "add":
            get_id = lambda x: x["id"]
        else:
            get_id = lambda x: None
        return {tuple(int(id_) for id_ in x["object_id_list"].split(',')): get_id(x) for x in relationships}

    def load_relationship_data(self):
        """Returns a dict that merges empty and full relationship data.

        Returns:
            dict: Key is object id tuple, value is True if a relationship exists, False otherwise.
        """
        data = self.load_empty_relationship_data()
        data.update(self.load_full_relationship_data())
        return data

    def _get_parameter_value_or_def_ids(self, item_type):
        """Returns a set of integer ids from the parameter model
        corresponding to the currently selected class and the given item type.

        Args:
            item_type (str): either "parameter value" or "parameter definition"

        Returns:
            set(int)
        """
        entity_class = self.db_mngr.get_item(self.db_map, self.current_class_type, self.current_class_id)
        model = {
            "object class": {
                "parameter value": self.object_parameter_value_model,
                "parameter definition": self.object_parameter_definition_model,
            },
            "relationship class": {
                "parameter value": self.relationship_parameter_value_model,
                "parameter definition": self.relationship_parameter_definition_model,
            },
        }[self.current_class_type][item_type]
        sub_models = [
            m for m in model.single_models if (m.db_map, m.entity_class_id) == (self.db_map, entity_class["id"])
        ]
        if not sub_models:
            return []
        for m in sub_models:
            if m.canFetchMore():
                model._fetch_sub_model = m
                model.fetchMore()
        return {id_ for m in sub_models for id_ in m._main_data}

    def _get_parameter_values_or_defs(self, item_type):
        """Returns a list of dict items from the parameter model
        corresponding to the currently selected class and the given item type.

        Args:
            item_type (str): either "parameter value" or "parameter definition"

        Returns:
            list(dict)
        """
        ids = self._get_parameter_value_or_def_ids(item_type)
        return [self.db_mngr.get_item(self.db_map, item_type, id_) for id_ in ids]

    def load_empty_parameter_value_data(self, entities=None, parameter_ids=None):
        """Returns a dict containing all possible combinations of entities and parameters for the current class.

        Args:
            entities (list, optional): if given, only load data for these entities
            parameter_ids (set, optional): if given, only load data for these parameter definitions

        Returns:
            dict: Key is a tuple object_id, ..., parameter_id, value is None.
        """
        if entities is None:
            entities = self._get_entities()
        if parameter_ids is None:
            parameter_ids = self._get_parameter_value_or_def_ids("parameter definition")
        if self.current_class_type == "relationship class":
            entity_ids = [tuple(int(id_) for id_ in e["object_id_list"].split(',')) for e in entities]
        else:
            entity_ids = [(e["id"],) for e in entities]
        if not entity_ids:
            entity_ids = [tuple(None for _ in self.current_object_class_id_list())]
        if not parameter_ids:
            parameter_ids = [None]
        return {entity_id + (parameter_id,): None for entity_id in entity_ids for parameter_id in parameter_ids}

    def load_expanded_parameter_value_data(self, entities=None, parameter_definition_ids=None):
        """
        Returns all permutations of entities as well as parameter indexes and values for the current class.

        Args:
            entities (list, optional): if given, only load data for these entities
            parameter_definition_ids (set, optional): if given, only load data for these parameter definitions

        Returns:
            dict: Key is a tuple object_id, ..., index, while value is None.
        """
        if entities is None:
            entities = self._get_entities()
        if self.current_class_type == "relationship class":
            entity_ids = [tuple(int(id_) for id_ in e["object_id_list"].split(",")) for e in entities]
        else:
            entity_ids = [(e["id"],) for e in entities]
        if not entity_ids:
            entity_ids = [tuple(None for _ in self.current_object_class_id_list())]
        if parameter_definition_ids is None:
            parameter_definition_ids = self._get_parameter_value_or_def_ids("parameter definition")
        value_ids = self._get_parameter_value_or_def_ids("parameter value")
        # Collecting date time indexes and values separately to facilitate plotting.
        # Other index types are converted to strings.
        (
            date_time_indexes,
            date_time_data,
            other_indexes,
            other_data,
            value_id_to_entity_and_definition,
        ) = _collect_indexes_and_values(entity_ids, value_ids, parameter_definition_ids, self.db_mngr, self.db_map)
        date_time_indexes = list(date_time_indexes)
        date_time_indexes.sort()
        sorted_date_time_values = _fill_gaps_by_nones(date_time_indexes, date_time_data)
        other_indexes = list(other_indexes)
        other_indexes.sort()
        sorted_other_values = _fill_gaps_by_nones(other_indexes, other_data)
        expanded_indexes = date_time_indexes + other_indexes
        expanded_values = _combine_date_time_and_other_values(
            len(date_time_indexes),
            sorted_date_time_values,
            len(other_indexes),
            sorted_other_values,
            value_ids,
            value_id_to_entity_and_definition,
        )
        missing_values = _expand_entities_without_values(
            expanded_values, entity_ids, len(expanded_indexes), parameter_definition_ids
        )
        expanded_values.update(missing_values)
        return {
            entity_id + (index, definition_id): value
            for entity_id in entity_ids
            for definition_id in parameter_definition_ids
            for value, index in zip(expanded_values[entity_id][definition_id], expanded_indexes)
        }

    def load_full_parameter_value_data(self, parameter_values=None, action="add"):
        """Returns a dict of parameter values for the current class.

        Args:
            parameter_values (list, optional)
            action (str)

        Returns:
            dict: Key is a tuple object_id, ..., parameter_id, value is the parameter value.
        """
        if parameter_values is None:
            parameter_values = self._get_parameter_values_or_defs("parameter value")
        if action == "add":
            get_id = lambda x: x["id"]
        else:
            get_id = lambda x: None
        if self.current_class_type == "object class":
            return {(x["object_id"], x["parameter_id"]): get_id(x) for x in parameter_values}
        return {
            tuple(int(id_) for id_ in x["object_id_list"].split(',')) + (x["parameter_id"],): get_id(x)
            for x in parameter_values
        }

    def load_parameter_value_data(self):
        """Returns a dict that merges empty and full parameter value data.

        Returns:
            dict: Key is a tuple object_id, ..., parameter_id, value is the parameter value or None if not specified.
        """
        data = self.load_empty_parameter_value_data()
        if self.current_input_type != self._INDEX_EXPANSION:
            data.update(self.load_full_parameter_value_data())
        return data

    def get_pivot_preferences(self, selection_key):
        """Returns saved or default pivot preferences.

        Args:
            selection_key (tuple(int,str,str)): Tuple of class id, class type, and input type.

        Returns
            list: indexes in rows
            list: indexes in columns
            list: frozen indexes
            tuple: selection in frozen table
        """
        if selection_key in self.class_pivot_preferences:
            # get previously used pivot
            rows = self.class_pivot_preferences[selection_key].index
            columns = self.class_pivot_preferences[selection_key].columns
            frozen = self.class_pivot_preferences[selection_key].frozen
            frozen_value = self.class_pivot_preferences[selection_key].frozen_value
        else:
            # use default pivot
            length = len(self.current_object_class_id_list())
            rows = list(range(length))
            if self.current_input_type == self._INDEX_EXPANSION:
                rows.append(IndexId.PARAMETER_INDEX)
            columns = (
                [IndexId.PARAMETER] if self.current_input_type in (self._PARAMETER_VALUE, self._INDEX_EXPANSION) else []
            )
            frozen = []
            frozen_value = ()
        return rows, columns, frozen, frozen_value

    @Slot(str)
    def reload_pivot_table(self, text=""):
        """Updates current class (type and id) and reloads pivot table for it."""
        if self._selection_source == self.ui.treeView_object:
            selected = self.ui.treeView_object.selectionModel().currentIndex()
            class_type = "object class"
        elif self._selection_source == self.ui.treeView_relationship:
            selected = self.ui.treeView_relationship.selectionModel().currentIndex()
            class_type = "relationship class"
        else:
            return
        if self._is_class_index(selected, class_type):
            self.current_class_type = class_type
            selected_item = selected.model().item_from_index(selected)
            self.current_class_id = selected_item.db_map_id(self.db_map)
            if self.current_class_id is not None:
                self.do_reload_pivot_table()

    @busy_effect
    def do_reload_pivot_table(self):
        """Reloads pivot table.
        """
        self.current_input_type = self.ui.comboBox_pivot_table_input_type.currentText()
        if self.current_input_type == self._RELATIONSHIP and self.current_class_type != "relationship class":
            self.clear_pivot_table()
            return
        length = len(self.current_object_class_id_list())
        index_ids = tuple(range(length))
        if self.current_input_type == self._PARAMETER_VALUE:
            data = self.load_parameter_value_data()
            index_ids += (IndexId.PARAMETER,)
        elif self.current_input_type == self._INDEX_EXPANSION:
            data = self.load_expanded_parameter_value_data()
            index_ids += (IndexId.PARAMETER_INDEX, IndexId.PARAMETER)
        else:
            data = self.load_relationship_data()
        # get pivot preference for current selection
        selection_key = (self.current_class_id, self.current_class_type, self.current_input_type)
        rows, columns, frozen, frozen_value = self.get_pivot_preferences(selection_key)
        self.wipe_out_filter_menus()
        self.pivot_table_model.reset_model(data, index_ids, rows, columns, frozen, frozen_value)
        self.pivot_table_proxy.clear_filter()
        if self.current_input_type == self._INDEX_EXPANSION:
            x_column = self.pivot_table_model.headerColumnCount() - 1
            self.pivot_table_model.set_plot_x_column(x_column, is_x=True)

    def clear_pivot_table(self):
        self.wipe_out_filter_menus()
        self.pivot_table_model.clear_model()
        self.pivot_table_proxy.clear_filter()

    def wipe_out_filter_menus(self):
        while self.filter_menus:
            _, menu = self.filter_menus.popitem()
            menu.wipe_out()

    @Slot()
    def make_pivot_headers(self):
        """
        Turns top left indexes in the pivot table into TabularViewHeaderWidget.
        """
        top_indexes, left_indexes = self.pivot_table_model.top_left_indexes()
        for index in left_indexes:
            proxy_index = self.pivot_table_proxy.mapFromSource(index)
            widget = self.create_header_widget(proxy_index.data(Qt.DisplayRole), "columns")
            self.ui.pivot_table.setIndexWidget(proxy_index, widget)
        for index in top_indexes:
            proxy_index = self.pivot_table_proxy.mapFromSource(index)
            widget = self.create_header_widget(proxy_index.data(Qt.DisplayRole), "rows")
            self.ui.pivot_table.setIndexWidget(proxy_index, widget)
        # TODO: find out why we need two processEvents here
        qApp.processEvents()  # pylint: disable=undefined-variable
        qApp.processEvents()  # pylint: disable=undefined-variable
        self.ui.pivot_table.resizeColumnsToContents()

    def make_frozen_headers(self):
        """
        Turns indexes in the first row of the frozen table into TabularViewHeaderWidget.
        """
        for column in range(self.frozen_table_model.columnCount()):
            index = self.frozen_table_model.index(0, column)
            widget = self.create_header_widget(index.data(Qt.DisplayRole), "frozen", with_menu=False)
            self.ui.frozen_table.setIndexWidget(index, widget)
            self.ui.frozen_table.horizontalHeader().resizeSection(column, widget.size().width())

    def create_filter_menu(self, identifier):
        """Returns a filter menu for given given object class identifier.

        Args:
            identifier (int)

        Returns:
            TabularViewFilterMenu
        """

        def object_id_to_name(id_):
            return self.db_mngr.get_field(self.db_map, "object", id_, "name")

        def parameter_id_to_name(id_):
            return self.db_mngr.get_field(self.db_map, "parameter definition", id_, "parameter_name")

        def parameter_index_to_value(index):
            return str(index)

        if identifier not in self.filter_menus:
            if identifier == IndexId.PARAMETER:
                data_to_value = parameter_id_to_name
            elif identifier == IndexId.PARAMETER_INDEX:
                data_to_value = parameter_index_to_value
            else:
                data_to_value = object_id_to_name
            self.filter_menus[identifier] = menu = TabularViewFilterMenu(
                self, identifier, data_to_value, show_empty=False
            )
            index_values = dict.fromkeys(self.pivot_table_model.model.index_values.get(identifier, []))
            index_values.pop(None, None)
            menu.set_filter_list(index_values.keys())
            menu.filterChanged.connect(self.change_filter)
        return self.filter_menus[identifier]

    def create_header_widget(self, identifier, area, with_menu=True):
        """
        Returns a TabularViewHeaderWidget for given object class identifier.

        Args:
            identifier (int)
            area (str)
            with_menu (bool)

        Returns:
            TabularViewHeaderWidget
        """
        if with_menu:
            menu = self.create_filter_menu(identifier)
        else:
            menu = None
        if identifier == IndexId.PARAMETER:
            name = self._PARAMETER
        elif identifier == IndexId.PARAMETER_INDEX:
            name = self._INDEX
        else:
            name = self.current_object_class_name_list()[identifier]
        widget = TabularViewHeaderWidget(identifier, name, area, menu=menu, parent=self)
        widget.header_dropped.connect(self.handle_header_dropped)
        return widget

    @staticmethod
    def _get_insert_index(pivot_list, catcher, position):
        """Returns an index for inserting a new element in the given pivot list.

        Returns:
            int
        """
        if isinstance(catcher, TabularViewHeaderWidget):
            i = pivot_list.index(catcher.identifier)
            if position == "after":
                i += 1
        else:
            i = 0
        return i

    @Slot(object, object, str)
    def handle_header_dropped(self, dropped, catcher, position=""):
        """
        Updates pivots when a header is dropped.

        Args:
            dropped (TabularViewHeaderWidget)
            catcher (TabularViewHeaderWidget, PivotTableHeaderView, FrozenTableView)
            position (str): either "before", "after", or ""
        """
        top_indexes, left_indexes = self.pivot_table_model.top_left_indexes()
        rows = [index.data(Qt.DisplayRole) for index in top_indexes]
        columns = [index.data(Qt.DisplayRole) for index in left_indexes]
        frozen = self.frozen_table_model.headers
        dropped_list = {"columns": columns, "rows": rows, "frozen": frozen}[dropped.area]
        catcher_list = {"columns": columns, "rows": rows, "frozen": frozen}[catcher.area]
        dropped_list.remove(dropped.identifier)
        i = self._get_insert_index(catcher_list, catcher, position)
        catcher_list.insert(i, dropped.identifier)
        if dropped.area == "frozen" or catcher.area == "frozen":
            if frozen:
                frozen_values = self.find_frozen_values(frozen)
                self.frozen_table_model.reset_model(frozen_values, frozen)
                self.make_frozen_headers()
                self.ui.frozen_table.resizeColumnsToContents()
            else:
                self.frozen_table_model.clear_model()
        frozen_value = self.get_frozen_value(self.ui.frozen_table.currentIndex())
        self.pivot_table_model.set_pivot(rows, columns, frozen, frozen_value)
        # save current pivot
        self.class_pivot_preferences[
            (self.current_class_id, self.current_class_type, self.current_input_type)
        ] = self.PivotPreferences(rows, columns, frozen, frozen_value)
        self.make_pivot_headers()

    def get_frozen_value(self, index):
        """
        Returns the value in the frozen table corresponding to the given index.

        Args:
            index (QModelIndex)
        Returns:
            tuple
        """
        if not index.isValid():
            return tuple(None for _ in range(self.frozen_table_model.columnCount()))
        return self.frozen_table_model.row(index)

    @Slot("QModelIndex", "QModelIndex")
    def change_frozen_value(self, current, previous):
        """Sets the frozen value from selection in frozen table.
        """
        frozen_value = self.get_frozen_value(current)
        self.pivot_table_model.set_frozen_value(frozen_value)
        # store pivot preferences
        self.class_pivot_preferences[
            (self.current_class_id, self.current_class_type, self.current_input_type)
        ] = self.PivotPreferences(
            self.pivot_table_model.model.pivot_rows,
            self.pivot_table_model.model.pivot_columns,
            self.pivot_table_model.model.pivot_frozen,
            self.pivot_table_model.model.frozen_value,
        )

    @Slot(int, set, bool)
    def change_filter(self, identifier, valid_values, has_filter):
        if has_filter:
            self.pivot_table_proxy.set_filter(identifier, valid_values)
        else:
            self.pivot_table_proxy.set_filter(identifier, None)  # None means everything passes

    def reload_frozen_table(self):
        """Resets the frozen model according to new selection in entity trees."""
        frozen = self.pivot_table_model.model.pivot_frozen
        frozen_value = self.pivot_table_model.model.frozen_value
        frozen_values = self.find_frozen_values(frozen)
        self.frozen_table_model.reset_model(frozen_values, frozen)
        self.make_frozen_headers()
        if frozen_value in frozen_values:
            # update selected row
            ind = frozen_values.index(frozen_value)
            self.ui.frozen_table.selectionModel().blockSignals(True)  # prevent selectionChanged signal when updating
            self.ui.frozen_table.selectRow(ind)
            self.ui.frozen_table.selectionModel().blockSignals(False)
        else:
            # frozen value not found, remove selection
            self.ui.frozen_table.selectionModel().blockSignals(True)  # prevent selectionChanged signal when updating
            self.ui.frozen_table.clearSelection()
            self.ui.frozen_table.selectionModel().blockSignals(False)
        self.ui.frozen_table.resizeColumnsToContents()

    def find_frozen_values(self, frozen):
        """Returns a list of tuples containing unique values (object ids) for the frozen indexes (object class ids).

        Args:
            frozen (tuple(int)): A tuple of currently frozen indexes
        Returns:
            list(tuple(list(int)))
        """
        return list(dict.fromkeys(zip(*[self.pivot_table_model.model.index_values.get(k, []) for k in frozen])).keys())

    @staticmethod
    def refresh_table_view(table_view):
        top_left = table_view.indexAt(table_view.rect().topLeft())
        bottom_right = table_view.indexAt(table_view.rect().bottomRight())
        if not bottom_right.isValid():
            model = table_view.model()
            bottom_right = table_view.model().index(model.rowCount() - 1, model.columnCount() - 1)
        table_view.model().dataChanged.emit(top_left, bottom_right)

    @staticmethod
    def _group_by_class(items, get_class_id):
        d = dict()
        for item in items:
            d.setdefault(get_class_id(item), []).append(item)
        return d

    def receive_data_added_or_removed(self, data, action):
        if action == "add":
            self.pivot_table_model.add_to_model(data)
        elif action == "remove":
            self.pivot_table_model.remove_from_model(data)
        for identifier, menu in self.filter_menus.items():
            index_values = dict.fromkeys(self.pivot_table_model.model.index_values.get(identifier, []))
            index_values.pop(None, None)
            if action == "add":
                menu.add_items_to_filter_list(list(index_values.keys()))
            elif action == "remove":
                previous = menu._filter._filter_model._data_set
                menu.remove_items_from_filter_list(list(previous - index_values.keys()))
        self.reload_frozen_table()

    def receive_objects_added_or_removed(self, db_map_data, action):
        items = db_map_data.get(self.db_map, set())
        if self.current_input_type == self._RELATIONSHIP and self.current_class_type == "relationship class":
            objects_per_class = self._group_by_class(items, lambda x: x["class_id"])
            if not set(objects_per_class.keys()).intersection(self.current_object_class_id_list()):
                return
            data = self.load_empty_relationship_data(objects_per_class=objects_per_class)
            self.receive_data_added_or_removed(data, action)
        elif self.current_input_type == self._PARAMETER_VALUE and self.current_class_type == "object class":
            objects = [x for x in items if x["class_id"] == self.current_class_id]
            if not objects:
                return
            data = self.load_empty_parameter_value_data(entities=objects)
            self.receive_data_added_or_removed(data, action)

    def receive_relationships_added_or_removed(self, db_map_data, action):
        items = db_map_data.get(self.db_map, set())
        if self.current_class_type != "relationship class":
            return
        relationships = [x for x in items if x["class_id"] == self.current_class_id]
        if not relationships:
            return
        if self.current_input_type == self._RELATIONSHIP:
            data = self.load_full_relationship_data(relationships=relationships, action=action)
            self.pivot_table_model.update_model(data)
            self.refresh_table_view(self.ui.pivot_table)
        elif self.current_input_type == self._PARAMETER_VALUE:
            data = self.load_empty_parameter_value_data(relationships)
            self.receive_data_added_or_removed(data, action)

    def receive_parameter_definitions_added_or_removed(self, db_map_data, action):
        items = db_map_data.get(self.db_map, set())
        if self.current_input_type != self._PARAMETER_VALUE:
            return
        parameters = [
            x for x in items if (x.get("object_class_id") or x.get("relationship_class_id")) == self.current_class_id
        ]
        if not parameters:
            return
        parameter_ids = {x["id"] for x in parameters}
        data = self.load_empty_parameter_value_data(parameter_ids=parameter_ids)
        self.receive_data_added_or_removed(data, action)

    def receive_parameter_values_added_or_removed(self, db_map_data, action):
        items = db_map_data.get(self.db_map, set())
        if self.current_input_type != self._PARAMETER_VALUE:
            return
        parameter_values = [
            x for x in items if (x.get("object_class_id") or x.get("relationship_class_id")) == self.current_class_id
        ]
        if not parameter_values:
            return
        data = self.load_full_parameter_value_data(parameter_values=parameter_values, action=action)
        self.pivot_table_model.update_model(data)
        self.refresh_table_view(self.ui.pivot_table)

    def receive_db_map_data_updated(self, db_map_data, get_class_id):
        items = db_map_data.get(self.db_map, set())
        for item in items:
            if get_class_id(item) == self.current_class_id:
                self.refresh_table_view(self.ui.pivot_table)
                self.refresh_table_view(self.ui.frozen_table)
                self.make_pivot_headers()
                break

    def receive_classes_removed(self, db_map_data):
        items = db_map_data.get(self.db_map, set())
        for item in items:
            if item["id"] == self.current_class_id:
                self.current_class_type = None
                self.current_class_id = None
                self.clear_pivot_table()
                break

    def receive_objects_added(self, db_map_data):
        """Reacts to objects added event."""
        super().receive_objects_added(db_map_data)
        self.receive_objects_added_or_removed(db_map_data, action="add")

    def receive_relationships_added(self, db_map_data):
        """Reacts to relationships added event."""
        super().receive_relationships_added(db_map_data)
        self.receive_relationships_added_or_removed(db_map_data, action="add")

    def receive_parameter_definitions_added(self, db_map_data):
        """Reacts to parameter definitions added event."""
        super().receive_parameter_definitions_added(db_map_data)
        self.receive_parameter_definitions_added_or_removed(db_map_data, action="add")

    def receive_parameter_values_added(self, db_map_data):
        """Reacts to parameter values added event."""
        super().receive_parameter_values_added(db_map_data)
        self.receive_parameter_values_added_or_removed(db_map_data, action="add")

    def receive_object_classes_updated(self, db_map_data):
        """Reacts to object classes updated event."""
        super().receive_object_classes_updated(db_map_data)
        self.receive_db_map_data_updated(db_map_data, get_class_id=lambda x: x["id"])

    def receive_objects_updated(self, db_map_data):
        """Reacts to objects updated event."""
        super().receive_objects_updated(db_map_data)
        self.receive_db_map_data_updated(db_map_data, get_class_id=lambda x: x["class_id"])

    def receive_relationship_classes_updated(self, db_map_data):
        """Reacts to relationship classes updated event."""
        super().receive_relationship_classes_updated(db_map_data)
        self.receive_db_map_data_updated(db_map_data, get_class_id=lambda x: x["id"])

    def receive_relationships_updated(self, db_map_data):
        """Reacts to relationships updated event."""
        super().receive_relationships_updated(db_map_data)
        self.receive_db_map_data_updated(db_map_data, get_class_id=lambda x: x["class_id"])

    def receive_parameter_values_updated(self, db_map_data):
        """Reacts to parameter values added event."""
        super().receive_parameter_values_updated(db_map_data)
        self.receive_db_map_data_updated(
            db_map_data, get_class_id=lambda x: x.get("object_class_id") or x.get("relationship_class_id")
        )

    def receive_parameter_definitions_updated(self, db_map_data):
        """Reacts to parameter definitions updated event."""
        super().receive_parameter_definitions_updated(db_map_data)
        self.receive_db_map_data_updated(
            db_map_data, get_class_id=lambda x: x.get("object_class_id") or x.get("relationship_class_id")
        )

    def receive_object_classes_removed(self, db_map_data):
        """Reacts to object classes removed event."""
        super().receive_object_classes_removed(db_map_data)
        self.receive_classes_removed(db_map_data)

    def receive_objects_removed(self, db_map_data):
        """Reacts to objects removed event."""
        super().receive_objects_removed(db_map_data)
        self.receive_objects_added_or_removed(db_map_data, action="remove")

    def receive_relationship_classes_removed(self, db_map_data):
        """Reacts to relationship classes remove event."""
        super().receive_relationship_classes_removed(db_map_data)
        self.receive_classes_removed(db_map_data)

    def receive_relationships_removed(self, db_map_data):
        """Reacts to relationships removed event."""
        super().receive_relationships_removed(db_map_data)
        self.receive_relationships_added_or_removed(db_map_data, action="remove")

    def receive_parameter_definitions_removed(self, db_map_data):
        """Reacts to parameter definitions removed event."""
        super().receive_parameter_definitions_removed(db_map_data)
        self.receive_parameter_definitions_added_or_removed(db_map_data, action="remove")

    def receive_parameter_values_removed(self, db_map_data):
        """Reacts to parameter values removed event."""
        super().receive_parameter_values_removed(db_map_data)
        self.receive_parameter_values_added_or_removed(db_map_data, action="remove")

    def receive_session_rolled_back(self, db_maps):
        """Reacts to session rolled back event."""
        super().receive_session_rolled_back(db_maps)
        self.reload_pivot_table()
        self.reload_frozen_table()


def _collect_indexes_and_values(entity_ids, value_ids, parameter_definition_ids, db_mngr, db_map):
    """
    Collects parameter indexes and values for expansion.

    Args:
        entity_ids (list): collect data from entities with these ids.
        value_ids (set): a set of parameter or parameter definition ids
        parameter_definition_ids (set): load data only for these parameter definition ids
        db_mngr (SpineDBManager): a database manager
        db_map (spinedb_api.DatabaseMapping): a database mapping

    Returns:
        tuple: date time and other indexes and values
            as well as mapping from value id to entity and parameter definition id.
    """
    date_time_indexes = set()
    date_time_data = dict()
    other_indexes = set()
    other_data = dict()
    value_id_to_entity_and_definition = dict()
    for id_ in value_ids:
        value_item = db_mngr.get_item(db_map, "parameter value", id_)
        if "object_id" in value_item:
            value_entity_id = (value_item["object_id"],)
        else:
            value_entity_id = tuple(int(object_id) for object_id in value_item["object_id_list"].split(","))
        value_definition_id = value_item["parameter_id"]
        if value_definition_id not in parameter_definition_ids or value_entity_id not in entity_ids:
            continue
        value_id_to_entity_and_definition[id_] = (value_entity_id, value_definition_id)
        parameter_value = db_mngr.get_value(db_map, "parameter value", id_, "value", role=EDITOR_ROLE)
        if isinstance(parameter_value, ParameterValueFormatError):
            other_indexes.add("")
            other_data[id_] = {"": "Error"}
        elif isinstance(parameter_value, TimeSeries):
            date_time_data[id_] = {i: float(v) for i, v in zip(parameter_value.indexes, parameter_value.values)}
            date_time_indexes |= set(parameter_value.indexes)
        elif isinstance(parameter_value, Map):
            indexes, values = _expand_map(parameter_value)
            other_indexes |= indexes
            other_data[id_] = values
        elif isinstance(parameter_value, IndexedValue):
            other_data[id_] = {i: float(v) for i, v in zip(parameter_value.indexes, parameter_value.values)}
            other_indexes |= set(parameter_value.indexes)
        else:
            other_indexes.add("")
            other_data[id_] = {"": parameter_value}
    return date_time_indexes, date_time_data, other_indexes, other_data, value_id_to_entity_and_definition


def _expand_map(map_to_expand, preceding_indexes=None):
    """
    Expands map indexes and values iteratively.

    Args:
        map_to_expand (spinedb_api.Map): a map to expand.
        preceding_indexes (list): a list of indexes indexing a nested map

    Return:
        tuple of set and dict: a set of map's indexes as comma-separated strings and a dict mapping each index string
            to the corresponding scalar value
    """
    current_indexes = map_to_expand.indexes
    if not current_indexes:
        return []
    if preceding_indexes is None:
        preceding_indexes = list()
    indexes = set()
    values = dict()
    for index, value in zip(current_indexes, map_to_expand.values):
        index_list = preceding_indexes + [index]
        if isinstance(value, Map):
            nested_indexes, nested_values = _expand_map(value, index_list)
            indexes |= nested_indexes
            values.update(nested_values)
        else:
            index_as_string = ", ".join(index_list)
            indexes.add(index_as_string)
            values[index_as_string] = value
    return indexes, values


def _fill_gaps_by_nones(indexes, data):
    """
    Makes value lists correspond to the full index lists by inserting Nones where a value is missing.

    Args:
        indexes (list): a list of indexes
        data (dict): a map from parameter or parameter definition id to a mapping from index to value.

    Returns:
        dict: a map from parameter or parameter definition id to a list of values
    """
    return {id_: [indexes_and_values.get(i) for i in indexes] for id_, indexes_and_values in data.items()}


def _combine_date_time_and_other_values(
    date_time_count,
    sorted_date_time_values,
    other_count,
    sorted_other_values,
    value_ids,
    value_id_to_entity_and_definition,
):
    """
    Combines the date time and other value lists filling missing data by Nones.

    Args:
        date_time_count (int): number of date time indexes
        sorted_date_time_values (dict): a map from value ids to gap-filled value lists
        other_count (int): number of other indexes
        sorted_other_values (dict): a map from value id to gap-filled value lists
        value_ids (set): a set of parameter or parameter definition ids
        value_id_to_entity_and_definition (dict): a map from value id to entity id and parameter definition id

    Returns:
        dict: a map from value id to full list of parameter values
    """
    expanded_values = dict()
    empty_date_time_values = date_time_count * [None]
    empty_other_values = other_count * [None]
    for id_ in value_ids:
        identifiers = value_id_to_entity_and_definition.get(id_)
        if identifiers is None:
            continue
        entity_id = identifiers[0]
        definition_id = identifiers[1]
        expandeds = expanded_values.setdefault(entity_id, dict())
        expandeds[definition_id] = sorted_date_time_values.get(id_, empty_date_time_values) + sorted_other_values.get(
            id_, empty_other_values
        )
    return expanded_values


def _expand_entities_without_values(expanded_values, entity_ids, index_count, parameter_definition_ids):
    """
    'Expands' non-existent values to null values.

    Args:
        expanded_values (dict): expanded data
        entity_ids (set): a set of entity ids
        index_count (int): number of expanded indexes
        parameter_definition_ids (set): a set of parameter definition ids

    Returns:
        dict: a map from entity ids to value dictionaries
    """
    expanded_empty = dict()
    for entity_id in entity_ids:
        if entity_id not in expanded_values:
            missing = dict()
            for definition_id in parameter_definition_ids:
                missing[definition_id] = index_count * [None]
            expanded_empty[entity_id] = missing
    return expanded_empty
