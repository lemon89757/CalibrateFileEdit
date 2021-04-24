from entity.FileHandler import FileHandler
from anytree import RenderTree
from anytree.render import AsciiStyle

file_path = r'C:\Users\helloTt\Desktop\tt\2021上半学期（电科）\learning_project\material\Json\2020-8-4-10-52-42ES1691FULL.json'
handler = FileHandler()

handler.get_calibrate_file(file_path)

# 测试单个信息获取
msg_1 = handler.load_calibrate_msg_from_file(1, 1250102)
msg_2 = handler.load_calibrate_msg_from_file(1, 1204100)
msg_3 = handler.load_calibrate_msg_from_file(1, 1204110)
msg_4 = handler.load_calibrate_msg_from_file(1, 1204101)
msg_5 = handler.load_calibrate_msg_from_file(1, 1204111)
msg_6 = handler.load_calibrate_msg_from_file(1, 1204102)
msg_7 = handler.load_calibrate_msg_from_file(1, 1204112)
msg_8 = handler.load_calibrate_msg_from_file(1, 1204103)
msg_9 = handler.load_calibrate_msg_from_file(1, 1204113)
msg_10 = handler.load_calibrate_msg_from_file(1, 1204104)
msg_11 = handler.load_calibrate_msg_from_file(1, 1204114)
msg_12 = handler.load_calibrate_msg_from_file(1, 1204002)
nodes = msg_12.calibrate_tree
root_node = nodes[0]
# print(RenderTree(root_node, style=AsciiStyle()))
for pre, _, node in RenderTree(root_node):
    treestr = u"%s%s" % (pre, node.parameter_id)
    print(treestr.ljust(8), node.parameter_segment, node.content)

# 测试获取全部校正信息
# channels = handler.load_all_calibrate_msg_from_file()
# channel = channels[0]
# calibrate_msg = channel[1204100]
# calibrate_tree = calibrate_msg.calibrate_tree
# root_node_1 = calibrate_tree[0]
# for pre, _, node in RenderTree(root_node_1):
#     treestr = u"%s%s" % (pre, node.parameter_id)
#     print(treestr.ljust(8), node.parameter_segment, node.content)
