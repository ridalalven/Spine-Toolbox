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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../spinetoolbox/ui/spine_datapackage_form.ui',
# licensing of '../spinetoolbox/ui/spine_datapackage_form.ui' applies.
#
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(921, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tabWidget_resources = QtWidgets.QTabWidget(self.splitter)
        self.tabWidget_resources.setObjectName("tabWidget_resources")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.treeView_resources = QtWidgets.QTreeView(self.tab)
        self.treeView_resources.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.treeView_resources.setObjectName("treeView_resources")
        self.verticalLayout_2.addWidget(self.treeView_resources)
        self.tabWidget_resources.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget_resources.addTab(self.tab_2, "")
        self.tabWidget_data_schema = QtWidgets.QTabWidget(self.splitter)
        self.tabWidget_data_schema.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget_data_schema.setTabsClosable(False)
        self.tabWidget_data_schema.setObjectName("tabWidget_data_schema")
        self.tab_data = QtWidgets.QWidget()
        self.tab_data.setObjectName("tab_data")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_data)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableView_resource_data = CustomQTableView(self.tab_data)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_resource_data.sizePolicy().hasHeightForWidth())
        self.tableView_resource_data.setSizePolicy(sizePolicy)
        self.tableView_resource_data.setTabKeyNavigation(False)
        self.tableView_resource_data.setObjectName("tableView_resource_data")
        self.tableView_resource_data.horizontalHeader().setVisible(True)
        self.tableView_resource_data.horizontalHeader().setHighlightSections(False)
        self.tableView_resource_data.verticalHeader().setVisible(False)
        self.tableView_resource_data.verticalHeader().setHighlightSections(False)
        self.verticalLayout.addWidget(self.tableView_resource_data)
        self.tabWidget_data_schema.addTab(self.tab_data, "")
        self.tab_schema = QtWidgets.QWidget()
        self.tab_schema.setObjectName("tab_schema")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_schema)
        self.verticalLayout_4.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_fields = QtWidgets.QGroupBox(self.tab_schema)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_fields.sizePolicy().hasHeightForWidth())
        self.groupBox_fields.setSizePolicy(sizePolicy)
        self.groupBox_fields.setObjectName("groupBox_fields")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox_fields)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.treeView_fields = QtWidgets.QTreeView(self.groupBox_fields)
        self.treeView_fields.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.treeView_fields.setObjectName("treeView_fields")
        self.verticalLayout_5.addWidget(self.treeView_fields)
        self.verticalLayout_4.addWidget(self.groupBox_fields)
        self.groupBox_foreign_keys = QtWidgets.QGroupBox(self.tab_schema)
        self.groupBox_foreign_keys.setObjectName("groupBox_foreign_keys")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.groupBox_foreign_keys)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.treeView_foreign_keys = QtWidgets.QTreeView(self.groupBox_foreign_keys)
        self.treeView_foreign_keys.setObjectName("treeView_foreign_keys")
        self.verticalLayout_6.addWidget(self.treeView_foreign_keys)
        self.verticalLayout_4.addWidget(self.groupBox_foreign_keys)
        self.tabWidget_data_schema.addTab(self.tab_schema, "")
        self.verticalLayout_3.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 921, 27))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setToolTipsVisible(True)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave_datapackage = QtWidgets.QAction(MainWindow)
        self.actionSave_datapackage.setObjectName("actionSave_datapackage")
        self.actionExport = QtWidgets.QAction(MainWindow)
        self.actionExport.setObjectName("actionExport")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionInfer_datapackage = QtWidgets.QAction(MainWindow)
        self.actionInfer_datapackage.setObjectName("actionInfer_datapackage")
        self.actionLoad_datapackage = QtWidgets.QAction(MainWindow)
        self.actionLoad_datapackage.setObjectName("actionLoad_datapackage")
        self.menuFile.addAction(self.actionSave_datapackage)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget_resources.setCurrentIndex(0)
        self.tabWidget_data_schema.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Spine datapackage", None, -1))
        self.tabWidget_resources.setTabText(self.tabWidget_resources.indexOf(self.tab), QtWidgets.QApplication.translate("MainWindow", "Resources", None, -1))
        self.tabWidget_resources.setTabText(self.tabWidget_resources.indexOf(self.tab_2), QtWidgets.QApplication.translate("MainWindow", "Tab 2", None, -1))
        self.tabWidget_data_schema.setTabText(self.tabWidget_data_schema.indexOf(self.tab_data), QtWidgets.QApplication.translate("MainWindow", "Data", None, -1))
        self.groupBox_fields.setTitle(QtWidgets.QApplication.translate("MainWindow", "Fields", None, -1))
        self.groupBox_foreign_keys.setTitle(QtWidgets.QApplication.translate("MainWindow", "Foreign keys", None, -1))
        self.tabWidget_data_schema.setTabText(self.tabWidget_data_schema.indexOf(self.tab_schema), QtWidgets.QApplication.translate("MainWindow", "Schema", None, -1))
        self.menuFile.setTitle(QtWidgets.QApplication.translate("MainWindow", "Datapackage", None, -1))
        self.menuHelp.setTitle(QtWidgets.QApplication.translate("MainWindow", "Help", None, -1))
        self.actionSave_datapackage.setText(QtWidgets.QApplication.translate("MainWindow", "Save descriptor", None, -1))
        self.actionSave_datapackage.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Save as \'datapackage.json\'", None, -1))
        self.actionSave_datapackage.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+S", None, -1))
        self.actionExport.setText(QtWidgets.QApplication.translate("MainWindow", "Export to \'Spine.sqlite\'", None, -1))
        self.actionExport.setToolTip(QtWidgets.QApplication.translate("MainWindow", "<html><head/><body><p>Export datapackage as an \'.sqlite\' file in Spine EAV format, to every Data Store connected to the output of this Data Connection.</p></body></html>", None, -1))
        self.actionExport.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+E", None, -1))
        self.actionQuit.setText(QtWidgets.QApplication.translate("MainWindow", "Quit", None, -1))
        self.actionQuit.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Q", None, -1))
        self.actionInfer_datapackage.setText(QtWidgets.QApplication.translate("MainWindow", "Infer from CSV", None, -1))
        self.actionInfer_datapackage.setToolTip(QtWidgets.QApplication.translate("MainWindow", "<html><head/><body><p>Infer datapackage from \'.csv\' files present in this Data Connection\'s directory.</p></body></html>", None, -1))
        self.actionInfer_datapackage.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+I", None, -1))
        self.actionLoad_datapackage.setText(QtWidgets.QApplication.translate("MainWindow", "Load from descriptor", None, -1))
        self.actionLoad_datapackage.setToolTip(QtWidgets.QApplication.translate("MainWindow", "<html><head/><body><p>Load datapackage from a descriptor file called \'datapackage.json\' in this Data Connection\'s directory.</p></body></html>", None, -1))
        self.actionLoad_datapackage.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+L", None, -1))

from widgets.custom_qtableview import CustomQTableView
import resources_icons_rc
