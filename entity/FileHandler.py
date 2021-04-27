# -*- coding: utf-8 -*-
import json
import os
import entity.CalibrateFile
from intervals import FloatInterval
from anytree import Node


class FileHandler:
    def __init__(self):
        self._json_handler = JsonHandler()
        self._sql_handler = None
        self._bin_handler = None

        self._calibrate_file = None
        self._current_calibrate_msg = None
        self._dependency_leaves = []
        self._parameter_nodes = []

    def save(self):
        pass

    @staticmethod
    def get_channel_number(channels):
        channel_number = len(channels)
        return channel_number

    def calibrate_msg_to_file(self, calibrate_msg):  # TODO
        pass
        # if not isinstance(calibrate_msg, entity.CalibrateFile.CalibrateMsg):
        #     raise ValueError
        # depends = calibrate_msg.dependency_list
        # model = calibrate_msg.calibrate_model
        # calibrate_parameter_id = calibrate_msg.parameter_id
        # entry = 0
        # msg = [calibrate_parameter_id, entry, depends, model, [], [], []]
        # for node in calibrate_msg.calibrate_tree:
        #     if not isinstance(node, entity.CalibrateFile.CalibrateLeavesNode):
        #         pass
        #     else:
        #         count = 0
        #         factors = node.content
        #         msg[6].append(factors)

    # 读取文件操作部分
    def get_calibrate_file(self, file_path):  # TODO
        suffix = os.path.splitext(file_path)[-1]
        if suffix == '.json':
            self._calibrate_file = self._json_handler.load(file_path)
        # elif suffix == '.bin':
        #     calibrate_file = self._bin_handler(file_path)
        #     return calibrate_file
        # elif suffix == '.sql':
        #     calibrate_file = self._sql_handler(file_path)
        #     return calibrate_file
        else:
            raise FileExistsError

    def load_calibrate_msg_from_file(self, channel_index, parameter_id):
        self._dependency_leaves = []
        self._parameter_nodes = []
        msg = entity.CalibrateFile.CalibrateMsg()
        msg.calibrate_tree = self.get_calibrate_tree(channel_index, parameter_id)
        msg.parameter_id = parameter_id
        msg.dependency_list = self._current_calibrate_msg[2]
        msg.calibrate_model = self._current_calibrate_msg[3]
        return msg

    def load_all_calibrate_msg_from_file(self):  # TODO 未包含通道[]
        all_channel_msgs = []
        channels = list(enumerate(self._calibrate_file[3]))
        for channel in channels[1:]:
            channel_msgs = {}
            channel_index = channel[0]
            for calibrate_msg in channel[1]:
                msg = self.load_calibrate_msg_from_file(channel_index, calibrate_msg[0])
                channel_msgs[calibrate_msg[0]] = msg
            all_channel_msgs.append(channel_msgs)
        return all_channel_msgs

    def get_calibrate_tree(self, channel_index, parameter_id):
        tree_nodes = []
        root_node = self.get_root_node(channel_index, parameter_id)
        tree_nodes.append(root_node)
        parent_nodes = root_node.children
        tree_nodes += parent_nodes
        dependency_nodes = []
        while True:
            try:
                next_nodes = self.get_next_dependency_nodes(parent_nodes)
                dependency_nodes += next_nodes
                parent_nodes = next_nodes
            except InterruptedError:
                break
        tree_nodes += dependency_nodes
        self.get_parameter_nodes()
        self.get_parameter_nodes_factors()
        tree_nodes += self._parameter_nodes
        return tree_nodes

    def get_root_node(self, channel_index, parameter_id):
        file_channels = self._calibrate_file[3]
        file_depends = self._calibrate_file[2]
        current_channel = file_channels[channel_index]
        # root_node = Node("{},{}".format(channel_index, parameter_id))
        root_node = entity.CalibrateFile.CalibrateParameterNode()
        root_node.parameter_id = parameter_id
        for calibrate_msg in current_channel:
            if parameter_id == calibrate_msg[0]:
                self._current_calibrate_msg = calibrate_msg
                entry = calibrate_msg[1]

                entry_dependency = file_depends[entry]
                for segment in entry_dependency[1]:
                    dependency_segment_node = entity.CalibrateFile.CalibrateDependencyNode()
                    parameter_id = entry_dependency[0]
                    dependency_segment_node.parameter_id = parameter_id
                    segment_upper = segment[0][1]
                    segment_lower = segment[0][0]
                    transfer_num = segment[1]
                    interval = FloatInterval.closed(segment_lower, segment_upper)
                    dependency_segment_node.parameter_segment = interval
                    dependency_segment_node.transfer_num = transfer_num
                    dependency_segment_node.parent = root_node
        return root_node

    def get_next_dependency_nodes(self, parent_nodes):
        file_depends = self._calibrate_file[2]
        next_nodes = []
        count = 0
        for parent_node in parent_nodes:
            if parent_node.transfer_num < 0:
                self._dependency_leaves.append(parent_node)
                count += 1
                if count == len(parent_nodes):
                    raise InterruptedError
            else:
                next_dependency = file_depends[parent_node.transfer_num]
                for segment in next_dependency[1]:
                    next_node = entity.CalibrateFile.CalibrateDependencyNode()
                    next_node.parameter_id = next_dependency[0]
                    segment_upper = segment[0][1]
                    segment_lower = segment[0][0]
                    transfer_num = segment[1]
                    next_node.transfer_num = transfer_num
                    next_node.parameter_segment = FloatInterval.closed(segment_lower, segment_upper)
                    next_node.parent = parent_node
                    next_nodes.append(next_node)
        return next_nodes

    def get_parameter_nodes(self):
        parameter_nodes = []
        hardware = self._current_calibrate_msg[5]
        for node in self._dependency_leaves:
            parameter_node = entity.CalibrateFile.CalibrateParameterNode()
            parameter_node.parameter_segments = hardware[-node.transfer_num-1]
            parameter_node.parameter_id = self._current_calibrate_msg[0]
            parameter_node.parent = node
            parameter_nodes.append(parameter_node)
        self._parameter_nodes += parameter_nodes

    def get_parameter_nodes_factors(self):
        all_factors = self._current_calibrate_msg[6]
        for node in self._parameter_nodes:
            for segment in node.parameter_segments:
                left_num = segment[0][0]
                right_num = segment[0][1]
                interval = FloatInterval.closed(left_num, right_num)
                segment[0] = interval
                transfer_num = segment[1]
                factors = all_factors[transfer_num]
                segment[1] = factors


class JsonHandler:
    def __init__(self):
        pass

    @staticmethod
    def load(file_path):
        with open(file_path) as file:
            data_json = json.load(file)  # TODO json.decoder.JSONDecodeError
            channel_number = data_json["channel_number"]
            rev_depends = data_json["rev_depends"]
            depends = data_json["depends"]
            channels = data_json["channels"]
            calibrate_file = [channel_number, rev_depends, depends, channels]
        return calibrate_file

    @staticmethod
    def save():
        pass
