import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from entity.CalibrateFile import CalibrateParameterNode
from presenter.SeniorUIPresenter import SeniorUIPresenter


class SeniorUI:
    def __init__(self):
        self.state = False
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

        self._segment_edit_ui = SegmentModifyUI()
        self._factors_edit_ui = FactorsModifyUI()
        self.init_child_ui()

    @property
    def presenter(self):
        return self._presenter

    def init_child_ui(self):
        self._segment_edit_ui.presenter = self._presenter
        self._factors_edit_ui.presenter = self._presenter

        self._segment_edit_ui.presenter.segment_view = self._segment_edit_ui
        self._factors_edit_ui.presenter.factors_view = self._factors_edit_ui

    def get_all_widget(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'SeniorUI.glade'))
        self.ui = builder.get_object('senior_box')
        self.parameter_choose = builder.get_object('parameter_choose_combo')
        self.parameter_choose.connect('changed', self.update_two_scrolled_win)
        self.all_msg_scrolled_win = builder.get_object('calibrate_msg_info_scrolled_win')
        self.dependencies_scrolled_win = builder.get_object('dependencies_scrolled_win')
        add_branch_button = builder.get_object('add_branch_button')
        add_branch_button.connect('clicked', self.add_branch)
        add_whole_branch_button = builder.get_object('add_whole_branch_button')
        add_whole_branch_button.connect('clicked', self.add_complete_branch)
        edit_segment_button = builder.get_object('edit_segment_button')
        edit_segment_button.connect('clicked', self.edit_choosed_segment)
        edit_factors_button = builder.get_object('edit_factors_button')
        edit_factors_button.connect('clicked', self.edit_choosed_factors)
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
        header = Gtk.HeaderBar(title='SeniorUI')
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
        self._presenter.update_main_ui_from_senior()
        self.state = False
        self.window.hide()

    def hide_and_update_main_ui(self):
        self._presenter.update_main_ui_from_senior()
        self.state = False
        self.window.hide()

    def maximize(self, widget):
        if self.window.is_maximized():
            self.window.unmaximize()
        else:
            self.window.maximize()

    def minimize(self, widget):
        self.window.iconify()

    def update_available_parameters(self):
        self.clear_dependencies_scrolled_win()
        self.clear_all_msg_scrolled_win()
        self.parameter_choose.clear()

        available_parameters = self._presenter.get_available_parameters()
        parameters_model = Gtk.ListStore(int)
        parameters_model.append([2020])
        for parameter in available_parameters:
            parameters_model.append([parameter])
        self.parameter_choose.set_model(parameters_model)
        parameter_cell = Gtk.CellRendererText()
        self.parameter_choose.pack_start(parameter_cell, True)
        self.parameter_choose.add_attribute(parameter_cell, 'text', 0)
        self.parameter_choose.set_active(0)

    def update_two_scrolled_win(self, widget):
        choosed_parameter = self._presenter.load_choosed_parameter()
        default_parameter = 2020
        if choosed_parameter == default_parameter:
            self.clear_dependencies_scrolled_win()
            self.clear_all_msg_scrolled_win()
        else:
            self.update_dependencies_scrolled_win(choosed_parameter)
            self.update_all_msg_scrolled_win(choosed_parameter)

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
            # self.all_msg_scrolled_win.remove(child)  这样后续操作会有Gtk警告和failed，不懂...

    def update_dependencies_scrolled_win(self, choosed_parameter):
        depends_id = self._presenter.get_depends_id(choosed_parameter)

        tree_view = Gtk.TreeView()
        tree_store = Gtk.TreeStore(int)
        parent = None
        for depend in depends_id:
            parent = tree_store.append(parent, [depend])
        tree_view.set_model(tree_store)

        cell_renderer_text = Gtk.CellRendererText()
        tree_view_column_1 = Gtk.TreeViewColumn("依赖ID")
        tree_view.append_column(tree_view_column_1)
        tree_view_column_1.pack_start(cell_renderer_text, True)
        tree_view_column_1.add_attribute(cell_renderer_text, "text", 0)

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

    def update_all_msg_scrolled_win(self, choosed_parameter):
        self._segment_msg = []
        self._all_msg_tree_store.clear()

        root_node = self._presenter.get_root_node(choosed_parameter)
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
            if isinstance(children[0], CalibrateParameterNode):
                # 因为叶结点没有子结点，因此应该也可以捕获children[0]处的错误，来结束更新函数的循环
                for child in children:
                    count = 0
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
                for child in children:
                    segment = child.parameter_segment
                    current_parent_store = self._segment_msg[parents.index(parent)]
                    segment_msg = self._all_msg_tree_store.append(current_parent_store, [child.parameter_id,
                                                                                         segment.lower, segment.upper,
                                                                                         None])
                    next_time_segment_msg.append(segment_msg)
        self._segment_msg = next_time_segment_msg

    def confirm(self, widget):
        pass

    def delete_dependency(self, widget):
        pass

    def add_dependency(self, widget):
        pass

    def edit_choosed_segment(self, widget):
        try:
            if not self._segment_edit_ui.state:
                _id, lower_num, upper_num = self._presenter.load_choosed_segment()
                self._segment_edit_ui.update_current_segment_display(_id, lower_num, upper_num)
                self._segment_edit_ui.state = True
                self._segment_edit_ui.window.show_all()
            else:
                self._segment_edit_ui.state = False
                self._segment_edit_ui.window.hide()
        except Exception as ex:
            print('error:', ex)

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
        choosed_parameter = self._presenter.load_choosed_parameter()
        self.update_all_msg_scrolled_win(choosed_parameter)

    def add_branch(self, widget):
        try:
            self._presenter.add_branch()
        except Exception as ex:
            print(ex)
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("结点选择有误，不能添加")
            dialog.run()
            dialog.destroy()

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
        except Exception as ex:
            print(ex)

    def edit_choosed_factors(self, widget):
        try:
            if not self._factors_edit_ui.state:
                factors = self._presenter.load_choosed_factors()
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
        except Exception as ex:
            print('error:', ex)


