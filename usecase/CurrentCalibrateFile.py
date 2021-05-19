# -*- coding: utf-8 -*-
from entity.FileHandler import FileHandler
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

    # 获取校正信息
    def get_file_channels(self):
        file_handler = FileHandler()
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

    def get_depends_id(self, channel_index, parameter_id):
        depends_id = []
        channel = self._current_channels[channel_index]
        calibrate_msg = channel[parameter_id]
        root_node = calibrate_msg.calibrate_tree
        leaf_nodes = root_node.leaves
        a_branch_node = leaf_nodes[0].ancestors
        for node in a_branch_node:
            depends_id.append(node.parameter_id)
        depends_id.pop(0)
        return depends_id

    def get_depend_parent_node(self, channel_index, calibrate_parameter_id, path, depend_id):
        choose_channel = self._current_channels[channel_index]
        calibrate_msg = choose_channel[calibrate_parameter_id]
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

    def get_depend_segments(self, channel_index, calibrate_parameter_id, path, depend_id):
        parent_node = self.get_depend_parent_node(channel_index, calibrate_parameter_id, path, depend_id)
        depend_segments = []
        children = parent_node.children
        for child in children:
            depend_segments.append(child.parameter_segment)
        return depend_segments

    def get_parameter_parent_node(self, channel_index, calibrate_parameter_id, path):
        choose_channel = self._current_channels[channel_index]
        calibrate_msg = choose_channel[calibrate_parameter_id]
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

    def get_calibrate_parameter_segments(self, channel_index, calibrate_parameter_id, path):
        # segments中包含全部待校参数分段，以及对应的校正系数
        depend_leaf_node = self.get_parameter_parent_node(channel_index, calibrate_parameter_id, path)
        parameter_node = depend_leaf_node.children[0]
        parameter_segments = self.get_segments_dict(parameter_node)
        return parameter_segments

    # 文件合并
    def merge_calibrate_file_by_method_two(self, merge_channel_index, another_channel_index, another_parameter_id):
        merge_channel = self._current_channels[merge_channel_index]
        self._merge.another_file = self._another_file_path
        new_channel = self._merge.merge_by_method_two(merge_channel, another_channel_index, another_parameter_id)
        self._current_channels[merge_channel_index] = new_channel

    def merge_calibrate_file_by_method_three(self, merge_channel_index, another_channel_index):
        merge_channel = self._current_channels[merge_channel_index]
        self._merge.another_file = self._another_file_path
        new_channel = self._merge.merge_by_method_three(merge_channel, another_channel_index)
        self._current_channels[merge_channel_index] = new_channel

    # 参数信息编辑  # TODO 得到是一个复制的结点？要是这样，修改完之后还要找到树中对应的结点然后替代？
    def modify_parameter_factors(self, channel_index, calibrate_parameter_id, path, segment, new_factors):
        dependency_leaf_node = self.get_parameter_parent_node(channel_index, calibrate_parameter_id, path)
        parameter_node = dependency_leaf_node.children[0]
        self._calibrate_parameter_editor.parameter_node = parameter_node
        self._calibrate_parameter_editor.modify_parameter_factors(new_factors, segment)
        return self._calibrate_parameter_editor.parameter_node

    def modify_calibrate_parameter_interval(self, parameter_node, segment, value):
        self._calibrate_parameter_editor.parameter_node = parameter_node
        self._calibrate_parameter_editor.modify_parameter_interval(value, segment)
        return self._calibrate_parameter_editor.parameter_node

    def add_parameter_segment(self, parameter_node, segment):
        self._calibrate_parameter_editor.parameter_node = parameter_node
        self._calibrate_parameter_editor.add_parameter_segment(segment)
        return self._calibrate_parameter_editor.parameter_node

    def delete_parameter_segment(self, parameter_node, segment):
        self._calibrate_parameter_editor.parameter_node = parameter_node
        self._calibrate_parameter_editor.delete_parameter_segment(segment)
        return self._calibrate_parameter_editor.parameter_node

    def add_parameter_node(self, root_node, parent_node):
        leaf_nodes = root_node.leaves
        parameter_id = leaf_nodes[0].parameter_id
        root_node = self._calibrate_parameter_editor.add_parameter_node(parameter_id, root_node, parent_node)
        return root_node

    def delete_parameter_node(self, root_node, parameter_node):
        root_node = self._calibrate_parameter_editor.delete_parameter_node(root_node, parameter_node)
        return root_node

    # 参数分段转化成dict形式便于查找
    def get_segments_dict(self, parameter_node):
        self._calibrate_parameter_editor.parameter_node = parameter_node
        segments_dict = self._calibrate_parameter_editor.get_segments_dict()
        return segments_dict

    # 显示系数曲线
    def show_current_factors_curve(self, segment):
        self._calibrate_parameter_editor.show_current_factors_curve(segment)

    def show_two_factors_curve(self, modified_segment, current_segment):
        self._calibrate_parameter_editor.show_two_factors_curve(modified_segment, current_segment)

    # 依赖编辑
    def add_depend(self, root_node, depend_id, parent_id):
        self._depend_editor.root_node = root_node
        self._depend_editor.add_depend(parent_id, depend_id)
        return self._depend_editor.root_node

    def delete_depend(self, root_node, depend_id):
        self._depend_editor.root_node = root_node
        self._depend_editor.delete_depend(depend_id)
        return self._depend_editor.root_node

    def add_depend_segment_until_leaf(self, root_node, start_depend_node):
        self._depend_editor.root_node = root_node
        self._depend_editor.add_depends_segment_nodes_until_leaf(start_depend_node)
        return self._depend_editor.root_node

    def delete_depend_segment(self, root_node, depend_node):
        self._depend_editor.root_node = root_node
        self._depend_editor.delete_depend_segment(depend_node)
        return self._depend_editor.root_node

    def modify_depend_segment(self, lower_num, upper_num, depend_node, root_node):
        self._depend_editor.root_node = root_node
        self._depend_editor.modify_depend_segment(lower_num, upper_num, depend_node)
        return self._depend_editor.root_node

    # 保存
    def save(self):
        file_handler = FileHandler()
        file_handler.file_path = self._current_file_path
        calibrate_file = file_handler.calibrate_msg_to_file_form(self._current_channels)
        file_handler.save(calibrate_file)

    def save_as(self, file_path):
        file_handler = FileHandler()
        calibrate_file = file_handler.calibrate_msg_to_file_form(self._current_channels)
        file_handler.save_as(calibrate_file, file_path)
