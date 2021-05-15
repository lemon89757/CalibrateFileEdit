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

    def get_calibrate_model(self, parameter_id, channel_index):
        calibrate_model = self._editor.get_calibrate_model(parameter_id, channel_index)
        return calibrate_model

    def get_dependencies_list(self, parameter_id, channel_index):
        dependencies_list = self._editor.get_dependencies_list(parameter_id, channel_index)
        return dependencies_list

    def get_depends_id(self, channel_index, parameter):
        depends_id = self._editor.get_depends_id(channel_index, parameter)
        return depends_id

    def get_depend_path(self, focus_depend_id):
        dependencies_segment_choose_scrolled_win = self._view.dependencies_segment_choose_scrolled_win
        viewport = dependencies_segment_choose_scrolled_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()

        calibrate_parameter = self.get_choosed_calibrate_parameter()
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

    def get_parameter_node_path(self):
        viewport = self._view.dependencies_segment_choose_scrolled_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()
        calibrate_parameter = self.get_choosed_calibrate_parameter()
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

    def get_depend_segments(self, channel_index, calibrate_parameter, path, depend_id):
        depend_segments = self._editor.get_depend_segments(channel_index, calibrate_parameter, path, depend_id)
        return depend_segments

    def get_calibrate_parameter_segments(self, channel_index, calibrate_parameter, parameter_path):
        parameter_segments = self._editor.get_calibrate_parameter_segments(channel_index, calibrate_parameter,
                                                                           parameter_path)
        return parameter_segments

    def get_channel_index(self):
        channel_combobox = self._view.channel_combobox
        channel_activated = channel_combobox.get_active()
        model = channel_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(channel_activated))
        channel_index = model.get_value(_iter, 0)
        return channel_index

    def get_choosed_calibrate_parameter(self):
        calibrate_parameter_choose_combobox = self._view.calibrate_parameter_choose_combobox
        parameter_activated = calibrate_parameter_choose_combobox.get_active()
        model = calibrate_parameter_choose_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(parameter_activated))
        calibrate_parameter = model.get_value(_iter, 0)
        return calibrate_parameter

    def get_focus_depend(self):
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

    def get_choosed_parameter_interval(self):
        interval_combobox = self._view.calibrate_parameter_interval_choose_combobox
        interval_activated = interval_combobox.get_active()
        model = interval_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(interval_activated))
        interval_str = model.get_value(_iter, 0)
        interval = FloatInterval.from_string(interval_str)
        return interval
