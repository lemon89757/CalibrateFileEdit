# -*- coding: utf-8 -*-
# import copy
from entity.FileHandler import FileHandler
from usecase.EditCalibrateParameter import EditCalibrateParameter
from usecase.EditCalibrateParameterDepends import EditCalibrateParameterDepends
from usecase.MergeCalibrateFile import MergeCalibrateFile


class CalibrateFileEdit:
    def __init__(self):
        self._calibrate_parameter_edit = EditCalibrateParameter()
        self._depend_edit = EditCalibrateParameterDepends()
        self._merge = MergeCalibrateFile()

        self._file_path = 'file_path'
        self._another_file_path = 'file_path'
        self._channels = None

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        if type(value) != str:
            raise value
        self._file_path = value

    @property
    def another_file_path(self):
        return self._another_file_path

    @another_file_path.setter
    def another_file_path(self, value):
        if type(value) != str:
            raise ValueError
        self._another_file_path = value

    def get_current_file_channels(self):
        file_handler = FileHandler()
        file_handler.get_calibrate_file(self._file_path)
        self._channels = file_handler.load_all_calibrate_msg_from_file()

    def merge_calibrate_file_by_method_two(self, merge_channel_index, another_channel_index, another_parameter_id):
        merge_channel = self._channels[merge_channel_index]
        self._merge.another_file = self._another_file_path
        new_channel = self._merge.merge_by_method_two(merge_channel, another_channel_index, another_parameter_id)
        self._channels[merge_channel_index] = new_channel

    def merge_calibrate_file_by_method_three(self, merge_channel_index, another_channel_index):
        merge_channel = self._channels[merge_channel_index]
        self._merge.another_file = self._another_file_path
        new_channel = self._merge.merge_by_method_three(merge_channel, another_channel_index)
        self._channels[merge_channel_index] = new_channel

    def modify_parameter_factors(self, parameter_node, segment, value):
        self._calibrate_parameter_edit.parameter_node = parameter_node
        self._calibrate_parameter_edit.modify_parameter_factors(value, segment)
        return self._calibrate_parameter_edit.parameter_node

    def modify_calibrate_parameter_interval(self, parameter_node, segment, value):
        self._calibrate_parameter_edit.parameter_node = parameter_node
        self._calibrate_parameter_edit.modify_parameter_interval(value, segment)
        return self._calibrate_parameter_edit.parameter_node

    def add_parameter_segment(self, parameter_node, segment):
        self._calibrate_parameter_edit.parameter_node = parameter_node
        self._calibrate_parameter_edit.add_parameter_segment(segment)
        return self._calibrate_parameter_edit.parameter_node

    def delete_parameter_segment(self, parameter_node, segment):
        self._calibrate_parameter_edit.parameter_node = parameter_node
        self._calibrate_parameter_edit.delete_parameter_segment(segment)
        return self._calibrate_parameter_edit.parameter_node

    def add_parameter_node(self, root_node, parent_node):
        leaf_nodes = root_node.leaves
        parameter_id = leaf_nodes[0].parameter_id
        root_node = self._calibrate_parameter_edit.add_parameter_node(parameter_id, root_node, parent_node)
        return root_node

    def delete_parameter_node(self, root_node, parameter_node):
        root_node = self._calibrate_parameter_edit.delete_parameter_node(root_node, parameter_node)
        return root_node

    def get_segments_dict(self, parameter_node):
        self._calibrate_parameter_edit.parameter_node = parameter_node
        segments_dict = self._calibrate_parameter_edit.get_segments_dict()
        return segments_dict

    def show_current_factors_curve(self, segment):
        self._calibrate_parameter_edit.show_current_factors_curve(segment)

    def show_two_factors_curve(self, modified_segment):
        self._calibrate_parameter_edit.show_two_factors_curve(modified_segment)

    def add_depend(self, root_node, depend_id, parent_id):
        self._depend_edit.root_node = root_node
        self._depend_edit.add_depend(parent_id, depend_id)
        return self._depend_edit.root_node

    def delete_depend(self, root_node, depend_id):
        self._depend_edit.root_node = root_node
        self._depend_edit.delete_depend(depend_id)
        return self._depend_edit.root_node

    def add_depend_segment_until_leaf(self, root_node, start_depend_node):
        self._depend_edit.root_node = root_node
        self._depend_edit.add_depends_segment_nodes_until_leaf(start_depend_node)
        return self._depend_edit.root_node

    def delete_depend_segment(self, root_node, depend_node):
        self._depend_edit.root_node = root_node
        self._depend_edit.delete_depend_segment(depend_node)
        return self._depend_edit.root_node

    def modify_depend_segment(self, lower_num, upper_num, depend_node, root_node):
        self._depend_edit.root_node = root_node
        self._depend_edit.modify_depend_segment(lower_num, upper_num, depend_node)
        return self._depend_edit.root_node

    def save(self):
        file_handler = FileHandler()
        file_handler.file_path = self._file_path
        calibrate_file = file_handler.calibrate_msg_to_file_form(self._channels)
        file_handler.save(calibrate_file)

    def save_as(self, file_path):
        file_handler = FileHandler()
        calibrate_file = file_handler.calibrate_msg_to_file_form(self._channels)
        file_handler.save_as(calibrate_file, file_path)
