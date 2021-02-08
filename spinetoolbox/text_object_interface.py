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

Contains an SVG interface class for drawing icons to QTextBrowsers.

:authors: P. Savolainen (VTT)
:date:   25.1.2021
"""

from PySide2.QtCore import QSizeF
from PySide2.QtGui import QPyTextObject
from PySide2.QtSvg import QSvgRenderer
from spinetoolbox.config import SVGTEXTFORMAT, SVGDATA


class SvgTextObject(QPyTextObject):
    """SVG interface class. Used as a QTextDocument layout handler."""

    def intrinsicSize(self, doc, posInDocument, format):
        renderer = QSvgRenderer(format.property(SVGDATA))  # .toByteArray() ?
        size = renderer.defaultSize()
        if size.height() > 18:
            size *= 18.0 / size.height()
        # print(f"size:{size}")
        return QSizeF(size)

    def drawObject(self, painter, rect, doc, posInDocument, format):
        renderer = QSvgRenderer(format.property(SVGDATA))  # .toByteArray() ?
        # print(f"rect:{rect}")
        renderer.render(painter, rect)
