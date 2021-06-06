import gi
import os
import intervals
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from entity.CalibrateFile import CalibrateParameterNode
from presenter.SeniorUIPresenter import SeniorUIPresenter


class SeniorUI:
    def __init__(self):
        self.state = False
        self.has_chosen_calibrate_parameter = False
        self._presenter = SeniorUIPresenter()
        self._presenter.view = self
        self.window = Gtk.Window()
        self.window.set_border_width(10)
        self.window.set_default_size(600, 400)
        self.set_window_header()

        self.ui = None
        self.parameter_choose = None
        self.all_msg_scrolled_win = None
        self.dependencies_scrolled_win = None
        self.get_all_widget()

        self._all_msg_tree_store = Gtk.TreeStore(int, float, float, str)
        self._segment_msg = []
        self._parameter_dict = None

        self._segment_edit_ui = SegmentModifyUI()
        self._factors_edit_ui = FactorsModifyUI()
        self._add_dependency_ui = AddDependencyUI()
        self.init_child_ui()

    @property
    def presenter(self):
        return self._presenter

    @property
    def parameter_dict(self):
        return self._parameter_dict

    @parameter_dict.setter
    def parameter_dict(self, value):
        self._parameter_dict = value

    def init_child_ui(self):
        self._segment_edit_ui.presenter = self._presenter
        self._factors_edit_ui.presenter = self._presenter
        self._add_dependency_ui.presenter = self._presenter

        self._segment_edit_ui.presenter.segment_view = self._segment_edit_ui
        self._factors_edit_ui.presenter.factors_view = self._factors_edit_ui
        self._add_dependency_ui.presenter.dependency_view = self._add_dependency_ui

    def get_all_widget(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'glade/SeniorUI.glade'))
        self.ui = builder.get_object('senior_grid')
        self.parameter_choose = builder.get_object('parameter_choose_combo')
        self.parameter_choose.connect('changed', self.update_two_scrolled_win)
        self.all_msg_scrolled_win = builder.get_object('calibrate_msg_info_scrolled_win')
        self.dependencies_scrolled_win = builder.get_object('dependencies_scrolled_win')
        add_branch_button = builder.get_object('add_branch_button')
        add_branch_button.connect('clicked', self.add_branch)
        add_whole_branch_button = builder.get_object('add_whole_branch_button')
        add_whole_branch_button.connect('clicked', self.add_complete_branch)
        edit_segment_button = builder.get_object('edit_segment_button')
        edit_segment_button.connect('clicked', self.show_edit_chosen_segment_ui)
        edit_factors_button = builder.get_object('edit_factors_button')
        edit_factors_button.connect('clicked', self.show_edit_chosen_factors_ui)
        delete_branch_button = builder.get_object('delete_branch_button')
        delete_branch_button.connect('clicked', self.delete_branch)
        add_dependency_button = builder.get_object('add_dependency_button')
        add_dependency_button.connect('clicked', self.add_dependency)
        delete_dependency_button = builder.get_object('delete_dependency_button')
        delete_dependency_button.connect('clicked', self.delete_dependency)
        confirm_button = builder.get_object('confirm_button')
        confirm_button.connect('clicked', self.confirm)
        cancel_button = builder.get_object('cancel_button')
        cancel_button.connect('clicked', self.hide)
        self.window.add(self.ui)

    def set_window_header(self):
        header = Gtk.HeaderBar(title='参数详细信息')
        header.props.show_close_button = False

        close_button = Gtk.Button()
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        close_button.set_image(img)
        close_button.connect('clicked', self.hide)

        max_button = Gtk.Button()
        max_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-maximize-symbolic", Gtk.IconSize.MENU)
        max_button.set_image(img)
        max_button.connect("clicked", self.maximize)

        min_button = Gtk.Button()
        min_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-minimize-symbolic", Gtk.IconSize.MENU)
        min_button.set_image(img)
        min_button.connect("clicked", self.minimize)

        header.pack_end(close_button)
        header.pack_end(max_button)
        header.pack_end(min_button)

        self.window.set_titlebar(header)

    def hide(self, widget):
        self.state = False
        self.has_chosen_calibrate_parameter = False
        self.window.hide()

    def hide_(self):
        self.state = False
        self.has_chosen_calibrate_parameter = False
        self.window.hide()

    def maximize(self, widget):
        if self.window.is_maximized():
            self.window.unmaximize()
        else:
            self.window.maximize()

    def minimize(self, widget):
        self.window.iconify()

    def update_available_parameters(self):
        self._presenter.get_current_channel()
        self.clear_dependencies_scrolled_win()
        self.clear_all_msg_scrolled_win()
        self.parameter_choose.clear()

        available_parameters = self._presenter.get_available_parameters()
        parameters_model = Gtk.ListStore(int, str)
        parameters_model.append([2020, '请选择校正参数'])
        for parameter in available_parameters:
            try:
                parameters_model.append([parameter, '{}--{}'.format(parameter, self._parameter_dict[parameter])])
            except KeyError:
                parameters_model.append([parameter, '{}--None'.format(parameter)])
        self.parameter_choose.set_model(parameters_model)
        parameter_cell = Gtk.CellRendererText()
        self.parameter_choose.pack_start(parameter_cell, True)
        self.parameter_choose.add_attribute(parameter_cell, 'text', 1)
        self.parameter_choose.set_active(0)

    def update_two_scrolled_win(self, widget):
        chosen_parameter = self._presenter.load_chosen_parameter()
        default_parameter = 2020
        if chosen_parameter == default_parameter:
            self.clear_dependencies_scrolled_win()
            self.clear_all_msg_scrolled_win()
        else:
            self.has_chosen_calibrate_parameter = True
            self.update_dependencies_scrolled_win(chosen_parameter)
            self.update_all_msg_scrolled_win(chosen_parameter)

    def clear_dependencies_scrolled_win(self):
        child = self.dependencies_scrolled_win.get_child()
        if child:
            tree_store = child.get_model()
            tree_store.clear()
            # self.dependencies_scrolled_win.remove(child)

    def clear_all_msg_scrolled_win(self):
        child = self.all_msg_scrolled_win.get_child()
        if child:
            tree_store = child.get_model()
            tree_store.clear()
            # self.all_msg_scrolled_win.remove(child)  这样后续操作会有Gtk警告和failed

    def update_dependencies_scrolled_win(self, chosen_parameter):
        depends_id = self._presenter.get_depends_id(chosen_parameter)
        tree_view = Gtk.TreeView()
        tree_store = Gtk.TreeStore(int, str)
        parent = None
        for depend in depends_id:
            try:
                parent = tree_store.append(parent, [depend, self._parameter_dict[depend]])
            except KeyError:
                parent = tree_store.append(parent, [depend, 'None'])
        tree_view.set_model(tree_store)

        cell_renderer_text = Gtk.CellRendererText()
        tree_view_column_1 = Gtk.TreeViewColumn("依赖ID")
        tree_view.append_column(tree_view_column_1)
        tree_view_column_1.pack_start(cell_renderer_text, True)
        tree_view_column_1.add_attribute(cell_renderer_text, "text", 0)
        tree_view_column_2 = Gtk.TreeViewColumn("依赖名")
        tree_view.append_column(tree_view_column_2)
        tree_view_column_2.pack_start(cell_renderer_text, True)
        tree_view_column_2.add_attribute(cell_renderer_text, "text", 1)
        child = self.dependencies_scrolled_win.get_child()
        if child:
            self.dependencies_scrolled_win.remove(child)
        self.dependencies_scrolled_win.add(tree_view)
        self.dependencies_scrolled_win.show_all()

    @staticmethod
    def get_tree_view():
        tree_view = Gtk.TreeView()
        cell_renderer_text = Gtk.CellRendererText()

        tree_view_column_1 = Gtk.TreeViewColumn("参数ID")
        tree_view.append_column(tree_view_column_1)
        tree_view_column_1.pack_start(cell_renderer_text, True)
        tree_view_column_1.add_attribute(cell_renderer_text, "text", 0)

        tree_view_column_2 = Gtk.TreeViewColumn("分段下界")
        tree_view.append_column(tree_view_column_2)
        tree_view_column_2.pack_start(cell_renderer_text, True)
        tree_view_column_2.add_attribute(cell_renderer_text, "text", 1)

        tree_view_column_3 = Gtk.TreeViewColumn("分段上界")
        tree_view.append_column(tree_view_column_3)
        tree_view_column_3.pack_start(cell_renderer_text, True)
        tree_view_column_3.add_attribute(cell_renderer_text, "text", 2)

        tree_view_column_4 = Gtk.TreeViewColumn("校正系数")
        tree_view.append_column(tree_view_column_4)
        tree_view_column_4.pack_start(cell_renderer_text, True)
        tree_view_column_4.add_attribute(cell_renderer_text, "text", 3)
        return tree_view

    def update_all_msg_scrolled_win(self, chosen_parameter):
        self._segment_msg = []
        self._all_msg_tree_store.clear()

        root_node = self._presenter.get_root_node(chosen_parameter)
        children = root_node.children
        for child in children:
            segment = child.parameter_segment
            segment_msg = self._all_msg_tree_store.append(None, [child.parameter_id, segment.lower, segment.upper, None])
            # append 返回一个Gtk.TreeIter
            self._segment_msg.append(segment_msg)
        next_time_parents = children
        while True:
            try:
                self.update_next_segment_msg(next_time_parents)
                temp = []
                for parent in next_time_parents:
                    for child in parent.children:
                        temp.append(child)
                next_time_parents = temp
            except StopIteration:
                break
        tree_view = self.get_tree_view()
        tree_view.set_model(self._all_msg_tree_store)
        child = self.all_msg_scrolled_win.get_child()
        if child:
            self.all_msg_scrolled_win.remove(child)
        self.all_msg_scrolled_win.add(tree_view)
        self.all_msg_scrolled_win.show_all()

    def update_next_segment_msg(self, parents):
        next_time_segment_msg = []
        for parent in parents:
            children = parent.children
            for child in children:
                if isinstance(child, CalibrateParameterNode):
                    count = 0
                    if not child.parameter_segments:
                        is_last_child = children.index(child) == len(children)-1 and \
                                        parents.index(parent) == len(parents)-1
                        if is_last_child:
                            raise StopIteration
                    else:
                        for segment in child.parameter_segments:
                            interval = segment[0]
                            factors_str = '{}'.format(segment[1])
                            current_parent_store = self._segment_msg[parents.index(parent)]
                            self._all_msg_tree_store.append(current_parent_store, [child.parameter_id,
                                                                                   interval.lower,
                                                                                   interval.upper, factors_str])
                            count += 1
                            is_last_segment = \
                                count == len(child.parameter_segments) and children.index(child) == len(children)-1 \
                                and parents.index(parent) == len(parents)-1
                            if is_last_segment:
                                raise StopIteration
                else:
                    segment = child.parameter_segment
                    current_parent_store = self._segment_msg[parents.index(parent)]
                    segment_msg = self._all_msg_tree_store.append(current_parent_store, [child.parameter_id,
                                                                                         segment.lower, segment.upper,
                                                                                         None])
                    next_time_segment_msg.append(segment_msg)
        self._segment_msg = next_time_segment_msg

    def confirm(self, widget):
        if self.has_chosen_calibrate_parameter:
            self._presenter.confirm_in_senior()
            self._presenter.update_main_ui_from_senior()
            self.hide_()
        else:
            self.hide_()

    def delete_dependency(self, widget):
        try:
            self._presenter.delete_dependency()
            self._presenter.update_add_or_delete_dependency_in_senior_ui()
        except AttributeError:
            pass
        except TypeError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择目标结点")
            dialog.run()
            dialog.destroy()

    def add_dependency(self, widget):
        try:
            if not self._add_dependency_ui.state:
                self._add_dependency_ui.show_chosen_dependency()
                self._add_dependency_ui.state = True
                self._add_dependency_ui.window.show_all()
            else:
                self._add_dependency_ui.state = False
                self._add_dependency_ui.hide_()
        except TypeError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择已存在依赖")
            dialog.run()
            dialog.destroy()
        except AttributeError:
            pass

    def show_edit_chosen_segment_ui(self, widget):
        try:
            if not self._segment_edit_ui.state:
                _id, lower_num, upper_num = self._presenter.load_chosen_segment()
                self._segment_edit_ui.update_current_segment_display(_id, lower_num, upper_num)
                self._segment_edit_ui.state = True
                self._segment_edit_ui.window.show_all()
            else:
                self._segment_edit_ui.state = False
                self._segment_edit_ui.window.hide()
        except TypeError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择目标结点")
            dialog.run()
            dialog.destroy()
        except AttributeError:
            pass

    def update_senior_ui_current_segment(self, segment_entry):
        all_msg_tree_view = self.all_msg_scrolled_win.get_child()
        focus_segment = all_msg_tree_view.get_selection()
        model, _iter = focus_segment.get_selected()
        model.set_value(_iter, 1, segment_entry.lower)
        model.set_value(_iter, 2, segment_entry.upper)

    def update_senior_ui_current_factors(self, factors_entry):
        all_msg_tree_view = self.all_msg_scrolled_win.get_child()
        focus_segment = all_msg_tree_view.get_selection()
        model, _iter = focus_segment.get_selected()
        model.set_value(_iter, 3, '{}'.format(factors_entry))

    def update_senior_ui_edit_branch(self):
        chosen_parameter = self._presenter.load_chosen_parameter()
        self.update_all_msg_scrolled_win(chosen_parameter)

    def update_senior_ui_add_branch(self):
        all_msg_tree_view = self.all_msg_scrolled_win.get_child()
        focus_segment = all_msg_tree_view.get_selection()
        model, _iter = focus_segment.get_selected()
        _id = model.get_value(_iter, 0)

        calibrate_parameter_id = self._presenter.load_chosen_parameter()
        depends_id = self._presenter.get_depends_id(calibrate_parameter_id)
        parameters_id = depends_id + [calibrate_parameter_id]
        id_index = parameters_id.index(_id)
        if id_index != len(parameters_id)-1:
            for parameter_id in parameters_id[id_index+1:]:
                if parameter_id != calibrate_parameter_id:
                    _iter = model.append(_iter, [parameter_id, float('-inf'), float('inf'), None])
                else:
                    model.append(_iter, [parameter_id, float('-inf'), float('inf'), '[0, 0, 0, 0, 0 , 0]'])
        else:
            _iter = model.iter_parent(_iter)
            model.append(_iter, [calibrate_parameter_id, float('-inf'), float('inf'), '[0, 0, 0, 0, 0 , 0]'])

    def update_senior_ui_delete_branch(self):
        all_msg_tree_view = self.all_msg_scrolled_win.get_child()
        focus_segment = all_msg_tree_view.get_selection()
        model, _iter = focus_segment.get_selected()
        if self._presenter.check_is_unique_child(model, _iter):
            _iter = self._presenter.find_has_siblings_node(model, _iter)
        model.remove(_iter)

    def add_branch(self, widget):  # 当选择结点是叶结点时，添加结果与选中该结点的父结点结果一样
        try:
            self._presenter.add_branch()
        except ValueError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("存在相同的分支路径，无法执行此操作")
            dialog.run()
            dialog.destroy()
        except TypeError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择目标结点")
            dialog.run()
            dialog.destroy()
        except AttributeError:
            pass

    def add_complete_branch(self, widget):
        try:
            self._presenter.add_complete_branch()
        except ValueError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请选择有效参数")
            dialog.run()
            dialog.destroy()

    def delete_branch(self, widget):
        try:
            self._presenter.delete_branch()
        except ValueError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("存在相同的分支路径，无法执行此操作")
            dialog.run()
            dialog.destroy()
        except TypeError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择目标结点")
            dialog.run()
            dialog.destroy()
        except AttributeError:
            pass

    def show_edit_chosen_factors_ui(self, widget):
        try:
            if not self._factors_edit_ui.state:
                factors = self._presenter.load_chosen_factors()
                if factors:
                    factors = eval(factors)
                    self._factors_edit_ui.update_current_factors(factors)
                    self._factors_edit_ui.state = True
                    self._factors_edit_ui.window.show_all()
                else:
                    dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                               buttons=Gtk.ButtonsType.OK, text="提示")
                    dialog.format_secondary_text("当前所选参数无校正系数")
                    dialog.run()
                    dialog.destroy()
            else:
                self._factors_edit_ui.state = False
                self._factors_edit_ui.window.hide()
        except AttributeError:
            pass
        except TypeError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择目标结点")
            dialog.run()
            dialog.destroy()


