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

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../spinetoolbox/ui/tree_view_form.ui',
# licensing of '../spinetoolbox/ui/tree_view_form.ui' applies.
#
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1077, 774)
        MainWindow.setLayoutDirection(QtCore.Qt.LeftToRight)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowNestedDocks|QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks|QtWidgets.QMainWindow.GroupedDragging)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_object_tree = QtWidgets.QLabel(self.centralwidget)
        self.label_object_tree.setObjectName("label_object_tree")
        self.verticalLayout_2.addWidget(self.label_object_tree)
        self.treeView_object = ObjectTreeView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView_object.sizePolicy().hasHeightForWidth())
        self.treeView_object.setSizePolicy(sizePolicy)
        self.treeView_object.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView_object.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed)
        self.treeView_object.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.treeView_object.setIconSize(QtCore.QSize(20, 20))
        self.treeView_object.setObjectName("treeView_object")
        self.verticalLayout_2.addWidget(self.treeView_object)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1077, 21))
        self.menubar.setNativeMenuBar(False)
        self.menubar.setObjectName("menubar")
        self.menuSession = QtWidgets.QMenu(self.menubar)
        self.menuSession.setObjectName("menuSession")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuToolbars = QtWidgets.QMenu(self.menuView)
        self.menuToolbars.setObjectName("menuToolbars")
        self.menuDock_Widgets = QtWidgets.QMenu(self.menuView)
        self.menuDock_Widgets.setObjectName("menuDock_Widgets")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget_parameter_value_list = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget_parameter_value_list.setObjectName("dockWidget_parameter_value_list")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeView_parameter_value_list = CopyTreeView(self.dockWidgetContents)
        self.treeView_parameter_value_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView_parameter_value_list.setEditTriggers(QtWidgets.QAbstractItemView.AnyKeyPressed|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.treeView_parameter_value_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.treeView_parameter_value_list.setObjectName("treeView_parameter_value_list")
        self.verticalLayout.addWidget(self.treeView_parameter_value_list)
        self.dockWidget_parameter_value_list.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_parameter_value_list)
        self.dockWidget_relationship_parameter_value = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget_relationship_parameter_value.setObjectName("dockWidget_relationship_parameter_value")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.tableView_relationship_parameter_value = AutoFilterCopyPasteTableView(self.dockWidgetContents_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_relationship_parameter_value.sizePolicy().hasHeightForWidth())
        self.tableView_relationship_parameter_value.setSizePolicy(sizePolicy)
        self.tableView_relationship_parameter_value.setMouseTracking(True)
        self.tableView_relationship_parameter_value.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView_relationship_parameter_value.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tableView_relationship_parameter_value.setTabKeyNavigation(False)
        self.tableView_relationship_parameter_value.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableView_relationship_parameter_value.setSortingEnabled(False)
        self.tableView_relationship_parameter_value.setWordWrap(False)
        self.tableView_relationship_parameter_value.setObjectName("tableView_relationship_parameter_value")
        self.tableView_relationship_parameter_value.horizontalHeader().setHighlightSections(False)
        self.tableView_relationship_parameter_value.verticalHeader().setVisible(False)
        self.tableView_relationship_parameter_value.verticalHeader().setHighlightSections(False)
        self.verticalLayout_5.addWidget(self.tableView_relationship_parameter_value)
        self.dockWidget_relationship_parameter_value.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_relationship_parameter_value)
        self.dockWidget_object_parameter_value = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget_object_parameter_value.setObjectName("dockWidget_object_parameter_value")
        self.dockWidgetContents_3 = QtWidgets.QWidget()
        self.dockWidgetContents_3.setObjectName("dockWidgetContents_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tableView_object_parameter_value = AutoFilterCopyPasteTableView(self.dockWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_object_parameter_value.sizePolicy().hasHeightForWidth())
        self.tableView_object_parameter_value.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.tableView_object_parameter_value.setFont(font)
        self.tableView_object_parameter_value.setMouseTracking(True)
        self.tableView_object_parameter_value.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView_object_parameter_value.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tableView_object_parameter_value.setTabKeyNavigation(False)
        self.tableView_object_parameter_value.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableView_object_parameter_value.setSortingEnabled(False)
        self.tableView_object_parameter_value.setWordWrap(False)
        self.tableView_object_parameter_value.setObjectName("tableView_object_parameter_value")
        self.tableView_object_parameter_value.horizontalHeader().setHighlightSections(False)
        self.tableView_object_parameter_value.verticalHeader().setVisible(False)
        self.tableView_object_parameter_value.verticalHeader().setHighlightSections(False)
        self.tableView_object_parameter_value.verticalHeader().setMinimumSectionSize(20)
        self.verticalLayout_3.addWidget(self.tableView_object_parameter_value)
        self.dockWidget_object_parameter_value.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_object_parameter_value)
        self.dockWidget_object_parameter_definition = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget_object_parameter_definition.setObjectName("dockWidget_object_parameter_definition")
        self.dockWidgetContents_4 = QtWidgets.QWidget()
        self.dockWidgetContents_4.setObjectName("dockWidgetContents_4")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.dockWidgetContents_4)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.tableView_object_parameter_definition = AutoFilterCopyPasteTableView(self.dockWidgetContents_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_object_parameter_definition.sizePolicy().hasHeightForWidth())
        self.tableView_object_parameter_definition.setSizePolicy(sizePolicy)
        self.tableView_object_parameter_definition.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView_object_parameter_definition.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tableView_object_parameter_definition.setTabKeyNavigation(False)
        self.tableView_object_parameter_definition.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableView_object_parameter_definition.setSortingEnabled(False)
        self.tableView_object_parameter_definition.setWordWrap(False)
        self.tableView_object_parameter_definition.setObjectName("tableView_object_parameter_definition")
        self.tableView_object_parameter_definition.horizontalHeader().setHighlightSections(False)
        self.tableView_object_parameter_definition.horizontalHeader().setSortIndicatorShown(False)
        self.tableView_object_parameter_definition.verticalHeader().setVisible(False)
        self.tableView_object_parameter_definition.verticalHeader().setHighlightSections(False)
        self.verticalLayout_8.addWidget(self.tableView_object_parameter_definition)
        self.dockWidget_object_parameter_definition.setWidget(self.dockWidgetContents_4)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_object_parameter_definition)
        self.dockWidget_relationship_parameter_definition = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget_relationship_parameter_definition.setObjectName("dockWidget_relationship_parameter_definition")
        self.dockWidgetContents_5 = QtWidgets.QWidget()
        self.dockWidgetContents_5.setObjectName("dockWidgetContents_5")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.dockWidgetContents_5)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.tableView_relationship_parameter_definition = AutoFilterCopyPasteTableView(self.dockWidgetContents_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView_relationship_parameter_definition.sizePolicy().hasHeightForWidth())
        self.tableView_relationship_parameter_definition.setSizePolicy(sizePolicy)
        self.tableView_relationship_parameter_definition.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView_relationship_parameter_definition.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tableView_relationship_parameter_definition.setTabKeyNavigation(False)
        self.tableView_relationship_parameter_definition.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.tableView_relationship_parameter_definition.setSortingEnabled(False)
        self.tableView_relationship_parameter_definition.setWordWrap(False)
        self.tableView_relationship_parameter_definition.setObjectName("tableView_relationship_parameter_definition")
        self.tableView_relationship_parameter_definition.horizontalHeader().setHighlightSections(False)
        self.tableView_relationship_parameter_definition.verticalHeader().setVisible(False)
        self.tableView_relationship_parameter_definition.verticalHeader().setHighlightSections(False)
        self.verticalLayout_10.addWidget(self.tableView_relationship_parameter_definition)
        self.dockWidget_relationship_parameter_definition.setWidget(self.dockWidgetContents_5)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget_relationship_parameter_definition)
        self.actionCommit = QtWidgets.QAction(MainWindow)
        self.actionCommit.setEnabled(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/ok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCommit.setIcon(icon)
        self.actionCommit.setObjectName("actionCommit")
        self.actionRollback = QtWidgets.QAction(MainWindow)
        self.actionRollback.setEnabled(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/nok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRollback.setIcon(icon1)
        self.actionRollback.setObjectName("actionRollback")
        self.actionClose = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/close.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionClose.setIcon(icon2)
        self.actionClose.setObjectName("actionClose")
        self.actionAdd_object_classes = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/icons/plus_object_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd_object_classes.setIcon(icon3)
        self.actionAdd_object_classes.setObjectName("actionAdd_object_classes")
        self.actionAdd_objects = QtWidgets.QAction(MainWindow)
        self.actionAdd_objects.setIcon(icon3)
        self.actionAdd_objects.setObjectName("actionAdd_objects")
        self.actionAdd_relationship_classes = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/icons/plus_relationship_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd_relationship_classes.setIcon(icon4)
        self.actionAdd_relationship_classes.setObjectName("actionAdd_relationship_classes")
        self.actionAdd_relationships = QtWidgets.QAction(MainWindow)
        self.actionAdd_relationships.setIcon(icon4)
        self.actionAdd_relationships.setObjectName("actionAdd_relationships")
        self.actionImport = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/icons/import_ds.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionImport.setIcon(icon5)
        self.actionImport.setObjectName("actionImport")
        self.actionExport = QtWidgets.QAction(MainWindow)
        self.actionExport.setEnabled(False)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/icons/export_ds.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExport.setIcon(icon6)
        self.actionExport.setObjectName("actionExport")
        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setEnabled(False)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/icons/copy.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCopy.setIcon(icon7)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setEnabled(False)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/icons/paste.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPaste.setIcon(icon8)
        self.actionPaste.setObjectName("actionPaste")
        self.actionRefresh = QtWidgets.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/icons/refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRefresh.setIcon(icon9)
        self.actionRefresh.setObjectName("actionRefresh")
        self.actionEdit_object_classes = QtWidgets.QAction(MainWindow)
        self.actionEdit_object_classes.setEnabled(False)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/icons/edit_object_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEdit_object_classes.setIcon(icon10)
        self.actionEdit_object_classes.setObjectName("actionEdit_object_classes")
        self.actionEdit_relationship_classes = QtWidgets.QAction(MainWindow)
        self.actionEdit_relationship_classes.setEnabled(False)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/icons/edit_relationship_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEdit_relationship_classes.setIcon(icon11)
        self.actionEdit_relationship_classes.setObjectName("actionEdit_relationship_classes")
        self.actionEdit_objects = QtWidgets.QAction(MainWindow)
        self.actionEdit_objects.setEnabled(False)
        self.actionEdit_objects.setIcon(icon10)
        self.actionEdit_objects.setObjectName("actionEdit_objects")
        self.actionEdit_relationships = QtWidgets.QAction(MainWindow)
        self.actionEdit_relationships.setEnabled(False)
        self.actionEdit_relationships.setIcon(icon11)
        self.actionEdit_relationships.setObjectName("actionEdit_relationships")
        self.actionManage_parameter_tags = QtWidgets.QAction(MainWindow)
        self.actionManage_parameter_tags.setObjectName("actionManage_parameter_tags")
        self.actionRemove_selection = QtWidgets.QAction(MainWindow)
        self.actionRemove_selection.setEnabled(False)
        self.actionRemove_selection.setObjectName("actionRemove_selection")
        self.actionRestore_Dock_Widgets = QtWidgets.QAction(MainWindow)
        self.actionRestore_Dock_Widgets.setObjectName("actionRestore_Dock_Widgets")
        self.menuSession.addAction(self.actionRefresh)
        self.menuSession.addAction(self.actionCommit)
        self.menuSession.addAction(self.actionRollback)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionAdd_object_classes)
        self.menuEdit.addAction(self.actionAdd_objects)
        self.menuEdit.addAction(self.actionAdd_relationship_classes)
        self.menuEdit.addAction(self.actionAdd_relationships)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionEdit_object_classes)
        self.menuEdit.addAction(self.actionEdit_objects)
        self.menuEdit.addAction(self.actionEdit_relationship_classes)
        self.menuEdit.addAction(self.actionEdit_relationships)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionRemove_selection)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionManage_parameter_tags)
        self.menuEdit.addSeparator()
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuDock_Widgets.addAction(self.actionRestore_Dock_Widgets)
        self.menuDock_Widgets.addSeparator()
        self.menuView.addAction(self.menuToolbars.menuAction())
        self.menuView.addAction(self.menuDock_Widgets.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuSession.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.treeView_object, self.tableView_object_parameter_value)
        MainWindow.setTabOrder(self.tableView_object_parameter_value, self.tableView_object_parameter_definition)
        MainWindow.setTabOrder(self.tableView_object_parameter_definition, self.tableView_relationship_parameter_value)
        MainWindow.setTabOrder(self.tableView_relationship_parameter_value, self.tableView_relationship_parameter_definition)
        MainWindow.setTabOrder(self.tableView_relationship_parameter_definition, self.treeView_parameter_value_list)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1))
        self.label_object_tree.setText(QtWidgets.QApplication.translate("MainWindow", "Object tree", None, -1))
        self.treeView_object.setAccessibleName(QtWidgets.QApplication.translate("MainWindow", "object tree", None, -1))
        self.menuSession.setTitle(QtWidgets.QApplication.translate("MainWindow", "Session", None, -1))
        self.menuEdit.setTitle(QtWidgets.QApplication.translate("MainWindow", "Edit", None, -1))
        self.menuFile.setTitle(QtWidgets.QApplication.translate("MainWindow", "File", None, -1))
        self.menuView.setTitle(QtWidgets.QApplication.translate("MainWindow", "View", None, -1))
        self.menuToolbars.setTitle(QtWidgets.QApplication.translate("MainWindow", "Toolbars", None, -1))
        self.menuDock_Widgets.setTitle(QtWidgets.QApplication.translate("MainWindow", "Dock Widgets", None, -1))
        self.dockWidget_parameter_value_list.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Parameter value list", None, -1))
        self.treeView_parameter_value_list.setAccessibleName(QtWidgets.QApplication.translate("MainWindow", "parameter value list", None, -1))
        self.dockWidget_relationship_parameter_value.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Relationship parameter value", None, -1))
        self.tableView_relationship_parameter_value.setAccessibleName(QtWidgets.QApplication.translate("MainWindow", "relationship parameter value", None, -1))
        self.dockWidget_object_parameter_value.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Object parameter value", None, -1))
        self.tableView_object_parameter_value.setAccessibleName(QtWidgets.QApplication.translate("MainWindow", "object parameter value", None, -1))
        self.dockWidget_object_parameter_definition.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Object parameter definition", None, -1))
        self.tableView_object_parameter_definition.setAccessibleName(QtWidgets.QApplication.translate("MainWindow", "object parameter definition", None, -1))
        self.dockWidget_relationship_parameter_definition.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "Relationship parameter definition", None, -1))
        self.tableView_relationship_parameter_definition.setAccessibleName(QtWidgets.QApplication.translate("MainWindow", "relationship parameter definition", None, -1))
        self.actionCommit.setText(QtWidgets.QApplication.translate("MainWindow", "Commit", None, -1))
        self.actionCommit.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Return", None, -1))
        self.actionRollback.setText(QtWidgets.QApplication.translate("MainWindow", "Rollback", None, -1))
        self.actionRollback.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Backspace", None, -1))
        self.actionClose.setText(QtWidgets.QApplication.translate("MainWindow", "Close", None, -1))
        self.actionClose.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+W", None, -1))
        self.actionAdd_object_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Add object classes", None, -1))
        self.actionAdd_object_classes.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add object classes", None, -1))
        self.actionAdd_objects.setText(QtWidgets.QApplication.translate("MainWindow", "Add objects", None, -1))
        self.actionAdd_objects.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add objects", None, -1))
        self.actionAdd_relationship_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Add relationship classes", None, -1))
        self.actionAdd_relationship_classes.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add relationship classes", None, -1))
        self.actionAdd_relationships.setText(QtWidgets.QApplication.translate("MainWindow", "Add relationships", None, -1))
        self.actionAdd_relationships.setToolTip(QtWidgets.QApplication.translate("MainWindow", "Add relationships", None, -1))
        self.actionImport.setText(QtWidgets.QApplication.translate("MainWindow", "Import", None, -1))
        self.actionExport.setText(QtWidgets.QApplication.translate("MainWindow", "Export", None, -1))
        self.actionCopy.setText(QtWidgets.QApplication.translate("MainWindow", "Copy", None, -1))
        self.actionCopy.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+C", None, -1))
        self.actionPaste.setText(QtWidgets.QApplication.translate("MainWindow", "Paste", None, -1))
        self.actionPaste.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+V", None, -1))
        self.actionRefresh.setText(QtWidgets.QApplication.translate("MainWindow", "Refresh", None, -1))
        self.actionRefresh.setShortcut(QtWidgets.QApplication.translate("MainWindow", "F5", None, -1))
        self.actionEdit_object_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Edit object classes", None, -1))
        self.actionEdit_relationship_classes.setText(QtWidgets.QApplication.translate("MainWindow", "Edit relationship classes", None, -1))
        self.actionEdit_objects.setText(QtWidgets.QApplication.translate("MainWindow", "Edit objects", None, -1))
        self.actionEdit_relationships.setText(QtWidgets.QApplication.translate("MainWindow", "Edit relationships", None, -1))
        self.actionManage_parameter_tags.setText(QtWidgets.QApplication.translate("MainWindow", "Manage parameter tags", None, -1))
        self.actionRemove_selection.setText(QtWidgets.QApplication.translate("MainWindow", "Remove selection", None, -1))
        self.actionRemove_selection.setShortcut(QtWidgets.QApplication.translate("MainWindow", "Ctrl+Del", None, -1))
        self.actionRestore_Dock_Widgets.setText(QtWidgets.QApplication.translate("MainWindow", "Restore Dock Widgets", None, -1))

from widgets.custom_qtreeview import CopyTreeView, ObjectTreeView
from widgets.custom_qtableview import AutoFilterCopyPasteTableView
import resources_icons_rc
