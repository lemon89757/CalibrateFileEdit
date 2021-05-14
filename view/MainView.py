import gi
import os
import copy
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from intervals import FloatInterval
from presenter.MainUIPresenter import MainUIPresenter


class MainUI(Gtk.Window):
    def __init__(self, presenter=None):
        self._presenter = presenter

        # 方式一
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(os.path.dirname(__file__), 'MainUI.glade'))
        self.main_window = Gtk.Window()
        self.main_window.set_border_width(10)
        self.main_window.set_default_size(600, 450)
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
        self._depends_id = None

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

    def update_channels_combobox(self):
        channels_combobox = self.builder.get_object('channel_combobox')
        channels_combobox.clear()
        channels_model = Gtk.ListStore(int, str)
        channels_model.append([2020, '2020'])    # 默认通道
        channels = copy.deepcopy(self._presenter.get_channels())
        for channel in channels:
            channels_model.append([channels.index(channel), '通道{}'.format(channels.index(channel)+1)])
        channels_combobox.set_model(channels_model)
        channels_cell = Gtk.CellRendererText()
        channels_combobox.pack_start(channels_cell, True)
        channels_combobox.add_attribute(channels_cell, 'text', 1)
        channels_combobox.set_active(0)
        channels_combobox.connect('changed', self.update_calibrate_parameter_choose_combobox)

    def update_calibrate_parameter_choose_combobox(self, widget):
        channels_combobox = self.builder.get_object('channel_combobox')
        channel_activated = channels_combobox.get_active()
        model = channels_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(channel_activated))
        channel_index = model.get_value(_iter, 0)
        self._choose_channel_index = channel_index

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
            empty_model = False
        else:
            self.init_calibrate_parameter_choose_combobox()
            empty_model = True
        if empty_model:
            self.init_calibrate_model()
            self.update_dependencies_list()
            self.init_dependencies_segment_choose()
        else:
            parameter_combobox.connect('changed', self.update_three_about)

    def init_calibrate_parameter_choose_combobox(self):
        parameter_combobox = self.builder.get_object('calibrate_parameter_choose_combobox')
        empty_type_model = Gtk.ListStore(int, str)
        parameter_combobox.set_model(empty_type_model)

    def update_three_about(self, widget):
        self.update_calibrate_model()
        self.update_dependencies_list()
        self.update_dependencies_segment_choose()

    def update_calibrate_model(self):
        calibrate_model_label = self.builder.get_object('model_show_label')
        if self._choose_channel_index != 2020:
            parameter_combobox = self.builder.get_object('calibrate_parameter_choose_combobox')
            parameter_activated = parameter_combobox.get_active()
            model = parameter_combobox.get_model()
            _iter = model.get_iter_from_string('{}'.format(parameter_activated))
            calibrate_parameter = model.get_value(_iter, 0)

            if calibrate_parameter == 2020:
                self.init_calibrate_model()
                # self.init_dependencies_segment_choose()
            else:
                # print(calibrate_parameter)   # TODO 多次输出同一参数值
                calibrate_model = self._presenter.get_calibrate_model(calibrate_parameter, self._choose_channel_index)
                calibrate_model_label.set_text('校正类型{}'.format(calibrate_model))
        else:
            calibrate_model_label.set_text('校正类型2020')

    def init_calibrate_model(self):
        calibrate_model_label = self.builder.get_object('model_show_label')
        calibrate_model_label.set_text('校正类型2020')

    def update_dependencies_list(self):
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

                self.update_dependencies_segment_choose()

        dependencies_text_view.set_buffer(dependencies_text_buffer)
        dependencies_scrolled_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        child = dependencies_scrolled_win.get_child()
        if child:
            dependencies_scrolled_win.remove(child)
        dependencies_scrolled_win.add(dependencies_text_view)

        dependencies_scrolled_win.show_all()    # TODO show_all() 才能显示其中内容

    def init_dependencies_segment_choose(self):
        dependencies_choose_scroll_win = self.builder.get_object('depend_segment_choose_scrolled_window')
        viewport = dependencies_choose_scroll_win.get_child()
        if isinstance(viewport, Gtk.Viewport):
            main_box = viewport.get_child()
            boxes = main_box.get_children()
            for box in boxes:
                children = box.get_children()
                combobox = children[1]
                combobox.clear()
                model = Gtk.ListStore()
                combobox.set_model(model)

    def update_dependencies_segment_choose(self):
        parameter_combobox = self.builder.get_object('calibrate_parameter_choose_combobox')
        parameter_activated = parameter_combobox.get_active()
        model = parameter_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(parameter_activated))
        calibrate_parameter = model.get_value(_iter, 0)
        self._choose_parameter = calibrate_parameter

        if calibrate_parameter == 2020:
            self.init_dependencies_segment_choose()
        else:
            dependencies_choose_scroll_win = self.builder.get_object('depend_segment_choose_scrolled_window')
            child = dependencies_choose_scroll_win.get_child()
            if child:
                dependencies_choose_scroll_win.remove(child)
            depends_id = self._presenter.get_depends_id(self._choose_channel_index, calibrate_parameter)
            self._depends_id = depends_id

            viewport = Gtk.Viewport()
            main_box = Gtk.Box()

            for value in depends_id:
                child_box = Gtk.Box()
                child_box.set_orientation(Gtk.Orientation.VERTICAL)
                label = Gtk.Label()
                label.set_text('{}'.format(value))
                child_box.pack_start(label, True, True, 2)
                child_combobox = Gtk.ComboBox()
                child_model = Gtk.ListStore()
                child_combobox.set_model(child_model)
                # child_combobox.set_active(0)

                # child_model = Gtk.ListStore(int, str)  # TODO 怎样才能只放一个数据进去
                # for segment in first_segments:
                #     lower_num = segment.lower
                #     upper_num = segment.upper
                #     child_model.append([2020, '[{}, {}]'.format(lower_num, upper_num)])
                # child_combobox.set_model(child_model)
                child_box.pack_start(child_combobox, True, True, 2)
                main_box.add(child_box)

            viewport.add(main_box)
            dependencies_choose_scroll_win.add(viewport)
            dependencies_choose_scroll_win.show_all()
            self.update_first_depend_segments()

    def update_first_depend_segments(self):
        dependencies_choose_scroll_win = self.builder.get_object('depend_segment_choose_scrolled_window')
        viewport = dependencies_choose_scroll_win.get_child()
        main_box = viewport.get_child()

        boxes = main_box.get_children()
        first_box = boxes[0]
        first_box_children = first_box.get_children()
        first_combobox = first_box_children[1]
        first_combobox.clear()

        first_path = [[self._choose_parameter, None]]
        first_depend_id = self._depends_id[0]
        first_segments = self._presenter.get_depend_segments(self._choose_channel_index, self._choose_parameter,
                                                             first_path, first_depend_id)
        first_model = Gtk.ListStore(int, str)
        first_model.append([2020, '[2020, 2020]'])
        for segment in first_segments:
            lower_num = segment.lower
            upper_num = segment.upper
            first_model.append([2020, '[{}, {}]'.format(lower_num, upper_num)])
        first_combobox.set_model(first_model)
        first_cell = Gtk.CellRendererText()
        first_combobox.pack_start(first_cell, True)
        first_combobox.add_attribute(first_cell, 'text', 1)
        # first_combobox.set_active(0)

        first_combobox.connect('changed', self.update_next_depend_segment)

    def update_next_depend_segment(self, widget):
        dependencies_choose_scroll_win = self.builder.get_object('depend_segment_choose_scrolled_window')
        viewport = dependencies_choose_scroll_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()

        focus_box = main_box.get_focus_child()
        focus_box_children = focus_box.get_children()
        focus_label = focus_box_children[0]
        focus_parameter_id = int(focus_label.get_text())
        focus_combobox = focus_box_children[1]
        segment_activated = focus_combobox.get_active()
        model = focus_combobox.get_model()
        _iter = model.get_iter_from_string('{}'.format(segment_activated))
        segment_str = model.get_value(_iter, 1)
        focus_segment = FloatInterval.from_string(segment_str)

        default_segment = FloatInterval.closed(2020, 2020)
        # if focus_segment != default_segment:
        #     depend_path = self.update_depend_path(focus_parameter_id)
        focus_parameter_id_index = self._depends_id.index(focus_parameter_id)    # TODO 这里也遇到了相同执行多次的问题: set_active的问题？
        if focus_parameter_id_index+1 < len(self._depends_id):
            next_parameter_id = self._depends_id[focus_parameter_id_index+1]
            next_model = Gtk.ListStore(int, str)
            if focus_segment != default_segment:
                depend_path = self.update_depend_path(focus_parameter_id)
                next_segments = self._presenter.get_depend_segments(self._choose_channel_index, self._choose_parameter,
                                                                    depend_path, next_parameter_id)
                next_model.append([2020, '[2020, 2020]'])
                for segment in next_segments:
                    lower_num = segment.lower
                    upper_num = segment.upper
                    next_model.append([2020, '[{}, {}]'.format(lower_num, upper_num)])
            # former_box = boxes[self._depend_choosed_num - 1]
            # former_combobox = former_box.get_children()[1]
            # segment_activated = former_combobox.get_active()
            # model = former_combobox.get_model()
            # _iter = model.get_iter_from_string('{}'.format(segment_activated))
            # segment_str = model.get_value(_iter, 1)
            # segment = FloatInterval.from_string(segment_str)
            # self._depend_path.append([self._depends_id[self._depend_choosed_num - 1], segment])
            next_box = boxes[focus_parameter_id_index+1]
            next_combobox = next_box.get_children()[1]
            next_combobox.clear()
            # current_depend_id = self._depends_id[self._depend_choosed_num]
            # current_segments = self._presenter.get_depend_segments
            # (self._choose_channel_index, self._choose_parameter, self._depend_path, current_depend_id)
            next_combobox.set_model(next_model)
            current_cell = Gtk.CellRendererText()
            next_combobox.pack_start(current_cell, True)
            next_combobox.add_attribute(current_cell, 'text', 1)
            # next_combobox.set_active(0)

            next_combobox.connect('changed', self.update_next_depend_segment)

    def update_depend_path(self, parameter_id):
        dependencies_choose_scroll_win = self.builder.get_object('depend_segment_choose_scrolled_window')
        viewport = dependencies_choose_scroll_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()

        depend_path = [[self._choose_parameter, None]]
        for box in boxes:
            children = box.get_children()
            label = children[0]
            depend_id = int(label.get_text())
            combobox = children[1]
            segment_activated = combobox.get_active()
            model = combobox.get_model()
            _iter = model.get_iter_from_string('{}'.format(segment_activated))
            segment_str = model.get_value(_iter, 1)
            segment = FloatInterval.from_string(segment_str)
            # print(label.get_text()) print(segment)
            depend_path.append([depend_id, segment])
            if depend_id == parameter_id:
                break
        return depend_path

    def init_all(self):     # TODO 没写完
        self.update_channels_combobox()

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
