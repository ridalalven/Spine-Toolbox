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
Class for a custom QTextBrowser for showing the logs and tool output.

:author: P. Savolainen (VTT)
:date:   6.2.2018
"""

import logging
from PySide2.QtCore import Slot, Qt
from PySide2.QtGui import QTextCursor, QTextDocument, QTextFrame, QTextFrameFormat, QBrush
from PySide2.QtWidgets import QTextBrowser, QAction
from spinetoolbox.helpers import add_message_to_document
from ..config import TEXTBROWSER_OVERRIDE_SS, TEXTBROWSER_SS


class SignedTextDocument(QTextDocument):
    def __init__(self, owner=""):
        super().__init__()
        self.owner = owner


class CustomQTextBrowser(QTextBrowser):
    """Custom QTextBrowser class."""

    def __init__(self, parent):
        """
        Args:
            parent (QWidget): Parent widget
        """
        super().__init__(parent=parent)
        self._toolbox = None
        self._original_document = SignedTextDocument()
        self.setDocument(self._original_document)
        self.setStyleSheet(TEXTBROWSER_SS)
        self._max_blocks = 2000
        self.setOpenExternalLinks(True)
        self.setOpenLinks(False)  # Don't try open file:/// links in the browser widget, we'll open them externally

    def set_toolbox(self, tb):
        self._toolbox = tb

    def mousePressEvent(self, ev):
        anchor = self.anchorAt(ev.pos())
        print(anchor)
        if not anchor.startswith("log_"):
            return super().mousePressEvent(ev)
        item_name, exec_id = anchor[4:].split(".")
        item = self._toolbox.project_item_model.get_item(item_name).project_item  # Get project item
        if not item:
            self._toolbox.msg_error.emit(f"Showing {item_name} log failed")
            return
        c = self.cursorForPosition(ev.pos())
        if not c.movePosition(QTextCursor.EndOfBlock):
            logging.error(f"Cursor moving failed Could not show log. mouse clicked at:{ev.pos()}")
            return
        item_doc = item.get_event_document(int(exec_id))
        # Compare the first line after anchor and the same first line of the item document, if they match, the document
        # is already shown and we should remove the lines from the main document. If they do not match, append the doc
        if item_doc.firstBlock().text() == "":
            # Remove new line because the first block is a newline for some reason
            logging.debug("Removing new line from item_doc")
            cc = QTextCursor(item_doc)
            cc.setPosition(0)
            cc.deleteChar()
        a = item_doc.firstBlock()
        logging.debug(f"item_doc first block:'{a.text()}'")
        b = c.block().next()  # This is the next block after the log title line
        logging.debug(f"block at cursor:'{b.text()}'")
        child_frames = self.document().rootFrame().childFrames()
        # logging.debug(f"Child frames:{len(child_frames)}. item_doc lineCount:{item_doc.lineCount()}")
        if a.text() == b.text():
            # Remove item document from main document
            logging.debug("Removing frame contents")
            # c = QTextCursor(child_frames[0])
            c.movePosition(QTextCursor.NextBlock)
            self.setTextCursor(c)
            # c = QTextCursor()
            c.deleteChar()
            c.select(QTextCursor.BlockUnderCursor)
            logging.debug(f"Removing line:{c.selectedText()}")
            c.removeSelectedText()
        else:
            self.setTextCursor(c)
            # Insert a frame and add item document there
            logging.debug(f"[{exec_id}] {item_name}. n:{item_doc.lineCount()}. doc:{item_doc.toPlainText()}")
            frame_format = QTextFrameFormat()
            frame_format.setBorder(1)
            frame_format.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
            frame_format.setBorderBrush(QBrush(Qt.white))
            frame_format.setLeftMargin(15)
            frame = c.insertFrame(frame_format)
            self.insertHtml(item_doc.toHtml())
            # self.insertHtml("<br/>")

    def set_override_document(self, document):
        """
        Sets the given document as the current document.

        Args:
            document (QTextDocument)
        """
        self.setDocument(document)
        self.scroll_to_bottom()
        self.setStyleSheet(TEXTBROWSER_OVERRIDE_SS)

    def restore_original_document(self):
        """
        Restores the original document
        """
        self.setDocument(self._original_document)
        self.scroll_to_bottom()
        self.setStyleSheet(TEXTBROWSER_SS)

    @Slot()
    def scroll_to_bottom(self):
        vertical_scroll_bar = self.verticalScrollBar()
        vertical_scroll_bar.setValue(vertical_scroll_bar.maximum())

    @Slot(str)
    def append(self, text):
        """
        Appends new text block to the end of the *original* document.

        If the document contains more text blocks after the addition than a set limit,
        blocks are deleted at the start of the contents.

        Args:
            text (str): text to add
        """
        cursor = add_message_to_document(self._original_document, text)
        block_count = self._original_document.blockCount()
        if block_count > self._max_blocks:
            blocks_to_remove = block_count - self._max_blocks
            cursor.movePosition(QTextCursor.Start)
            for _ in range(blocks_to_remove):
                cursor.select(QTextCursor.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()  # Remove the trailing newline
        if self.document() == self._original_document:
            self.scroll_to_bottom()
        # Restore the main document by deselecting the executed item icon,
        # **except** if there's an execution in progress
        toolbox = self.nativeParentWidget()
        if toolbox.execution_in_progress:
            return
        if toolbox.executed_item is not None:
            toolbox.executed_item.get_icon().execution_icon.setSelected(False)

    def contextMenuEvent(self, event):
        """Reimplemented method to add a clear action into the default context menu.

        Args:
            event (QContextMenuEvent): Received event
        """
        clear_action = QAction("Clear", self)
        # noinspection PyUnresolvedReferences
        clear_action.triggered.connect(lambda: self.clear())  # pylint: disable=unnecessary-lambda
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        menu.addAction(clear_action)
        menu.exec_(event.globalPos())

    @property
    def max_blocks(self):
        """int: the upper limit of text blocks that can be appended to the widget."""
        return self._max_blocks

    @max_blocks.setter
    def max_blocks(self, new_max):
        self._max_blocks = new_max if new_max > 0 else 2000
