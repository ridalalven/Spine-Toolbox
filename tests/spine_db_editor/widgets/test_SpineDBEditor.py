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
Unit tests for SpineDBEditor classes.

:author: M. Marin (KTH)
:date:   6.12.2018
"""

import unittest
from unittest import mock
import logging
import sys
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QItemSelectionModel
import spinetoolbox.resources_icons_rc  # pylint: disable=unused-import
from spinetoolbox.spine_db_manager import SpineDBManager
from spinetoolbox.spine_db_editor.widgets.spine_db_editor import SpineDBEditor
from spinetoolbox.spine_db_editor.mvcmodels.compound_parameter_models import CompoundParameterModel
from .test_SpineDBEditorAdd import TestSpineDBEditorAddMixin
from .test_SpineDBEditorUpdate import TestSpineDBEditorUpdateMixin
from .test_SpineDBEditorRemove import TestSpineDBEditorRemoveMixin
from .test_SpineDBEditorFilter import TestSpineDBEditorFilterMixin


class TestSpineDBEditor(
    TestSpineDBEditorAddMixin,
    TestSpineDBEditorUpdateMixin,
    TestSpineDBEditorRemoveMixin,
    TestSpineDBEditorFilterMixin,
    unittest.TestCase,
):
    @staticmethod
    def _object_class(*args):
        return dict(zip(["id", "name", "description", "display_order", "display_icon"], args))

    @staticmethod
    def _object(*args):
        return dict(zip(["id", "class_id", "name", "description"], args))

    @staticmethod
    def _relationship_class(*args):
        return dict(zip(["id", "name", "object_class_id_list", "object_class_name_list"], args))

    @staticmethod
    def _relationship(*args):
        return dict(
            zip(
                ["id", "class_id", "name", "class_name", "object_class_id_list", "object_id_list", "object_name_list"],
                args,
            )
        )

    @staticmethod
    def _object_parameter_definition(*args):
        d = dict(zip(["id", "object_class_id", "object_class_name", "parameter_name"], args))
        return d

    @staticmethod
    def _relationship_parameter_definition(*args):
        d = dict(
            zip(
                [
                    "id",
                    "relationship_class_id",
                    "relationship_class_name",
                    "object_class_id_list",
                    "object_class_name_list",
                    "parameter_name",
                ],
                args,
            )
        )
        return d

    @staticmethod
    def _object_parameter_value(*args):
        d = dict(
            zip(
                [
                    "id",
                    "object_class_id",
                    "object_class_name",
                    "object_id",
                    "object_name",
                    "parameter_id",
                    "parameter_name",
                    "value",
                ],
                args,
            )
        )
        d["entity_id"] = d["object_id"]
        return d

    @staticmethod
    def _relationship_parameter_value(*args):
        d = dict(
            zip(
                [
                    "id",
                    "relationship_class_id",
                    "relationship_class_name",
                    "object_class_id_list",
                    "object_class_name_list",
                    "relationship_id",
                    "object_id_list",
                    "object_name_list",
                    "parameter_id",
                    "parameter_name",
                    "value",
                ],
                args,
            )
        )
        d["entity_id"] = d["relationship_id"]
        return d

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
        cls.create_mock_dataset()

    @classmethod
    def create_mock_dataset(cls):
        cls.fish_class = cls._object_class(1, "fish", "A fish.", 1, None)
        cls.dog_class = cls._object_class(2, "dog", "A dog.", 3, None)
        cls.fish_dog_class = cls._relationship_class(
            3,
            "fish__dog",
            str(cls.fish_class["id"]) + "," + str(cls.dog_class["id"]),
            cls.fish_class["name"] + "," + cls.dog_class["name"],
        )
        cls.dog_fish_class = cls._relationship_class(
            4,
            "dog__fish",
            str(cls.dog_class["id"]) + "," + str(cls.fish_class["id"]),
            cls.dog_class["name"] + "," + cls.fish_class["name"],
        )
        cls.nemo_object = cls._object(1, cls.fish_class["id"], 'nemo', 'The lost one.')
        cls.pluto_object = cls._object(2, cls.dog_class["id"], 'pluto', "Mickey's.")
        cls.scooby_object = cls._object(3, cls.dog_class["id"], 'scooby', 'Scooby-Dooby-Doo.')
        cls.pluto_nemo_rel = cls._relationship(
            4,
            cls.dog_fish_class["id"],
            "dog__fish_pluto__nemo",
            cls.dog_fish_class["name"],
            str(cls.dog_class["id"]) + "," + str(cls.fish_class["id"]),
            str(cls.pluto_object["id"]) + "," + str(cls.nemo_object["id"]),
            cls.pluto_object["name"] + "," + cls.nemo_object["name"],
        )
        cls.nemo_pluto_rel = cls._relationship(
            5,
            cls.fish_dog_class["id"],
            "fish__dog_nemo__pluto",
            cls.fish_dog_class["name"],
            str(cls.fish_class["id"]) + "," + str(cls.dog_class["id"]),
            str(cls.nemo_object["id"]) + "," + str(cls.pluto_object["id"]),
            cls.nemo_object["name"] + "," + cls.pluto_object["name"],
        )
        cls.nemo_scooby_rel = cls._relationship(
            6,
            cls.fish_dog_class["id"],
            "fish__dog_nemo__scooby",
            cls.fish_dog_class["name"],
            str(cls.fish_class["id"]) + "," + str(cls.dog_class["id"]),
            str(cls.nemo_object["id"]) + "," + str(cls.scooby_object["id"]),
            cls.nemo_object["name"] + "," + cls.scooby_object["name"],
        )
        cls.water_parameter = cls._object_parameter_definition(1, cls.fish_class["id"], cls.fish_class["name"], "water")
        cls.breed_parameter = cls._object_parameter_definition(2, cls.dog_class["id"], cls.dog_class["name"], "breed")
        cls.relative_speed_parameter = cls._relationship_parameter_definition(
            3,
            cls.fish_dog_class["id"],
            cls.fish_dog_class["name"],
            cls.fish_dog_class["object_class_id_list"],
            cls.fish_dog_class["object_class_name_list"],
            "relative_speed",
        )
        cls.combined_mojo_parameter = cls._relationship_parameter_definition(
            4,
            cls.dog_fish_class["id"],
            cls.dog_fish_class["name"],
            cls.dog_fish_class["object_class_id_list"],
            cls.dog_fish_class["object_class_name_list"],
            "combined_mojo",
        )
        cls.nemo_water = cls._object_parameter_value(
            1,
            cls.water_parameter["object_class_id"],
            cls.water_parameter["object_class_name"],
            cls.nemo_object["id"],
            cls.nemo_object["name"],
            cls.water_parameter["id"],
            cls.water_parameter["parameter_name"],
            '"salt"',
        )
        cls.pluto_breed = cls._object_parameter_value(
            2,
            cls.breed_parameter["object_class_id"],
            cls.breed_parameter["object_class_name"],
            cls.pluto_object["id"],
            cls.pluto_object["name"],
            cls.breed_parameter["id"],
            cls.breed_parameter["parameter_name"],
            '"bloodhound"',
        )
        cls.scooby_breed = cls._object_parameter_value(
            3,
            cls.breed_parameter["object_class_id"],
            cls.breed_parameter["object_class_name"],
            cls.scooby_object["id"],
            cls.scooby_object["name"],
            cls.breed_parameter["id"],
            cls.breed_parameter["parameter_name"],
            '"great dane"',
        )
        cls.nemo_pluto_relative_speed = cls._relationship_parameter_value(
            4,
            cls.relative_speed_parameter["relationship_class_id"],
            cls.relative_speed_parameter["relationship_class_name"],
            cls.relative_speed_parameter["object_class_id_list"],
            cls.relative_speed_parameter["object_class_name_list"],
            cls.nemo_pluto_rel["id"],
            cls.nemo_pluto_rel["object_id_list"],
            cls.nemo_pluto_rel["object_name_list"],
            cls.relative_speed_parameter["id"],
            cls.relative_speed_parameter["parameter_name"],
            "-1",
        )
        cls.nemo_scooby_relative_speed = cls._relationship_parameter_value(
            5,
            cls.relative_speed_parameter["relationship_class_id"],
            cls.relative_speed_parameter["relationship_class_name"],
            cls.relative_speed_parameter["object_class_id_list"],
            cls.relative_speed_parameter["object_class_name_list"],
            cls.nemo_scooby_rel["id"],
            cls.nemo_scooby_rel["object_id_list"],
            cls.nemo_scooby_rel["object_name_list"],
            cls.relative_speed_parameter["id"],
            cls.relative_speed_parameter["parameter_name"],
            "5",
        )
        cls.pluto_nemo_combined_mojo = cls._relationship_parameter_value(
            6,
            cls.combined_mojo_parameter["relationship_class_id"],
            cls.combined_mojo_parameter["relationship_class_name"],
            cls.combined_mojo_parameter["object_class_id_list"],
            cls.combined_mojo_parameter["object_class_name_list"],
            cls.pluto_nemo_rel["id"],
            cls.pluto_nemo_rel["object_id_list"],
            cls.pluto_nemo_rel["object_name_list"],
            cls.combined_mojo_parameter["id"],
            cls.combined_mojo_parameter["parameter_name"],
            "100",
        )

    def setUp(self):
        """Overridden method. Runs before each test. Makes instances of SpineDBEditor classes."""
        with mock.patch(
            "spinetoolbox.spine_db_editor.widgets.spine_db_editor.SpineDBEditor.restore_ui"
        ), mock.patch("spinetoolbox.spine_db_editor.widgets.spine_db_editor.SpineDBEditor.show"):
            mock_settings = mock.Mock()
            mock_settings.value.side_effect = lambda *args, **kwards: 0
            self.db_mngr = SpineDBManager(mock_settings, None)
            self.db_mngr.fetch_db_maps_for_listener = lambda *args: None

            logger = mock.MagicMock()
            self.db_mngr.get_db_map("sqlite://", logger, codename="database", create=True)
            self.spine_db_editor = SpineDBEditor(self.db_mngr, {"sqlite://": "database"})
            self.mock_db_map = self.spine_db_editor.first_db_map
            self.spine_db_editor.pivot_table_model = mock.MagicMock()

    def tearDown(self):
        """Overridden method. Runs after each test.
        Use this to free resources after a test if needed.
        """
        with mock.patch(
            "spinetoolbox.spine_db_editor.widgets.spine_db_editor.SpineDBEditor.save_window_state"
        ) as mock_save_w_s, mock.patch("spinetoolbox.spine_db_manager.QMessageBox"):
            self.spine_db_editor.close()
            mock_save_w_s.assert_called_once()
        QApplication.removePostedEvents(None)  # Clean up unfinished fetcher signals
        self.db_mngr.close_all_sessions()
        self.db_mngr.clean_up()
        self.spine_db_editor.deleteLater()
        self.spine_db_editor = None

    def put_mock_object_classes_in_db_mngr(self):
        """Put fish and dog object classes in the db mngr."""
        object_classes = [self.fish_class, self.dog_class]
        with mock.patch("spinetoolbox.spine_db_manager.SpineDBManager.entity_class_icon") as mock_icon:
            mock_icon.return_value = None
            self.db_mngr.object_classes_added.emit({self.mock_db_map: object_classes})
            mock_icon.assert_called()

    def put_mock_objects_in_db_mngr(self):
        """Put nemo, pluto and scooby objects in the db mngr."""
        objects = [self.nemo_object, self.pluto_object, self.scooby_object]
        self.db_mngr.objects_added.emit({self.mock_db_map: objects})

    def put_mock_relationship_classes_in_db_mngr(self):
        """Put dog__fish and fish__dog relationship classes in the db mngr."""
        relationship_classes = [self.fish_dog_class, self.dog_fish_class]
        with mock.patch("spinetoolbox.spine_db_manager.SpineDBManager.entity_class_icon") as mock_icon:
            mock_icon.return_value = None
            self.db_mngr.relationship_classes_added.emit({self.mock_db_map: relationship_classes})
            mock_icon.assert_called()

    def put_mock_relationships_in_db_mngr(self):
        """Put pluto_nemo, nemo_pluto and nemo_scooby relationships in the db mngr."""
        relationships = [self.pluto_nemo_rel, self.nemo_pluto_rel, self.nemo_scooby_rel]
        self.db_mngr.relationships_added.emit({self.mock_db_map: relationships})

    def put_mock_object_parameter_definitions_in_db_mngr(self):
        """Put water and breed object parameter definitions in the db mngr."""
        parameter_definitions = [self.water_parameter, self.breed_parameter]
        with mock.patch.object(CompoundParameterModel, "_modify_data_in_filter_menus"):
            self.db_mngr.parameter_definitions_added.emit({self.mock_db_map: parameter_definitions})

    def put_mock_relationship_parameter_definitions_in_db_mngr(self):
        """Put relative speed and combined mojo relationship parameter definitions in the db mngr."""
        parameter_definitions = [self.relative_speed_parameter, self.combined_mojo_parameter]
        with mock.patch.object(CompoundParameterModel, "_modify_data_in_filter_menus"):
            self.db_mngr.parameter_definitions_added.emit({self.mock_db_map: parameter_definitions})

    def put_mock_object_parameter_values_in_db_mngr(self):
        """Put some object parameter values in the db mngr."""
        parameter_values = [self.nemo_water, self.pluto_breed, self.scooby_breed]
        with mock.patch.object(CompoundParameterModel, "_modify_data_in_filter_menus"):
            self.db_mngr.parameter_values_added.emit({self.mock_db_map: parameter_values})

    def put_mock_relationship_parameter_values_in_db_mngr(self):
        """Put some relationship parameter values in the db mngr."""
        parameter_values = [
            self.nemo_pluto_relative_speed,
            self.nemo_scooby_relative_speed,
            self.pluto_nemo_combined_mojo,
        ]
        with mock.patch.object(CompoundParameterModel, "_modify_data_in_filter_menus"):
            self.db_mngr.parameter_values_added.emit({self.mock_db_map: parameter_values})

    def put_mock_dataset_in_db_mngr(self):
        """Put mock dataset in the db mngr."""
        self.put_mock_object_classes_in_db_mngr()
        self.put_mock_objects_in_db_mngr()
        self.put_mock_relationship_classes_in_db_mngr()
        self.put_mock_relationships_in_db_mngr()
        self.put_mock_object_parameter_definitions_in_db_mngr()
        self.put_mock_relationship_parameter_definitions_in_db_mngr()
        self.put_mock_object_parameter_values_in_db_mngr()
        self.put_mock_relationship_parameter_values_in_db_mngr()
        self.fetch_object_tree_model()

    def fetch_object_tree_model(self):
        for item in self.spine_db_editor.object_tree_model.visit_all():
            if item.can_fetch_more():
                item.fetch_more()

    def test_set_object_parameter_definition_defaults(self):
        """Test that defaults are set in object parameter_definition models according the object tree selection."""
        self.spine_db_editor.init_models()
        self.put_mock_object_classes_in_db_mngr()
        self.fetch_object_tree_model()
        # Select fish item in object tree
        root_item = self.spine_db_editor.object_tree_model.root_item
        fish_item = root_item.child(0)
        fish_index = self.spine_db_editor.object_tree_model.index_from_item(fish_item)
        self.spine_db_editor.ui.treeView_object.setCurrentIndex(fish_index)
        self.spine_db_editor.ui.treeView_object.selectionModel().select(fish_index, QItemSelectionModel.Select)
        # Check default in object parameter_definition
        model = self.spine_db_editor.object_parameter_definition_model
        model.empty_model.fetchMore()
        h = model.header.index
        row_data = []
        for row in range(model.rowCount()):
            row_data.append(tuple(model.index(row, h(field)).data() for field in ("object_class_name", "database")))
        self.assertIn(("fish", "database"), row_data)

    @unittest.skip("TODO")
    def test_set_object_parameter_value_defaults(self):
        """Test that defaults are set in relationship parameter_definition
        models according the object tree selection.
        """
        self.fail()

    @unittest.skip("TODO")
    def test_set_relationship_parameter_definition_defaults(self):
        """Test that defaults are set in relationship parameter_definition
        models according the object tree selection.
        """
        self.fail()

    @unittest.skip("TODO")
    def test_set_relationship_parameter_value_defaults(self):
        """Test that defaults are set in relationship parameter_definition
        models according the object tree selection.
        """
        self.fail()


if __name__ == '__main__':
    unittest.main()
