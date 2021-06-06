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
        parameter_id = self._editor.load_chosen_calibrate_parameter()
        dependencies_id = self._editor.get_depends_id_in_main(parameter_id)
        return dependencies_id

    def load_chosen_dependency(self):
        combobox = self._view.dependencies_choose
        parameter_activated = combobox.get_active()
        model = combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(parameter_activated))
        chosen_dependency = model.get_value(_iter, 0)
        return chosen_dependency

    def get_current_segment(self, chosen_dependency):
        segment = self._editor.load_chosen_dependency_segment(chosen_dependency)
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
        chosen_dependency = self.load_chosen_dependency()
        self._editor.modify_dependency_segment(lower_num, upper_num, chosen_dependency)

    def update_modified_dependency_segment(self):
        chosen_dependency = self.load_chosen_dependency()
        lower_num, upper_num = self.load_current_entry()
        self._editor.update_modified_dependency_segment(chosen_dependency, lower_num, upper_num)