class SegmentModifyUI:
    def __init__(self):
        self._presenter = None
        self.state = False
        self.entries = []

        self.window = Gtk.Window()
        self.window.set_border_width(10)
        self.window.set_default_size(500, 150)
        self.ui = None
        self.current_lower_label = None
        self.current_upper_label = None
        self.id_label = None
        self.get_all_widget()
        self.set_window_header()
        self.window.add(self.ui)

    @property
    def presenter(self):
        return self._presenter

    @presenter.setter
    def presenter(self, value):
        self._presenter = value

    def set_window_header(self):
        header = Gtk.HeaderBar(title='分段（区间）编辑')
        header.props.show_close_button = False

        close_button = Gtk.Button()
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        close_button.set_image(img)
        close_button.connect('clicked', self.hide)

        max_button = Gtk.Button()
        max_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-maximize-symbolic", Gtk.IconSize.MENU)
        max_button.set_image(img)
        max_button.connect("clicked", self.maximize)

        min_button = Gtk.Button()
        min_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-minimize-symbolic", Gtk.IconSize.MENU)
        min_button.set_image(img)
        min_button.connect("clicked", self.minimize)

        header.pack_end(close_button)
        header.pack_end(max_button)
        header.pack_end(min_button)

        self.window.set_titlebar(header)

    def hide(self, widget):
        self.clear_entries()
        self.state = False
        self.window.hide()

    def maximize(self, widget):
        if self.window.is_maximized():
            self.window.unmaximize()
        else:
            self.window.maximize()

    def minimize(self, widget):
        self.window.iconify()

    def clear_entries(self):
        for entry in self.entries:
            entry.delete_text(0, -1)

    def get_all_widget(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'glade/EditSegmentUI.glade'))
        self.ui = builder.get_object('edit_segment_in_senior_grid')
        self.id_label = builder.get_object('current_chosen_parameter_id_label')
        self.current_lower_label = builder.get_object('current_segment_lower_label')
        self.current_upper_label = builder.get_object('current_segment_upper_label')
        lower_num_entry = builder.get_object('new_segment_lower_entry')
        upper_num_entry = builder.get_object('new_segment_upper_entry')
        self.entries = [lower_num_entry, upper_num_entry]
        confirm_button = builder.get_object('confirm_button')
        confirm_button.connect('clicked', self.confirm)
        cancel_button = builder.get_object('cancel_button')
        cancel_button.connect('clicked', self.cancel)

    def update_current_segment_display(self, _id, lower_num, upper_num):
        self.current_lower_label.set_text('{}'.format(lower_num))
        self.current_upper_label.set_text('{}'.format(upper_num))
        self.id_label.set_text('{}'.format(_id))

    def confirm(self, widget):
        try:
            self._presenter.modify_segment_in_senior()
            self._presenter.update_modified_segment()
            _id, lower_num, upper_num = self._presenter.load_chosen_segment()
            self.update_current_segment_display(_id, lower_num, upper_num)
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("修改成功")
            dialog.run()
            dialog.destroy()
        except ValueError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("输入格式不正确："
                                         "请输入整数或浮点数")
            dialog.run()
            dialog.destroy()
        except intervals.exc.RangeBoundsException:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("输入格式不正确："
                                         "上界比下界小")
            dialog.run()
            dialog.destroy()

    def cancel(self, widget):
        self.clear_entries()
        self.state = False
        self.window.hide()


