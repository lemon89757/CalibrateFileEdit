# -*- coding: utf-8 -*-
from intervals import FloatInterval
from entity.CalibrateFile import CalibrateDependencyNode
from entity.CalibrateFile import CalibrateParameterNode
from usecase.EditCalibrateParameter import EditCalibrateParameter


class EditCalibrateParameterDepends:
    def __init__(self):
        self._root_node = None
        self._child_node = None

    @property
    def root_node(self):
        return self._root_node

    @root_node.setter
    def root_node(self, value):
        if not isinstance(value, CalibrateParameterNode):
            raise ValueError('node type is not CalibrateParameterNode')
        self._root_node = value

    def add_depend(self, parent_id, depend_id):
        for node in self._root_node.descendants:
            if parent_id == node.parameter_id:
                children_nodes = node.children
                node.children = []

                depend_node = CalibrateDependencyNode()
                depend_node.parameter_id = depend_id
                default_segment = FloatInterval.closed(float('-inf'), float('inf'))
                depend_node.parameter_segment = default_segment
                depend_node.parent = node
                depend_node.children = children_nodes

    def add_depends_segment_nodes_until_leaf(self, start_depend_node):
        self._child_node = None
        remain_branch_length = start_depend_node.height
        handler_parameter_node = EditCalibrateParameter()
        if remain_branch_length == 1:
            handler_parameter_node.parameter_node = start_depend_node.children[0]
            handler_parameter_node.add_parameter_segment()
        else:
            remain_branch_id = self.get_remain_branch_id(start_depend_node.parameter_id)
            parent_node = start_depend_node
            count = 1
            for i in range(remain_branch_length):
                if count < remain_branch_length:
                    child_id = remain_branch_id[count]
                    self.add_depend_segment_node(parent_node, child_id)
                    parent_node = self._child_node
                    count += 1
                elif count == remain_branch_length:
                    parameter_id = remain_branch_id[-1]
                    handler_parameter_node.add_parameter_node(parameter_id, parent_node)

    def add_depend_segment_node(self, parent_node, child_id, segment=FloatInterval.closed(float('-inf'), float('inf'))):
        # 当父节点在分支中的位置不是参数节点的前一级时，需考虑添加多级的分段
        child_node = CalibrateDependencyNode()
        child_node.parameter_segment = segment
        child_node.parameter_id = child_id
        child_node.parent = parent_node
        self._child_node = child_node

    def get_remain_branch_id(self, start_depend_id):
        complete_branch_id = []
        leaf_nodes = self._root_node.leaves
        a_leaf_node = leaf_nodes[0]
        a_branch_nodes = a_leaf_node.ancestors
        for node in a_branch_nodes:
            complete_branch_id.append(node.parameter_id)
        complete_branch_id.append(a_leaf_node.parameter_id)
        index = complete_branch_id.index(start_depend_id)
        return complete_branch_id[index:]

    def delete_depend(self, depend_id):   # 只是将所有该依赖的分段变为从负无穷至正无穷
        for node in self._root_node.descendants:
            if depend_id == node.parameter_id:
                segment = FloatInterval.closed(float('-inf'), float('inf'))
                node.parameter_segment = segment

    @staticmethod
    def delete_depend_segment(depend_node):
        same_parent_node = depend_node.siblings
        parent_node = depend_node.parent
        parent_node.children = same_parent_node

    @staticmethod
    def modify_depend_segment(lower_num, upper_num, depend_node):
        if not isinstance(depend_node, CalibrateDependencyNode):
            raise TypeError
        check_lower = isinstance(lower_num, int) or isinstance(lower_num, float)
        check_upper = isinstance(upper_num, int) or isinstance(upper_num, float)
        if not check_upper and not check_lower:
            raise ValueError('upper bound or lower bound type error')
        new_segment = FloatInterval.closed(lower_num, upper_num)
        depend_node.parameter_segment = new_segment

# a_branch_nodes = one_leaf_node.ancestors  # 分支节点中第一个为根节点
