import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from presenter.MergeUIPresenter import MergeUIPresenter


class MergeView:
    def __init__(self):
        self._presenter = MergeUIPresenter()
        self._presenter.view = self
        self.state = False
        self.chosen_merged_channel_index = None
        self.chosen_other_channel_index = None
        self.chosen_other_calibrate_parameter = None
        self.file_chooser = None

        self.window = Gtk.Window()
        self.window.set_border_width(10)
        self.window.set_default_size(400, 150)
        self.ui = None
        self.get_all_widget()
        self.set_window_header()
        self.window.add(self.ui)

    @property
    def presenter(self):
        return self._presenter

    def set_window_header(self):
        header = Gtk.HeaderBar(title='文件合并')
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
        self.file_chooser.set_filename('(无)')
        self.state = False
        self.window.hide()

    def hide_(self):
        self.file_chooser.set_filename('(无)')
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
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'glade/MergeUI.glade'))
        self.ui = builder.get_object('merge_grid')
        self.chosen_merged_channel_index = builder.get_object('into_file_ channel_choose_combo')
        self.chosen_other_channel_index = builder.get_object('current_file_channel_choose_combo')
        self.chosen_other_channel_index.connect('changed', self.update_other_available_calibrate_parameter)
        self.chosen_other_calibrate_parameter = builder.get_object('calibrate_parameter_choose_combo')
        into_channel_button = builder.get_object('into_channel_button')
        into_channel_button.connect('clicked', self.confirm_channel)
        into_parameter_button = builder.get_object('into_parameter_button')
        into_parameter_button.connect('clicked', self.confirm_parameter)
        cancel_button = builder.get_object('cancel_button')
        cancel_button.connect('clicked', self.hide)
        self.file_chooser = builder.get_object('file_chooser_button')
        self.file_chooser.connect('file_set', self.open_file)

    def update_merged_file_channel_choose(self):
        self.chosen_merged_channel_index.clear()
        channels_model = Gtk.ListStore(int, str)
        channels = self._presenter.get_channels()
        for channel in channels:
            channels_model.append([channels.index(channel), '通道{}'.format(channels.index(channel) + 1)])
        self.chosen_merged_channel_index.set_model(channels_model)
        channels_cell = Gtk.CellRendererText()
        self.chosen_merged_channel_index.pack_start(channels_cell, True)
        self.chosen_merged_channel_index.add_attribute(channels_cell, 'text', 1)
        self.chosen_merged_channel_index.set_active(0)

    def update_other_available_calibrate_parameter(self, widget):
        channel_index = self._presenter.load_other_channel_index()
        if channel_index != 2020:
            parameters_model = Gtk.ListStore(int, str)
            parameters_model.append([2020, '--请先选择校正参数--'])  # 默认参数
            channels = self._presenter.get_other_file_channels()
            chosen_channel = channels[channel_index]
            for parameter in chosen_channel.keys():
                parameters_model.append([parameter, '{}'.format(parameter)])
            self.chosen_other_calibrate_parameter.clear()
            self.chosen_other_calibrate_parameter.set_model(parameters_model)
            parameter_cell = Gtk.CellRendererText()
            self.chosen_other_calibrate_parameter.pack_start(parameter_cell, True)
            self.chosen_other_calibrate_parameter.add_attribute(parameter_cell, 'text', 1)
            self.chosen_other_calibrate_parameter.set_active(0)
        else:
            self.clear_other_calibrate_parameter_combobox()

    def clear_other_calibrate_parameter_combobox(self):
        empty_model = Gtk.ListStore()
        self.chosen_other_calibrate_parameter.clear()
        self.chosen_other_calibrate_parameter.set_model(empty_model)

    def clear_all_other_file_widget(self):
        empty_model = Gtk.ListStore()   # 不添加这个空模式，重复点击出合并界面时会崩溃
        self.chosen_other_calibrate_parameter.clear()
        self.chosen_other_calibrate_parameter.set_model(empty_model)
        self.chosen_other_channel_index.clear()
        self.chosen_other_channel_index.set_model(empty_model)

    def confirm_parameter(self, widget):
        try:
            self._presenter.confirm_parameter()
            self._presenter.update_main_ui()
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("操作成功")
            dialog.run()
            dialog.destroy()
        except ValueError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("所选参数不符要求，请检查通道中是否已存在此参数")
            dialog.run()
            dialog.destroy()
        self.clear_all_other_file_widget()
        self.hide_()

    def confirm_channel(self, widget):
        try:
            self._presenter.confirm_channel()
            self._presenter.update_main_ui()
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("操作成功")
            dialog.run()
            dialog.destroy()
        except ValueError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请检查是否选择有效通道")
            dialog.run()
            dialog.destroy()
        self.clear_all_other_file_widget()
        self.hide_()

    def update_other_file_channel_choose(self):
        self.chosen_other_calibrate_parameter.clear()
        self.chosen_other_channel_index.clear()

        channels_model = Gtk.ListStore(int, str)
        channels_model.append([2020, '--请先选择通道--'])  # 默认通道
        channels = self._presenter.get_other_file_channels()
        for channel in channels:
            channels_model.append([channels.index(channel), '通道{}'.format(channels.index(channel) + 1)])
        self.chosen_other_channel_index.set_model(channels_model)
        channels_cell = Gtk.CellRendererText()
        self.chosen_other_channel_index.pack_start(channels_cell, True)
        self.chosen_other_channel_index.add_attribute(channels_cell, 'text', 1)
        self.chosen_other_channel_index.set_active(0)

    def open_file(self, widget):
        file_name = self.file_chooser.get_filename()
        try:
            self._presenter.load_other_file(file_name)
            self.update_other_file_channel_choose()
        except Exception as ex:
            print(ex)
            error_dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.ERROR,
                                                     Gtk.ButtonsType.CANCEL, "ERROR")
            error_dialog.format_secondary_text("文件选择有误，无法载入!")
            error_dialog.run()
            error_dialog.destroy()