class FactorsModifyUI:
    def __init__(self):
        self._presenter = None
        self.entries = None
        self.current_factors = None
        self.state = False
        self._curves = Image()

        self.window = Gtk.Window()
        self.window.set_border_width(10)
        self.window.set_default_size(300, 150)
        self.ui = None
        self.get_all_widget()
        self.set_window_header()
        self.window.add(self.ui)

    @property
    def presenter(self):
        return self._presenter

    @presenter.setter
    def presenter(self, value):
        self._presenter = value

    def get_all_widget(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'glade/EditFactorsInSeniorUI.glade'))
        self.ui = builder.get_object('edit_factors_in_senior_grid')
        current_factor_5 = builder.get_object('current_factor_5_label')
        current_factor_4 = builder.get_object('current_factor_4_label')
        current_factor_3 = builder.get_object('current_factor_3_label')
        current_factor_2 = builder.get_object('current_factor_2_label')
        current_factor_1 = builder.get_object('current_factor_1_label')
        current_factor_0 = builder.get_object('current_factor_0_label')
        self.current_factors = [current_factor_5, current_factor_4, current_factor_3, current_factor_2,
                                current_factor_1, current_factor_0]
        confirm_button = builder.get_object('confirm_button')
        confirm_button.connect('clicked', self.confirm)
        cancel_button = builder.get_object('cancel_button')
        cancel_button.connect('clicked', self.hide)
        curves_button = builder.get_object('curves_button')
        curves_button.connect('clicked', self.check)
        factor_5_entry = builder.get_object('factor_5_entry')
        factor_4_entry = builder.get_object('factor_4_entry')
        factor_3_entry = builder.get_object('factor_3_entry')
        factor_2_entry = builder.get_object('factor_2_entry')
        factor_1_entry = builder.get_object('factor_1_entry')
        factor_0_entry = builder.get_object('factor_0_entry')
        self.entries = [factor_5_entry, factor_4_entry, factor_3_entry, factor_2_entry, factor_1_entry,
                        factor_0_entry]

    def update_current_factors(self, current_factors):
        count = 0
        for factor in current_factors:
            current_factor = self.current_factors[count]
            current_factor.set_text('{}'.format(factor))
            count += 1

    def set_window_header(self):
        header = Gtk.HeaderBar(title='校正系数修改')
        header.props.show_close_button = False

        close_button = Gtk.Button()
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        close_button.set_image(img)
        close_button.connect('clicked', self.hide)

        max_button = Gtk.Button()
        max_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-maximize-symbolic", Gtk.IconSize.MENU)
        max_button.set_image(img)
        max_button.connect("clicked", self.maximize)

        min_button = Gtk.Button()
        min_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-minimize-symbolic", Gtk.IconSize.MENU)
        min_button.set_image(img)
        min_button.connect("clicked", self.minimize)

        header.pack_end(close_button)
        header.pack_end(max_button)
        header.pack_end(min_button)
        self.window.set_titlebar(header)

    def hide(self, widget):
        for entry in self.entries:
            entry.delete_text(0, -1)
        self.state = False
        self.window.hide()

    def maximize(self, widget):
        if self.window.is_maximized():
            self.window.unmaximize()
        else:
            self.window.maximize()

    def minimize(self, widget):
        self.window.iconify()

    def confirm(self, widget):
        try:
            factors = self._presenter.load_factors_entry()
            self.update_current_factors(factors)
            self._presenter.modify_factors_in_senior()
            self._presenter.update_modified_factors_in_senior()
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("修改成功")
            dialog.run()
            dialog.destroy()
        except ValueError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("输入格式不正确，"
                                         "请输入整数或浮点数")
            dialog.run()
            dialog.destroy()

    def cancel(self, widget):
        for entry in self.entries:
            entry.delete_text(0, -1)
        self.state = False
        self.window.hide()

    def check(self, widget):
        try:
            self._presenter.show_two_curves_in_senior()
            if not self._curves.is_show:
                self._curves.update_img()
                self._curves.window.show_all()
                self._curves.is_show = True
            else:
                self._curves.window.hide()
                self._curves.is_show = False
        except ValueError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("无法显示校正曲线，"
                                         "请检查系数区间或输入系数")
            dialog.run()
            dialog.destroy()


