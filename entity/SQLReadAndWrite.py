import sqlite3
import anytree
import os
from intervals import FloatInterval, RangeBoundsException
from entity.CalibrateFile import CalibrateParameterNode, CalibrateDependencyNode, CalibrateMsg


class SQLHandler:
    def __init__(self):
        self._cursor = None
        self._conn = None
        self._nodes = None

        self._write_conn = None
        self._write_cursor = None

        self._depend_leaf_nodes_pos = None

    # 读取文件，生成cursor
    def connect_db_file(self, file_path):
        # try:
        self._conn = sqlite3.connect(file_path)
        self._cursor = self._conn.cursor()

    # 获取参数
    def get_parameters_from_table(self):
        self._cursor.execute('SELECT * FROM parameters')
        parameters_msg = self._cursor.fetchall()
        return parameters_msg

    # 获取参数所在的通道
    def get_channels_parameters_value(self, parameters_value):
        channels_parameters_value = dict()
        for value in parameters_value:
            parameter_id = value[0]
            self._cursor.execute('SELECT DISTINCT channel FROM sections '
                                 'where parameter_id = {}'.format(parameter_id))
            channels_parameters_value[parameter_id] = self._cursor.fetchall()
        return channels_parameters_value

    # 生成通道信息
    @staticmethod
    def generate_channels_msg(channels_parameters_value):
        channels = dict()
        for parameter_id, about_channel in channels_parameters_value.items():
            for channel_num in about_channel:
                parameter_calibrate_msg = CalibrateMsg()
                channel_key = channel_num[0]
                if channel_key in channels:
                    channel_msg = channels[channel_key]
                    channel_msg[parameter_id] = parameter_calibrate_msg
                else:
                    channel_msg = dict()
                    channel_msg[parameter_id] = parameter_calibrate_msg
                    channels[channel_key] = channel_msg
        return channels

    def get_leaf_node_interval_msg(self, parameter_id, channel):  # root_node.parameter_id
        msg_value = self._cursor.execute('SELECT id, upper_bound, lower_bound FROM sections '
                                         'where parameter_id = ? and channel = ?', (parameter_id, channel))
        interval_msg = msg_value.fetchall()
        return interval_msg

    def get_the_same_parent_node_interval_msg(self, interval_msg, channel, parameter_id):
        leaf_nodes_msg = dict()
        for msg in interval_msg:
            _id = msg[0]
            depend_id = self.get_depend_id_by_id_in_sections(_id)
            msg_value = self._cursor.execute('SELECT id, upper_bound, lower_bound FROM sections '
                                             'where depend_id=? and parameter_id=? and channel=?',
                                             (depend_id, parameter_id, channel))
            msg_value = msg_value.fetchall()
            leaf_nodes_msg[depend_id] = msg_value
        return leaf_nodes_msg

    def get_leaf_node_factors(self, section_id):
        factors_value = self._cursor.execute('SELECT coefficient FROM coefficients '
                                             'where section_id = {}'.format(section_id))
        factors = factors_value.fetchall()
        factors_list = []
        for factor in factors:
            factors_list.append(factor[0])
        return factors_list

    def create_leaf_nodes(self, leaf_nodes_msg, parameter_id, repeat_read):
        leaf_nodes = {}
        for depend_id, msgs in leaf_nodes_msg.items():
            leaf_node = CalibrateParameterNode()
            segments = []
            for msg in msgs:
                section_id = msg[0]
                upper_num = msg[1]
                lower_num = msg[2]
                if not repeat_read:
                    interval = FloatInterval.closed(lower_num, upper_num)
                else:
                    try:
                        interval = FloatInterval.closed(lower_num, upper_num)
                    except RangeBoundsException:
                        interval = FloatInterval.closed(lower_num, lower_num + 2)
                factors = self.get_leaf_node_factors(section_id)
                segment = [interval, factors]
                segments.append(segment)
                leaf_node.parameter_id = parameter_id
                leaf_node.parameter_segments = segments
                leaf_nodes[depend_id] = leaf_node
        return leaf_nodes

    def get_depend_id_by_id_in_sections(self, _id):
        _id_value = self._cursor.execute('SELECT depend_id FROM sections '
                                         'where id={}'.format(_id))
        depend_id = _id_value.fetchall()  # depend_id = [(2,)]
        depend_id = depend_id[0][0]
        return depend_id

    def get_record_by_id_in_depends(self, _id):
        record_value = self._cursor.execute('SELECT id, parameter_id, upper_bound, lower_bound, parent_id FROM depends '
                                            'where id={}'.format(_id))
        record = record_value.fetchall()  # record = [(0, 1250104, 10000, 1, 0)]
        record = record[0]
        return record

    # 生成校正树信息
    def find_node_by_record(self, record):
        upper_num = record[2]
        lower_num = record[3]
        segment = FloatInterval.closed(lower_num, upper_num)
        parameter_id = record[1]
        transfer_num = record[4]
        for node_i in self._nodes:
            if transfer_num == node_i.transfer_num and parameter_id == node_i.parameter_id and segment == \
                    node_i.parameter_segment:
                return node_i

    def link_leaf_node(self, leaf_nodes):
        depend_nodes = []
        for depend_id, leaf_node in leaf_nodes.items():
            record = self.get_record_by_id_in_depends(depend_id)
            depend_node = self.find_node_by_record(record)
            if not depend_node:
                depend_node = CalibrateDependencyNode()
                self._nodes.append(depend_node)
                depend_nodes.append(depend_node)
                upper_num = record[2]
                lower_num = record[3]
                depend_node.parameter_id = record[1]
                depend_node.parameter_segment = FloatInterval.closed(lower_num, upper_num)
                depend_node.transfer_num = record[4]
            leaf_node.parent = depend_node
        return depend_nodes

    def link_depend_node(self, depend_child_node):
        record = self.get_record_by_id_in_depends(depend_child_node.transfer_num)
        _id = record[0]
        parent_id = record[4]
        if parent_id == _id:
            raise StopIteration
        depend_node = self.find_node_by_record(record)
        if not depend_node:
            depend_node = CalibrateDependencyNode()
            self._nodes.append(depend_node)
            upper_num = record[2]
            lower_num = record[3]
            depend_node.parameter_id = record[1]
            depend_node.parameter_segment = FloatInterval.closed(lower_num, upper_num)
            depend_node.transfer_num = record[4]
        depend_child_node.parent = depend_node
        return depend_node

    def link_root_node(self, root_node, depend_nodes):
        for node in depend_nodes:
            record = self.get_record_by_id_in_depends(node.transfer_num)
            depend_node = self.find_node_by_record(record)
            if not depend_node:
                depend_node = CalibrateDependencyNode()
                upper_num = record[2]
                lower_num = record[3]
                depend_node.parameter_id = record[1]
                depend_node.parameter_segment = FloatInterval.closed(lower_num, upper_num)
                depend_node.transfer_num = record[4]
                self._nodes.append(depend_node)
            try:
                node.parent = depend_node
            except anytree.node.exceptions.LoopError:
                pass
            depend_node.parent = root_node

    @staticmethod
    def get_dependency_list(root_node):
        dependency_list = []
        leaf_nodes = root_node.leaves
        one_leaf_node = leaf_nodes[0]
        for node in one_leaf_node.path:
            dependency_list.append(node.parameter_id)
        dependency_list.pop()
        dependency_list.pop(0)
        return dependency_list

    def get_calibrate_model(self, parameter_id):
        model_value = self._cursor.execute('SELECT calibration_mode FROM parameters '
                                           'where id={}'.format(parameter_id))
        model = model_value.fetchall()
        model = model[0][0]
        return model

    def get_join_parameter_list(self, parameter_id):
        join_parameter_list = []
        calc_dep_id_value = self._cursor.execute('SELECT calc_dep_id FROM parameters '
                                                 'where id={}'.format(parameter_id))
        calc_dep_id = calc_dep_id_value.fetchall()
        calc_dep_id = calc_dep_id[0][0]
        if calc_dep_id:
            return join_parameter_list
        else:
            join_parameter_list.append(calc_dep_id)  # 暂时只考虑了参与校正参数只有一个的情况
            return join_parameter_list

    def generate_calibrate_tree(self, root_node, parameter_id, channel_order, repeat_read):
        root_node.parameter_id = parameter_id
        leaf_node_interval_msg = self.get_leaf_node_interval_msg(parameter_id, channel_order)
        leaf_nodes_msg = self.get_the_same_parent_node_interval_msg(leaf_node_interval_msg, channel_order,
                                                                    parameter_id)
        leaf_nodes = self.create_leaf_nodes(leaf_nodes_msg, parameter_id, repeat_read)
        depend_nodes = self.link_leaf_node(leaf_nodes)
        while True:
            next_depend_nodes = []
            count = 0
            for node in depend_nodes:
                try:
                    depend_node = self.link_depend_node(node)
                    next_depend_nodes.append(depend_node)
                except StopIteration:
                    count += 1
            if count == len(leaf_nodes):
                self.link_root_node(root_node, depend_nodes)
                break
            depend_nodes = next_depend_nodes

    def generate_channel(self, channel_msg, channel_order, repeat_read):
        channel = dict()
        for parameter_id, calibrate_msg in channel_msg.items():
            self._nodes = []
            root_node = CalibrateParameterNode()
            calibrate_msg.parameter_id = parameter_id
            calibrate_msg.calibrate_tree = root_node
            self.generate_calibrate_tree(root_node, parameter_id, channel_order, repeat_read)
            calibrate_msg.calibrate_model = self.get_calibrate_model(parameter_id)
            calibrate_msg.join_parameters_list = self.get_join_parameter_list(parameter_id)
            calibrate_msg.dependency_list = self.get_dependency_list(root_node)
            channel[parameter_id] = calibrate_msg
        return channel

    def load_all_calibrate_msg_from_db(self, repeat_read):
        all_calibrate_msg = []
        parameters_msg = self.get_parameters_from_table()
        channels_parameters_value = self.get_channels_parameters_value(parameters_msg)
        channels = self.generate_channels_msg(channels_parameters_value)
        for channel_order, channel_msg in channels.items():
            channel = self.generate_channel(channel_msg, channel_order, repeat_read)
            all_calibrate_msg.append(channel)
        self._conn.close()
        return all_calibrate_msg

    # 写入数据库文件
    @staticmethod
    def create_sql_file(file_path):
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE parameters
                            (id                 INTEGER PRIMARY KEY,
                            depends_id          INTEGER REFERENCES depends (id),
                            calibration_mode    INTEGER NOT NULL,
                            calc_dep_id         INTEGER);''')
        cursor.execute('''CREATE TABLE depends
                            (id                 INTEGER PRIMARY KEY
                                                        UNIQUE,
                            parameter_id        INTEGER NOT NULL
                                                        REFERENCES parameters (id),
                            upper_bound         DECIMAL NOT NULL,
                            lower_bound         DECIMAL NOT NULL,
                            parent_id           INTEGER NOT NULL,
                            is_leaf             INTEGER NOT NULL,
                            channel             INTEGER NOT NULL);''')
        cursor.execute('''CREATE TABLE sections
                            (id                 INTEGER PRIMARY KEY
                                                        UNIQUE,
                            parameter_id        INTEGER NOT NULL
                                                        REFERENCES parameters (id),
                            depend_id           INTEGER NOT NULL
                                                        REFERENCES depends (id),
                            upper_bound         DECIMAL NOT NULL,
                            lower_bound         DECIMAL NOT NULL,
                            channel             INTEGER NOT NULL);''')
        cursor.execute('''CREATE TABLE coefficients
                            (id                 INTEGER PRIMARY KEY
                                                        UNIQUE,
                            section_id          INTEGER REFERENCES sections (id)
                                                        NOT NULL,
                            coefficient         DECIMAL NUO NULL);''')
        cursor.execute('''CREATE TABLE rev_depends
                            (id                 INTEGER PRIMARY KEY
                                                        UNIQUE,
                            parameter_id        INTEGER REFERENCES parameters (id),
                            parent_id           INTEGER NOT NULL);''')
        conn.commit()
        conn.close()

    @staticmethod
    def clear_db_all_table(file_path):
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM parameters')
        cursor.execute('DELETE FROM depends')
        cursor.execute('DELETE FROM sections')
        cursor.execute('DELETE FROM coefficients')
        cursor.execute('DELETE FROM rev_depends')
        conn.commit()
        conn.close()

    def write_data_to_db(self, file_path, all_channels, save_type, rev_depends, load_file_path):
        suffix = os.path.splitext(load_file_path)[-1]
        if suffix == '.db':
            no_depend_parameters = self.get_no_depend_parameters(load_file_path)
        else:
            no_depend_parameters = self.find_no_depend_parameters(all_channels)
        if save_type == 'save':
            self.clear_db_all_table(file_path)
        elif save_type == 'save_as':
            self.create_sql_file(file_path)
        self.write_data_to_parameters(file_path, all_channels, no_depend_parameters, suffix)
        self.write_data_to_depends(all_channels)
        self.write_data_to_sections_and_coefficients(all_channels)
        self.write_data_to_rev_depends(rev_depends)
        self._write_conn.commit()
        self._write_conn.close()

    @staticmethod
    def get_no_depend_parameters(load_file_path):
        conn = sqlite3.connect(load_file_path)
        cursor = conn.cursor()
        parameters_value = cursor.execute('SELECT id, calibration_mode, calc_dep_id FROM parameters '
                                          'where depends_id IS NULL')
        parameters = parameters_value.fetchall()
        return parameters

    def write_no_depend_parameters(self, load_file_suffix, no_depend_parameters):
        if load_file_suffix == '.db':
            for parameter in no_depend_parameters:
                _id = parameter[0]
                calibration_mode = parameter[1]
                calc_id = parameter[2]
                self.write_to_parameters(_id, None, calibration_mode, calc_id)
        else:
            for parameter in no_depend_parameters:
                self.write_to_parameters(parameter, None, 0, None)          # 默认模式为0，参与校正id为空

    def write_data_to_parameters(self, file_path, all_channels, no_depend_parameters, load_file_suffix):
        self._write_conn = sqlite3.connect(file_path)
        self._write_cursor = self._write_conn.cursor()
        self.write_no_depend_parameters(load_file_suffix, no_depend_parameters)
        count = 0
        for channel in all_channels:
            for calibrate_msg in channel.values():
                if len(calibrate_msg.join_parameters_list) == 0:
                    calc_dep_id = 0
                else:
                    calc_dep_id = calibrate_msg.join_parameters_list[0]     # 暂时只考虑参与校正参数个数为1的情况
                try:
                    self.write_to_parameters(calibrate_msg.parameter_id, count, calibrate_msg.calibrate_model,
                                             calc_dep_id)
                except sqlite3.IntegrityError:
                    pass                                                    # 略过相同参数
                else:
                    root_node = calibrate_msg.calibrate_tree
                    step = len(root_node.descendants) - len(root_node.leaves)
                    count += step

    def write_to_parameters(self, _id, depend_entry, mode, calc_id):
        self._write_cursor.execute("INSERT INTO parameters (id, depends_id, calibration_mode, calc_dep_id) "
                                   "VALUES (?, ?, ?, ?)", (_id, depend_entry, mode, calc_id))

    def write_data_to_depends(self, all_channels):    # TODO
        self._depend_leaf_nodes_pos = []
        count = 0
        step = 0
        for channel in all_channels:
            channel_index = all_channels.index(channel)
            for calibrate_msg in channel.values():
                parent_nodes = (calibrate_msg.calibrate_tree, )
                while True:
                    try:
                        next_time_parent_nodes = []
                        parent_count = 0
                        child_count = 0
                        for parent_node in parent_nodes:
                            for node in parent_node.children:
                                if node.depth == 1:
                                    self.write_depend_root_node_to_depends(node, count, channel_index+1)
                                elif isinstance(node, CalibrateDependencyNode):
                                    step_sum = step - parent_count + child_count
                                    self.write_other_depend_node_to_depends(node, count, step_sum, channel_index+1)
                                elif isinstance(node, CalibrateParameterNode):
                                    raise TypeError
                                child_count += 1
                                count += 1
                            next_time_parent_nodes += list(parent_node.children)
                            parent_count += 1
                        parent_nodes = next_time_parent_nodes
                        step = len(parent_nodes)
                    except TypeError:
                        break

    def write_depend_root_node_to_depends(self, node, count, channel_index):
        if node.height == 1:
            is_leaf = 1
            self._depend_leaf_nodes_pos.append(count)
        else:
            is_leaf = 0
        segment = node.parameter_segment
        self._write_cursor.execute("INSERT INTO depends (id, parameter_id, upper_bound,"
                                   " lower_bound, parent_id, is_leaf, channel) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                   (count, node.parameter_id, segment.upper, segment.lower,
                                    count, is_leaf, channel_index))

    def write_other_depend_node_to_depends(self, node, count, step, channel_index):
        segment = node.parameter_segment
        if node.height == 1:
            is_leaf = 1
            self._depend_leaf_nodes_pos.append(count)
        else:
            is_leaf = 0
        self._write_cursor.execute("INSERT INTO depends (id, parameter_id, upper_bound,"
                                   " lower_bound, parent_id, is_leaf, channel) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                   (count, node.parameter_id, segment.upper, segment.lower,
                                    count - step, is_leaf, channel_index))

    def write_data_to_sections_and_coefficients(self, all_channels):
        leaf_intervals_count = 0
        channel_count = 1
        leaf_node_count = 0
        for channel in all_channels:
            for calibrate_msg in channel.values():
                root_node = calibrate_msg.calibrate_tree
                leaf_nodes = root_node.leaves
                for node in leaf_nodes:
                    for segment in node.parameter_segments:
                        interval = segment[0]
                        factors = segment[1]
                        self.write_data_to_coefficients(factors, leaf_intervals_count)
                        self.write_leaf_interval_to_section(node, channel_count, leaf_node_count,
                                                            interval, leaf_intervals_count)
                        leaf_intervals_count += 1
                    leaf_node_count += 1
            channel_count += 1

    def write_leaf_interval_to_section(self, leaf_node, channel, count, interval, leaf_intervals_count):
        # depend_id = self.find_leaf_node_id(leaf_node.parameter_id, count)
        depend_id = self._depend_leaf_nodes_pos[count]
        self._write_cursor.execute("INSERT INTO sections (id, parameter_id, depend_id, upper_bound, "
                                   "lower_bound, channel) VALUES (?, ?, ?, ?, ?, ?)",
                                   (leaf_intervals_count, leaf_node.parameter_id, depend_id, interval.upper,
                                    interval.lower, channel))

    def write_data_to_coefficients(self, factors, section_id):
        count = 6 * section_id                                  # 现在只考虑了6个校正系数的情况
        for factor in factors:
            self._write_cursor.execute("INSERT INTO coefficients (id, section_id, coefficient) VALUES (?, ?, ?)",
                                       (count, section_id, factor))
            count += 1

    def write_data_to_rev_depends(self, rev_depends):
        count = 0
        for value in rev_depends:
            dependency = value[0]
            rev_depend_list = value[1]
            for parameter in rev_depend_list:
                self._write_cursor.execute("INSERT INTO rev_depends (id, parameter_id, parent_id) VALUES (?, ?, ?)",
                                           (count, dependency, parameter))
                count += 1

    # def find_leaf_node_id(self, parameter_id, count):
    #     try:
    #         depend_id = self._depend_leaf_nodes_pos[count]
    #     except IndexError:
    #         _index = self._parameters.index(parameter_id)
    #         depend_id = self._depend_leaf_nodes_pos[_index]
    #     return depend_id

    def find_no_depend_parameters(self, all_channels):
        parameters = []
        for channel in all_channels:
            for calibrate_msg in channel.values():
                dependency_list = calibrate_msg.dependency_list
                for depend in dependency_list:
                    if depend not in parameters and depend not in channel:
                        parameters.append(depend)
        self.check_parameters(all_channels, parameters)
        return parameters

    @staticmethod
    def check_parameters(all_channels, parameters):
        for channel in all_channels:
            for parameter_id in channel.keys():
                if parameter_id in parameters:
                    parameters.remove(parameter_id)
