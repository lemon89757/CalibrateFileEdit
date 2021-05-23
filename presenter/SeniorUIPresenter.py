from intervals import FloatInterval


class SeniorUIPresenter:
    def __init__(self):
        self._view = None
        self._segment_view = None
        self._factors_view = None
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

    @property
    def segment_view(self):
        return self._segment_view

    @segment_view.setter
    def segment_view(self, value):
        self._segment_view = value

    @property
    def factors_view(self):
        return self._factors_view

    @factors_view.setter
    def factors_view(self, value):
        self._factors_view = value

    @editor.setter
    def editor(self, value):
        self._editor = value

    def get_available_parameters(self):
        available_parameters = self._editor.get_available_parameters()
        return available_parameters

    def load_choosed_parameter(self):
        combobox = self._view.parameter_choose
        model = combobox.get_model()
        _iter = combobox.get_active_iter()
        choosed_parameter = model.get_value(_iter, 0)
        return choosed_parameter

    def get_root_node(self, parameter_id):
        root_node = self._editor.get_root_node(parameter_id)
        return root_node

    def get_depends_id(self, parameter_id):
        channel_index = self._editor.load_channel_index()
        depends_id = self._editor.get_depends_id(channel_index, parameter_id)
        return depends_id

    def load_choosed_segment(self):
        all_msg_tree_view = self._view.all_msg_scrolled_win.get_child()
        focus_segment = all_msg_tree_view.get_selection()
        model, _iter = focus_segment.get_selected()
        parameter_id = model.get_value(_iter, 0)
        segment_lower_num = model.get_value(_iter, 1)
        segment_upper_num = model.get_value(_iter, 2)
        return parameter_id, segment_lower_num, segment_upper_num

    def load_choosed_factors(self):
        all_msg_tree_view = self._view.all_msg_scrolled_win.get_child()
        focus_segment = all_msg_tree_view.get_selection()
        model, _iter = focus_segment.get_selected()
        factors = model.get_value(_iter, 3)
        return factors

    def load_choosed_path(self):
        path = []
        all_msg_tree_view = self._view.all_msg_scrolled_win.get_child()
        focus_segment = all_msg_tree_view.get_selection()
        model, _iter = focus_segment.get_selected()
        depth = model.iter_depth(_iter)

        current__id = model.get_value(_iter, 0)
        current_segment_lower_num = model.get_value(_iter, 1)
        current_segment_upper_num = model.get_value(_iter, 2)
        current_segment = FloatInterval.closed(current_segment_lower_num, current_segment_upper_num)
        path.insert(0, [current__id, current_segment])
        parent_iter = _iter
        for i in range(depth):
            parent_iter = model.iter_parent(parent_iter)
            parent_id = model.get_value(parent_iter, 0)
            parent_segment_lower_num = model.get_value(parent_iter, 1)
            parent_segment_upper_num = model.get_value(parent_iter, 2)
            parent_segment = FloatInterval.closed(parent_segment_lower_num, parent_segment_upper_num)
            path.insert(0, [parent_id, parent_segment])
        calibrate_parameter = self.load_choosed_parameter()
        path.insert(0, [calibrate_parameter, None])
        return path

    def load_segment_entries(self):
        interval_list = []
        for entry in self._segment_view.entries:
            num = float(entry.get_text())
            interval_list.append(num)
        lower_num = interval_list[0]
        upper_num = interval_list[1]
        interval = FloatInterval.closed(lower_num, upper_num)
        return interval

    def modify_segment(self):
        path = self.load_choosed_path()
        entry = self.load_segment_entries()
        modified_parameter_id = path[-1][0]
        current_choosed_calibrate_parameter = self.load_choosed_parameter()
        current_factors_str = self.load_choosed_factors()
        self._editor.modify_segment(current_choosed_calibrate_parameter, current_factors_str, modified_parameter_id,
                                    path, entry)

    def update_modified_segment(self):
        segment_entry = self.load_segment_entries()
        self._view.update_senior_ui_current_segment(segment_entry)

    def update_main_ui_from_senior(self):
        self._editor.update_main_ui_from_senior()

    def load_factors_entry(self):
        factors = []
        for entry in self._factors_view.entries:
            factor = float(entry.get_text())
            factors.append(factor)
        return factors

    def modify_factors(self):
        path = self.load_choosed_path()
        path = path[:-1]
        calibrate_parameter_id, lower_num, upper_num = self.load_choosed_segment()
        current_factors_str = self.load_choosed_factors()
        current_factors = eval(current_factors_str)
        current_interval = FloatInterval.closed(lower_num, upper_num)
        segment = [current_interval, current_factors]
        modified_factors = self.load_factors_entry()
        self._editor.modify_parameter_factors(calibrate_parameter_id, path, segment, modified_factors)

    def update_modified_factors(self):
        factors_entry = self.load_factors_entry()
        self._view.update_senior_ui_current_factors(factors_entry)

    def show_two_curves(self):
        _id, lower_num, upper_num = self.load_choosed_segment()
        current_interval = FloatInterval.closed(lower_num, upper_num)
        current_factors_str = self.load_choosed_factors()
        current_factors = eval(current_factors_str)
        modified_factors = self.load_factors_entry()
        modified_segment = [current_interval, modified_factors]
        current_segment = [current_interval, current_factors]
        self._editor.show_two_factors_curve(modified_segment, current_segment)

    def add_branch(self):
        path = self.load_choosed_path()
        calibrate_parameter_id = self.load_choosed_parameter()
        self._editor.add_branch(calibrate_parameter_id, path)
        self._view.update_senior_ui_edit_branch()

    def delete_branch(self):
        path = self.load_choosed_path()
        calibrate_parameter_id = self.load_choosed_parameter()
        self._editor.delete_branch(calibrate_parameter_id, path)
        self._view.update_senior_ui_edit_branch()

    def add_complete_branch(self):
        default_parameter_id = 2020
        calibrate_parameter_id = self.load_choosed_parameter()
        if calibrate_parameter_id == default_parameter_id:
            raise ValueError
        self._editor.add_complete_branch(calibrate_parameter_id)
        self._view.update_senior_ui_edit_branch()
