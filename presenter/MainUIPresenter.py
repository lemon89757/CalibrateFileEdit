from intervals import FloatInterval
from usecase.CurrentCalibrateFile import CalibrateFileEdit


class MainUIPresenter:
    def __init__(self):
        self._editor = CalibrateFileEdit()
        self._view = None

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, value):
        self._view = value

    def load_channels(self, file_path):
        self._editor.current_file_path = file_path
        channels = self._editor.get_file_channels()
        self._editor.current_channels = channels

    def get_channels(self):
        return self._editor.current_channels

    def get_chosen_channel(self, channel_index):
        channels = self.get_channels()
        chosen_channel = channels[channel_index]
        return chosen_channel

    def get_calibrate_model(self):
        parameter_id = self.load_chosen_calibrate_parameter()
        channel_index = self.load_channel_index()
        calibrate_model = self._editor.get_calibrate_model(parameter_id, channel_index)
        return calibrate_model

    def get_dependencies_list(self):
        parameter_id = self.load_chosen_calibrate_parameter()
        channel_index = self.load_channel_index()
        dependencies_list = self._editor.get_dependencies_list(parameter_id, channel_index)
        return dependencies_list

    def get_depends_id_in_main(self, parameter):
        channel_index = self.load_channel_index()
        chosen_channel = self.get_chosen_channel(channel_index)
        depends_id = self.get_depends_id(chosen_channel, parameter)
        return depends_id

    def get_depends_id(self, channel, parameter_id):
        depends_id = self._editor.get_depends_id(channel, parameter_id)
        return depends_id

    def load_depend_path(self, focus_depend_id):
        dependencies_segment_choose_scrolled_win = self._view.dependencies_segment_choose_scrolled_win
        viewport = dependencies_segment_choose_scrolled_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()

        calibrate_parameter = self.load_chosen_calibrate_parameter()
        depend_path = [[calibrate_parameter, None]]
        for box in boxes:
            children = box.get_children()
            label = children[0]
            depend_id = int(label.get_text())
            combobox = children[1]
            segment_activated = combobox.get_active()
            model = combobox.get_model()
            _iter = model.get_iter_from_string('{}'.format(segment_activated))
            segment_str = model.get_value(_iter, 0)
            segment = FloatInterval.from_string(segment_str)
            # print(label.get_text()) print(segment)
            depend_path.append([depend_id, segment])
            if depend_id == focus_depend_id:
                break
        return depend_path

    def load_parameter_node_path(self):
        viewport = self._view.dependencies_segment_choose_scrolled_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()
        calibrate_parameter = self.load_chosen_calibrate_parameter()
        parameter_path = [[calibrate_parameter, None]]
        for box in boxes:
            children = box.get_children()
            label = children[0]
            depend_id = int(label.get_text())
            combobox = children[1]
            segment_activated = combobox.get_active()
            model = combobox.get_model()
            _iter = model.get_iter_from_string('{}'.format(segment_activated))
            segment_str = model.get_value(_iter, 0)
            focus_segment = FloatInterval.from_string(segment_str)
            parameter_path.append([depend_id, focus_segment])
        return parameter_path

    def get_depend_segments(self, path, depend_id):
        channel_index = self.load_channel_index()
        chosen_channel = self.get_chosen_channel(channel_index)
        calibrate_parameter = self.load_chosen_calibrate_parameter()
        depend_segments = self._editor.get_depend_segments(chosen_channel, calibrate_parameter, path, depend_id)
        return depend_segments

    def get_calibrate_parameter_segments(self):
        calibrate_parameter = self.load_chosen_calibrate_parameter()
        parameter_path = self.load_parameter_node_path()
        channel_index = self.load_channel_index()
        chosen_channel = self.get_chosen_channel(channel_index)
        parameter_segments = self._editor.get_calibrate_parameter_segments(chosen_channel, calibrate_parameter,
                                                                           parameter_path)
        return parameter_segments

    def load_channel_index(self):
        channel_combobox = self._view.channel_combobox
        channel_activated = channel_combobox.get_active()
        model = channel_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(channel_activated))
        channel_index = model.get_value(_iter, 0)
        return channel_index

    def load_chosen_calibrate_parameter(self):
        calibrate_parameter_choose_combobox = self._view.calibrate_parameter_choose_combobox
        parameter_activated = calibrate_parameter_choose_combobox.get_active()
        model = calibrate_parameter_choose_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(parameter_activated))
        calibrate_parameter = model.get_value(_iter, 0)
        return calibrate_parameter

    def load_focus_depend(self):
        dependencies_segment_choose_scrolled_win = self._view.dependencies_segment_choose_scrolled_win
        viewport = dependencies_segment_choose_scrolled_win.get_child()
        main_box = viewport.get_child()

        focus_box = main_box.get_focus_child()
        focus_box_children = focus_box.get_children()
        focus_label = focus_box_children[0]
        focus_depend_id = int(focus_label.get_text())
        focus_combobox = focus_box_children[1]
        segment_activated = focus_combobox.get_active()
        model = focus_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(segment_activated))
        segment_str = model.get_value(_iter, 0)
        focus_segment = FloatInterval.from_string(segment_str)
        return focus_depend_id, focus_segment

    def load_last_dependency_segment(self):
        viewport = self._view.dependencies_segment_choose_scrolled_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()
        last_box = boxes[-1]
        last_combobox = last_box.get_children()[1]
        segment_activated = last_combobox.get_active()
        model = last_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(segment_activated))
        segment_str = model.get_value(_iter, 0)
        last_segment = FloatInterval.from_string(segment_str)
        return last_segment

    def load_chosen_parameter_interval_index(self):
        interval_combobox = self._view.calibrate_parameter_interval_choose_combobox
        interval_activated = interval_combobox.get_active()
        model = interval_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(interval_activated))
        interval_index = model.get_value(_iter, 0)
        return interval_index

    def load_chosen_parameter_interval(self):
        index = self.load_chosen_parameter_interval_index()
        segments = self.get_calibrate_parameter_segments()
        interval = segments[index][0]
        return interval

    def load_current_factors(self):
        text_view = self._view.factors_scrolled_win.get_child()
        buffer = text_view.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text = buffer.get_text(start_iter, end_iter, False)
        factors = eval(text)
        return factors

    def show_factors_curve(self):
        interval_index = self.load_chosen_parameter_interval_index()
        parameter_segments = self.get_calibrate_parameter_segments()
        segment = parameter_segments[interval_index]
        self._editor.show_current_factors_curve(segment)

    def modify_parameter_factors_in_main(self, calibrate_parameter_id, path, segment, modified_factors):
        channel_index = self.load_channel_index()
        channel = self.get_chosen_channel(channel_index)
        self._editor.modify_parameter_factors(channel, calibrate_parameter_id, path, segment, modified_factors)

    def save(self):
        self._editor.save()

    def save_as(self, file_path):
        self._editor.save_as(file_path)

    def update_modified_factors(self, new_factors):
        self._view.update_modified_factors_scrolled_win(new_factors)
        self._view.update_file_name_state()

    def show_two_factors_curve(self, modified_segment, current_segment):
        self._editor.show_two_factors_curve(modified_segment, current_segment)

    def modify_calibrate_parameter_interval_in_main(self, modified_interval):
        chosen_parameter = self.load_chosen_calibrate_parameter()
        path = self.load_parameter_node_path()
        segments = self.get_calibrate_parameter_segments()
        current_interval_index = self.load_chosen_parameter_interval_index()
        current_segment = segments[current_interval_index]
        channel_index = self.load_channel_index()
        chosen_channel = self.get_chosen_channel(channel_index)
        self._editor.modify_calibrate_parameter_interval(chosen_channel, chosen_parameter, path,
                                                         current_segment, modified_interval)

    def update_modified_interval(self, interval):
        self._view.update_modified_interval(interval)
        self._view.update_file_name_state()

    def load_chosen_dependency_segment(self, dependency_id):
        viewport = self._view.dependencies_segment_choose_scrolled_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()
        for box in boxes:
            children = box.get_children()
            label = children[0]
            depend = int(label.get_text())
            if dependency_id == depend:
                combobox = children[1]
                segment_activated = combobox.get_active()
                model = combobox.get_model()
                _iter = model.get_iter_from_string('{}'.format(segment_activated))
                segment_str = model.get_value(_iter, 0)
                segment = FloatInterval.from_string(segment_str)
                return segment

    def modify_dependency_segment(self, lower_num, upper_num, dependency_id):
        chosen_channel_index = self.load_channel_index()
        chosen_channel = self.get_chosen_channel(chosen_channel_index)
        calibrate_parameter = self.load_chosen_calibrate_parameter()
        dependency_path = self.load_depend_path(dependency_id)
        current_segment = self.load_chosen_dependency_segment(dependency_id)
        dependency_path.append([dependency_id, current_segment])
        self._editor.modify_depend_segment(chosen_channel, calibrate_parameter, lower_num, upper_num,
                                           dependency_path)

    def update_modified_dependency_segment(self, dependency_id, lower_num, upper_num):
        self._view.update_modified_depend_segment(dependency_id, lower_num, upper_num)
        self._view.update_file_name_state()

    def get_available_parameters(self):
        channel_index = self.load_channel_index()
        available_parameters = self._editor.get_available_parameters(channel_index)
        return available_parameters

    def get_root_node(self, channel, parameter_id):
        root_node = self._editor.get_root_node(channel, parameter_id)
        return root_node

    def modify_segment(self, channel, calibrate_parameter_id, modified_parameter_id, path, current_factors_str,
                       new_segment):
        if calibrate_parameter_id == modified_parameter_id:
            current_interval = path[-1][1]
            path = path[:-1]
            current_factors = eval(current_factors_str)
            current_segment = [current_interval, current_factors]
            new_interval = new_segment
            self._editor.modify_calibrate_parameter_interval(channel, calibrate_parameter_id, path,
                                                             current_segment, new_interval)
        else:
            # current_segment = path[-1][1]
            # path = path[:-1]
            self._editor.modify_depend_segment(channel, calibrate_parameter_id, new_segment.lower,
                                               new_segment.upper, path)

    def update_main_ui_from_senior(self):
        self._view.update_file_name_state()
        self._view.update_channel_combobox()

    def add_branch(self, channel, calibrate_parameter_id, path):
        self._editor.add_branch(channel, calibrate_parameter_id, path)

    def delete_branch(self, channel, calibrate_parameter_id, path):
        self._editor.delete_branch(channel, calibrate_parameter_id, path)

    def add_complete_branch(self, channel, calibrate_parameter_id):
        self._editor.add_complete_branch(channel, calibrate_parameter_id)

    def modify_parameter_factors_in_senior(self, channel, calibrate_parameter_id, path, segment, modified_factors):
        self._editor.modify_parameter_factors(channel, calibrate_parameter_id, path, segment, modified_factors)

    def confirm_in_senior(self, channel, channel_index):
        self._editor.confirm_in_senior(channel, channel_index)

    def add_dependency(self, channel, calibrate_parameter_id, dependency_in, pos, new_dependency):
        root_node = self.get_root_node(channel, calibrate_parameter_id)
        self._editor.add_depend(root_node, dependency_in, pos, new_dependency)

    def delete_dependency(self, channel, calibrate_parameter_id, dependency_id):
        root_node = self.get_root_node(channel, calibrate_parameter_id)
        self._editor.delete_depend(root_node, dependency_id)

    def load_other_file(self, file_path):
        self._editor.another_file_path = file_path

    def get_other_file_channels(self):
        channels = self._editor.get_other_file_channels()
        self._editor.another_channels = channels
        return channels

    def merge_parameter(self, merged_channel_index, other_channel_index, other_calibrate_parameter):
        self._editor.merge_calibrate_file_by_method_two(merged_channel_index, other_channel_index,
                                                        other_calibrate_parameter)

    def merge_channel(self, other_channel_index):
        self._editor.merge_calibrate_file_by_method_three(other_channel_index)

    def update_main_ui_from_merge(self):
        self._view.update_channel_combobox()
        self._view.update_file_name_state()

    def get_parameter_dict(self):
        parameter_dict = self._editor.get_parameter_dict()
        return parameter_dict
