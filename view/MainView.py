import gi
import os
import copy
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from intervals import FloatInterval
from presenter.MainUIPresenter import MainUIPresenter
from view.FactorsEditView import FactorsEditView


class MainUI(Gtk.Window):
    def __init__(self):
        self._factors_edit_ui = FactorsEditView()
        self._presenter = MainUIPresenter()
        self._presenter.view = self

        # 方式一
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(os.path.dirname(__file__), 'MainUI.glade'))
        self.main_window = Gtk.Window()
        self.main_window.set_border_width(10)
        self.main_window.set_default_size(500, 450)
        self.ui = self.builder.get_object('main_box')
        self.set_window_header()
        self.main_window.add(self.ui)
        self.main_window.show_all()

        self.channel_combobox = None
        self.calibrate_parameter_choose_combobox = None
        self.model_display_label = None
        self.dependencies_list_scrolled_win = None
        self.dependencies_segment_choose_scrolled_win = None
        self.calibrate_parameter_interval_choose_combobox = None
        self.factors_scrolled_win = None

        self._state = False
        self._depends_id = None
        self._parameter_segments = None
        self.curve = Image()

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

        # show_two_curves_menu_item = self.builder.get_object('display_two_curves_item')
        # show_two_curves_menu_item.connect('activate', self.show_two_curves)

    def init_others(self):
        senior_menu_item = self.builder.get_object('senior_item')
        senior_menu_item.connect('activate', self.show_calibrate_tree_edit_ui)

        merge_file_menu_item = self.builder.get_object('merge_file_item')
        merge_file_menu_item.connect('activate', self.show_merge_file_ui)

    def init_all_display_widget(self):
        self.channel_combobox = self.builder.get_object('channel_combobox')
        self.calibrate_parameter_choose_combobox = self.builder.get_object('calibrate_parameter_choose_combobox')
        self.model_display_label = self.builder.get_object('model_show_label')
        self.dependencies_list_scrolled_win = self.builder.get_object('dependencies_scrolled_window')
        self.dependencies_segment_choose_scrolled_win = self.builder.get_object('depend_segment_choose_scrolled_window')
        self.calibrate_parameter_interval_choose_combobox = \
            self.builder.get_object('calibrate_parameter_segment_choose_combobox')
        self.factors_scrolled_win = self.builder.get_object('calibrate_factors_scrolled_window')

    def update_channel_combobox(self):
        self.channel_combobox.clear()
        channels_model = Gtk.ListStore(int, str)
        channels_model.append([2020, '2020'])    # 默认通道
        channels = copy.deepcopy(self._presenter.get_channels())
        for channel in channels:
            channels_model.append([channels.index(channel), '通道{}'.format(channels.index(channel)+1)])
        self.channel_combobox.set_model(channels_model)
        channels_cell = Gtk.CellRendererText()
        self.channel_combobox.pack_start(channels_cell, True)
        self.channel_combobox.add_attribute(channels_cell, 'text', 1)
        self.channel_combobox.set_active(0)
        self.channel_combobox.connect('changed', self.update_calibrate_parameter_choose_combobox)

    def update_calibrate_parameter_choose_combobox(self, widget):
        channel_index = self._presenter.load_channel_index()
        if channel_index != 2020:
            parameters_model = Gtk.ListStore(int)
            parameters_model.append([2020])          # 默认参数
            channels = self._presenter.get_channels()
            choosed_channel = channels[channel_index]
            for parameter in choosed_channel.keys():
                parameters_model.append([parameter])
            self.calibrate_parameter_choose_combobox.clear()
            self.calibrate_parameter_choose_combobox.set_model(parameters_model)
            parameter_cell = Gtk.CellRendererText()
            self.calibrate_parameter_choose_combobox.pack_start(parameter_cell, True)
            self.calibrate_parameter_choose_combobox.add_attribute(parameter_cell, 'text', 0)
            self.calibrate_parameter_choose_combobox.set_active(0)
            empty_model = False
        else:
            self.clear_calibrate_parameter_choose_combobox()
            empty_model = True
        if empty_model:
            self.init_calibrate_model()
            self.update_dependencies_list()
            self.clear_dependencies_segment_choose()
            self.clear_calibrate_parameter_interval_combobox()
            self.clear_factors_scrolled_win()
        else:
            self.calibrate_parameter_choose_combobox.connect('changed', self.update_next_about)

    def clear_calibrate_parameter_choose_combobox(self):
        empty_type_model = Gtk.ListStore()
        self.calibrate_parameter_choose_combobox.set_model(empty_type_model)

    def update_next_about(self, widget):
        self.clear_factors_scrolled_win()
        self.clear_calibrate_parameter_interval_combobox()
        self.update_calibrate_model()
        self.update_dependencies_list()
        self.update_dependencies_segment_choose()

    def update_calibrate_model(self):
        channel_index = self._presenter.load_channel_index()
        if channel_index != 2020:
            calibrate_parameter = self._presenter.load_choosed_calibrate_parameter()
            if calibrate_parameter == 2020:
                self.init_calibrate_model()
            else:
                # print(calibrate_parameter)   # TODO 多次输出同一参数值
                calibrate_model = self._presenter.get_calibrate_model(calibrate_parameter, channel_index)
                self.model_display_label.set_text('校正类型{}'.format(calibrate_model))
        else:
            self.model_display_label.set_text('校正类型2020')

    def init_calibrate_model(self):
        self.model_display_label.set_text('校正类型2020')

    def update_dependencies_list(self):
        self.dependencies_list_scrolled_win.set_sensitive(True)
        dependencies_text_buffer = Gtk.TextBuffer()
        dependencies_text_view = Gtk.TextView()
        dependencies_text_view.set_sensitive(False)

        channel_index = self._presenter.load_channel_index()
        if channel_index != 2020:
            calibrate_parameter = self._presenter.load_choosed_calibrate_parameter()
            if calibrate_parameter != 2020 and channel_index != 2020:
                dependencies_list = self._presenter.get_dependencies_list(calibrate_parameter, channel_index)
                dependencies_text_buffer.set_text('{}'.format(dependencies_list))
                # self.update_dependencies_segment_choose()

        dependencies_text_view.set_buffer(dependencies_text_buffer)
        self.dependencies_list_scrolled_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        child = self.dependencies_list_scrolled_win.get_child()
        if child:
            self.dependencies_list_scrolled_win.remove(child)
        self.dependencies_list_scrolled_win.add(dependencies_text_view)
        self.dependencies_list_scrolled_win.show_all()    # TODO show_all() 才能显示其中内容

    def clear_dependencies_segment_choose(self):
        viewport = self.dependencies_segment_choose_scrolled_win.get_child()
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
        calibrate_parameter = self._presenter.load_choosed_calibrate_parameter()
        channel_index = self._presenter.load_channel_index()

        if calibrate_parameter == 2020:
            self.clear_dependencies_segment_choose()
            self.clear_calibrate_parameter_interval_combobox()
        else:
            child = self.dependencies_segment_choose_scrolled_win.get_child()
            if child:
                self.dependencies_segment_choose_scrolled_win.remove(child)
            depends_id = self._presenter.get_depends_id(channel_index, calibrate_parameter)
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
                child_box.pack_start(child_combobox, True, True, 2)
                main_box.add(child_box)

            viewport.add(main_box)
            self.dependencies_segment_choose_scrolled_win.add(viewport)
            self.dependencies_segment_choose_scrolled_win.show_all()
            self.update_first_depend_segments()

    def update_first_depend_segments(self):
        calibrate_parameter = self._presenter.load_choosed_calibrate_parameter()
        channel_index = self._presenter.load_channel_index()

        viewport = self.dependencies_segment_choose_scrolled_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()
        first_box = boxes[0]
        first_box_children = first_box.get_children()
        first_combobox = first_box_children[1]
        first_combobox.clear()

        first_path = [[calibrate_parameter, None]]
        first_depend_id = self._depends_id[0]
        first_segments = self._presenter.get_depend_segments(channel_index, calibrate_parameter,
                                                             first_path, first_depend_id)
        first_model = Gtk.ListStore(str)
        first_model.append(['[2020, 2020]'])
        for segment in first_segments:
            lower_num = segment.lower
            upper_num = segment.upper
            first_model.append(['[{}, {}]'.format(lower_num, upper_num)])
        first_combobox.set_model(first_model)
        first_cell = Gtk.CellRendererText()
        first_combobox.pack_start(first_cell, True)
        first_combobox.add_attribute(first_cell, 'text', 0)
        # first_combobox.set_active(0)
        if len(self._depends_id) != 1:
            first_combobox.connect('changed', self.update_next_depend_segment)
        else:
            first_combobox.connect('changed', self.update_calibrate_parameter_interval_combobox)

    def update_next_depend_segment(self, widget):
        self.clear_calibrate_parameter_interval_combobox()
        self.clear_factors_scrolled_win()

        viewport = self.dependencies_segment_choose_scrolled_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()

        channel_index = self._presenter.load_channel_index()
        calibrate_parameter = self._presenter.load_choosed_calibrate_parameter()
        focus_depend_id, focus_segment = self._presenter.load_focus_depend()
        default_segment = FloatInterval.closed(2020, 2020)
        # if focus_segment != default_segment:
        #     depend_path = self.update_depend_path(focus_depend_id)
        focus_depend_id_index = self._depends_id.index(focus_depend_id)    # TODO 这里也遇到了相同执行多次的问题: set_active的问题？
        if focus_depend_id_index+1 < len(self._depends_id):
            next_parameter_id = self._depends_id[focus_depend_id_index+1]
            next_model = Gtk.ListStore(str)
            if focus_segment != default_segment:
                depend_path = self._presenter.load_depend_path(focus_depend_id)
                next_segments = self._presenter.get_depend_segments(channel_index, calibrate_parameter,
                                                                    depend_path, next_parameter_id)
                next_model.append(['[2020, 2020]'])
                for segment in next_segments:
                    lower_num = segment.lower
                    upper_num = segment.upper
                    next_model.append(['[{}, {}]'.format(lower_num, upper_num)])
                next_box = boxes[focus_depend_id_index+1]
                next_label = next_box.get_children()[0]
                next_depend_id = int(next_label.get_text())
                next_combobox = next_box.get_children()[1]
                next_combobox.clear()
                next_combobox.set_model(next_model)
                current_cell = Gtk.CellRendererText()
                next_combobox.pack_start(current_cell, True)
                next_combobox.add_attribute(current_cell, 'text', 0)
                # next_combobox.set_active(0)
                if next_depend_id == self._depends_id[-1]:
                    next_combobox.connect('changed', self.update_calibrate_parameter_interval_combobox)
                else:
                    next_combobox.connect('changed', self.update_next_depend_segment)
            else:
                for box in boxes[focus_depend_id_index+1:]:
                    combobox = box.get_children()[1]
                    combobox.clear()
                    empty_model = Gtk.ListStore()
                    combobox.set_model(empty_model)

    def clear_calibrate_parameter_interval_combobox(self):
        empty_model = Gtk.ListStore()
        self.calibrate_parameter_interval_choose_combobox.clear()
        self.calibrate_parameter_interval_choose_combobox.set_model(empty_model)

    def update_calibrate_parameter_interval_combobox(self, widget):
        self.clear_factors_scrolled_win()
        self.calibrate_parameter_interval_choose_combobox.clear()

        calibrate_parameter = self._presenter.load_choosed_calibrate_parameter()
        channel_index = self._presenter.load_channel_index()
        last_segment = self._presenter.load_last_dependency_segment()
        default_segment = FloatInterval.closed(2020, 2020)

        if last_segment == default_segment:
            self.clear_calibrate_parameter_interval_combobox()
        else:
            parameter_path = self._presenter.load_parameter_node_path()
            parameter_segments = self._presenter.get_calibrate_parameter_segments(channel_index,
                                                                                  calibrate_parameter, parameter_path)
            self._parameter_segments = parameter_segments

            interval_model = Gtk.ListStore(str)
            interval_model.append(['[2020, 2020]'])
            for interval in parameter_segments.keys():
                lower_num = interval.lower
                upper_num = interval.upper
                interval_model.append(['[{}, {}]'.format(lower_num, upper_num)])
            self.calibrate_parameter_interval_choose_combobox.set_model(interval_model)
            cell = Gtk.CellRendererText()
            self.calibrate_parameter_interval_choose_combobox.pack_start(cell, True)
            self.calibrate_parameter_interval_choose_combobox.add_attribute(cell, 'text', 0)
            self.calibrate_parameter_interval_choose_combobox.connect('changed', self.update_factors_scrolled_win)

    def clear_factors_scrolled_win(self):
        self.factors_scrolled_win.set_sensitive(False)
        factors_text_view = Gtk.TextView()
        child = self.factors_scrolled_win.get_child()
        if child:
            self.factors_scrolled_win.remove(child)
        self.factors_scrolled_win.add(factors_text_view)

    def update_factors_scrolled_win(self, widget):
        self.factors_scrolled_win.set_sensitive(True)
        factors_text_buffer = Gtk.TextBuffer()
        factors_text_view = Gtk.TextView()
        factors_text_view.set_sensitive(False)   # TODO 滚动窗口的显示有较长延迟

        interval = self._presenter.load_choosed_parameter_interval()
        default_interval = FloatInterval.closed(2020, 2020)
        if default_interval == interval:
            self.clear_factors_scrolled_win()
        else:
            factors = self._parameter_segments[interval]
            factors_text_buffer.set_text('{}'.format(factors))
            factors_text_view.set_buffer(factors_text_buffer)

            self.factors_scrolled_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            child = self.factors_scrolled_win.get_child()
            if child:
                self.factors_scrolled_win.remove(child)
            self.factors_scrolled_win.add(factors_text_view)

        self.factors_scrolled_win.show_all()

    def init_all(self):     # TODO 没写完
        if not self._state:
            self.init_all_display_widget()
            self.init_display()
            self.init_edit_operate()
            self.update_channel_combobox()
            self._state = True
        else:
            title_bar = self.main_window.get_titlebar()
            title_bar.set_title('CalibrateFileEdit')
            self.update_channel_combobox()

    def update_modified_factors_scrolled_win(self, new_factors):
        calibrate_parameter = self._presenter.load_choosed_calibrate_parameter()
        channel_index = self._presenter.load_channel_index()
        parameter_path = self._presenter.load_parameter_node_path()
        self._parameter_segments = self._presenter.get_calibrate_parameter_segments(channel_index,
                                                                                    calibrate_parameter, parameter_path)
        # 更新self._parameter_segments

        self.factors_scrolled_win.set_sensitive(True)
        factors_text_buffer = Gtk.TextBuffer()
        factors_text_view = Gtk.TextView()
        factors_text_view.set_sensitive(False)

        factors_text_buffer.set_text('{}'.format(new_factors))
        factors_text_view.set_buffer(factors_text_buffer)

        child = self.factors_scrolled_win.get_child()
        if child:
            self.factors_scrolled_win.remove(child)
        self.factors_scrolled_win.add(factors_text_view)
        self.factors_scrolled_win.show_all()

    def update_file_name_state(self):
        title_bar = self.main_window.get_titlebar()
        title_bar.set_title('CalibrateFileEdit*')

    def open_file(self, widget):  # TODO
        dialog = Gtk.FileChooserDialog(title="文件选择", parent=self.main_window,
                                       action=Gtk.FileChooserAction.OPEN,
                                       buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
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

    def save(self, widget):
        self._presenter.save()
        title_bar = self.main_window.get_titlebar()
        title_bar.set_title('CalibrateFileEdit')

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

    def show_factors_edit_ui(self, widget):
        try:
            if not self._factors_edit_ui.state:
                factors = self._presenter.load_current_factors()
                # self._factors_edit_ui.clear()
                # self._factors_edit_ui.init_ui()
                self._factors_edit_ui.presenter.editor = self.presenter
                self._factors_edit_ui.update_current_factors(factors)
                self._factors_edit_ui.window.show_all()
                self._factors_edit_ui.state = True
            else:
                self._factors_edit_ui.window.hide()
                self._factors_edit_ui.state = False
        except Exception as ex:
            print(ex)
            dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择出校正系数")
            dialog.run()
            dialog.destroy()

    def show_factors_curve(self, widget):
        try:
            # text_view = self.factors_scrolled_win.get_child()
            # buffer = text_view.get_buffer()
            # start_iter = buffer.get_start_iter()
            # end_iter = buffer.get_end_iter()
            # text = buffer.get_text(start_iter, end_iter, False)
            # if len(text) == 0:
            #     raise ValueError
            # factors = eval(text)
            # print(type(text), eval(text))   # TODO 换文件（或通道）后同样的会执行多次，即输出多次，（后面图片显示也出现多个）；还未第一次更新系数滚动窗口却已经有text_view
            self._presenter.show_factors_curve()  # TODO 关闭matplotlib画出的图像，程序结束运行；将图像保存再显示，但同次运行程序多次画图结果会叠加在一起（直接显示也是如此）
            if not self.curve.is_show:
                self.curve.update_img()
                self.curve.window.show_all()
                self.curve.is_show = True
            else:
                self.curve.window.hide()     # TODO 还是存在之前可以打开多个的问题， 或者不能重复打开
                self.curve.is_show = False
        except Exception as ex:
            print(ex)
            dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择出校正系数")
            dialog.run()
            dialog.destroy()
        # self._presenter.show_factors_curve()  # 先检查系数是否为空 AttributeError

    def show_two_curves(self, widget):
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
        self.image.set_from_file(r"..\image\factors_curve.png")
        self.window.add(self.image)

    def set_window_header(self):
        header = Gtk.HeaderBar(title='factors curve')
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

    def hide(self, widget):  # close的问题：关闭之后程序虽然不结束运行，但是不能再次正确打开
        self.is_show = False
        self.window.hide()

    def maximize(self, widget):
        if self.window.is_maximized():
            self.window.unmaximize()
        else:
            self.window.maximize()

    def minimize(self, widget):
        self.window.iconify()


if __name__ == '__main__':
    main_window = MainUI()
    main_window.init_file_operate()
    Gtk.main()

# TODO 设置控件比例、get_path
