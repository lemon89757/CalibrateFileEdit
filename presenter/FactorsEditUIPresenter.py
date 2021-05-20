class FactorsEditUIPresenter:   # TODO 可将MainUIPresenter作为editor(只作为转递信息的作用)传进来？ 将文件作为各种编辑器共同的属性（同一文件）会不会好一点（结构改变，需要大修改）？
    def __init__(self):
        self._editor = None
        self._view = None

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
        factors = []
        for entry in self._view.entries:
            factor = float(entry.get_text())
            factors.append(factor)
        return factors

    def show_two_curves(self):
        current_interval = self._editor.load_choosed_parameter_interval()
        current_factors = self._editor.load_current_factors()
        modified_factors = self.load_current_entry()
        modified_segment = [current_interval, modified_factors]
        current_segment = [current_interval, current_factors]
        self._editor.show_two_factors_curve(modified_segment, current_segment)

    def modify_factors(self):
        channel_index = self._editor.load_channel_index()
        calibrate_parameter_id = self._editor.load_choosed_calibrate_parameter()
        path = self._editor.load_parameter_node_path()
        current_factors = self._editor.load_current_factors()
        current_interval = self._editor.load_choosed_parameter_interval()
        segment = [current_interval, current_factors]
        modified_factors = self.load_current_entry()
        self._editor.modify_parameter_factors(channel_index, calibrate_parameter_id, path, segment, modified_factors)
        print("yes")

    def update_modified_factors(self):
        modified_factors = self.load_current_entry()
        self._editor.update_modified_factors(modified_factors)
