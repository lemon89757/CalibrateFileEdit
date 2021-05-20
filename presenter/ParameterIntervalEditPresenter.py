from intervals import FloatInterval


class ParameterIntervalEditPresenter:
    def __init__(self):
        self._view = None
        self._editor = None

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, value):
        self._view = value

    @property
    def editor(self):
        return self._editor

    @editor.setter
    def editor(self, value):
        self._editor = value

    def load_current_entry(self):
        interval_list = []
        for entry in self._view.entries:
            num = float(entry.get_text())
            interval_list.append(num)
        lower_num = interval_list[0]
        upper_num = interval_list[1]
        interval = FloatInterval.closed(lower_num, upper_num)
        return interval

    def modify_parameter_interval(self):
        channel_index = self._editor.load_channel_index()
        choosed_parameter = self._editor.load_choosed_calibrate_parameter()
        path = self._editor.load_parameter_node_path()
        current_factors = self._editor.load_current_factors()
        current_interval = self._editor.load_choosed_parameter_interval()
        current_segment = [current_interval, current_factors]
        modified_interval = self.load_current_entry()
        self._editor.modify_calibrate_parameter_interval(channel_index, choosed_parameter, path, current_segment,
                                                         modified_interval)

    def update_modified_parameter_interval(self):
        self._editor.update_modified_interval()