class AddDependencyUI:
    def __init__(self):
        self.state = False
        self.window = Gtk.Window()
        self.set_window_header()
        self._presenter = None

        self.ui = None
        self.chosen_dependency_label = None
        self.entry_id = None
        self.pos_combo = None
        self.get_all_widget()

        self.window.add(self.ui)

    @property
    def presenter(self):
        return self._presenter

    @presenter.setter
    def presenter(self, value):
        self._presenter = value

    def set_window_header(self):
        header = Gtk.HeaderBar(title='添加新依赖')
        header.props.show_close_button = False

        close_button = Gtk.Button()
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        close_button.set_image(img)
        close_button.connect('clicked', self.hide)

        max_button = Gtk.Button()
        max_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-maximize-symbolic", Gtk.IconSize.MENU)
        max_button.set_image(img)
        max_button.connect("clicked", self.maximize)

        min_button = Gtk.Button()
        min_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-minimize-symbolic", Gtk.IconSize.MENU)
        min_button.set_image(img)
        min_button.connect("clicked", self.minimize)

        header.pack_end(close_button)
        header.pack_end(max_button)
        header.pack_end(min_button)
        self.window.set_titlebar(header)

    def hide(self, widget):
        self.state = False
        self.entry_id.delete_text(0, -1)
        self.window.hide()

    def hide_(self):
        self.state = False
        self.entry_id.delete_text(0, -1)
        self.window.hide()

    def maximize(self, widget):
        if self.window.is_maximized():
            self.window.unmaximize()
        else:
            self.window.maximize()

    def minimize(self, widget):
        self.window.iconify()

    def get_all_widget(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'glade/AddDependencyUI.glade'))
        self.ui = builder.get_object('add_depend_grid')
        self.chosen_dependency_label = builder.get_object('current_chosen_dependency_label')
        confirm_button = builder.get_object('confirm_button')
        confirm_button.connect('clicked', self.confirm)
        cancel_button = builder.get_object('cancel_button')
        cancel_button.connect('clicked', self.hide)
        self.entry_id = builder.get_object('new_dependency_entry')

        self.pos_combo = builder.get_object('pos_combo')
        pos_model = Gtk.ListStore(int, str)
        pos_model.append([0, '选择依赖前'])
        pos_model.append([1, '选择依赖后'])
        self.pos_combo.set_model(pos_model)
        cell = Gtk.CellRendererText()
        self.pos_combo.pack_start(cell, True)
        self.pos_combo.add_attribute(cell, 'text', 1)
        self.pos_combo.set_active(0)

    def confirm(self, widget):
        try:
            self._presenter.confirm_add_dependency()
            self._presenter.update_add_or_delete_dependency_in_senior_ui()
            self.hide_()
        except ValueError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请输入依赖ID")
            dialog.run()
            dialog.destroy()

    def show_chosen_dependency(self):
        dependency = self._presenter.load_dependencies_scrolled_win_chosen()
        self.chosen_dependency_label.set_text('{}'.format(dependency))


