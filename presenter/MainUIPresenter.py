from usecase.CurrentCalibrateFile import CalibrateFileEdit


class MainUIPresenter:
    def __init__(self):
        self._editor = CalibrateFileEdit()

    def load_channels(self, file_path):
        self._editor.file_path = file_path
        channels = self._editor.get_file_channels()
        self._editor.channels = channels

    def get_channels(self):
        return self._editor.channels

    def get_calibrate_model(self, parameter_id, channel_index):
        calibrate_model = self._editor.get_calibrate_model(parameter_id, channel_index)
        return calibrate_model

    def get_dependencies_list(self, parameter_id, channel_index):
        dependencies_list = self._editor.get_dependencies_list(parameter_id, channel_index)
        return dependencies_list

    def get_depends_id(self, channel_index, parameter):
        depends_id = self._editor.get_depends_id(channel_index, parameter)
        return depends_id

    def get_depend_parent_node(self, channel_index, calibrate_parameter_id, path, depend_id):
        channels = self._editor.channels
        choose_channel = channels[channel_index]
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
        depend_segments = self._editor.get_depend_segments(parent_node)
        return depend_segments

    def get_parameter_parent_node(self, channel_index, calibrate_parameter_id, path):
        channels = self._editor.channels
        choose_channel = channels[channel_index]
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
        parameter_segments = self._editor.get_parameter_segments(depend_leaf_node)
        return parameter_segments
