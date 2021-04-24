# -*- coding: utf-8 -*-
from anytree import NodeMixin
from anytree import Node
from intervals import FloatInterval


class Segment:
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


class Factor:
    def __init__(self, content):
        self._content = content

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if type(value) != list:
            raise ValueError
        self._content = value


class CalibrateTreeNode(Segment, NodeMixin):
    def __init__(self, parameter_id=0, parameter_segment=None, parent=None, transfer_num=None, children=None):
        super(CalibrateTreeNode, self).__init__(parameter_id=parameter_id, parameter_segment=parameter_segment,
                                                transfer_num=transfer_num)
        super(Segment, self).__init__()
        self.parent = parent
        self._content = None
        if children:
            self.children = children

    @property
    def content(self):
        return self._content


class CalibrateLeavesNode(Factor, NodeMixin):
    def __init__(self, content=None, parent=None):
        super(CalibrateLeavesNode, self).__init__(content=content)
        super(Factor, self).__init__()
        self.parent = parent
        self._parameter_id = None
        self._parameter_segment = None

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


class CalibrateMsg:
    def __init__(self, parameter_id=0, dependency_list=None, calibrate_model=0, calibrate_tree=None):
        self._parameter_id = parameter_id
        self._dependency_list = dependency_list
        self._calibrate_model = calibrate_model
        self._calibrate_tree = calibrate_tree

    @property
    def calibrate_tree(self):
        return self._calibrate_tree

    @calibrate_tree.setter
    def calibrate_tree(self, value):
        if not all([isinstance(x, CalibrateTreeNode) or isinstance(x, CalibrateLeavesNode)
                    or isinstance(x, Node)for x in value]):
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

    def add_dependency(self, value):
        if isinstance(value, list):
            if not all([isinstance(x, CalibrateTreeNode) for x in value]):
                raise ValueError
            else:
                self._calibrate_tree += value
        elif isinstance(value, CalibrateTreeNode):
            self._calibrate_tree.append(value)
        else:
            raise ValueError

    def delete_dependency(self, value):
        if type(value) != CalibrateTreeNode:
            raise ValueError
        for node in self._calibrate_tree:
            if value.parameter_id == node.parameter_id and value.parent == node.parent and value.parameter_segment == node.parameter_segment:
                self._calibrate_tree.remove(node)

    def get_dependency_list(self):
        pass
