# -*- coding: utf-8 -*-
import json
import os
import entity.CalibrateFile
from intervals import FloatInterval


class FileHandler:
    def __init__(self):
        self._json_handler = JsonHandler()
        self._sql_handler = None
        self._bin_handler = None

        self._calibrate_file = None
        self._calibrate_msgs = None
        self._hardwares = None
        self._segments = None

    def read(self, file_path):
        suffix = os.path.splitext(file_path[-1])
        if suffix == '.json':
            self._calibrate_file = self._json_handler.load(file_path)
            channel_number = self.get_channel_number()
            rev_depends = self.get_rev_depends()
            depends = self.get_depends()
            channels = self.get_channels()
            calibrate_file = [channel_number, rev_depends, depends, channels]
            return calibrate_file
        # elif suffix == '.bin':
        #     calibrate_file = self._bin_handler(file_path)
        #     return calibrate_file
        # elif suffix == '.sql':
        #     calibrate_file = self._sql_handler(file_path)
        #     return calibrate_file
        else:
            raise FileExistsError

    def save(self):
        pass

    def get_channel_number(self):
        channel_number = self._calibrate_file[0]
        return channel_number

    def get_rev_depends(self):
        rev_depends = []
        rev_depends_msgs = self._calibrate_file[1]
        for rev_depends_msg in rev_depends_msgs:
            unit = entity.CalibrateFile.RevDepend()
            unit.calibrate_parameter_id = rev_depends_msg[0]
            unit.rev_depends = rev_depends_msg[1]
            rev_depends.append(unit)
        return rev_depends

    def get_depends(self):
        depends = entity.CalibrateFile.Depends()
        depends_msgs = self._calibrate_file[2]
        depends_msgs = enumerate(depends_msgs)
        for depends_msg in depends_msgs:
            unit = entity.CalibrateFile.Depend()
            unit.parameter_index = depends_msg[0]
            msg = depends_msg[1]
            unit.parameter_id = msg[0]
            unit.parameter_segments = []
            segments = msg[1]
            for segment in segments:
                segment_unit = entity.CalibrateFile.DependencySegment()
                segment_unit.transfer_number = segment[1]
                segment_unit.segment = FloatInterval.closed(segment[0][0], segment[0][1])
                unit.parameter_segments.append(segment_unit)
            depends.append(unit)
        return depends

    def get_channels(self):  # 未算channels中[]
        channels = []
        channels_msgs = self._calibrate_file[3]
        channels_msgs = enumerate(channels_msgs)
        for channel_msgs in channels_msgs[1:]:
            unit = entity.CalibrateFile.Channel()
            unit.channel_index = channel_msgs[0]
            calibrate_msgs = channel_msgs[1]
            self._calibrate_msgs = enumerate(calibrate_msgs)
            unit.channel_msgs = self.transfer_calibrate_msgs()
            channels.append(unit)
        return channels

    def transfer_calibrate_msgs(self):
        calibrate_msgs = []
        for msg in self._calibrate_msgs:
            calibrate_msg_unit = entity.CalibrateFile.CalibrateMsg
            calibrate_msg_unit.index = msg[0]
            calibrate_msg = msg[1]
            calibrate_msg_unit.calibrate_parameter_id = calibrate_msg[0]
            calibrate_msg_unit.entry = calibrate_msg[1]
            calibrate_msg_unit.dependencies = calibrate_msg[2]
            calibrate_msg_unit.model = calibrate_msg[3]
            calibrate_msg_unit.join_parameters = calibrate_msg[4]
            calibrate_msg_unit.calibrate_factors = calibrate_msg[6]
            hardwares = calibrate_msg[5]
            self._hardwares = enumerate(hardwares)
            calibrate_msg_unit.hardwares = self.transfer_hardwares()
            calibrate_msgs.append(calibrate_msg_unit)
        return calibrate_msgs

    def transfer_hardwares(self):
        hardwares = []
        for hardware in self._hardwares:
            hardware_unit = entity.CalibrateFile.Hardware()
            hardware_unit.index = hardware[0]
            self._segments = hardware[1]
            hardware_unit.hardware_segments = self.transfer_hardware_segments()
            hardwares.append(hardware_unit)
        return hardwares

    def transfer_hardware_segments(self):
        hardware_segments = []
        for hardware_segment in self._segments:
            hardware_segment_unit = entity.CalibrateFile.HardwareSegment()
            hardware_segment_unit.transfer_number = hardware_segment[1]
            hardware_segment_unit.segment = FloatInterval.closed(hardware_segment[0][0], hardware_segment[0][1])
            hardware_segments.append(hardware_segment)
        return hardware_segments


class JsonHandler:
    def __init__(self):
        pass

    @staticmethod
    def load(file_path):
        with open(file_path) as file:
            data_json = json.load(file)  # TODO json.decoder.JSONDecodeError
            channel_number = data_json["channel_number"]
            rev_depends = data_json["rev_depends"]
            depends = data_json["depends"]
            channels = data_json["channels"]
            calibrate_file = [channel_number, rev_depends, depends, channels]
        return calibrate_file

    @staticmethod
    def save():
        pass
