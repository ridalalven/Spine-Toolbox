# -*- coding: utf-8 -*-
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

# Form implementation generated from reading ui file 'C:\data\src\toolbox\bin\..\spinetoolbox\project_items\tool\ui\tool_properties.ui',
# licensing of 'C:\data\src\toolbox\bin\..\spinetoolbox\project_items\tool\ui\tool_properties.ui' applies.
#
# Created: Wed Jan 15 13:11:31 2020
#      by: pyside2-uic  running on PySide2 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(390, 424)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_tool_name = QtWidgets.QLabel(Form)
        self.label_tool_name.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_tool_name.sizePolicy().hasHeightForWidth())
        self.label_tool_name.setSizePolicy(sizePolicy)
        self.label_tool_name.setMinimumSize(QtCore.QSize(0, 20))
        self.label_tool_name.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(50)
        font.setBold(False)
        self.label_tool_name.setFont(font)
        self.label_tool_name.setStyleSheet("background-color: #ecd8c6;")
        self.label_tool_name.setFrameShape(QtWidgets.QFrame.Box)
        self.label_tool_name.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.label_tool_name.setAlignment(QtCore.Qt.AlignCenter)
        self.label_tool_name.setWordWrap(True)
        self.label_tool_name.setObjectName("label_tool_name")
        self.verticalLayout.addWidget(self.label_tool_name)
        self.scrollArea_3 = QtWidgets.QScrollArea(Form)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName("scrollArea_3")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 388, 402))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.verticalLayout_17 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setSpacing(4)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_tool_specification = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_tool_specification.sizePolicy().hasHeightForWidth())
        self.label_tool_specification.setSizePolicy(sizePolicy)
        self.label_tool_specification.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_tool_specification.setFont(font)
        self.label_tool_specification.setObjectName("label_tool_specification")
        self.horizontalLayout_9.addWidget(self.label_tool_specification)
        self.comboBox_tool = QtWidgets.QComboBox(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_tool.sizePolicy().hasHeightForWidth())
        self.comboBox_tool.setSizePolicy(sizePolicy)
        self.comboBox_tool.setObjectName("comboBox_tool")
        self.horizontalLayout_9.addWidget(self.comboBox_tool)
        self.toolButton_tool_specification = QtWidgets.QToolButton(self.scrollAreaWidgetContents_3)
        self.toolButton_tool_specification.setMinimumSize(QtCore.QSize(22, 22))
        self.toolButton_tool_specification.setMaximumSize(QtCore.QSize(22, 22))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/wrench.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_tool_specification.setIcon(icon)
        self.toolButton_tool_specification.setIconSize(QtCore.QSize(16, 16))
        self.toolButton_tool_specification.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.toolButton_tool_specification.setObjectName("toolButton_tool_specification")
        self.horizontalLayout_9.addWidget(self.toolButton_tool_specification)
        self.verticalLayout_17.addLayout(self.horizontalLayout_9)
        self.lineEdit_tool_args = QtWidgets.QLineEdit(self.scrollAreaWidgetContents_3)
        self.lineEdit_tool_args.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lineEdit_tool_args.setFont(font)
        self.lineEdit_tool_args.setCursor(QtCore.Qt.ArrowCursor)
        self.lineEdit_tool_args.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lineEdit_tool_args.setReadOnly(True)
        self.lineEdit_tool_args.setObjectName("lineEdit_tool_args")
        self.verticalLayout_17.addWidget(self.lineEdit_tool_args)
        self.treeView_specification = QtWidgets.QTreeView(self.scrollAreaWidgetContents_3)
        self.treeView_specification.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView_specification.setIndentation(20)
        self.treeView_specification.setUniformRowHeights(True)
        self.treeView_specification.setAnimated(True)
        self.treeView_specification.setObjectName("treeView_specification")
        self.verticalLayout_17.addWidget(self.treeView_specification)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setSpacing(6)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem)
        self.pushButton_tool_results = QtWidgets.QPushButton(self.scrollAreaWidgetContents_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_tool_results.sizePolicy().hasHeightForWidth())
        self.pushButton_tool_results.setSizePolicy(sizePolicy)
        self.pushButton_tool_results.setMinimumSize(QtCore.QSize(75, 23))
        self.pushButton_tool_results.setMaximumSize(QtCore.QSize(75, 23))
        self.pushButton_tool_results.setObjectName("pushButton_tool_results")
        self.horizontalLayout_11.addWidget(self.pushButton_tool_results)
        self.verticalLayout_17.addLayout(self.horizontalLayout_11)
        self.line_4 = QtWidgets.QFrame(self.scrollAreaWidgetContents_3)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.verticalLayout_17.addWidget(self.line_4)
        self.label_2 = QtWidgets.QLabel(self.scrollAreaWidgetContents_3)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_17.addWidget(self.label_2)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.radioButton_execute_in_work = QtWidgets.QRadioButton(self.scrollAreaWidgetContents_3)
        self.radioButton_execute_in_work.setChecked(True)
        self.radioButton_execute_in_work.setObjectName("radioButton_execute_in_work")
        self.horizontalLayout_15.addWidget(self.radioButton_execute_in_work)
        self.radioButton_execute_in_source = QtWidgets.QRadioButton(self.scrollAreaWidgetContents_3)
        self.radioButton_execute_in_source.setObjectName("radioButton_execute_in_source")
        self.horizontalLayout_15.addWidget(self.radioButton_execute_in_source)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_15.addItem(spacerItem1)
        self.toolButton_tool_open_dir = QtWidgets.QToolButton(self.scrollAreaWidgetContents_3)
        self.toolButton_tool_open_dir.setMinimumSize(QtCore.QSize(22, 22))
        self.toolButton_tool_open_dir.setMaximumSize(QtCore.QSize(22, 22))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/menu_icons/folder-open-solid.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_tool_open_dir.setIcon(icon1)
        self.toolButton_tool_open_dir.setObjectName("toolButton_tool_open_dir")
        self.horizontalLayout_15.addWidget(self.toolButton_tool_open_dir)
        self.verticalLayout_17.addLayout(self.horizontalLayout_15)
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)
        self.verticalLayout.addWidget(self.scrollArea_3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.label_tool_name.setText(QtWidgets.QApplication.translate("Form", "Name", None, -1))
        self.label_tool_specification.setText(QtWidgets.QApplication.translate("Form", "Specification", None, -1))
        self.comboBox_tool.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Tool specification for this Tool</p></body></html>", None, -1))
        self.toolButton_tool_specification.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Tool specification options.</p></body></html>", None, -1))
        self.lineEdit_tool_args.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Command line arguments used when starting the main program. Edit Tool specification to modify these.</p></body></html>", None, -1))
        self.lineEdit_tool_args.setPlaceholderText(QtWidgets.QApplication.translate("Form", "Command line arguments", None, -1))
        self.pushButton_tool_results.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Open results archive in file browser</p></body></html>", None, -1))
        self.pushButton_tool_results.setText(QtWidgets.QApplication.translate("Form", "Results...", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Form", "Execute in", None, -1))
        self.radioButton_execute_in_work.setText(QtWidgets.QApplication.translate("Form", "Work directory", None, -1))
        self.radioButton_execute_in_source.setText(QtWidgets.QApplication.translate("Form", "Source directory", None, -1))
        self.toolButton_tool_open_dir.setToolTip(QtWidgets.QApplication.translate("Form", "<html><head/><body><p>Open this Tool\'s project directory in file browser</p></body></html>", None, -1))

from spinetoolbox import resources_icons_rc
