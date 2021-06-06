import gi
import os
import intervals
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
        self.ui = None
        self.get_all_widget()
        self.set_window_header()
        self.window.add(self.ui)

    @property
    def presenter(self):
        return self._presenter

    def set_window_header(self):
        header = Gtk.HeaderBar(title='依赖分段编辑')
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

    def hide_(self):
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

    def get_all_widget(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'glade/EditDependencySegmentUI.glade'))
        self.ui = builder.get_object('edit_dependency_segment_grid')
        current_lower_label = builder.get_object('current_segment_lower_label')
        self._current_segment_display.append(current_lower_label)
        current_upper_label = builder.get_object('current_segment_upper_label')
        self._current_segment_display.append(current_upper_label)
        lower_num_entry = builder.get_object('segment_lower_num_entry')
        upper_num_entry = builder.get_object('segment_upper_num_entry')
        self.entries = [lower_num_entry, upper_num_entry]
        confirm_button = builder.get_object('confirm_button')
        confirm_button.connect('clicked', self.confirm)
        cancel_button = builder.get_object('cancel_button')
        cancel_button.connect('clicked', self.cancel)
        self.dependencies_choose = builder.get_object('dependency_choose_combo')
        self.dependencies_choose.connect('changed', self.update_current_dependency_segment)

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
            except ValueError:
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
                self.hide_()
            except ValueError:
                dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                           buttons=Gtk.ButtonsType.OK, text="提示")
                dialog.format_secondary_text("输入格式不正确:"
                                             "请输入浮点数或整数")
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

