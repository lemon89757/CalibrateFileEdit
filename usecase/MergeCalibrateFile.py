# -*- coding: utf-8 -*-
import json
from entity.FileHandler import FileHandler


class MergeCalibrateFile:
    def __init__(self):
        self._another_file = 'file_path'

    @property
    def another_file(self):
        return self._another_file

    @another_file.setter
    def another_file(self, value):
        if type(value) != str:
            raise ValueError('please input file path')
        self._another_file = value

    def get_another_file_channels_msg(self):
        file_handler = FileHandler()
        file_handler.get_calibrate_file(self._another_file)
        channels = file_handler.load_all_calibrate_msg_from_file()
        return channels

    def merge_by_method_one(self, merge_file_channels):
        # 直接将两个文件合并，通道数等于两文件通道数之和
        another_file_channels = self.get_another_file_channels_msg()
        new_channels = merge_file_channels + another_file_channels
        return new_channels

    def get_calibrate_msg(self, channel_index, parameter_id):
        file_handler = FileHandler()
        file_handler.get_calibrate_file(self._another_file)
        calibrate_msg = file_handler.load_calibrate_msg_from_file(channel_index, parameter_id)
        return calibrate_msg

    def merge_by_method_two(self, choose_merge_channel, another_file_channel_index, another_file_parameter_id):
        # 选择另一文件的某个校正信息放入合并文件的被选择通道中
        calibrate_msg = self.get_calibrate_msg(another_file_channel_index, another_file_parameter_id)
        exit_calibrate_parameter = []
        for key in choose_merge_channel.keys():
            exit_calibrate_parameter.append(key)
        if calibrate_msg.parameter_id in exit_calibrate_parameter:
            raise ValueError('该通道中已经存在此校正参数')
        choose_merge_channel[calibrate_msg.parameter_id] = calibrate_msg
        return choose_merge_channel

    def merge_by_method_three(self, choose_merge_channel, another_file_channel_index):
        # 选择另一文件中某个通道的全部信息放入合并文件的被选择通道中
        try:
            with open(self._another_file) as file:
                calibrate_file = json.load(file)
        except json.decoder.JSONDecodeError:
            raise ValueError('文件为空')
        another_file_channel = calibrate_file['channels'][another_file_channel_index]
        file_handler = FileHandler()
        file_handler.get_calibrate_file(self._another_file)
        for msg in another_file_channel:
            calibrate_msg = file_handler.load_calibrate_msg_from_file(another_file_channel_index, msg[0])
            exit_calibrate_parameter = []
            for key in choose_merge_channel.keys():
                exit_calibrate_parameter.append(key)
            if calibrate_msg.parameter_id in exit_calibrate_parameter:
                raise ValueError('该通道中已经存在校正参数{}'.format(calibrate_msg.parameter_id))
            choose_merge_channel[calibrate_msg.parameter_id] = calibrate_msg
        return choose_merge_channel
