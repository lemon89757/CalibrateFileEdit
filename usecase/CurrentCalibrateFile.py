# -*- coding: utf-8 -*-
from entity.FileReadAndWrite import FileRW
from usecase.EditCalibrateParameter import EditCalibrateParameter
from usecase.EditCalibrateParameterDepends import EditCalibrateParameterDepends
from usecase.MergeCalibrateFile import MergeCalibrateFile


class CalibrateFileEdit:
    def __init__(self):
        self._calibrate_parameter_editor = EditCalibrateParameter()
        self._depend_editor = EditCalibrateParameterDepends()
        self._merge = MergeCalibrateFile()

        self._current_file_path = 'file_path'
        self._another_file_path = 'file_path'
        self._current_channels = None   # 当前文件的channels
        self._another_channels = None

    @property
    def current_file_path(self):
        return self._current_file_path

    @current_file_path.setter
    def current_file_path(self, value):
        if type(value) != str:
            raise value
        self._current_file_path = value

    @property
    def another_file_path(self):
        return self._another_file_path

    @another_file_path.setter
    def another_file_path(self, value):
        if type(value) != str:
            raise ValueError
        self._another_file_path = value

    @property
    def current_channels(self):
        return self._current_channels

    @current_channels.setter
    def current_channels(self, value):
        self._current_channels = value

    @property
    def another_channels(self):
        return self._another_channels

    @another_channels.setter
    def another_channels(self, value):
        self._another_channels = value

    # 获取校正信息
    def get_file_channels(self):
        file_handler = FileRW()
        file_handler.get_calibrate_file(self._current_file_path)
        channels = file_handler.load_all_calibrate_msg_from_file()
        return channels

    def get_calibrate_model(self, parameter_id, channel_index):
        channel = self._current_channels[channel_index]
        calibrate_msg = channel[parameter_id]
        model = calibrate_msg.calibrate_model
        return model

    def get_dependencies_list(self, parameter_id, channel_index):
        channel = self._current_channels[channel_index]
        calibrate_msg = channel[parameter_id]
        dependencies_list = calibrate_msg.dependency_list
        return dependencies_list

    @staticmethod
    def get_depends_id(channel, parameter_id):
        depends_id = []
        calibrate_msg = channel[parameter_id]
        root_node = calibrate_msg.calibrate_tree
        leaf_nodes = root_node.leaves
        a_branch_node = leaf_nodes[0].ancestors
        for node in a_branch_node:
            depends_id.append(node.parameter_id)
        depends_id.pop(0)
        return depends_id

    @staticmethod
    def get_depend_parent_node(channel, calibrate_parameter_id, path, depend_id):
        calibrate_msg = channel[calibrate_parameter_id]
        root_node = calibrate_msg.calibrate_tree
        same_id_depend_nodes = []
        for node in root_node.descendants:
            if depend_id == node.parameter_id:
                same_id_depend_nodes.append(node)
        for same_id_node in same_id_depend_nodes:
            path_i = same_id_node.path
            count = 0
            for node_i in path_i:
                realistic_parameter_id = path[count][0]
                realistic_parameter_segment = path[count][1]
                if node_i.parameter_id == realistic_parameter_id \
                        and node_i.parameter_segment == realistic_parameter_segment:
                    count += 1
                if count == len(path):
                    return same_id_node.parent

    def get_depend_segments(self, channel, calibrate_parameter_id, path, depend_id):
        parent_node = self.get_depend_parent_node(channel, calibrate_parameter_id, path, depend_id)
        depend_segments = []
        children = parent_node.children
        for child in children:
            depend_segments.append(child.parameter_segment)
        return depend_segments

    @staticmethod
    def get_parameter_parent_node(channel, calibrate_parameter_id, path):
        calibrate_msg = channel[calibrate_parameter_id]
        root_node = calibrate_msg.calibrate_tree

        for node in root_node.leaves:
            count = 0
            for node_i in node.path:
                realistic_parameter_id = path[count][0]
                realistic_parameter_segment = path[count][1]
                if realistic_parameter_id == node_i.parameter_id \
                        and realistic_parameter_segment == node_i.parameter_segment:
                    count += 1
                if count == len(path):
                    return node_i

    def get_calibrate_parameter_segments(self, channel, calibrate_parameter_id, path):
        # segments中包含全部待校参数分段，以及对应的校正系数
        depend_leaf_node = self.get_parameter_parent_node(channel, calibrate_parameter_id, path)
        parameter_node = depend_leaf_node.children[0]
        # parameter_segments = self.get_segments_dict(parameter_node)
        return parameter_node.parameter_segments

    def get_available_parameters(self, channel_index):
        available_parameters = []
        chosen_channel = self._current_channels[channel_index]
        for parameter in chosen_channel.keys():
            available_parameters.append(parameter)
        return available_parameters

    @staticmethod
    def get_root_node(channel, parameter_id):
        calibrate_msg = channel[parameter_id]
        root_node = calibrate_msg.calibrate_tree
        return root_node

    # 文件合并
    def merge_calibrate_file_by_method_two(self, merge_channel_index, another_channel_index, another_parameter_id):
        merge_channel = self._current_channels[merge_channel_index]
        another_channel = self._another_channels[another_channel_index]
        another_parameter_calibrate_msg = another_channel[another_parameter_id]
        new_channel = self._merge.merge_by_method_two(merge_channel, another_parameter_calibrate_msg)
        self._current_channels[merge_channel_index] = new_channel

    def merge_calibrate_file_by_method_three(self, another_channel_index):
        another_channel = self._another_channels[another_channel_index]
        self._current_channels.append(another_channel)

    # 参数信息编辑
    def modify_parameter_factors(self, channel, calibrate_parameter_id, path, segment, new_factors):
        dependency_leaf_node = self.get_parameter_parent_node(channel, calibrate_parameter_id, path)
        parameter_node = dependency_leaf_node.children[0]
        self._calibrate_parameter_editor.parameter_node = parameter_node
        self._calibrate_parameter_editor.modify_parameter_factors(new_factors, segment)

    def modify_calibrate_parameter_interval(self, channel, calibrate_parameter_id, path, segment, new_interval):
        dependency_leaf_node = self.get_parameter_parent_node(channel, calibrate_parameter_id, path)
        parameter_node = dependency_leaf_node.children[0]
        self._calibrate_parameter_editor.parameter_node = parameter_node
        self._calibrate_parameter_editor.modify_parameter_interval(new_interval, segment)

    # def add_parameter_segment(self, parameter_node, segment):
    #     self._calibrate_parameter_editor.parameter_node = parameter_node
    #     self._calibrate_parameter_editor.add_parameter_segment(segment)
    #     return self._calibrate_parameter_editor.parameter_node

    def delete_parameter_segment(self, parameter_node, interval):
        self._calibrate_parameter_editor.parameter_node = parameter_node
        self._calibrate_parameter_editor.delete_parameter_segment(interval)
        # return self._calibrate_parameter_editor.parameter_node

    # def add_parameter_node(self, root_node, parent_node):
    #     leaf_nodes = root_node.leaves
    #     parameter_id = leaf_nodes[0].parameter_id
    #     root_node = self._calibrate_parameter_editor.add_parameter_node(parameter_id, root_node, parent_node)
    #     return root_node

    def delete_parameter_node(self, root_node, parameter_node):
        root_node = self._calibrate_parameter_editor.delete_parameter_node(root_node, parameter_node)
        return root_node

    # 参数分段转化成dict形式便于查找(但存在重复校正系数区间，不同校正系数间相互覆盖的问题)
    # def get_segments_dict(self, parameter_node):
    #     self._calibrate_parameter_editor.parameter_node = parameter_node
    #     segments_dict = self._calibrate_parameter_editor.get_segments_dict()
    #     return segments_dict

    # 显示系数曲线
    def show_current_factors_curve(self, segment):
        self._calibrate_parameter_editor.show_current_factors_curve(segment)

    def show_two_factors_curve(self, modified_segment, current_segment):
        self._calibrate_parameter_editor.show_two_factors_curve(modified_segment, current_segment)

    # 依赖编辑
    def add_depend(self, root_node, depend_id, pos, new_dependency):
        self._depend_editor.root_node = root_node
        self._depend_editor.add_depend(depend_id, pos, new_dependency)
        # return self._depend_editor.root_node

    def delete_depend(self, root_node, depend_id):
        self._depend_editor.root_node = root_node
        self._depend_editor.delete_depend(depend_id)
        # return self._depend_editor.root_node

    def add_depend_segment_until_leaf(self, root_node, start_depend_node):
        self._depend_editor.root_node = root_node
        self._depend_editor.add_depends_segment_nodes_until_leaf(start_depend_node)
        # return self._depend_editor.root_node

    def delete_depend_segment(self, depend_node):
        self._depend_editor.delete_depend_segment(depend_node)
        # return self._depend_editor.root_node

    def modify_depend_segment(self, channel, calibrate_parameter, lower_num, upper_num, depend_path, depend_id,
                              current_segment):
        depend_parent_node = self.get_depend_parent_node(channel, calibrate_parameter, depend_path, depend_id)
        for child in depend_parent_node.children:
            if current_segment == child.parameter_segment:
                self._depend_editor.modify_depend_segment(lower_num, upper_num, child)
                break

    # 保存
    def save(self):
        file_handler = FileRW()
        file_handler.file_path = self._current_file_path
        calibrate_file = file_handler.calibrate_msg_to_file_form(self._current_channels)
        file_handler.save(calibrate_file)

    def save_as(self, file_path):
        file_handler = FileRW()
        calibrate_file = file_handler.calibrate_msg_to_file_form(self._current_channels)
        file_handler.save_as(calibrate_file, file_path)

    def get_current_node(self, channel, calibrate_parameter_id, path):
        current_chosen_id = path[-1][0]
        current_chosen_segment = path[-1][1]
        if current_chosen_id != calibrate_parameter_id:
            current_parent_node = self.get_depend_parent_node(channel, calibrate_parameter_id, path[:-1],
                                                              current_chosen_id)
            for node in current_parent_node.children:
                if node.parameter_id == current_chosen_id and node.parameter_segment == current_chosen_segment:
                    return node

    def add_branch(self, channel, calibrate_parameter_id, path):
        node = self.get_current_node(channel, calibrate_parameter_id, path)
        root_node = self.get_root_node(channel, calibrate_parameter_id)
        self.add_depend_segment_until_leaf(root_node, node)

    def delete_branch(self, channel, calibrate_parameter_id, path):
        current_chosen_id = path[-1][0]
        if current_chosen_id == calibrate_parameter_id:
            calibrate_parameter_parent_node = self.get_parameter_parent_node(channel, calibrate_parameter_id,
                                                                             path[:-1])
            current_node = calibrate_parameter_parent_node.children[0]
            current_chosen_interval = path[-1][1]
            self.delete_parameter_segment(current_node, current_chosen_interval)
        else:
            current_node = self.get_current_node(channel, calibrate_parameter_id, path)
            self.delete_depend_segment(current_node)

    def add_complete_branch(self, channel, calibrate_parameter_id):
        root_node = self.get_root_node(channel, calibrate_parameter_id)
        self.add_depend_segment_until_leaf(root_node, root_node)

    def confirm_in_senior(self, channel, channel_index):
        self._current_channels[channel_index] = channel

    def get_other_file_channels(self):
        file_handler = FileRW()
        file_handler.get_calibrate_file(self._another_file_path)
        channels = file_handler.load_all_calibrate_msg_from_file()
        return channels

    @staticmethod
    def get_parameter_dict():
        file_handler = FileRW()
        parameter_dict = file_handler.get_parameter_dict()
        return parameter_dict
