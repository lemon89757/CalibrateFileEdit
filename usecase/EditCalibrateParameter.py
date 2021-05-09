# -*- coding: utf-8 -*-
from intervals import FloatInterval
from entity.CalibrateFile import CalibrateParameterNode


# segment = [具体硬件分段，对应校正系数] eg:[FloatInterval('[0.0, 2.0]'), [0, 0, 0, 0, 0, 0.9570842738562383]]
class EditCalibrateParameter:
    def __init__(self):
        self._parameter_node = None

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
                parameter_node.parent = parent_node

    @staticmethod
    def delete_parameter_node(root_node, parameter_node):
        for node in root_node.descendants:
            if parameter_node == node:
                same_parent_node = parameter_node.siblings
                parent_node = parameter_node.parent
                parent_node.children = same_parent_node

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
                segment_in[1] = value
        self._parameter_node.parameter_segments = segments
        # segment = [具体硬件分段，对应校正系数] eg:[FloatInterval('[0.0, 2.0]'), [0, 0, 0, 0, 0, 0.9570842738562383]]

    def get_segments_dict(self):
        # 数据处理时的segment形式应该为[FloatInterval('[0.0, 2.0]'), [0, 0, 0, 0, 0, 0.9570842738562383]，此处理为方便显示时查找。
        segments = self._parameter_node.parameter_segments
        for segment in segments:
            interval = segment[0]
            factors = segment[1]
            segment = dict()
            segment[interval] = factors
        return segments
