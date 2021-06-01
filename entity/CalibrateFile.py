# -*- coding: utf-8 -*-
from anytree import NodeMixin
from intervals import FloatInterval


class Dependency:
    def __init__(self, parameter_id=0, parameter_segment=None, transfer_num=None):
        self._parameter_id = parameter_id
        self._parameter_segment = parameter_segment
        self._transfer_num = transfer_num

    @property
    def parameter_id(self):
        return self._parameter_id

    @parameter_id.setter
    def parameter_id(self, value):
        if type(value) != int:
            raise ValueError
        self._parameter_id = value

    @property
    def parameter_segment(self):
        return self._parameter_segment

    @parameter_segment.setter
    def parameter_segment(self, value):
        if not isinstance(value, FloatInterval):
            raise ValueError
        self._parameter_segment = value

    @property
    def transfer_num(self):
        return self._transfer_num

    @transfer_num.setter
    def transfer_num(self, value):
        if type(value) != int:
            raise ValueError
        self._transfer_num = value


class CalibrateParameter:
    def __init__(self, parameter_id=0, parameter_segments=None):
        self._parameter_id = parameter_id
        self._parameter_segments = parameter_segments

    @property
    def parameter_id(self):
        return self._parameter_id

    @parameter_id.setter
    def parameter_id(self, value):
        if type(value) != int:
            raise ValueError
        self._parameter_id = value

    @property
    def parameter_segments(self):
        return self._parameter_segments

    @parameter_segments.setter
    def parameter_segments(self, value):
        if not all([isinstance(x, list) for x in value]):
            raise ValueError
        self._parameter_segments = value


class CalibrateDependencyNode(Dependency, NodeMixin):
    def __init__(self, parameter_id=0, parameter_segment=None, parent=None, transfer_num=None, children=None):
        super(CalibrateDependencyNode, self).__init__(parameter_id=parameter_id, parameter_segment=parameter_segment,
                                                      transfer_num=transfer_num)
        super(Dependency, self).__init__()
        self.parent = parent
        if children:
            self.children = children
        self.parameter_segments = None


class CalibrateParameterNode(CalibrateParameter, NodeMixin):
    def __init__(self, parameter_id=0, parameter_segments=None, parent=None, children=None):
        super(CalibrateParameterNode, self).__init__(parameter_id=parameter_id, parameter_segments=parameter_segments)
        super(CalibrateParameter, self).__init__()
        self.parent = parent
        if children:
            self.children = children
        self.parameter_segment = None


class CalibrateMsg:
    def __init__(self, parameter_id=0, dependency_list=None, calibrate_model=0, calibrate_tree=None):
        self._parameter_id = parameter_id
        self._dependency_list = dependency_list
        self._calibrate_model = calibrate_model   # 没有校正模式的更改
        self._join_parameters_list = None         # 没有参与校正参数的更改
        self._calibrate_tree = calibrate_tree

    @property
    def calibrate_tree(self):
        return self._calibrate_tree

    @calibrate_tree.setter
    def calibrate_tree(self, value):
        if not isinstance(value, CalibrateParameterNode):
            raise ValueError
        self._calibrate_tree = value

    @property
    def parameter_id(self):
        return self._parameter_id

    @parameter_id.setter
    def parameter_id(self, value):
        if type(value) != int:
            raise ValueError
        self._parameter_id = value

    @property
    def dependency_list(self):
        return self._dependency_list

    @dependency_list.setter
    def dependency_list(self, value):
        if type(value) != list:
            raise ValueError
        self._dependency_list = value

    @property
    def calibrate_model(self):
        return self._calibrate_model

    @calibrate_model.setter
    def calibrate_model(self, value):
        if type(value) != int:
            raise ValueError
        self._calibrate_model = value

    @property
    def join_parameters_list(self):
        return self._join_parameters_list

    @join_parameters_list.setter
    def join_parameters_list(self, value):
        if type(value) != list:
            raise ValueError
        self._join_parameters_list = value
