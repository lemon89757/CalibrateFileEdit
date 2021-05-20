from intervals import FloatInterval


class DependenciesEditUIPresenter:
    def __init__(self):
        self._editor = None
        self._view = None

    @property
    def editor(self):
        return self._editor

    @editor.setter
    def editor(self, value):
        self._editor = value

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, value):
        self._view = value

    def get_dependencies_id(self):
        channel_index = self._editor.load_channel_index()
        calibrate_parameter = self._editor.load_choosed_calibrate_parameter()
        dependencies_id = self._editor.get_depends_id(channel_index, calibrate_parameter)
        return dependencies_id

    def load_choosed_dependency(self):
        combobox = self._view.dependencies_choose
        parameter_activated = combobox.get_active()
        model = combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(parameter_activated))
        choosed_dependency = model.get_value(_iter, 0)
        return choosed_dependency

    def get_current_segment(self, choosed_dependency):
        segment = self._editor.load_choosed_dependency_segment(choosed_dependency)
        return segment

    def load_current_entry(self):
        segment_list = []
        for entry in self._view.entries:
            num = float(entry.get_text())
            segment_list.append(num)
        lower_num = segment_list[0]
        upper_num = segment_list[1]
        return lower_num, upper_num

    def modify_dependency_segment(self):
        lower_num, upper_num = self.load_current_entry()
        choosed_dependency = self.load_choosed_dependency()
        self._editor.modify_dependency_segment(lower_num, upper_num, choosed_dependency)

    def update_modified_dependency_segment(self):
        self._editor.update_modified_dependency_segment()
