import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from presenter.DepdendciesEditUIPresenter import DependenciesEditUIPresenter


class DependenciesSegmentEditView:
    def __init__(self):
        self._presenter = DependenciesEditUIPresenter()
        self._presenter.view = self
        self.state = False
        self.entries = []
        self._current_segment_display = []
        self.dependencies_choose = None

        self.window = Gtk.Window()
        self.window.set_border_width(10)
        self.window.set_default_size(500, 150)
        self.ui = Gtk.Box()
        self.init_ui()
        self.set_window_header()
        self.window.add(self.ui)

    @property
    def presenter(self):
        return self._presenter

    def set_window_header(self):
        header = Gtk.HeaderBar(title='DependenciesSegmentEdit')
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

    def init_ui(self):
        self.ui.set_orientation(Gtk.Orientation.VERTICAL)

        dependencies_choose_box = Gtk.Box()
        dependencies_choose_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        choose_label = Gtk.Label(label='依赖选择')
        dependencies_choose_box.pack_start(choose_label, False, True, 10)
        self.dependencies_choose = Gtk.ComboBox()
        self.dependencies_choose.set_margin_top(10)
        self.dependencies_choose.set_margin_bottom(10)
        self.dependencies_choose.connect('changed', self.update_current_dependency_segment)
        # 一种信号的连接，在初始时连接好（只连接了一次）；否则会遇到重复连接函数执行的问题
        dependencies_choose_box.pack_start(self.dependencies_choose, False, True, 10)
        self.ui.add(dependencies_choose_box)

        info_box = Gtk.Box()
        info_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        info_box.set_homogeneous(True)
        empty_label = Gtk.Label()
        info_box.pack_start(empty_label, True, True, 0)
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
        current_lower_label = Gtk.Label(label='2020')
        self._current_segment_display.append(current_lower_label)
        current_upper_label = Gtk.Label(label='2020')
        self._current_segment_display.append(current_upper_label)
        current_interval_box.pack_start(current_lower_label, True, True, 0)
        current_interval_box.pack_start(current_upper_label, True, True, 0)
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

    def update_dependencies_choose(self):
        dependencies = self._presenter.get_dependencies_id()
        model = Gtk.ListStore(int, str)
        model.append([2020, '依赖参数选择'])
        for dependency in dependencies:
            model.append([dependency, '{}'.format(dependency)])
        child = self.dependencies_choose.get_child()
        if child:
            self.dependencies_choose.clear()
        self.dependencies_choose.set_model(model)
        cell = Gtk.CellRendererText()
        self.dependencies_choose.pack_start(cell, True)
        self.dependencies_choose.add_attribute(cell, 'text', 1)
        self.dependencies_choose.set_active(0)

    def clear_entries(self):
        for entry in self.entries:
            entry.delete_text(0, -1)

    def init_current_dependency_segment(self):
        for label in self._current_segment_display:
            label.set_text('请先选择依赖参数')

    def update_current_dependency_segment(self, widget):
        chosen_dependency = self._presenter.load_chosen_dependency()
        default_dependency = 2020
        if chosen_dependency == default_dependency:
            self.init_current_dependency_segment()
            self.clear_entries()
        else:
            try:
                current_segment = self._presenter.get_current_segment(chosen_dependency)
                lower_num = current_segment.lower
                upper_num = current_segment.upper
                lower_label = self._current_segment_display[0]
                upper_label = self._current_segment_display[1]
                lower_label.set_text('{}'.format(lower_num))
                upper_label.set_text('{}'.format(upper_num))
            except Exception as ex:
                print(ex)
                dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                           buttons=Gtk.ButtonsType.OK, text="提示")
                dialog.format_secondary_text("未完成选择依赖分段")
                dialog.run()
                dialog.destroy()

    def confirm(self, widget):
        current_depend = self._presenter.load_chosen_dependency()
        default_depend = 2020
        if current_depend == default_depend:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请选择有效依赖")
            dialog.run()
            dialog.destroy()
        else:
            try:
                self._presenter.modify_dependency_segment()
                self._presenter.update_modified_dependency_segment()
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


# if __name__ == '__main__':
#     window = DependenciesSegmentEditView()
#     Gtk.main()
