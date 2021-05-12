from usecase.CurrentCalibrateFile import CalibrateFileEdit


class MainUIPresenter:
    def __init__(self):
        self._editor = CalibrateFileEdit()

    def load_channels(self, file_path):
        self._editor.file_path = file_path
        channels = self._editor.get_file_channels()
        self._editor.channels = channels

    def get_channels(self):
        return self._editor.channels

    def get_calibrate_model(self, parameter_id, channel_index):
        calibrate_model = self._editor.get_calibrate_model(parameter_id, channel_index)
        return calibrate_model

    def get_dependencies_list(self, parameter_id, channel_index):
        dependencies_list = self._editor.get_dependencies_list(parameter_id, channel_index)
        return dependencies_list
