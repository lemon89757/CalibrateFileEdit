import copy
from intervals import FloatInterval


class SeniorUIPresenter:
    def __init__(self):
        self._view = None
        self._segment_view = None
        self._factors_view = None
        self._dependency_view = None
        self._editor = None

        self._channel = None

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

    @property
    def dependency_view(self):
        return self._dependency_view

    @dependency_view.setter
    def dependency_view(self, value):
        self._dependency_view = value

    @editor.setter
    def editor(self, value):
        self._editor = value

    def get_current_channel(self):
        channel_index = self._editor.load_channel_index()
        channel = self._editor.get_chosen_channel(channel_index)
        self._channel = copy.deepcopy(channel)

    def get_available_parameters(self):
        available_parameters = self._editor.get_available_parameters()
        return available_parameters

    def load_chosen_parameter(self):
        combobox = self._view.parameter_choose
        model = combobox.get_model()
        _iter = combobox.get_active_iter()
        chosen_parameter = model.get_value(_iter, 0)
        return chosen_parameter

    def get_root_node(self, parameter_id):
        root_node = self._editor.get_root_node(self._channel, parameter_id)
        return root_node

    def get_depends_id(self, parameter_id):
        depends_id = self._editor.get_depends_id(self._channel, parameter_id)
        return depends_id

    def load_chosen_segment(self):
        all_msg_tree_view = self._view.all_msg_scrolled_win.get_child()
        focus_segment = all_msg_tree_view.get_selection()
        model, _iter = focus_segment.get_selected()
        parameter_id = model.get_value(_iter, 0)
        segment_lower_num = model.get_value(_iter, 1)
        segment_upper_num = model.get_value(_iter, 2)
        return parameter_id, segment_lower_num, segment_upper_num

    def load_chosen_factors(self):
        all_msg_tree_view = self._view.all_msg_scrolled_win.get_child()
        focus_segment = all_msg_tree_view.get_selection()
        model, _iter = focus_segment.get_selected()
        factors = model.get_value(_iter, 3)
        return factors

    def load_chosen_path(self):
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
        calibrate_parameter = self.load_chosen_parameter()
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

    def modify_segment_in_senior(self):
        path = self.load_chosen_path()
        entry = self.load_segment_entries()
        modified_parameter_id = path[-1][0]
        current_chosen_calibrate_parameter = self.load_chosen_parameter()
        current_factors_str = self.load_chosen_factors()
        self._editor.modify_segment(self._channel, current_chosen_calibrate_parameter, modified_parameter_id,
                                    path, current_factors_str, entry)

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

    def modify_factors_in_senior(self):
        path = self.load_chosen_path()
        path = path[:-1]
        calibrate_parameter_id, lower_num, upper_num = self.load_chosen_segment()
        current_factors_str = self.load_chosen_factors()
        current_factors = eval(current_factors_str)
        current_interval = FloatInterval.closed(lower_num, upper_num)
        segment = [current_interval, current_factors]
        modified_factors = self.load_factors_entry()
        self._editor.modify_parameter_factors_in_senior(self._channel, calibrate_parameter_id,
                                                        path, segment, modified_factors)

    def update_modified_factors_in_senior(self):
        factors_entry = self.load_factors_entry()
        self._view.update_senior_ui_current_factors(factors_entry)

    def show_two_curves_in_senior(self):
        _id, lower_num, upper_num = self.load_chosen_segment()
        current_interval = FloatInterval.closed(lower_num, upper_num)
        current_factors_str = self.load_chosen_factors()
        current_factors = eval(current_factors_str)
        modified_factors = self.load_factors_entry()
        modified_segment = [current_interval, modified_factors]
        current_segment = [current_interval, current_factors]
        self._editor.show_two_factors_curve(modified_segment, current_segment)

    def add_branch(self):
        path = self.load_chosen_path()
        calibrate_parameter_id = self.load_chosen_parameter()
        self._editor.add_branch(self._channel, calibrate_parameter_id, path)
        self._view.update_senior_ui_add_branch()

    def delete_branch(self):
        path = self.load_chosen_path()
        calibrate_parameter_id = self.load_chosen_parameter()
        self._editor.delete_branch(self._channel, calibrate_parameter_id, path)
        self._view.update_senior_ui_delete_branch()

    def add_complete_branch(self):
        default_parameter = 2020
        calibrate_parameter_id = self.load_chosen_parameter()
        if calibrate_parameter_id == default_parameter:
            raise ValueError
        self._editor.add_complete_branch(self._channel, calibrate_parameter_id)
        self._view.update_senior_ui_edit_branch()

    def confirm_in_senior(self):
        channel_index = self._editor.load_channel_index()
        self._editor.confirm_in_senior(self._channel, channel_index)

    def load_add_dependency_ui_msg(self):
        pos_combobox = self._dependency_view.chosen_pos
        pos_active = pos_combobox.get_active()
        model = pos_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(pos_active))
        chosen_pos = model.get_value(_iter, 0)  # 0表示前， 1表示后

        # dependency_combobox = self._dependency_view.chosen_dependency
        # dependency_active = dependency_combobox.get_active()
        # model = dependency_combobox.get_model()
        # _iter = model.get_iter_from_string('{}'.format(dependency_active))
        # chosen_dependency = model.get_value(_iter, 0)
        dependency_label = self._dependency_view.chosen_dependency
        chosen_dependency = int(dependency_label.get_text())

        entry = self._dependency_view.entry_id
        entry_id = int(entry.get_text())
        return chosen_dependency, chosen_pos, entry_id

    def confirm_add_dependency(self):
        chosen_dependency, chosen_pos, new_dependency = self.load_add_dependency_ui_msg()
        calibrate_parameter = self.load_chosen_parameter()
        depends_id = self.get_depends_id(calibrate_parameter)
        if new_dependency in depends_id:
            raise ValueError('已存在此依赖')
        self._editor.add_dependency(self._channel, calibrate_parameter, chosen_dependency, chosen_pos, new_dependency)

    def update_add_or_delete_dependency_in_senior_ui(self):
        calibrate_parameter_id = self.load_chosen_parameter()
        self._view.update_dependencies_scrolled_win(calibrate_parameter_id)
        self._view.update_all_msg_scrolled_win(calibrate_parameter_id)

    def load_dependencies_scrolled_win_chosen(self):
        dependencies_scrolled_win = self._view.dependencies_scrolled_win.get_child()
        focus = dependencies_scrolled_win.get_selection()
        model, _iter = focus.get_selected()
        depend_id = model.get_value(_iter, 0)
        return depend_id

    def delete_dependency(self):
        calibrate_parameter_id = self.load_chosen_parameter()
        depend_id = self.load_dependencies_scrolled_win_chosen()
        self._editor.delete_dependency(self._channel, calibrate_parameter_id, depend_id)

    def check_same_segment(self):
        pass
