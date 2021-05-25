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
        if lower_num > upper_num:
            raise ValueError('输入区间不正确，上界比下界小')
        interval = FloatInterval.closed(lower_num, upper_num)
        return interval

    def modify_parameter_interval(self):
        modified_interval = self.load_current_entry()
        self._editor.modify_calibrate_parameter_interval_in_main(modified_interval)

    def update_modified_parameter_interval(self):
        self._editor.update_modified_interval()
