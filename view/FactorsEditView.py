import gi
gi.require_version("Gtk", '3.0')
from gi.repository import Gtk
from presenter.FactorsEditUIPresenter import FactorsEditUIPresenter


class FactorsEditView:
    def __init__(self):
        self._presenter = FactorsEditUIPresenter()
        self._presenter.view = self
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
            # current_factor_show.set_text('{}'.format(self._current_factors[i]))
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
        header = Gtk.HeaderBar(title='FactorsEdit')
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

    def hide_(self):
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
            self._presenter.modify_factors()
            self._presenter.update_modified_factors()
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("修改成功")
            dialog.run()
            dialog.destroy()
            self.hide_()
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
            self.presenter.show_two_curves()
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
#     window = FactorsEditView()
#     Gtk.main()
