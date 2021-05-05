def get_depends(self, calibrate_tree):
    depends = []
    one_node = calibrate_tree[1]
    root_node = one_node.root
    leaf_nodes = root_node.leaves
    for node in leaf_nodes:
        branch_depends = self.a_branch_depends_to_file(node)
        depends.append(branch_depends)
    one_branch = depends[0]
    merge_pos_order = list(range(len(one_branch)))
    merge_pos_order.reverse()
    for order in merge_pos_order:
        for branch in depends:
            remain_depends = copy.deepcopy(depends)
            remain_depends.remove(branch)
            for else_branch in remain_depends:
                try:
                    branch_sum = self.merge_two_branch_depends(branch, else_branch, order)
                    depends.append(branch_sum)
                    depends.remove(branch)
                    depends.remove(else_branch)
                except ValueError:
                    pass
    return depends


def merge_two_branch_depends(self, branch_depends_1, branch_depends_2, pos):
    count = 0
    remain_depends_2 = []
    for value in branch_depends_1:
        if value == branch_depends_2[count]:
            count += 1
        elif count < len(branch_depends_1):
            if count != pos:
                raise ValueError
            else:
                depend_2 = branch_depends_2[count]
                if value[0] == depend_2[0]:
                    remain_depends_2 = branch_depends_2[count + 1:]
                    count += len(branch_depends_1)
                    value[1] = self.add_segment_to_segments(depend_2[1], value[1], 1)
                    break
                else:
                    raise TypeError
    branch_depends_1.append(remain_depends_2)
    branch_depends_1.remove([])
    return branch_depends_1


@staticmethod
def next_node(nodes, node):
    count = 0
    for i in nodes:
        count += 1
        if i == node:
            return nodes[count]


def a_branch_depends_to_file(self, leaf_node):
    leaf_ancestors = leaf_node.ancestors
    a_branch_depends = []  # 一个分支的依赖
    for node in leaf_ancestors[1:]:
        left_index = node.parameter_segment.lower
        right_index = node.parameter_segment.upper
        transfer_num = None
        segment = [[left_index, right_index], transfer_num]
        current_dependency = [node.parameter_id, segment]

        if not node == leaf_ancestors[-1]:
            next_one = self.next_node(leaf_ancestors, node)
            next_left_index = next_one.parameter_segment.lower
            next_right_index = next_one.parameter_segment.upper
            next_transfer_num = None
            next_segment = [[next_left_index, next_right_index], next_transfer_num]
            next_dependency = [next_one.parameter_id, next_segment]

            next_dependency_pos = self.get_next_dependency_pos(next_dependency, a_branch_depends)
            self.add_current_dependency_to_branch_depends(current_dependency, a_branch_depends, next_dependency_pos)
        else:
            self.add_current_dependency_to_branch_depends(current_dependency, a_branch_depends, None)
    return a_branch_depends


def add_current_dependency_to_branch_depends(self, current_dependency, a_branch_depends, next_dependency_pos):
    # 添加当前依赖至分支依赖列表
    count_2 = count_1 = count = 1
    segment = current_dependency[1]
    for value_1 in a_branch_depends:
        if current_dependency[0] == value_1[0]:
            transfer_num = next_dependency_pos
            try:
                self.check_segment_in_and_update_transfer_num(segment, value_1[1], transfer_num, count_1)
            except FileNotFoundError:
                segment[1] = transfer_num
                value_1[1] = self.add_segment_to_segments(segment, value_1[1], count)
                count += 1
        elif count_2 == len(a_branch_depends):
            transfer_num = next_dependency_pos + 1
            segment[1] = transfer_num
            current_dependency = [current_dependency[0], segment]
            a_branch_depends.insert(0, current_dependency)
        else:
            count_2 += 1


@staticmethod
def add_segment_to_segments(segment, segments, count):
    if count == 1:
        temp = segments
        segments = list()
        segments.append(temp)
        segments.append(segment)
    else:
        segments[1].append(segment)
    return segments


@staticmethod
def check_segment_in_and_update_transfer_num(segment, segments, transfer_num, count_1):
    if count_1 == 1:
        segments = [segments]
        count_1 += 1
    count = 0
    for value in segments:
        if segment[0] == value[0]:
            segment[1] = transfer_num
        else:
            count += 1
    if count == len(segments):
        raise FileNotFoundError


def get_next_dependency_pos(self, next_dependency, a_branch_depends):  # 将下一个依赖以文件中形式写入depends，并获取其位置
    count = count_1 = 1
    next_depend_pos = None
    if len(a_branch_depends) == 0:
        a_branch_depends.append(next_dependency)
        next_depend_pos = len(a_branch_depends) - 1
    else:
        for value in a_branch_depends:
            if next_dependency[0] == value[0]:
                value[1] = self.add_segment_to_segments(next_dependency[1], value[1], count_1)
                next_depend_pos = count - 1
                count_1 += 1
            elif count == len(a_branch_depends):
                a_branch_depends.append(next_dependency)
                next_depend_pos = len(a_branch_depends) - 1
            else:
                count += 1
    return next_depend_pos
