import sqlite3
import anytree
import copy
from intervals import FloatInterval
from entity.CalibrateFile import CalibrateParameterNode, CalibrateDependencyNode, CalibrateMsg


class SQLHandler:
    def __init__(self):
        self._cursor = None
        self._conn = None
        self._nodes = None

        self._write_conn = None
        self._write_cursor = None

        self._depend_leaf_nodes_pos = None
        self._parameters = []

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

    def create_leaf_nodes(self, leaf_nodes_msg, parameter_id):
        leaf_nodes = {}
        for depend_id, msgs in leaf_nodes_msg.items():
            leaf_node = CalibrateParameterNode()
            segments = []
            for msg in msgs:
                section_id = msg[0]
                upper_num = msg[1]
                lower_num = msg[2]
                interval = FloatInterval.closed(lower_num, upper_num)
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

    def generate_no_depend_parameters_channel(self):
        channel = dict()
        record_values = self._cursor.execute('SELECT id, calibration_mode, calc_dep_id FROM parameters '
                                             'where depends_id IS NULL')
        record_values = record_values.fetchall()
        for value in record_values:
            parameter_id = value[0]
            calc_dep_id = value[2]
            calibration_mode = value[1]
            if calc_dep_id == 0:
                join_parameter_list = []
            else:
                join_parameter_list = []   # TODO 需要确定参与校正参数是什么，暂定为空
            calibrate_msg = CalibrateMsg()
            calibrate_msg.parameter_id = parameter_id
            calibrate_msg.calibrate_model = calibration_mode
            calibrate_msg.join_parameters_list = join_parameter_list
            channel[parameter_id] = calibrate_msg
        return channel

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
        one_unknown = 0
        if calc_dep_id == one_unknown:
            return join_parameter_list

    def generate_calibrate_tree(self, root_node, parameter_id, channel_order):
        root_node.parameter_id = parameter_id
        leaf_node_interval_msg = self.get_leaf_node_interval_msg(parameter_id, channel_order)
        leaf_nodes_msg = self.get_the_same_parent_node_interval_msg(leaf_node_interval_msg, channel_order,
                                                                    parameter_id)
        leaf_nodes = self.create_leaf_nodes(leaf_nodes_msg, parameter_id)
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

    def generate_channel(self, channel_msg, channel_order):
        channel = dict()
        for parameter_id, calibrate_msg in channel_msg.items():
            self._nodes = []
            root_node = CalibrateParameterNode()
            calibrate_msg.parameter_id = parameter_id
            calibrate_msg.calibrate_tree = root_node
            self.generate_calibrate_tree(root_node, parameter_id, channel_order)
            calibrate_msg.calibrate_model = self.get_calibrate_model(parameter_id)
            calibrate_msg.join_parameters_list = self.get_join_parameter_list(parameter_id)
            calibrate_msg.dependency_list = self.get_dependency_list(root_node)
            channel[parameter_id] = calibrate_msg
        return channel

    def load_all_calibrate_msg_from_db(self):
        all_calibrate_msg = []
        # empty_depend_channel = self.generate_no_depend_parameters_channel()  # TODO 暂未处理依赖为空的参数
        # all_calibrate_msg.append(empty_depend_channel)
        parameters_msg = self.get_parameters_from_table()
        channels_parameters_value = self.get_channels_parameters_value(parameters_msg)
        channels = self.generate_channels_msg(channels_parameters_value)
        for channel_order, channel_msg in channels.items():
            channel = self.generate_channel(channel_msg, channel_order)
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
                            is_leaf             INTEGER NOT NULL);''')
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

    def write_data_to_db(self, file_path, all_channels, save_type, rev_depends):
        if save_type == 'save':
            self.clear_db_all_table(file_path)
            self.write_data_to_parameters(file_path, all_channels)
            self.write_data_to_depends(all_channels)
            self.write_data_to_sections_and_coefficients(all_channels)
            self.write_data_to_rev_depends(rev_depends)
            self._write_conn.commit()
            self._write_conn.close()
        elif save_type == 'save_as':
            self.create_sql_file(file_path)
            self.write_data_to_parameters(file_path, all_channels)
            self.write_data_to_depends(all_channels)
            self.write_data_to_sections_and_coefficients(all_channels)
            self.write_data_to_rev_depends(rev_depends)
            self._write_conn.commit()
            self._write_conn.close()

    def write_data_to_parameters(self, file_path, all_channels):
        self._parameters = []
        self._write_conn = sqlite3.connect(file_path)
        self._write_cursor = self._write_conn.cursor()
        count = 0
        for channel in all_channels:
            for calibrate_msg in channel.values():
                if len(calibrate_msg.join_parameters_list) == 0:
                    calc_dep_id = 0
                else:
                    calc_dep_id = 1
                try:
                    self._write_cursor.execute("INSERT INTO parameters (id, depends_id, calibration_mode, calc_dep_id) "
                                               "VALUES (?, ?, ?, ?)", (calibrate_msg.parameter_id, count,
                                                                       calibrate_msg.calibrate_model, calc_dep_id))
                except sqlite3.IntegrityError:
                    pass                       # 略过相同参数
                else:
                    self._parameters.append(calibrate_msg.parameter_id)
                    root_node = calibrate_msg.calibrate_tree
                    step = len(root_node.descendants) - len(root_node.leaves)
                    count += step
            # TODO 数据库中校正模式不为-1和1（本来不是0和1吗？）是为什么？这些没有依赖的参数是不是应该放入0通道或者不用考虑（可以不放入参数表格中和通道信息中），
            #  因为校正文件中未含有该参数的完整校正信息。另外要是读json文件后写入db文件， 这时没有依赖的参数既没有校正模式也没有参与校正id怎么办？
            # TODO 暂未处理这种参数 （没有依赖的参数（即root_node.children为（））放入了通道中）

    def write_data_to_depends(self, all_channels):
        parameters = copy.deepcopy(self._parameters)
        self._depend_leaf_nodes_pos = []
        count = 0
        step = 0
        for channel in all_channels:
            for calibrate_msg in channel.values():
                if calibrate_msg.parameter_id not in parameters:
                    continue
                parameters.remove(calibrate_msg.parameter_id)
                parent_nodes = (calibrate_msg.calibrate_tree, )
                while True:
                    try:
                        next_time_parent_nodes = []
                        parent_count = 0
                        for parent_node in parent_nodes:
                            child_count = 0
                            for node in parent_node.children:
                                if node.depth == 1:
                                    self.write_depend_root_node_to_depends(node, count)
                                elif isinstance(node, CalibrateDependencyNode):
                                    step_sum = step + parent_count + child_count
                                    self.write_other_depend_node_to_depends(node, count, step_sum)
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

    def write_depend_root_node_to_depends(self, node, count):
        if node.height == 1:
            is_leaf = 1
            self._depend_leaf_nodes_pos.append(count)
        else:
            is_leaf = 0
        segment = node.parameter_segment
        self._write_cursor.execute("INSERT INTO depends (id, parameter_id, upper_bound,"
                                   " lower_bound, parent_id, is_leaf) VALUES (?, ?, ?, ?, ?, ?)",
                                   (count, node.parameter_id, segment.upper, segment.lower,
                                    count, is_leaf))

    def write_other_depend_node_to_depends(self, node, count, step):
        segment = node.parameter_segment
        if node.height == 1:
            is_leaf = 1
            self._depend_leaf_nodes_pos.append(count)
        else:
            is_leaf = 0
        self._write_cursor.execute("INSERT INTO depends (id, parameter_id, upper_bound,"
                                   " lower_bound, parent_id, is_leaf) VALUES (?, ?, ?, ?, ?, ?)",
                                   (count, node.parameter_id, segment.upper, segment.lower,
                                    count - step, is_leaf))

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
        depend_id = self.find_leaf_node_id(leaf_node.parameter_id, count)
        self._write_cursor.execute("INSERT INTO sections (id, parameter_id, depend_id, upper_bound, "
                                   "lower_bound, channel) VALUES (?, ?, ?, ?, ?, ?)",
                                   (leaf_intervals_count, leaf_node.parameter_id, depend_id, interval.upper,
                                    interval.lower, channel))

    def write_data_to_coefficients(self, factors, section_id):
        count = 6 * section_id
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

    def find_leaf_node_id(self, parameter_id, count):
        try:
            depend_id = self._depend_leaf_nodes_pos[count]
        except IndexError:
            _index = self._parameters.index(parameter_id)
            depend_id = self._depend_leaf_nodes_pos[_index]
        return depend_id


# if __name__ == '__main__':
#     file_path_1 = r'C:\Users\helloTt\Desktop\Mock-2021-01-20-18-02-39.db'
#     sql_handler = SQLHandler()
#     sql_handler.connect_db_file(file_path_1)
#     msg_1 = sql_handler.load_all_calibrate_msg_from_db()
#     channel_1 = msg_1[2]
#     msg_1 = channel_1[1252525]
#     root_node_1 = msg_1.calibrate_tree
#     for pre, _, node_1 in anytree.RenderTree(root_node_1):
#         treestr = u"%s%s" % (pre, node_1.parameter_id)
#         print(treestr.ljust(8), node_1.parameter_segment, node_1.parameter_segments)
