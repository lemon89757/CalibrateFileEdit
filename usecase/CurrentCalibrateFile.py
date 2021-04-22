# -*- coding: utf-8 -*-
import copy
import entity.CalibrateFile
from intervals import FloatInterval
from entity.FileHandler import FileHandler


class CurrentFile(entity.CalibrateFile.CalibrateFile):
    def __init__(self, file_path=None):
        super().__init__()
        self._file_path = file_path
        self._file_handler = FileHandler()
        self._calibrate_file = self._file_handler.read(self._file_path)  # 需在此处捕捉错误
        # self._calibrate_tree = self.create_calibrate_tree()

        self._channel_number = self._calibrate_file[0]
        self._rev_depends = self._calibrate_file[1]
        self._depends = self._calibrate_file[2]
        self._channels = self._calibrate_file[3]

    # @property
    # def calibrate_tree(self):
    #     return self._calibrate_tree

    def create_calibrate_tree(self, entry, channel_index):  # 返回一个树节点的列表
        calibrate_tree = []
        dependency_tree_nodes = self.create_dependency_tree(entry)
        hardware_nodes = self.create_hardware_node(channel_index, dependency_tree_nodes)
        calibrate_factor_nodes = self.create_factor_node(channel_index, hardware_nodes)
        for node in dependency_tree_nodes:
            calibrate_tree.append(node)
        for node in hardware_nodes:
            calibrate_tree.append(node)
        for node in calibrate_factor_nodes:
            calibrate_tree.append(node)
        # calibrate_tree = dependency_tree_nodes + hardware_nodes + calibrate_factor_nodes
        return calibrate_tree

    def create_dependency_tree(self, entry):
        dependency_tree = []
        self._depends.entry = entry
        root_node = None
        for dependency in self._depends:
            count = 0
            if count == 0:
                root_node = entity.CalibrateFile.CalibrateFileRootNode(dependency.calibrate_parameter_id, entry)
                dependency_tree.append(root_node)
                count += 1
            elif count == 1:
                for segment in dependency.parameter_segments:
                    root_child_node = entity.CalibrateFile.CalibrateFileDependencyNode()
                    root_child_node.parameter_segment = segment
                    root_child_node.parameter_id = dependency.parameter_id
                    root_child_node.parameter_index = dependency.parameter_index
                    root_child_node.parent = root_node
                    dependency_tree.append(root_child_node)
                    count += 1
            else:
                for segment in dependency.parameter_segments:
                    child_node = entity.CalibrateFile.CalibrateFileDependencyNode()
                    child_node.parameter_id = dependency.parameter_id
                    child_node.parameter_index = dependency.parameter_index
                    child_node.parameter_segment = segment
                    for node in dependency_tree:
                        if child_node.parameter_index == node.parameter_segment.transfer_number:
                            child_node.parent = node
                            dependency_tree.append(child_node)
        return dependency_tree
        # root_nodes = self.get_root_nodes()
        # for root_node in root_nodes:
        #     dependency_tree.append(root_node)
        #     entry_dependency = self.find_entry_dependency(root_node.entry)
        #     for segment in entry_dependency.parameter_segments:
        #         child_node = entity.CalibrateFile.CalibrateFileDependencyNode(
        #             entry_dependency.parameter_id, entry_dependency.parameter_index, segment)
        #         child_node.parent = root_node
        #         dependency_tree.append(child_node)
        #         self._root_child_nodes.append(child_node)
        #     root_node.children = self._root_child_nodes
        # return dependency_tree

    def create_hardware_node(self, channel_index, dependency_tree_nodes):
        current_channel = None
        dependency_leaves_nodes = []
        for channel in self.channels:
            if channel.channel_index == channel_index:
                current_channel = channel
        for hardware in current_channel.channel_msgs.hardwares:
            for hardware_segment in hardware.hardware_segments:
                for dependency_node in dependency_tree_nodes:
                    if hardware.index == dependency_node.parameter_segment.transfer_number:
                        hardware_node = entity.CalibrateFile.CalibrateFileHardwareNode()
                        hardware_node.parent = dependency_node
                        hardware_node.index = hardware.index
                        hardware_node.segment = hardware_segment
                        dependency_leaves_nodes.append(hardware_node)
        return dependency_leaves_nodes

    def create_factor_node(self, channel_index, hardware_nodes):
        current_channel = None
        calibrate_factor_nodes = []
        for channel in self.channels:
            if channel_index == channel.channel_index:
                current_channel = channel
        calibrate_factors = enumerate(current_channel.channel_msgs.calibrate_factors)
        for calibrate_factor in calibrate_factors:
            for dependency_leaf_node in hardware_nodes:
                if calibrate_factor[0] == dependency_leaf_node.segment.transfer_number:
                    calibrate_factor_node = entity.CalibrateFile.CalibrateFileFactorNode()
                    calibrate_factor_node.content = calibrate_factor[1]
                    calibrate_factor_node.parent = dependency_leaf_node
                    calibrate_factor_nodes.append(calibrate_factor_node)
        return calibrate_factor_nodes

    # def get_child_nodes(self, parent_nodes):
    #     child_nodes = []
    #     for node in parent_nodes:
    #         if node.segment < 0:
    #             raise StopIteration
    #         else:
    #
    #
    # def get_root_nodes(self):
    #     root_nodes = []
    #     channels = self.channels
    #     for channel in channels:
    #         for calibrate_msg in channel.channel_msgs:
    #             root_node = \
    #     entity.CalibrateFile.CalibrateFileRootNode(calibrate_msg.calibrate_parameter_id, calibrate_msg.entry)
    #             root_nodes.append(root_node)
    #     return root_nodes
