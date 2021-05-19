# -*- coding: utf-8 -*-
import numpy as np
from matplotlib import pyplot as plt
from intervals import FloatInterval
from entity.CalibrateFile import CalibrateParameterNode


# segment = [具体硬件分段，对应校正系数] eg:[FloatInterval('[0.0, 2.0]'), [0, 0, 0, 0, 0, 0.9570842738562383]]
class EditCalibrateParameter:
    def __init__(self):
        self._parameter_node = None
        self._parameter_factors_before = None

    @property
    def parameter_node(self):
        return self._parameter_node

    @parameter_node.setter
    def parameter_node(self, value):
        if not isinstance(value, CalibrateParameterNode):
            raise ValueError
        self._parameter_node = value

    @staticmethod
    def add_parameter_node(parameter_id, root_node, parent_node):
        for node in root_node.descendants:
            if node == parent_node:
                default_interval = FloatInterval.closed(float('-inf'), float('inf'))
                default_factors = [0, 0, 0, 0, 0, 0]
                default_segment = [default_interval, default_factors]
                parameter_node = CalibrateParameterNode()
                parameter_node.parameter_id = parameter_id
                parameter_node.parameter_segments = []
                parameter_node.parameter_segments.append([default_segment])
                parameter_node.parent = node
        return root_node

    @staticmethod
    def delete_parameter_node(root_node, parameter_node):
        for node in root_node.descendants:
            if parameter_node == node:
                same_parent_node = node.siblings
                parent_node = node.parent
                parent_node.children = same_parent_node
        return root_node

    def add_parameter_segment(self, segment):
        calibrate_factors = segment[1]
        parameter_interval = segment[0]
        new_parameter_node = self.add_parameter_interval(parameter_interval, self._parameter_node)
        new_parameter_node = self.add_calibrate_factors(calibrate_factors, new_parameter_node)
        self._parameter_node = new_parameter_node

    @staticmethod
    def add_calibrate_factors(value, parameter_node):
        if len(value) != 6:
            raise TypeError
        if not all(isinstance(x, float) or isinstance(x, int) for x in value):
            raise ValueError
        segments = parameter_node.parameter_segments
        new_segment = segments[-1]
        new_segment[1] = value
        segments[-1] = new_segment
        parameter_node.parameter_segments = segments
        return parameter_node

    @staticmethod
    def add_parameter_interval(value, parameter_node):
        if type(value) != FloatInterval:
            raise ValueError
        segments = parameter_node.parameter_segments
        factors = []
        new_segment = [value, factors]
        segments.append(new_segment)
        parameter_node.parameter_segments = segments
        return parameter_node

    def delete_parameter_segment(self, segment):
        segments = self._parameter_node.parameter_segments
        for segment_in in segments:
            if segment == segment_in:
                segments.remove(segment_in)
        self._parameter_node.parameter_segments = segments

    def modify_parameter_interval(self, value, segment):
        if type(value) != FloatInterval:
            raise ValueError
        segments = self._parameter_node.parameter_segments
        for segment_in in segments:
            if segment == segment_in:
                segment_in[0] = value
        self._parameter_node.parameter_segments = segments

    def modify_parameter_factors(self, value, segment):
        if len(value) != 6:
            raise TypeError
        if not all(isinstance(x, float) or isinstance(x, int) for x in value):
            raise ValueError
        segments = self._parameter_node.parameter_segments
        for segment_in in segments:
            if segment == segment_in:
                self._parameter_factors_before = segment[1]
                segment_in[1] = value
        self._parameter_node.parameter_segments = segments
        # segment = [具体硬件分段，对应校正系数] eg:[FloatInterval('[0.0, 2.0]'), [0, 0, 0, 0, 0, 0.9570842738562383]]

    def get_segments_dict(self):
        # 数据处理时的segment形式应该为[FloatInterval('[0.0, 2.0]'), [0, 0, 0, 0, 0, 0.9570842738562383]，此处理为方便显示时查找。
        segments = self._parameter_node.parameter_segments
        segments_dict = dict()
        for segment in segments:
            interval = segment[0]
            factors = segment[1]
            segments_dict[interval] = factors
        return segments_dict

    @staticmethod
    def show_current_factors_curve(segment):
        parameter_interval = segment[0]
        upper_num = parameter_interval.upper
        lower_num = parameter_interval.lower
        calibrate_factors = segment[1]
        x = np.linspace(lower_num, upper_num, 1000)
        y = calibrate_factors[0] * x**5 + calibrate_factors[1] * x**4 + calibrate_factors[2] * x**3 \
            + calibrate_factors[3] * x**2 + calibrate_factors[4]*x + calibrate_factors[5]
        plt.figure(num='校正函数图像')
        plt.xlabel("calibrate parameter input")
        plt.ylabel("calibrate parameter output")
        plt.plot(x, y)
        plt.savefig(r"..\image\factors_curve.png")
        plt.cla()
        # plt.show()

    @staticmethod
    def show_two_factors_curve(modified_segment, current_segment):
        parameter_interval = modified_segment[0]
        upper_num = parameter_interval.upper
        lower_num = parameter_interval.lower
        calibrate_factors = modified_segment[1]
        x = np.linspace(lower_num, upper_num, 1000)
        y = calibrate_factors[0] * x ** 5 + calibrate_factors[1] * x ** 4 + calibrate_factors[2] * x ** 3 \
            + calibrate_factors[3] * x ** 2 + calibrate_factors[4] * x + calibrate_factors[5]
        before_modify_factors = current_segment[1]
        modify_before_y = \
            before_modify_factors[0] * x ** 5 + before_modify_factors[1] * x ** 4 + before_modify_factors[2] * x ** 3 \
            + before_modify_factors[3] * x ** 2 + before_modify_factors[4] * x + before_modify_factors[5]
        plt.figure(num='校正函数图像')
        plt.xlabel("calibrate parameter input")
        plt.ylabel("calibrate parameter output")
        plt.plot(x, y, 'r', label='modified curve')
        plt.plot(x, modify_before_y, 'b', label='curve before modified')
        plt.legend(loc='upper right')
        plt.savefig(r"..\image\two_factors_curves.png")
        plt.cla()
        # plt.show()
