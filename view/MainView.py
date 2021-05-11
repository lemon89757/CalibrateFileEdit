import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from presenter.MainUIPresenter import MainUIPresenter


class MainUI(Gtk.Window):
    def __init__(self, presenter=None):
        self._presenter = presenter
        # 方式一
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(os.path.dirname(__file__), 'MainUI.glade'))
        self.main_window = Gtk.Window()
        self.main_window.set_border_width(10)
        self.main_window.set_default_size(600, 400)
        self.main_window_state = False  # TODO

        self.ui = self.builder.get_object('main_box')
        self.set_window_header()
        self.main_window.add(self.ui)
        self.main_window.show_all()
        # 方式二
        # Gtk.Window.__init__(self, title="AWGCalibration")
        # self.set_border_width(10)
        # self.set_default_size(600, 400)
        # self.builder = Gtk.Builder()
        # self.builder.add_from_file(os.path.join(os.path.dirname(__file__), 'MainUI.glade'))
        # self.view = self.builder.get_object('main_box')
        # self.set_window_header()
        # self.add(self.view)
        # self.show_all()

        self._channels = None

    @property
    def presenter(self):
        return self._presenter

    @presenter.setter
    def presenter(self, value):
        self._presenter = value

    def set_window_header(self):
        header = Gtk.HeaderBar(title='CalibrateFileEdit')
        header.props.show_close_button = False  # TODO
        # 方式一 上述状态改为False
        close_button = Gtk.Button()
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)  # TODO"window-close-symbolic"???
        close_button.set_image(img)
        close_button.connect('clicked', Gtk.main_quit)

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

        self.main_window.set_titlebar(header)
        # 方式二 上述状态改为True
        # self.set_titlebar(header)

    def maximize(self, widget):  # TODO
        if self.main_window.is_maximized():
            self.main_window.unmaximize()
        else:
            self.main_window.maximize()

    def minimize(self, widget):          # TODO
        self.main_window.iconify()

    def file_status_monitor(self):  # TODO 文件存在改动，文件名加后缀'*'
        # connect('chang', func)
        pass

    def init_button(self):
        senior_button = self.builder.get_object('senior_button')
        senior_button.connect('clicked', self.show_calibrate_tree_edit_ui)

        merge_file_button = self.builder.get_object('file_merge_button')
        merge_file_button.connect('clicked', self.show_merge_file_ui)

        edit_dependencies_button = self.builder.get_object('edit_depend_segment_button')
        edit_dependencies_button.connect('clicked', self.show_dependencies_edit_ui)

        edit_parameter_intervals_button = self.builder.get_object('calibrate_parameter_segment_edit_button')
        edit_parameter_intervals_button.connect('clicked', self.show_parameter_intervals_edit_ui)

        edit_factors_button = self.builder.get_object('calibrate_factors_edit_button')
        edit_factors_button.connect('clicked', self.show_factors_edit_ui)

        show_factors_curve_button = self.builder.get_object('current_factors_curve_button')
        show_factors_curve_button.connect('clicked', self.show_factors_curve)

        show_two_curves_button = self.builder.get_object('two_curves_button')
        show_two_curves_button.connect('clicked', self.show_two_curves)

    def init_channels_combobox(self):
        channels_combobox = self.builder.get_object('channel_combobox')
        channels_type_model = Gtk.ListStore(int, str)
        channels = self._presenter.get_channels()
        self._channels = channels
        for channel in channels:
            channels_type_model.append([channels.index(channel), '通道{}'.format(channels.index(channel))])
        channels_combobox.set_model(channels_type_model)
        channels_cell = Gtk.CellRendererText()
        channels_combobox.pack_start(channels_cell, True)
        channels_combobox.add_attribute(channels_cell, 'text', 1)
        channels_combobox.set_active(0)

    def init_calibrate_parameter_choose_combobox(self):
        channels_combobox = self.builder.get_object('channel_combobox')
        channel_index = channels_combobox.get_active()

        parameter_combobox = self.builder.get_object('calibrate_parameter_choose_combobox')
        parameter_type_model = Gtk.ListStore(int, int)
        choosed_channel = self._channels[channel_index]
        for parameter in choosed_channel.keys():
            parameter_type_model.append([parameter, parameter])
        parameter_combobox.set_model(parameter_type_model)
        parameter_cell = Gtk.CellRendererText()
        parameter_combobox.pack_start(parameter_cell, True)
        parameter_combobox.add_attribute(parameter_cell, 'text', 1)
        parameter_combobox.set_active(0)

    def init_calibrate_model(self):
        calibrate_model_label = self.builder.get_object('model_show_label')
        calibrate_model = self._presenter.get_calibrate_model()
        calibrate_model_label.set_text(calibrate_model)

    def init_file_open(self):
        open_item = self.builder.get_object('open_item')
        open_item.connect('activate', self.open_file)

    def open_file(self, widget):
        dialog = Gtk.FileChooserDialog()
        dialog.run()

    def show_calibrate_tree_edit_ui(self):
        pass

    def show_merge_file_ui(self):
        pass

    def show_dependencies_edit_ui(self):
        pass

    def show_parameter_intervals_edit_ui(self):
        pass

    def show_factors_edit_ui(self):
        pass

    def show_factors_curve(self):
        pass

    def show_two_curves(self):
        pass


if __name__ == '__main__':
    main_window = MainUI()
    main_window.init_file_open()
    Gtk.main()
