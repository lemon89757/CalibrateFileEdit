import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from presenter.MergeUIPresenter import MergeUIPresenter


class MergeView:
    def __init__(self):
        self._presenter = MergeUIPresenter()
        self._presenter.view = self
        self.state = False

        self.window = Gtk.Window()
        self.window.set_border_width(10)
        self.window.set_default_size(500, 150)
        self.ui = Gtk.Box()
        self.set_window_header()
        self.window.add(self.ui)

        self.chosen_merged_channel_index = None
        self.chosen_other_channel_index = None
        self.chosen_other_calibrate_parameter = None
        self.init_ui()

    @property
    def presenter(self):
        return self._presenter

    def set_window_header(self):
        header = Gtk.HeaderBar(title='Merge')
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
        self.window.hide()

    def hide_(self):
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

        open_file_box = Gtk.Box()
        open_file_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        open_file_button = Gtk.Button(label='文件选择')
        open_file_button.connect('clicked', self.open_file)
        open_file_button.set_margin_top(10)
        open_file_button.set_margin_bottom(10)
        open_file_box.pack_start(open_file_button, False, True, 10)
        self.ui.add(open_file_box)

        merged_file_box = Gtk.Box()
        merged_file_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        # current_file_box.set_homogeneous(True)
        merged_file_label = Gtk.Label(label='导入文件通道选择')
        merged_file_box.pack_start(merged_file_label, False, True, 10)
        self.chosen_merged_channel_index = Gtk.ComboBox()
        self.chosen_merged_channel_index.set_margin_top(10)
        self.chosen_merged_channel_index.set_margin_bottom(10)
        merged_file_box.pack_end(self.chosen_merged_channel_index, True, True, 10)
        self.ui.add(merged_file_box)

        other_file_box = Gtk.Box()
        other_file_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        # other_file_box.set_homogeneous(True)
        other_file_label = Gtk.Label(label='当前文件参数选择')
        other_file_box.pack_start(other_file_label, False, True, 10)
        self.chosen_other_channel_index = Gtk.ComboBox()
        self.chosen_other_channel_index.set_margin_top(10)
        self.chosen_other_channel_index.set_margin_bottom(10)
        self.chosen_other_channel_index.connect('changed', self.update_other_available_calibrate_parameter)
        other_file_box.pack_start(self.chosen_other_channel_index, True, True, 10)
        self.chosen_other_calibrate_parameter = Gtk.ComboBox()
        self.chosen_other_calibrate_parameter.set_margin_top(10)
        self.chosen_other_calibrate_parameter.set_margin_bottom(10)
        other_file_box.pack_end(self.chosen_other_calibrate_parameter, True, True, 10)
        self.ui.add(other_file_box)

        button_choose_box = Gtk.Box()
        button_choose_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        # interval_input_box.set_homogeneous(True)
        merge_channel_button = Gtk.Button(label='合并通道')
        merge_channel_button.connect('clicked', self.confirm_channel)
        merge_channel_button.set_margin_top(10)
        merge_channel_button.set_margin_bottom(10)
        button_choose_box.pack_start(merge_channel_button, False, True, 0)
        merge_parameter_button = Gtk.Button(label='合并参数')
        merge_parameter_button.connect('clicked', self.confirm_parameter)
        merge_parameter_button.set_margin_top(10)
        merge_parameter_button.set_margin_bottom(10)
        button_choose_box.pack_start(merge_parameter_button, False, True, 120)
        cancel_button = Gtk.Button(label='取消')
        cancel_button.connect('clicked', self.hide)
        cancel_button.set_margin_top(10)
        cancel_button.set_margin_bottom(10)
        button_choose_box.pack_end(cancel_button, False, True, 0)
        self.ui.add(button_choose_box)

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
        except Exception as ex:
            print(ex)
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
        except Exception as ex:
            print(ex)
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
        dialog = Gtk.FileChooserDialog(title="文件选择", parent=self.window,
                                       action=Gtk.FileChooserAction.OPEN,
                                       buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            try:
                filename = dialog.get_filename()
                self._presenter.load_other_file(filename)
                self.update_other_file_channel_choose()
                dialog.destroy()
            except Exception as ex:
                print(ex)
                error_dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.ERROR,
                                                 Gtk.ButtonsType.CANCEL, "ERROR")
                error_dialog.format_secondary_text("文件选择有误，无法载入!")
                error_dialog.run()
                error_dialog.destroy()
                dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()


# if __name__ == '__main__':
#     win = MergeView()
#     win.window.show_all()
#     Gtk.main()