class SegmentModifyUI:
    def __init__(self):
        self._presenter = None
        self.state = False
        self.entries = []

        self.window = Gtk.Window()
        self.window.set_border_width(10)
        self.window.set_default_size(500, 150)
        self.ui = Gtk.Box()
        self.ui.set_orientation(Gtk.Orientation.VERTICAL)
        self.current_lower_label = Gtk.Label()
        self.current_upper_label = Gtk.Label()
        self.id_label = Gtk.Label()
        self.init_ui()
        self.set_window_header()
        self.window.add(self.ui)

    @property
    def presenter(self):
        return self._presenter

    @presenter.setter
    def presenter(self, value):
        self._presenter = value

    def set_window_header(self):
        header = Gtk.HeaderBar(title='SegmentModify')
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

    def init_ui(self):
        children = self.ui.get_children()
        if children:
            for child in children:
                self.ui.remove(child)

        info_box = Gtk.Box()
        info_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        info_box.set_homogeneous(True)
        info_box.pack_start(self.id_label, True, True, 0)
        upper_num_label = Gtk.Label(label="上界")
        lower_num_label = Gtk.Label(label="下界")
        info_box.pack_start(lower_num_label, True, True, 0)
        info_box.pack_start(upper_num_label, True, True, 0)
        self.ui.add(info_box)

        current_interval_box = Gtk.Box()
        current_interval_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        current_interval_box.set_homogeneous(True)
        current_label = Gtk.Label(label='当前区间')
        current_interval_box.pack_start(current_label, True, True, 0)
        current_interval_box.pack_start(self.current_lower_label, True, True, 0)
        current_interval_box.pack_start(self.current_upper_label, True, True, 0)
        self.ui.add(current_interval_box)

        interval_input_box = Gtk.Box()
        interval_input_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        interval_input_box.set_homogeneous(True)
        label = Gtk.Label(label='新区间')
        interval_input_box.pack_start(label, True, True, 0)
        lower_num_entry = Gtk.Entry()
        self.entries.append(lower_num_entry)
        upper_num_entry = Gtk.Entry()
        self.entries.append(upper_num_entry)
        interval_input_box.pack_start(lower_num_entry, True, True, 0)
        interval_input_box.pack_start(upper_num_entry, True, True, 0)
        self.ui.add(interval_input_box)

        button_box = Gtk.Box()
        button_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        confirm_button = Gtk.Button(label='确定修改')
        confirm_button.set_margin_top(5)
        confirm_button.set_margin_bottom(5)
        confirm_button.connect('clicked', self.confirm)
        button_box.pack_start(confirm_button, True, True, 50)
        cancel_button = Gtk.Button(label='取消')
        cancel_button.connect('clicked', self.cancel)
        cancel_button.set_margin_top(5)
        cancel_button.set_margin_bottom(5)
        button_box.pack_start(cancel_button, True, True, 50)
        self.ui.add(button_box)

    def update_current_segment_display(self, _id, lower_num, upper_num):
        self.current_lower_label.set_text('{}'.format(lower_num))
        self.current_upper_label.set_text('{}'.format(upper_num))
        self.id_label.set_text('{}'.format(_id))

    def confirm(self, widget):
        try:
            self._presenter.modify_segment()
            self._presenter.update_modified_segment()
            _id, lower_num, upper_num = self._presenter.load_choosed_segment()
            self.update_current_segment_display(_id, lower_num, upper_num)
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("修改成功")
            dialog.run()
            dialog.destroy()
        except Exception as ex:
            print(ex)
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("输入格式不正确")
            dialog.run()
            dialog.destroy()

    def cancel(self, widget):
        self.clear_entries()
        self.state = False
        self.window.hide()


