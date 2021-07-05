# -*- coding: utf-8 -*-
import os
import pandas as pd
from entity.SQLReadAndWrite import SQLHandler
from entity.JsonBinReadAndWrite import JsonBinHandler


class FileRW:
    def __init__(self):
        self._json_bin_handler = JsonBinHandler()
        self._sql_handler = SQLHandler()

        self._file_path = 'file_path'
        self._load_file_suffix = None

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        if type(value) != str:
            raise ValueError
        self._file_path = value

    # 文件保存部分
    def save(self, channels):
        suffix = os.path.splitext(self.file_path)[-1]
        if suffix == '.json' or suffix == '.bin':
            calibrate_file = self._json_bin_handler.calibrate_msg_to_file_form(channels)
            self._json_bin_handler.save(self._file_path, suffix, calibrate_file)
        elif suffix == '.db':
            rev_depends = self._json_bin_handler.get_rev_depends(channels)
            save_type = 'save'
            self._sql_handler.write_data_to_db(self._file_path, channels, save_type, rev_depends, self._file_path)

    def save_as(self, channels, file_path, load_file_path):
        suffix = os.path.splitext(file_path)[-1]
        if suffix == '.json' or suffix == '.bin':
            calibrate_file = self._json_bin_handler.calibrate_msg_to_file_form(channels)
            self._json_bin_handler.save(file_path, suffix, calibrate_file)
        elif suffix == '.db':
            rev_depends = self._json_bin_handler.get_rev_depends(channels)
            save_type = 'save_as'
            self._sql_handler.write_data_to_db(file_path, channels, save_type, rev_depends, load_file_path)

    # 读取文件部分
    def get_calibrate_file(self, file_path):
        suffix = os.path.splitext(file_path)[-1]
        self._load_file_suffix = suffix
        if suffix == '.json' or suffix == '.bin':
            calibrate_file = self._json_bin_handler.load(file_path, suffix)
            self._json_bin_handler.calibrate_file = calibrate_file
            self._file_path = file_path
        elif suffix == '.db':
            self._sql_handler.connect_db_file(file_path)
            self._file_path = file_path
        else:
            raise FileExistsError

    def load_all_calibrate_msg_from_file(self):  # 未包含通道[]
        if self._load_file_suffix == '.db':
            all_channel_msgs = self._sql_handler.load_all_calibrate_msg_from_db()
        else:
            all_channel_msgs = self._json_bin_handler.load_all_calibrate_msg_from_file()
        return all_channel_msgs

    # 获取与参数ID对应参数名的文件信息
    @staticmethod
    def get_parameter_dict():
        sheet_in_file = pd.read_excel(r'document\ParameterName_ID.xlsx', sheet_name='Sheet1', dtype={'属性ID': 'Int64'})
        sheet_in_file = sheet_in_file.dropna(axis=0, how='all')
        parameter_dict = dict()
        for index_ in sheet_in_file.index:
            parameter_dict[sheet_in_file.loc[index_].values[1]] = sheet_in_file.loc[index_].values[0]
        return parameter_dict
