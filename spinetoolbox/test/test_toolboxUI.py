######################################################################################################################
# Copyright (C) 2017 - 2019 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Unit tests for ToolboxUI class.

:author: P. Savolainen (VTT)
:date:   22.8.2018
"""

import unittest
from unittest import mock
import logging
import os
import sys
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtCore import SIGNAL, Qt, QPoint
from PySide2.QtTest import QTest
from ..ui_main import ToolboxUI
from ..project import SpineToolboxProject
from .mock_helpers import MockQWidget, qsettings_value_side_effect
from ..config import APPLICATION_PATH
from ..graphics_items import ProjectItemIcon, Link
from ..project_item import RootProjectItem


# noinspection PyUnusedLocal,DuplicatedCode
class TestToolboxUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Overridden method. Runs once before all tests in this class."""
        try:
            cls.app = QApplication().processEvents()
        except RuntimeError:
            pass
        logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    def setUp(self):
        """Overridden method. Runs before each test. Makes an instance of ToolboxUI class
        without opening previous project."""
        with mock.patch("spinetoolbox.ui_main.JuliaREPLWidget") as mock_julia_repl, mock.patch(
            "spinetoolbox.ui_main.PythonReplWidget"
        ) as mock_python_repl, mock.patch("spinetoolbox.ui_main.QSettings.value") as mock_qsettings_value:
            # Replace Julia and Python REPLs with a QWidget so that the DeprecationWarning from qtconsole is not printed
            mock_julia_repl.return_value = QWidget()
            mock_python_repl.return_value = MockQWidget()  # Hack, because QWidget does not have test_push_vars()
            mock_qsettings_value.side_effect = qsettings_value_side_effect  # override 'open previous project' setting
            self.toolbox = ToolboxUI()

    def tearDown(self):
        """Overridden method. Runs after each test.
        Use this to free resources after a test if needed.
        """
        self.toolbox.deleteLater()
        self.toolbox = None

    def test_init_project_item_model_without_project(self):
        """Test that a new project item model contains 4 items (Data Stores, Data Connections, Tools, and Views).
        Note: This test is done WITHOUT a project open.
        """
        self.assertIsNone(self.toolbox.project())  # Make sure that there is no project open
        self.toolbox.init_project_item_model()
        self.check_init_project_item_model()

    def test_init_project_item_model_with_project(self):
        """Test that project item model is initialized successfully.
        Note: This test is done WITH a project.
        Mock save_project() and create_dir() so that .proj file and project directory (and work directory) are
        not actually created.
        """
        with mock.patch("spinetoolbox.ui_main.ToolboxUI.save_project") as mock_save_project, mock.patch(
            "spinetoolbox.project.create_dir"
        ) as mock_create_dir:
            self.toolbox.create_project("UnitTest Project", "Project for unit tests.")
        self.assertIsInstance(self.toolbox.project(), SpineToolboxProject)  # Check that a project is open
        self.toolbox.init_project_item_model()
        self.check_init_project_item_model()

    def check_init_project_item_model(self):
        """Checks that category items are created as expected."""
        n = self.toolbox.project_item_model.rowCount()
        # Data Stores, Data Connections, Tools, Views, Data Interfaces, Exporting
        self.assertEqual(n, 6)
        # Check that there's only one column
        self.assertEqual(self.toolbox.project_item_model.columnCount(), 1)
        # Check that the items DisplayRoles are (In this particular order)
        item1 = self.toolbox.project_item_model.root().child(0)
        self.assertTrue(item1.name == "Data Stores", "Item on row 0 is not 'Data Stores'")
        self.assertTrue(
            isinstance(item1.parent(), RootProjectItem), "Parent item of category item on row 0 should be root"
        )
        item2 = self.toolbox.project_item_model.root().child(1)
        self.assertTrue(item2.name == "Data Connections", "Item on row 1 is not 'Data Connections'")
        self.assertTrue(
            isinstance(item2.parent(), RootProjectItem), "Parent item of category item on row 1 should be root"
        )
        item3 = self.toolbox.project_item_model.root().child(2)
        self.assertTrue(item3.name == "Tools", "Item on row 2 is not 'Tools'")
        self.assertTrue(
            isinstance(item3.parent(), RootProjectItem), "Parent item of category item on row 2 should be root"
        )
        item4 = self.toolbox.project_item_model.root().child(3)
        self.assertTrue(item4.name == "Views", "Item on row 3 is not 'Views'")
        self.assertTrue(
            isinstance(item4.parent(), RootProjectItem), "Parent item of category item on row 3 should be root"
        )
        item5 = self.toolbox.project_item_model.root().child(4)
        self.assertTrue(item5.name == "Data Interfaces", "Item on row 4 is not 'Data Interfaces'")
        self.assertTrue(
            isinstance(item5.parent(), RootProjectItem), "Parent item of category item on row 4 should be root"
        )
        item6 = self.toolbox.project_item_model.root().child(5)
        self.assertTrue(item6.name == "Data Exporters", "Item on row 5 is not 'Data Exporters'")
        self.assertTrue(
            isinstance(item6.parent(), RootProjectItem), "Parent item of category item on row 5 should be root"
        )

    def test_init_tool_template_model(self):
        """Check that tool template model has no items after init and that
        signals are connected just once.
        """
        self.assertIsNone(self.toolbox.project())  # Make sure that there is no project open
        self.toolbox.init_tool_template_model(list())
        self.assertEqual(self.toolbox.tool_template_model.rowCount(), 0)
        # Test that QLisView signals are connected only once.
        n_dbl_clicked_recv = self.toolbox.ui.listView_tool_templates.receivers(SIGNAL("doubleClicked(QModelIndex)"))
        self.assertEqual(n_dbl_clicked_recv, 1)
        n_context_menu_recv = self.toolbox.ui.listView_tool_templates.receivers(
            SIGNAL("customContextMenuRequested(QPoint)")
        )
        self.assertEqual(n_context_menu_recv, 1)
        # Initialize ToolTemplateModel again and see that the signals are connected only once
        self.toolbox.init_tool_template_model(list())
        # Test that QLisView signals are connected only once.
        n_dbl_clicked_recv = self.toolbox.ui.listView_tool_templates.receivers(SIGNAL("doubleClicked(QModelIndex)"))
        self.assertEqual(n_dbl_clicked_recv, 1)
        n_context_menu_recv = self.toolbox.ui.listView_tool_templates.receivers(
            SIGNAL("customContextMenuRequested(QPoint)")
        )
        self.assertEqual(n_context_menu_recv, 1)
        # Check that there's still no items in the model
        self.assertEqual(self.toolbox.tool_template_model.rowCount(), 0)

    def test_create_project(self):
        """Test that create_project method makes a SpineToolboxProject instance.
        Skips creating a .proj file and creating directories.
        """
        with mock.patch("spinetoolbox.ui_main.ToolboxUI.save_project") as mock_save_project, mock.patch(
            "spinetoolbox.project.create_dir"
        ) as mock_create_dir:
            self.toolbox.create_project("UnitTest Project", "Project for unit tests.")
        self.assertIsInstance(self.toolbox.project(), SpineToolboxProject)  # Check that a project is open

    def test_open_project(self):
        """Test that opening a project file works.
        The project should contain four items. Data Store 'a',
        Data Connection 'b', Tool 'c', and View 'd'. The items are connected
        a->b->c->d.
        """
        test_project_path = os.path.join(APPLICATION_PATH, "test", "project_files", "unit_test_project.proj")
        if not os.path.exists(test_project_path):
            self.skipTest("Test project file not found in path:'{0}'".format(test_project_path))
            return
        self.assertIsNone(self.toolbox.project())
        with mock.patch("spinetoolbox.ui_main.ToolboxUI.save_project") as mock_save_project, mock.patch(
            "spinetoolbox.project.create_dir"
        ) as mock_create_dir, mock.patch("spinetoolbox.project_item.create_dir") as mock_create_dir:
            self.toolbox.open_project(test_project_path)
        self.assertIsInstance(self.toolbox.project(), SpineToolboxProject)
        # Check that project contains four items
        self.assertEqual(self.toolbox.project_item_model.n_items(), 4)
        # Check that design view has three links
        links = self.toolbox.ui.graphicsView.links()
        self.assertEqual(len(links), 3)
        # Check project items have the right links
        index_a = self.toolbox.project_item_model.find_item("a")
        item_a = self.toolbox.project_item_model.project_item(index_a)
        icon_a = item_a.get_icon()
        links_a = [link for conn in icon_a.connectors.values() for link in conn.links]
        index_b = self.toolbox.project_item_model.find_item("b")
        item_b = self.toolbox.project_item_model.project_item(index_b)
        icon_b = item_b.get_icon()
        links_b = [link for conn in icon_b.connectors.values() for link in conn.links]
        index_c = self.toolbox.project_item_model.find_item("c")
        item_c = self.toolbox.project_item_model.project_item(index_c)
        icon_c = item_c.get_icon()
        links_c = [link for conn in icon_c.connectors.values() for link in conn.links]
        index_d = self.toolbox.project_item_model.find_item("d")
        item_d = self.toolbox.project_item_model.project_item(index_d)
        icon_d = item_d.get_icon()
        links_d = [link for conn in icon_d.connectors.values() for link in conn.links]
        self.assertEqual(len(links_a), 1)
        self.assertEqual(links_a[0].src_connector._parent, icon_a)
        self.assertEqual(links_a[0].dst_connector._parent, icon_b)
        self.assertEqual(len(links_b), 2)
        self.assertTrue(links_a[0] in links_b)
        links_b.remove(links_a[0])
        self.assertEqual(links_b[0].src_connector._parent, icon_b)
        self.assertEqual(links_b[0].dst_connector._parent, icon_c)
        self.assertEqual(len(links_c), 2)
        self.assertTrue(links_b[0] in links_c)
        links_c.remove(links_b[0])
        self.assertEqual(links_c[0].src_connector._parent, icon_c)
        self.assertEqual(links_c[0].dst_connector._parent, icon_d)
        self.assertEqual(len(links_d), 1)
        self.assertEqual(links_c[0], links_d[0])
        # Check that DAG graph is correct
        dag_hndlr = self.toolbox.project().dag_handler
        self.assertTrue(len(dag_hndlr.dags()) == 1)  # Only one graph
        g = dag_hndlr.dags()[0]
        self.assertTrue(len(g.nodes()) == 4)  # graph has four nodes
        self.assertTrue(len(g.edges()) == 3)  # graph has three edges
        self.assertTrue(g.has_node("a"))
        self.assertTrue(g.has_node("b"))
        self.assertTrue(g.has_node("c"))
        self.assertTrue(g.has_node("d"))
        self.assertTrue(g.has_edge("a", "b"))
        self.assertTrue(g.has_edge("b", "c"))
        self.assertTrue(g.has_edge("c", "d"))

    def test_selection_in_project_item_list_1(self):
        """Test item selection in treeView_project. Simulates a mouse click on a Data Store item
        in the project Tree View widget (i.e. the project item list).
        """
        with mock.patch("spinetoolbox.ui_main.ToolboxUI.save_project") as mock_save_project, \
                mock.patch("spinetoolbox.project.create_dir") as mock_create_dir:
            self.toolbox.create_project("UnitTest Project", "")
        # self.toolbox.create_project("UnitTest Project", "")
        ds1 = "DS1"
        self.add_ds(ds1)
        n_items = self.toolbox.project_item_model.n_items()
        self.assertEqual(n_items, 1)  # Check that the project contains one item
        ds_ind = self.toolbox.project_item_model.find_item(ds1)
        tv = self.toolbox.ui.treeView_project
        tv.expandAll()  # NOTE: mouseClick does not work without this
        tv_sm = tv.selectionModel()
        # Scroll to item -> get rectangle -> click
        tv.scrollTo(ds_ind)  # Make sure the item is 'visible'
        ds1_rect = tv.visualRect(ds_ind)
        # logging.debug("viewport geometry:{0}".format(tv.viewport().geometry()))  # this is pos() and size() combined
        # logging.debug("item rect:{0}".format(ds1_rect))
        # Simulate mouse click on selected item
        QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, ds1_rect.center())
        self.assertTrue(tv_sm.isSelected(ds_ind))
        self.assertEqual(tv_sm.currentIndex(), ds_ind)
        self.assertEqual(1, len(tv_sm.selectedIndexes()))
        # Active project item should be DS1
        self.assertEqual(self.toolbox.project_item_model.project_item(ds_ind), self.toolbox.active_project_item)

    def test_selection_in_project_item_list_2(self):
        """Test item selection in treeView_project. Simulates mouse clicks on a Data Store items.
        Click on a project item and then on another project item.
        """
        self.toolbox.create_project("UnitTest Project", "")
        ds1 = "DS1"
        ds2 = "DS2"
        self.add_ds(ds1)
        self.add_ds(ds2)
        n_items = self.toolbox.project_item_model.n_items()
        self.assertEqual(n_items, 2)
        ds1_ind = self.toolbox.project_item_model.find_item(ds1)
        ds2_ind = self.toolbox.project_item_model.find_item(ds2)
        tv = self.toolbox.ui.treeView_project
        tv.expandAll()
        tv_sm = tv.selectionModel()
        # Scroll to item -> get rectangle -> click
        tv.scrollTo(ds1_ind)
        ds1_rect = tv.visualRect(ds1_ind)
        QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, ds1_rect.center())
        # Scroll to item -> get rectangle -> click
        tv.scrollTo(ds2_ind)
        ds2_rect = tv.visualRect(ds2_ind)
        QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.NoModifier, ds2_rect.center())
        self.assertTrue(tv_sm.isSelected(ds2_ind))
        self.assertEqual(tv_sm.currentIndex(), ds2_ind)
        self.assertEqual(1, len(tv_sm.selectedIndexes()))
        # Active project item should be DS2
        self.assertEqual(self.toolbox.project_item_model.project_item(ds2_ind), self.toolbox.active_project_item)

    def test_selection_in_project_item_list_3(self):
        """Test item selection in treeView_project. Simulates mouse clicks on a Data Store items.
        Test multiple selection (Ctrl-pressed) with two Data Store items.
        """
        self.toolbox.create_project("UnitTest Project", "")
        ds1 = "DS1"
        ds2 = "DS2"
        self.add_ds(ds1)
        self.add_ds(ds2)
        n_items = self.toolbox.project_item_model.n_items()
        self.assertEqual(n_items, 2)
        ds1_ind = self.toolbox.project_item_model.find_item(ds1)
        ds2_ind = self.toolbox.project_item_model.find_item(ds2)
        tv = self.toolbox.ui.treeView_project
        tv.expandAll()
        tv_sm = tv.selectionModel()
        # Scroll to item -> get rectangle -> click
        tv.scrollTo(ds1_ind)
        ds1_rect = tv.visualRect(ds1_ind)
        QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.ControlModifier, ds1_rect.center())
        # Scroll to item -> get rectangle -> click
        tv.scrollTo(ds2_ind)
        ds2_rect = tv.visualRect(ds2_ind)
        QTest.mouseClick(tv.viewport(), Qt.LeftButton, Qt.ControlModifier, ds2_rect.center())
        # Both items should be selected and current item should be DS2
        self.assertTrue(tv_sm.isSelected(ds1_ind))
        self.assertTrue(tv_sm.isSelected(ds2_ind))
        self.assertEqual(tv_sm.currentIndex(), ds2_ind)
        self.assertEqual(2, len(tv_sm.selectedIndexes()))
        # There should also be 2 items selected in the Design View
        n_selected_items_in_design_view = len(self.toolbox.ui.graphicsView.scene().selectedItems())
        self.assertEqual(2, n_selected_items_in_design_view)
        # Active project item should be None
        self.assertIsNone(self.toolbox.active_project_item)

    def test_selection_in_design_view_1(self):
        """Test item selection in Design View. Simulates mouse click on a Data Connection item.
        Test a single item selection.
        """
        self.toolbox.create_project("UnitTest Project", "")
        dc1 = "DC1"
        self.add_dc(dc1, x=0, y=0)
        n_items = self.toolbox.project_item_model.n_items()
        self.assertEqual(n_items, 1)  # Check that the project contains one item
        dc1_index = self.toolbox.project_item_model.find_item(dc1)
        gv = self.toolbox.ui.graphicsView
        dc1_item = self.toolbox.project_item_model.project_item(dc1_index)
        dc1_center_point = self.find_click_point_of_pi(dc1_item, gv)  # Center point in graphics view viewport coords.
        # Simulate mouse click on Data Connection in Design View
        QTest.mouseClick(gv.viewport(), Qt.LeftButton, Qt.NoModifier, dc1_center_point)
        tv_sm = self.toolbox.ui.treeView_project.selectionModel()
        self.assertTrue(tv_sm.isSelected(dc1_index))
        self.assertEqual(dc1_index, tv_sm.currentIndex())
        self.assertEqual(1, len(tv_sm.selectedIndexes()))
        self.assertEqual(1, len(gv.scene().selectedItems()))
        # Active project item should be DC1
        self.assertEqual(self.toolbox.project_item_model.project_item(dc1_index), self.toolbox.active_project_item)

    def test_selection_in_design_view_2(self):
        """Test item selection in Design View.
        First mouse click on project item. Second mouse click on a project item.
        """
        self.toolbox.create_project("UnitTest Project", "")
        dc1 = "DC1"
        dc2 = "DC2"
        self.add_dc(dc1, x=0, y=0)
        self.add_dc(dc2, x=100, y=100)
        n_items = self.toolbox.project_item_model.n_items()
        self.assertEqual(n_items, 2)  # Check the number of project items
        dc1_index = self.toolbox.project_item_model.find_item(dc1)
        dc2_index = self.toolbox.project_item_model.find_item(dc2)
        gv = self.toolbox.ui.graphicsView
        dc1_item = self.toolbox.project_item_model.project_item(dc1_index)
        dc2_item = self.toolbox.project_item_model.project_item(dc2_index)
        dc1_center_point = self.find_click_point_of_pi(dc1_item, gv)
        dc2_center_point = self.find_click_point_of_pi(dc2_item, gv)
        # Mouse click on dc1
        QTest.mouseClick(gv.viewport(), Qt.LeftButton, Qt.NoModifier, dc1_center_point)
        # Then mouse click on dc2
        QTest.mouseClick(gv.viewport(), Qt.LeftButton, Qt.NoModifier, dc2_center_point)
        tv_sm = self.toolbox.ui.treeView_project.selectionModel()
        self.assertTrue(tv_sm.isSelected(dc2_index))
        self.assertEqual(dc2_index, tv_sm.currentIndex())
        self.assertEqual(1, len(tv_sm.selectedIndexes()))
        self.assertEqual(1, len(gv.scene().selectedItems()))
        # Active project item should be DC2
        self.assertEqual(self.toolbox.project_item_model.project_item(dc2_index), self.toolbox.active_project_item)

    def test_selection_in_design_view_3(self):
        """Test item selection in Design View.
        First mouse click on project item. Second mouse click on design view.
        """
        self.toolbox.create_project("UnitTest Project", "")
        dc1 = "DC1"
        self.add_dc(dc1, x=0, y=0)
        dc1_index = self.toolbox.project_item_model.find_item(dc1)
        gv = self.toolbox.ui.graphicsView
        dc1_item = self.toolbox.project_item_model.project_item(dc1_index)
        dc1_center_point = self.find_click_point_of_pi(dc1_item, gv)
        # Mouse click on dc1
        QTest.mouseClick(gv.viewport(), Qt.LeftButton, Qt.NoModifier, dc1_center_point)
        # Then mouse click somewhere else in Design View (not on project item)
        QTest.mouseClick(gv.viewport(), Qt.LeftButton, Qt.NoModifier, QPoint(1, 1))
        # Treeview current index should be dc1_index
        tv_sm = self.toolbox.ui.treeView_project.selectionModel()
        self.assertEqual(dc1_index, tv_sm.currentIndex())
        self.assertEqual(0, len(tv_sm.selectedIndexes()))  # No items in pi list should be selected
        self.assertEqual(0, len(gv.scene().selectedItems()))  # No items in design view should be selected
        # Active project item should be None
        self.assertIsNone(self.toolbox.active_project_item)

    def test_selection_in_design_view_4(self):
        """Test item selection in Design View.
        Mouse click on a link. Check that Link is selected.
        """
        self.toolbox.create_project("UnitTest Project", "")
        dc1 = "DC1"
        dc2 = "DC2"
        self.add_dc(dc1, x=0, y=0)
        self.add_dc(dc2, x=100, y=100)
        n_items = self.toolbox.project_item_model.n_items()
        self.assertEqual(n_items, 2)  # Check the number of project items
        dc1_index = self.toolbox.project_item_model.find_item(dc1)
        dc2_index = self.toolbox.project_item_model.find_item(dc2)
        gv = self.toolbox.ui.graphicsView
        dc1_item = self.toolbox.project_item_model.project_item(dc1_index)
        dc2_item = self.toolbox.project_item_model.project_item(dc2_index)
        # Add link between dc1 and dc2
        gv.add_link(dc1_item.get_icon().conn_button("bottom"), dc2_item.get_icon().conn_button("bottom"))
        # Find link
        dc1_links = dc1_item.get_icon().conn_button("bottom").links
        dc2_links = dc2_item.get_icon().conn_button("bottom").links
        self.assertEqual(dc1_links, dc2_links)
        links = dc2_links
        self.assertEqual(1, len(links))
        link_center_point = self.find_click_point_of_link(links[0], gv)
        # Mouse click on link
        QTest.mouseClick(gv.viewport(), Qt.LeftButton, Qt.NoModifier, link_center_point)
        tv_sm = self.toolbox.ui.treeView_project.selectionModel()
        # Check that dc1 is NOT selected
        self.assertFalse(tv_sm.isSelected(dc1_index))
        # Check that dc2 is NOT selected
        self.assertFalse(tv_sm.isSelected(dc2_index))
        # No items should be selected in the tree view
        self.assertEqual(0, len(tv_sm.selectedIndexes()))
        # One item should be selected in Design View (the Link)
        selected_items = gv.scene().selectedItems()
        self.assertEqual(1, len(selected_items))
        # The Link item should be selected in Design View
        self.assertIsInstance(selected_items[0], Link)
        # Active project item should be None
        self.assertIsNone(self.toolbox.active_project_item)

    @unittest.skip("Reveals bug in issue #339")
    def test_selection_in_design_view_5(self):
        """Test item selection in Design View.
        First mouse click on project item, then mouse click on a Link.
        """
        self.toolbox.create_project("UnitTest Project", "")
        dc1 = "DC1"
        dc2 = "DC2"
        self.add_dc(dc1, x=0, y=0)
        self.add_dc(dc2, x=100, y=100)
        n_items = self.toolbox.project_item_model.n_items()
        self.assertEqual(n_items, 2)  # Check the number of project items
        dc1_index = self.toolbox.project_item_model.find_item(dc1)
        dc2_index = self.toolbox.project_item_model.find_item(dc2)
        gv = self.toolbox.ui.graphicsView
        dc1_item = self.toolbox.project_item_model.project_item(dc1_index)
        dc2_item = self.toolbox.project_item_model.project_item(dc2_index)
        # Add link between dc1 and dc2
        gv.add_link(dc1_item.get_icon().conn_button("bottom"), dc2_item.get_icon().conn_button("bottom"))
        # Find link
        dc1_links = dc1_item.get_icon().conn_button("bottom").links
        dc2_links = dc2_item.get_icon().conn_button("bottom").links
        self.assertEqual(dc1_links, dc2_links)
        links = dc2_links
        self.assertEqual(1, len(links))
        dc1_center_point = self.find_click_point_of_pi(dc1_item, gv)
        link_center_point = self.find_click_point_of_link(links[0], gv)
        # Mouse click on dc1
        QTest.mouseClick(gv.viewport(), Qt.LeftButton, Qt.NoModifier, dc1_center_point)
        # Mouse click on link
        QTest.mouseClick(gv.viewport(), Qt.LeftButton, Qt.NoModifier, link_center_point)
        tv_sm = self.toolbox.ui.treeView_project.selectionModel()
        # Check that dc1 is NOT selected
        self.assertFalse(tv_sm.isSelected(dc1_index))
        # Check that dc2 is NOT selected
        self.assertFalse(tv_sm.isSelected(dc2_index))
        # No items should be selected in the tree view
        self.assertEqual(0, len(tv_sm.selectedIndexes()))
        # One item should be selected in Design View (the Link)
        selected_items = gv.scene().selectedItems()
        self.assertEqual(1, len(selected_items))
        # The Link item should be selected in Design View
        self.assertIsInstance(selected_items[0], Link)
        # Active project item should be None
        self.assertIsNone(self.toolbox.active_project_item)

    def test_selection_in_design_view_6(self):
        """Test multiple item selection in Design View.
        First mouse click on project item (Ctrl-key pressed).
        Second mouse click on a project item (Ctrl-key pressed).
        """
        self.toolbox.create_project("UnitTest Project", "")
        dc1 = "DC1"
        dc2 = "DC2"
        self.add_dc(dc1, x=0, y=0)
        self.add_dc(dc2, x=100, y=100)
        n_items = self.toolbox.project_item_model.n_items()
        self.assertEqual(n_items, 2)  # Check the number of project items
        dc1_index = self.toolbox.project_item_model.find_item(dc1)
        dc2_index = self.toolbox.project_item_model.find_item(dc2)
        gv = self.toolbox.ui.graphicsView
        dc1_item = self.toolbox.project_item_model.project_item(dc1_index)
        dc2_item = self.toolbox.project_item_model.project_item(dc2_index)
        dc1_center_point = self.find_click_point_of_pi(dc1_item, gv)
        dc2_center_point = self.find_click_point_of_pi(dc2_item, gv)
        # Mouse click on dc1
        QTest.mouseClick(gv.viewport(), Qt.LeftButton, Qt.ControlModifier, dc1_center_point)
        # Then mouse click on dc2
        QTest.mouseClick(gv.viewport(), Qt.LeftButton, Qt.ControlModifier, dc2_center_point)
        tv_sm = self.toolbox.ui.treeView_project.selectionModel()
        self.assertEqual(2, len(tv_sm.selectedIndexes()))
        self.assertTrue(tv_sm.isSelected(dc1_index))
        self.assertTrue(tv_sm.isSelected(dc2_index))
        # NOTE: No test for tv_sm current index here!
        self.assertEqual(2, len(gv.scene().selectedItems()))
        # Active project item should be None
        self.assertIsNone(self.toolbox.active_project_item)

    def test_remove_item(self):
        """Test removing a single project item."""
        self.toolbox.create_project("UnitTest Project", "")
        dc1 = "DC1"
        self.add_dc(dc1)
        dc1_index = self.toolbox.project_item_model.find_item(dc1)
        # Check the size of project item model
        n_items = self.toolbox.project_item_model.n_items()
        self.assertEqual(n_items, 1)
        # Check DAG handler
        dags = self.toolbox.project().dag_handler.dags()
        self.assertEqual(1, len(dags))  # Number of DAGs (DiGraph objects) in project
        self.assertEqual(1, len(dags[0].nodes()))  # Number of nodes in the DiGraph
        # Check number of items in Design View
        items_in_design_view = self.toolbox.ui.graphicsView.scene().items()
        n_items_in_design_view = len([item for item in items_in_design_view if isinstance(item, ProjectItemIcon)])
        self.assertEqual(n_items_in_design_view, 1)
        # NOW REMOVE DC1
        self.toolbox.remove_item(dc1_index, delete_item=False)
        self.assertEqual(self.toolbox.project_item_model.n_items(), 0)  # Check the number of project items
        dags = self.toolbox.project().dag_handler.dags()
        self.assertEqual(0, len(dags))  # Number of DAGs (DiGraph) objects in project
        items_in_design_view = self.toolbox.ui.graphicsView.scene().items()
        n_items_in_design_view = len([item for item in items_in_design_view if isinstance(item, ProjectItemIcon)])
        self.assertEqual(n_items_in_design_view, 0)

    @unittest.skip("TODO")
    def test_add_tool_template(self):
        self.fail()

    @unittest.skip("TODO")
    def test_remove_tool_template(self):
        self.fail()

    def add_ds(self, name, x=0, y=0):
        """Helper method to create a Data Store with the given name and coordinates."""
        item = dict(name=name, description="", url=dict(), x=x, y=y)
        # TODO: Mocking create_dir does not work here since DataStore class was moved to project_items directory
        with mock.patch("spinetoolbox.project_item.create_dir") as mock_create_dir:
            self.toolbox.project().add_project_items("Data Stores", item)
        return

    def add_dc(self, name, x=0, y=0):
        """Helper method to create a Data Connection with the given name and coordinates."""
        item = dict(name=name, description="", references=list(), x=x, y=y)
        with mock.patch("spinetoolbox.project_item.create_dir") as mock_create_dir:
            self.toolbox.project().add_project_items("Data Connections", item)
        return

    @staticmethod
    def find_click_point_of_pi(pi, gv):
        """Maps given project item icons center coordinates to given Graphics View viewport coordinates.

        Args:
            pi (ProjectItem): Project item to process
            gv (QGraphicsView): View that contains the scene where the project item icon is shown

        Returns:
            (QPoint): Center point of the project item icon in graphics view viewport coordinates.
        """
        # We need to map item coordinates to scene coordinates to graphics view viewport coordinates
        # Get project item icon rectangle
        qrectf = pi.get_icon().rect()  # Returns a rectangle in item coordinate system
        # Map project item icon rectangle center point to scene coordinates
        qpointf = pi.get_icon().mapToScene(qrectf.center())  # Returns a point in scene coordinate system
        # Map scene coordinates to graphics view viewport coordinates
        qpoint = gv.mapFromScene(qpointf)  # Returns a point in Graphics view viewport coordinate system
        return qpoint

    @staticmethod
    def find_click_point_of_link(link, gv):
        """Maps given Link icons center coordinates to given Graphics View viewport coordinates.

        Args:
            link (QGraphicsPathItem): Link to process
            gv (QGraphicsView): Graphics View containing the scene that displays the link

        Returns:
            (QPoint): Center point of the Link in graphics view viewport coordinates.
        """
        # We need to map item coordinates to scene coordinates to graphics view viewport coordinates
        # Get project item icon rectangle
        qrectf = link.boundingRect()  # Returns a rectangle in item coordinate system
        # Map project item icon rectangle center point to scene coordinates
        qpointf = link.mapToScene(qrectf.center())  # Returns a point in scene coordinate system
        # Map scene coordinates to graphics view viewport coordinates
        qpoint = gv.mapFromScene(qpointf)  # Returns a point in Graphics view viewport coordinate system
        return qpoint


if __name__ == '__main__':
    unittest.main()