class FactorsModifyUI:
    def __init__(self):
        self._presenter = None
        self.entries = []
        self.state = False
        self._curves = Image()

        self.window = Gtk.Window()
        self.window.set_border_width(10)
        self.window.set_default_size(300, 150)
        self.ui = Gtk.Box()
        self.init_ui()
        self.set_window_header()
        self.window.add(self.ui)

    @property
    def presenter(self):
        return self._presenter

    @presenter.setter
    def presenter(self, value):
        self._presenter = value

    def init_ui(self):
        self.ui.set_orientation(Gtk.Orientation.VERTICAL)

        label_box = Gtk.Box()
        label_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        label_box.set_homogeneous(True)
        current_factors_label = Gtk.Label()
        modified_factors_label = Gtk.Label()
        current_factors_label.set_text('当前校正系数')
        modified_factors_label.set_text('输入新系数')
        label_box.pack_start(current_factors_label, True, True, 0)
        label_box.pack_start(modified_factors_label, True, True, 0)
        self.ui.add(label_box)

        for i in range(6):
            child_box = Gtk.Box()
            child_box.set_orientation(Gtk.Orientation.HORIZONTAL)
            child_box.set_homogeneous(True)
            current_factor_show = Gtk.Label()
            modified_factor_entry = Gtk.Entry()
            child_box.pack_start(current_factor_show, True, True, 0)
            child_box.pack_start(modified_factor_entry, True, True, 0)
            self.entries.append(modified_factor_entry)
            self.ui.add(child_box)

        buttons_box = Gtk.Box()
        confirm_button = Gtk.Button(label='确定')
        confirm_button.set_margin_top(5)
        confirm_button.set_margin_bottom(5)
        confirm_button.connect('clicked', self.confirm)
        buttons_box.pack_start(confirm_button, True, True, 10)
        cancel_button = Gtk.Button(label='取消')
        cancel_button.connect('clicked', self.cancel)
        cancel_button.set_margin_top(5)
        cancel_button.set_margin_bottom(5)
        buttons_box.pack_start(cancel_button, True, True, 10)
        check_button = Gtk.Button(label='曲线')
        check_button.connect('clicked', self.check)
        check_button.set_margin_top(5)
        check_button.set_margin_bottom(5)
        buttons_box.pack_start(check_button, True, True, 10)
        self.ui.add(buttons_box)

    def update_current_factors(self, current_factors):
        factors_show_boxes = self.ui.get_children()[1:-1]
        for box in factors_show_boxes:
            current_factor_label = box.get_children()[0]
            current_index = factors_show_boxes.index(box)
            current_factor_label.set_text('{}'.format(current_factors[current_index]))

    def set_window_header(self):
        header = Gtk.HeaderBar(title='FactorsModify')
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

    def clear(self):
        children = self.ui.get_children()
        for child in children:
            self.ui.remove(child)

    def confirm(self, widget):
        try:
            factors = self._presenter.load_factors_entry()
            self.update_current_factors(factors)
            self._presenter.modify_factors()
            self._presenter.update_modified_factors()
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("修改成功")
            dialog.run()
            dialog.destroy()
        except Exception as ex:
            print(ex)
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("输入格式不正确")
            dialog.run()
            dialog.destroy()

    def cancel(self, widget):
        for entry in self.entries:
            entry.delete_text(0, -1)
        self.state = False
        self.window.hide()

    def check(self, widget):
        try:
            self._presenter.show_two_curves()
            if not self._curves.is_show:
                self._curves.update_img()
                self._curves.window.show_all()
                self._curves.is_show = True
            else:
                self._curves.window.hide()
                self._curves.is_show = False
        except Exception as ex:
            print(ex)
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("输入格式不正确")
            dialog.run()
            dialog.destroy()


class AddDependencyUI:
    def __init__(self):
        pass


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
        header = Gtk.HeaderBar(title='factors curves')
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