class Image:
    def __init__(self):
        self.window = Gtk.Window()
        self.set_window_header()
        self.is_show = False

        self.image = Gtk.Image()

    def update_img(self):
        child = self.window.get_child()
        if child:
            self.window.remove(child)
        self.image.set_from_file(r"image\two_factors_curves.png")
        self.window.add(self.image)

    def set_window_header(self):
        header = Gtk.HeaderBar(title='校正系数曲线')
        header.props.show_close_button = False

        close_button = Gtk.Button()
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
        close_button.set_image(img)
        close_button.connect('clicked', self.hide)

        max_button = Gtk.Button()
        max_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-maximize-symbolic", Gtk.IconSize.MENU)
        max_button.set_image(img)
        max_button.connect("clicked", self.maximize)

        min_button = Gtk.Button()
        min_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-minimize-symbolic", Gtk.IconSize.MENU)
        min_button.set_image(img)
        min_button.connect("clicked", self.minimize)

        header.pack_end(close_button)
        header.pack_end(max_button)
        header.pack_end(min_button)

        self.window.set_titlebar(header)

    def hide(self, widget):
        self.is_show = False
        self.window.hide()

    def maximize(self, widget):
        if self.window.is_maximized():
            self.window.unmaximize()
        else:
            self.window.maximize()

    def minimize(self, widget):
        self.window.iconify()

# if __name__ == '__main__':
#     win = SeniorUI()
#     win.window.show_all()
#     Gtk.main()
