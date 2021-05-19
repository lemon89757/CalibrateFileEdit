# -*- coding: utf-8 -*-
import json
import os
import entity.CalibrateFile
from intervals import FloatInterval


class FileHandler:
    def __init__(self):
        self._json_handler = JsonHandler()
        self._sql_handler = None
        self._bin_handler = None

        self._file_path = 'file_path'

        self._calibrate_file = None
        self._current_calibrate_msg = None
        self._dependency_leaves = []
        self._parameter_nodes = []

        self._former_nodes_num = 0
        self._dependency_entry_list = []

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        if type(value) != str:
            raise ValueError
        self._file_path = value

    def save(self, calibrate_file):
        suffix = os.path.splitext(self.file_path)[-1]
        if suffix == '.json':
            self._json_handler.save(self._file_path, calibrate_file)
            print("save yes")
        if suffix == '.bin':
            pass
        if suffix == '.sql':
            pass

    def save_as(self, calibrate_file, file_path):  # TODO
        suffix = os.path.splitext(file_path)[-1]
        if suffix == '.json':
            self._json_handler.save(file_path, calibrate_file)

    # 校正文件生成部分
    def calibrate_msg_to_file_form(self, all_channel_msg):
        calibrate_file = dict()
        calibrate_file["channel_number"] = self.get_channel_number(all_channel_msg)
        calibrate_file["rev_depends"] = self.get_rev_depends(all_channel_msg)
        root_nodes = []
        for channel in all_channel_msg:
            for calibrate_msg in channel.values():
                root_nodes.append(calibrate_msg.calibrate_tree)
        calibrate_file["depends"] = self.depends_to_file_form(root_nodes)   # TODO 命名,依赖入口的生成考虑放在这里
        calibrate_file["channels"] = self.channels_to_file_form(all_channel_msg)
        return calibrate_file

    # 获取通道数量
    @staticmethod
    def get_channel_number(all_channel_msg):
        channel_number = len(all_channel_msg)
        return channel_number

    # 生成反向依赖
    @staticmethod
    def correct_rev_depends(rev_depends):  # 保证生成的反向依赖列表第一个元素为参数本身id
        for rev_depend in rev_depends:
            rev_depend_list = rev_depend[1]
            expect_parameter_id = rev_depend[0]
            dependency_parameter_id = rev_depend[1][0]
            if expect_parameter_id != dependency_parameter_id:
                rev_depend_list.remove(expect_parameter_id)
                rev_depend_list.insert(0, expect_parameter_id)
                rev_depend[1] = rev_depend_list

    def get_rev_depends(self, channels):  # TODO 反向依赖的生成
        rev_depends = []
        for channel in channels:
            for calibrate_msg in channel.values():
                root_node = calibrate_msg.calibrate_tree
                parameter_dependency_list = self.get_dependency_list(root_node)
                parameter_dependency_list.insert(0, calibrate_msg.parameter_id)
                for dependency_id in parameter_dependency_list:
                    if len(rev_depends) == 0:
                        rev_depend = [dependency_id, [dependency_id, calibrate_msg.parameter_id]]
                        rev_depend[1] = list(set(rev_depend[1]))
                        rev_depends.append(rev_depend)
                    else:
                        count = 0
                        for i in rev_depends:
                            parameter_id = i[0]
                            # rev_depend_list = i[1]
                            if dependency_id == parameter_id:
                                i[1].append(calibrate_msg.parameter_id)
                                i[1] = list(set(i[1]))
                            else:
                                count += 1
                        if count == len(rev_depends):
                            rev_depend = [dependency_id, [dependency_id, calibrate_msg.parameter_id]]
                            rev_depend[1] = list(set(rev_depend[1]))
                            rev_depends.append(rev_depend)
        self.correct_rev_depends(rev_depends)
        return rev_depends

    # 通道文件生成(先生成依赖文件再执行此步骤)
    # 依赖入口列表的生成是在depends_to_file中
    def channels_to_file_form(self, all_channel_msg):
        channels = []                             # 考虑0通道
        channel_0 = []
        channels.append(channel_0)
        for channel in all_channel_msg:
            channel_file = self.channel_to_file_form(channel)
            channels.append(channel_file)
        return channels

    def channel_to_file_form(self, channel):
        channel_to_file = []
        root_node_index = 0
        for calibrate_msg in channel.values():
            dependency_entry = self.get_dependency_entry(root_node_index)
            dependency_list = self.get_dependency_list(calibrate_msg.calibrate_tree)
            calibrate_model = calibrate_msg.calibrate_model
            join_parameters_list = calibrate_msg.join_parameters_list
            parameter_msg = self.get_hardware_list_and_calibrate_factors_list(calibrate_msg.calibrate_tree)
            hardware_segments_list = parameter_msg[0]
            calibrate_factors_list = parameter_msg[1]
            calibrate_msg_file = [calibrate_msg.parameter_id, dependency_entry, dependency_list, calibrate_model,
                                  join_parameters_list, hardware_segments_list, calibrate_factors_list]
            channel_to_file.append(calibrate_msg_file)
            root_node_index += 1
        return channel_to_file

    @staticmethod
    def get_hardware_list_and_calibrate_factors_list(root_node):
        hardware_list = []
        factor_list = []
        parameter_nodes = root_node.leaves
        transfer_num = 0
        for node in parameter_nodes:
            hardware = []
            for segment in node.parameter_segments:
                interval = segment[0]
                factors = segment[1]
                left_num = interval.lower
                right_num = interval.upper
                file_interval = [left_num, right_num]
                file_segment = [file_interval, transfer_num]
                hardware.append(file_segment)
                transfer_num += 1
                factor_list.append(factors)
            hardware_list.append(hardware)
        return hardware_list, factor_list

    def get_dependency_entry(self, root_node_index):
        dependency_entry = self._dependency_entry_list[root_node_index]
        return dependency_entry

    @staticmethod
    def get_dependency_list(root_node):
        dependency_list = []
        leaf_nodes = root_node.leaves
        one_leaf_node = leaf_nodes[0]
        one_branch = one_leaf_node.path
        one_dependency_branch = one_branch[1:-1]
        for dependency in one_dependency_branch:
            dependency_list.append(dependency.parameter_id)
        return dependency_list

    # 依赖文件生成
    def depends_to_file_form(self, root_nodes):  # TODO 公共树文件怎么生成
        depends = []
        for node in root_nodes:
            one_root_depends = self.root_depends_to_file_form(node)
            self.update_depends_transfer_num(one_root_depends, depends)
            entry = len(depends)
            self._dependency_entry_list.append(entry)
            depends += one_root_depends
        return depends

    @staticmethod
    def get_leaf_nodes_num(root_node):
        leaf_nodes = root_node.leaves
        leaf_nodes_num = len(leaf_nodes)
        return leaf_nodes_num

    def root_depends_to_file_form(self, root_node):
        self._former_nodes_num = 0
        leaf_nodes_num = self.get_leaf_nodes_num(root_node)
        root_depends = []
        parent_node = root_node
        # self.update_children_depends_transfer_num(parent_node)
        # children_nodes = parent_node.children
        # children_depend = self.children_depend_to_file_form(children_nodes)
        # depends.append(children_depend)
        parent_nodes = [parent_node]
        next_parent_nodes = []
        leaf_nodes_count = 0
        while True:
            for node in parent_nodes:
                try:
                    self.update_children_depends_transfer_num(node)
                    children_nodes = node.children
                    next_parent_nodes += children_nodes
                    children_depend = self.children_depend_to_file_form(children_nodes)
                    root_depends.append(children_depend)
                except ValueError:
                    leaf_nodes_count = leaf_nodes_count + len(node.children)
                    children_nodes = node.children
                    # next_parent_nodes += children_nodes
                    children_depend = self.children_depend_to_file_form(children_nodes)
                    root_depends.append(children_depend)
            if leaf_nodes_count == leaf_nodes_num:
                break
            parent_nodes = next_parent_nodes
        self.update_leaf_dependency_transfer_num(root_depends)
        return root_depends

    @staticmethod
    def update_leaf_dependency_transfer_num(root_depends):
        leaf_node_count = 0
        for depend in root_depends:
            for segment in depend[1]:
                if segment[1] < 0:
                    leaf_node_count += 1
                    segment[1] = -leaf_node_count

    @staticmethod
    def update_depends_transfer_num(root_depends, depends):  # root_depends放入depends前更新
        for depend in root_depends:
            segments = depend[1]
            for segment in segments:
                transfer_num = segment[1]
                if transfer_num > 0:
                    transfer_num = len(depends) + transfer_num
                    segment[1] = transfer_num
                elif transfer_num < 0:
                    pass
            depend[1] = segments

    @staticmethod
    def children_depend_to_file_form(children_nodes):  # 同一父结点的子依赖结点的to_file
        one_child_node = children_nodes[0]
        children_depend = [one_child_node.parameter_id, []]
        segments = children_depend[1]
        for node in children_nodes:
            left_num = node.parameter_segment.lower
            right_num = node.parameter_segment.upper
            interval = [left_num, right_num]
            transfer_num = node.transfer_num
            segment = [interval, transfer_num]
            segments.append(segment)
        return children_depend

    def update_children_depends_transfer_num(self, parent_node):
        children_nodes = list(parent_node.children)
        leaf_depend_node_count = 0
        child_node_count = 0
        for node in children_nodes:
            child_node_count += 1
            if node.height == 1:
                leaf_depend_node_count += 1
                node.transfer_num = -child_node_count
            else:
                node.transfer_num = self._former_nodes_num + child_node_count
        if leaf_depend_node_count == len(children_nodes):
            raise ValueError
        self._former_nodes_num += len(children_nodes)

    # 读取文件部分
    def get_calibrate_file(self, file_path):  # TODO
        suffix = os.path.splitext(file_path)[-1]
        if suffix == '.json':
            self._calibrate_file = self._json_handler.load(file_path)
            self._file_path = file_path
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
        msg.join_parameters_list = self.get_join_parameters_list()
        msg.parameter_id = parameter_id
        msg.dependency_list = self._current_calibrate_msg[2]
        msg.calibrate_model = self._current_calibrate_msg[3]
        return msg

    def load_all_calibrate_msg_from_file(self):  # TODO 未包含通道[]
        all_channel_msgs = []
        # channels = list(enumerate(self._calibrate_file[3]))
        # lambda函数、for i, k in enumerate(list)、 list.index(channels.index) enumerate(channels)后的对象不可channels[1:]
        channels = self._calibrate_file["channels"]
        for channel in channels[1:]:
            channel_msgs = {}
            channel_index = channels.index(channel)
            for calibrate_msg in channel:
                msg = self.load_calibrate_msg_from_file(channel_index, calibrate_msg[0])
                channel_msgs[calibrate_msg[0]] = msg
            all_channel_msgs.append(channel_msgs)
        return all_channel_msgs

    def get_calibrate_tree(self, channel_index, parameter_id):
        root_node = self.get_root_node(channel_index, parameter_id)
        parent_nodes = root_node.children
        while True:
            try:
                next_nodes = self.get_next_dependency_nodes(parent_nodes)
                parent_nodes = next_nodes
            except InterruptedError:
                break
        self.get_parameter_nodes()
        self.get_parameter_nodes_factors()
        return root_node

    def get_root_node(self, channel_index, parameter_id):
        file_channels = self._calibrate_file['channels']
        file_depends = self._calibrate_file['depends']
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

    def get_join_parameters_list(self):
        join_parameters_list = self._current_calibrate_msg[4]
        return join_parameters_list

    def get_next_dependency_nodes(self, parent_nodes):
        file_depends = self._calibrate_file['depends']
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
    def __init__(self, file_path=None):
        pass

    # @property
    # def file_path(self):
    #     return self._file_path
    #
    # @file_path.setter
    # def file_path(self, value):
    #     suffix = os.path.splitext(value)[-1]
    #     if suffix != '.json':
    #         raise ValueError
    #     self._file_path = value

    @staticmethod
    def load(file_path):
        with open(file_path) as file:
            calibrate_file = json.load(file)  # TODO json.decoder.JSONDecodeError
            # channel_number = data_json["channel_number"]
            # rev_depends = data_json["rev_depends"]
            # depends = data_json["depends"]
            # channels = data_json["channels"]
            # calibrate_file = [channel_number, rev_depends, depends, channels]
        return calibrate_file                # 直接返回一个字典

    @staticmethod
    def save(file_path, calibrate_file):
        json_file_data = json.dumps(calibrate_file)
        with open(file_path, 'w') as file:
            file.write(json_file_data)


class BinHandler:
    def __init__(self):
        pass


class SQLHandler:
    def __init__(self):
        pass
