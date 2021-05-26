class MergeUIPresenter:
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

    def get_channels(self):
        channels = self._editor.get_channels()
        return channels

    def get_other_file_channels(self):
        channels = self._editor.get_other_file_channels()
        return channels

    def load_other_file(self, file_path):
        self._editor.load_other_file(file_path)

    def load_merged_channel_index(self):
        channel_combobox = self._view.chosen_merged_channel_index
        channel_activated = channel_combobox.get_active()
        model = channel_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(channel_activated))
        channel_index = model.get_value(_iter, 0)
        return channel_index

    def load_other_channel_index(self):
        channel_combobox = self._view.chosen_other_channel_index
        channel_activated = channel_combobox.get_active()
        model = channel_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(channel_activated))
        channel_index = model.get_value(_iter, 0)
        return channel_index

    def load_other_chosen_calibrate_parameter(self):
        parameter_combobox = self._view.chosen_other_calibrate_parameter
        parameter_activated = parameter_combobox.get_active()
        model = parameter_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(parameter_activated))
        parameter_id = model.get_value(_iter, 0)
        return parameter_id

    def confirm(self):
        other_calibrate_parameter = self.load_other_chosen_calibrate_parameter()
        other_channel_index = self.load_other_channel_index()
        merged_channel_index = self.load_merged_channel_index()
        default_parameter = 2020
        default_other_channel_index = 2020
        if other_calibrate_parameter == default_parameter or other_channel_index == default_other_channel_index:
            raise ValueError
        self._editor.merge(merged_channel_index, other_channel_index, other_calibrate_parameter)

    def update_main_ui(self):
        self._editor.update_main_ui_from_merge()
