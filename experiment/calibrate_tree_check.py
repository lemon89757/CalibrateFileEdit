from entity.FileHandler import FileHandler
import json
from anytree import RenderTree
from anytree.render import AsciiStyle

file_path = r'C:\Users\helloTt\Desktop\tt\2021上半学期（电科）\learning_project\material\Json\2020-8-4-10-52-42ES1691FULL.json'
file_path_2 = r'..\experiment\file_output_check.json'
handler = FileHandler()

handler.get_calibrate_file(file_path_2)

# 测试单个信息获取
# msg_1 = handler.load_calibrate_msg_from_file(1, 1250102)
# msg_2 = handler.load_calibrate_msg_from_file(1, 1204100)
# msg_3 = handler.load_calibrate_msg_from_file(1, 1204110)
# msg_4 = handler.load_calibrate_msg_from_file(1, 1204101)
# msg_5 = handler.load_calibrate_msg_from_file(1, 1204111)
# msg_6 = handler.load_calibrate_msg_from_file(1, 1204102)
# msg_7 = handler.load_calibrate_msg_from_file(1, 1204112)
# msg_8 = handler.load_calibrate_msg_from_file(1, 1204103)
# msg_9 = handler.load_calibrate_msg_from_file(1, 1204113)
# msg_10 = handler.load_calibrate_msg_from_file(1, 1204104)
# msg_11 = handler.load_calibrate_msg_from_file(1, 1204114)
msg_12 = handler.load_calibrate_msg_from_file(1, 1204002)
#
root_node = msg_12.calibrate_tree
# root_nodes = [msg_1.calibrate_tree, msg_2.calibrate_tree, msg_3.calibrate_tree, msg_4.calibrate_tree,
#               msg_5.calibrate_tree, msg_6.calibrate_tree, msg_7.calibrate_tree, msg_8.calibrate_tree,
#               msg_9.calibrate_tree, msg_10.calibrate_tree, msg_11.calibrate_tree, msg_12.calibrate_tree]

# leaves_nodes = root_node.leaves
# one_leaf_node = leaves_nodes[0]  # 第一个叶节点
# leaf_ancestors = one_leaf_node.ancestors


# def next_node(nodes_1, node_1):
#     count_1 = 0
#     for i in nodes_1:
#         count_1 += 1
#         if i == node_1:
#             return nodes_1[count_1]
#         else:
#             pass
#
#
# depends_msg = []  # 一个分支的依赖
# for node in leaf_ancestors[1:-1]:
#     left_index = node.parameter_segment.lower
#     right_index = node.parameter_segment.upper
#     segment = [left_index, right_index]
#
#     next_one = next_node(leaf_ancestors, node)
#     if leaf_ancestors[-1] == next_one:
#         pass
#     else:
#         next_left_index = next_one.parameter_segment.lower
#         next_right_index = next_one.parameter_segment.upper
#         next_segment = [next_left_index, next_right_index]
#         transfer_num = 2021
#
#         count = 1
#         if len(depends_msg) == 0:
#             dependency_1 = [next_one.parameter_id, [next_segment]]
#             depends_msg.append(dependency_1)
#             transfer_num = len(depends_msg) - 1
#         else:
#             for msg in depends_msg:
#                 if next_one.parameter_id == msg[0]:
#                     msg[1].append(next_segment)
#                     transfer_num = count - 1
#                 elif count == len(depends_msg):
#                     dependency_1 = [next_one.parameter_id, [next_segment]]
#                     depends_msg.append(dependency_1)
#                     transfer_num = len(depends_msg) - 1
#                 else:
#                     count += 1
#
#         segment_msg = [segment, transfer_num]
#         count_2 = 1
#         for msg_1 in depends_msg:
#             if node.parameter_id == msg_1[0]:
#                 msg_1[1].append(segment_msg)
#             elif count_2 == len(depends_msg):
#                 segment_msg = [segment_msg[0], segment_msg[1] + 1]
#                 dependency_2 = [node.parameter_id, segment_msg]
#                 depends_msg.insert(0, dependency_2)
#             else:
#                 count_2 += 1
#
# # print(len(leaf_ancestors))
# print(depends_msg)
#
# _id = root_node.parameter_id
# entry_dependency = leaf_ancestors[1]
# entry = 0
# model = 0
# join_parameter = []
# hardware_node = leaf_ancestors[-1]
#
# msg = [_id, entry, [], model, join_parameter, [], []]
# msg[2] += depends
# msg[6].append(one_leaf_node.content)
# left_index = hardware_node.parameter_segment.lower
# right_index = hardware_node.parameter_segment.upper
# transfer_num = len(msg[6])-1
# segment = [[left_index, right_index], transfer_num]
# msg[5].append(segment)

# print(msg)

# print(RenderTree(root_node, style=AsciiStyle()))
# branches = root_node.descendants
# for node in branches:
#     print(node.parameter_id, node.parameter_segment)
for pre, _, node in RenderTree(root_node):
    treestr = u"%s%s" % (pre, node.parameter_id)
    print(treestr.ljust(8), node.parameter_segment, node.parameter_segments)
# print(len(root_node.leaves))

# 测试获取全部校正信息
# channels = handler.load_all_calibrate_msg_from_file()
# channel = channels[0]
# calibrate_msg = channel[1204100]
# calibrate_tree = calibrate_msg.calibrate_tree
# root_node_1 = calibrate_tree
# for pre, _, node in RenderTree(root_node_1):
#     treestr = u"%s%s" % (pre, node.parameter_id)
#     print(treestr.ljust(8), node.parameter_segment, node.parameter_segments)

# 测试一个分支的依赖文件生成
# count = 1
# for node in leaves_nodes:
#     print(handler.a_branch_depends_to_file(node))
# branch_1 = handler.a_branch_depends_to_file(leaves_nodes[0])
# branch_2 = handler.a_branch_depends_to_file(leaves_nodes[1])
# branch = handler.merge_two_branch_depends(branch_1, branch_2, 1)
# print(branch)

# TODO 合并两个分支的函数、获取依赖叶节点的函数
# depends = handler.get_depends(nodes)
# print(depends)
# for i in depends:
#     print(i)

# root_depends = handler.root_depends_to_json_file(root_node)
# print(root_depends)
# 测试channels_to_file
# root_nodes = []
# for calibrate_msg in channel.values():
#     root_node = calibrate_msg.calibrate_tree
#     root_nodes.append(root_node)
# depends = handler.depends_to_file(root_nodes)
# print(depends)
#
# channel_file = handler.channels_to_file(channels)
# print(channel_file)
#
# json_file_path = "file_output_check"
# data = dict()
# data["channels"] = channel_file
# data_json = json.dumps(data)
# with open(json_file_path, "w") as file:
#     file.write(data_json)
# 测试get_rev_depends
# calibrate_file = handler.calibrate_msg_to_file(channels)
# json_file_path = "file_output_check.json"
# data = dict()
# # data["channels"] = rev_depends
# data_json = json.dumps(calibrate_file)
# with open(json_file_path, "w") as file:
#     file.write(data_json)
