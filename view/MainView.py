import gi
import os
import copy
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

        self._choose_channel_index = None
        self._choose_parameter = None

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

    def init_file_operate(self):
        open_menu_item = self.builder.get_object('open_item')
        open_menu_item.connect('activate', self.open_file)

        new_menu_item = self.builder.get_object('new_item')
        new_menu_item.connect('activate', self.new_file)

        save_menu_item = self.builder.get_object('save_item')
        save_menu_item.connect('activate', self.save)

        save_as_menu_item = self.builder.get_object('save_as_item')
        save_as_menu_item.connect('activate', self.save_as)

    def init_edit_operate(self):
        edit_dependencies_menu_item = self.builder.get_object('edit_depend_segment_item')
        edit_dependencies_menu_item.connect('activate', self.show_dependencies_edit_ui)

        edit_parameter_intervals_menu_item = self.builder.get_object('edit_parameter_item')
        edit_parameter_intervals_menu_item.connect('activate', self.show_parameter_intervals_edit_ui)

        edit_factors_menu_item = self.builder.get_object('edit_factors_item')
        edit_factors_menu_item.connect('activate', self.show_factors_edit_ui)

    def init_display(self):
        show_factors_curve_menu_item = self.builder.get_object('display_factors_curve_item')
        show_factors_curve_menu_item.connect('activate', self.show_factors_curve)

        show_two_curves_menu_item = self.builder.get_object('display_two_curves_item')
        show_two_curves_menu_item.connect('activate', self.show_two_curves)

    def init_others(self):
        senior_menu_item = self.builder.get_object('senior_item')
        senior_menu_item.connect('activate', self.show_calibrate_tree_edit_ui)

        merge_file_menu_item = self.builder.get_object('merge_file_item')
        merge_file_menu_item.connect('activate', self.show_merge_file_ui)

    def init_channels_combobox(self):
        channels_combobox = self.builder.get_object('channel_combobox')
        channels_combobox.clear()
        channels_model = Gtk.ListStore(int, str)
        channels_model.append([2020, '通道2020'])    # 默认通道
        channels = copy.deepcopy(self._presenter.get_channels())
        for channel in channels:
            channels_model.append([channels.index(channel), '通道{}'.format(channels.index(channel)+1)])
        channels_combobox.set_model(channels_model)
        channels_cell = Gtk.CellRendererText()
        channels_combobox.pack_start(channels_cell, True)
        channels_combobox.add_attribute(channels_cell, 'text', 1)
        channels_combobox.set_active(0)
        channels_combobox.connect('changed', self.init_calibrate_parameter_choose_combobox)

    def init_calibrate_parameter_choose_combobox(self, widget):
        channels_combobox = self.builder.get_object('channel_combobox')
        channel_activated = channels_combobox.get_active()
        model = channels_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(channel_activated))
        channel_index = model.get_value(_iter, 0)
        self._choose_channel_index = channel_index
        empty_model = False

        parameter_combobox = self.builder.get_object('calibrate_parameter_choose_combobox')
        if channel_index != 2020:
            parameters_model = Gtk.ListStore(int, int)
            parameters_model.append([2020, 2020])          # 默认参数
            channels = self._presenter.get_channels()
            choosed_channel = channels[channel_index]
            for parameter in choosed_channel.keys():
                parameters_model.append([parameter, parameter])
            parameter_combobox.clear()
            parameter_combobox.set_model(parameters_model)
            parameter_cell = Gtk.CellRendererText()
            parameter_combobox.pack_start(parameter_cell, True)
            parameter_combobox.add_attribute(parameter_cell, 'text', 1)
            parameter_combobox.set_active(0)
        else:
            empty_type_model = Gtk.ListStore(int, str)
            parameter_combobox.set_model(empty_type_model)
            empty_model = True
        if empty_model:
            self.init_calibrate_model()
            self.init_dependencies_list()
        else:
            parameter_combobox.connect('changed', self.init_two_about)

    def init_two_about(self, widget):
        self.init_calibrate_model()
        self.init_dependencies_list()

    def init_calibrate_model(self):
        calibrate_model_label = self.builder.get_object('model_show_label')
        if self._choose_channel_index != 2020:
            parameter_combobox = self.builder.get_object('calibrate_parameter_choose_combobox')
            parameter_activated = parameter_combobox.get_active()
            model = parameter_combobox.get_model()
            _iter = model.get_iter_from_string('{}'.format(parameter_activated))
            calibrate_parameter = model.get_value(_iter, 0)
            self._choose_parameter = calibrate_parameter

            if calibrate_parameter == 2020:
                calibrate_model_label.set_text('校正类型2020')
            else:
                # print(calibrate_parameter)   # TODO 多次输出同一参数值
                calibrate_model = self._presenter.get_calibrate_model(calibrate_parameter, self._choose_channel_index)
                calibrate_model_label.set_text('校正类型{}'.format(calibrate_model))
        else:
            calibrate_model_label.set_text('校正类型2020')

    def init_dependencies_list(self):
        dependencies_scrolled_win = self.builder.get_object('dependencies_scrolled_window')
        dependencies_scrolled_win.set_sensitive(False)
        dependencies_text_buffer = Gtk.TextBuffer()
        dependencies_text_view = Gtk.TextView()
        if self._choose_channel_index != 2020:
            parameter_combobox = self.builder.get_object('calibrate_parameter_choose_combobox')
            parameter_activated = parameter_combobox.get_active()
            model = parameter_combobox.get_model()
            _iter = model.get_iter_from_string('{}'.format(parameter_activated))
            calibrate_parameter = model.get_value(_iter, 0)

            if calibrate_parameter != 2020 and self._choose_channel_index != 2020:
                dependencies_list = self._presenter.get_dependencies_list(calibrate_parameter,
                                                                          self._choose_channel_index)
                dependencies_text_buffer.set_text('{}'.format(dependencies_list))

                self.init_dependencies_segment_choose()

        dependencies_text_view.set_buffer(dependencies_text_buffer)
        dependencies_scrolled_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        child = dependencies_scrolled_win.get_child()
        if child:
            dependencies_scrolled_win.remove(child)
        dependencies_scrolled_win.add(dependencies_text_view)

        dependencies_scrolled_win.show_all()    # TODO show_all() 才能显示其中内容

    def init_dependencies_segment_choose(self):
        dependencies_choose_scroll_win = self.builder.get_object('depend_segment_choose_scrolled_window')

    def init_all(self):     # TODO 没写完
        self.init_channels_combobox()

    def open_file(self, widget):  # TODO
        dialog = Gtk.FileChooserDialog("文件选择", self.main_window,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            try:
                filename = dialog.get_filename()
                self._presenter.load_channels(filename)
                self.init_all()
                dialog.destroy()
            except Exception as ex:
                print(ex)
                error_dialog = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.ERROR,
                                                 Gtk.ButtonsType.CANCEL, "ERROR")
                error_dialog.format_secondary_text("文件选择有误，无法载入!")
                error_dialog.run()
                error_dialog.destroy()
                dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    def new_file(self):
        pass

    def save(self):
        pass

    def save_as(self):
        pass

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
    main_window.presenter = MainUIPresenter()
    main_window.init_file_operate()
    Gtk.main()

# TODO 设置控件比例、get_path
