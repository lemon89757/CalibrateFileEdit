import gi
import os
import copy
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from intervals import FloatInterval
from presenter.MainUIPresenter import MainUIPresenter
from view.FactorsEditView import FactorsEditView
from view.ParameterIntervalEditView import ParameterIntervalEditView
from view.DependenciesSegmentEditView import DependenciesSegmentEditView
from view.SeniorView import SeniorUI
from view.MergeView import MergeView


class MainUI:
    def __init__(self):
        self._factors_edit_ui = FactorsEditView()
        self._parameter_interval_ui = ParameterIntervalEditView()
        self._dependencies_segment_ui = DependenciesSegmentEditView()
        self._senior_ui = SeniorUI()
        self._merge_ui = MergeView()
        self._presenter = MainUIPresenter()
        self._presenter.view = self

        # 方式一
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(os.path.dirname(__file__), 'glade/MainUI.glade'))
        self.main_window = Gtk.Window()
        self.main_window.set_border_width(10)
        self.main_window.set_default_size(500, 450)
        self.ui = self.builder.get_object('main_container')
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
        self._is_update_all_dependencies_segment_choose = False
        self._depends_id = None
        self._parameter_segments = None
        self.curve = Image()
        self._parameter_dict = self._presenter.get_parameter_dict()

        self.init_child_ui_editor()

    @property
    def presenter(self):
        return self._presenter

    @presenter.setter
    def presenter(self, value):
        self._presenter = value

    def set_window_header(self):
        header = Gtk.HeaderBar(title='校正文件编辑')
        header.props.show_close_button = False  # TODO

        # 方式一 上述状态改为False
        close_button = Gtk.Button()
        close_button.set_relief(Gtk.ReliefStyle.NONE)
        img = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.MENU)
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

    def maximize(self, widget):
        if self.main_window.is_maximized():
            self.main_window.unmaximize()
        else:
            self.main_window.maximize()

    def minimize(self, widget):
        self.main_window.iconify()

    def init_child_ui_editor(self):
        self._dependencies_segment_ui.presenter.editor = self.presenter
        self._factors_edit_ui.presenter.editor = self.presenter
        self._parameter_interval_ui.presenter.editor = self.presenter
        self._senior_ui.presenter.editor = self._presenter
        self._merge_ui.presenter.editor = self._presenter

    def init_file_operate(self):
        open_menu_item = self.builder.get_object('open_item')
        open_menu_item.connect('activate', self.open_file)

        save_menu_item = self.builder.get_object('save_item')
        save_menu_item.connect('activate', self.save)

        save_as_menu_item = self.builder.get_object('save_as_item')
        save_as_menu_item.connect('activate', self.save_as)

    def init_edit_operate(self):
        edit_dependencies_menu_item = self.builder.get_object('edit_depend_segment_button')
        edit_dependencies_menu_item.connect('clicked', self.show_dependencies_edit_ui)

        edit_parameter_intervals_menu_item = self.builder.get_object('edit_parameter_button')
        edit_parameter_intervals_menu_item.connect('clicked', self.show_parameter_intervals_edit_ui)

        edit_factors_menu_item = self.builder.get_object('edit_factors_button')
        edit_factors_menu_item.connect('clicked', self.show_factors_edit_ui)

    def init_display(self):
        show_factors_curve_menu_item = self.builder.get_object('display_factors_curve_button')
        show_factors_curve_menu_item.connect('clicked', self.show_factors_curve)

    def init_others(self):
        senior_menu_item = self.builder.get_object('senior_item')
        senior_menu_item.connect('activate', self.show_calibrate_tree_edit_ui)

        merge_file_menu_item = self.builder.get_object('merge_file_item')
        merge_file_menu_item.connect('activate', self.show_merge_file_ui)

    def init_all_display_widget(self):
        self.channel_combobox = self.builder.get_object('channel_combobox')
        self.channel_combobox.connect('changed', self.update_calibrate_parameter_choose_combobox)
        self.calibrate_parameter_choose_combobox = self.builder.get_object('calibrate_parameter_choose_combobox')
        self.calibrate_parameter_choose_combobox.connect('changed', self.update_next_about)
        self.model_display_label = self.builder.get_object('model_show_label')
        self.dependencies_list_scrolled_win = self.builder.get_object('dependencies_scrolled_window')
        self.dependencies_segment_choose_scrolled_win = self.builder.get_object('depend_segment_choose_scrolled_window')
        self.calibrate_parameter_interval_choose_combobox = \
            self.builder.get_object('calibrate_parameter_segment_choose_combobox')
        self.calibrate_parameter_interval_choose_combobox.connect('changed', self.update_factors_scrolled_win)
        self.factors_scrolled_win = self.builder.get_object('calibrate_factors_scrolled_window')

    def update_channel_combobox(self):
        self.channel_combobox.clear()
        channels_model = Gtk.ListStore(int, str)
        channels_model.append([2020, '--请先选择通道--'])    # 默认通道
        channels = copy.deepcopy(self._presenter.get_channels())
        channel_num = len(channels)
        for i in range(channel_num):
            channels_model.append([i, '通道{}'.format(i+1)])
        self.channel_combobox.set_model(channels_model)
        channels_cell = Gtk.CellRendererText()
        self.channel_combobox.pack_start(channels_cell, True)
        self.channel_combobox.add_attribute(channels_cell, 'text', 1)
        self.channel_combobox.set_active(0)

    def update_calibrate_parameter_choose_combobox(self, widget):
        channel_index = self._presenter.load_channel_index()
        if channel_index != 2020:
            parameters_model = self.get_parameters_model(channel_index)
            self.calibrate_parameter_choose_combobox.clear()
            self.calibrate_parameter_choose_combobox.set_model(parameters_model)
            parameter_cell = Gtk.CellRendererText()
            self.calibrate_parameter_choose_combobox.pack_start(parameter_cell, True)
            self.calibrate_parameter_choose_combobox.add_attribute(parameter_cell, 'text', 1)
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

    def get_parameters_model(self, channel_index):
        parameters_model = Gtk.ListStore(int, str)
        parameters_model.append([2020, '--请先选择校正参数--'])  # 默认参数
        channels = self._presenter.get_channels()
        chosen_channel = channels[channel_index]
        for parameter in chosen_channel.keys():
            try:
                parameters_model.append([parameter, '{}--{}'.format(parameter, self._parameter_dict[parameter])])
            except KeyError:
                dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                           buttons=Gtk.ButtonsType.OK, text="提示")
                dialog.format_secondary_text("不存在参数{}的属性名".format(parameter))
                dialog.run()
                dialog.destroy()
                parameters_model.append([parameter, '{}--None'.format(parameter)])
        return parameters_model

    def clear_calibrate_parameter_choose_combobox(self):
        empty_type_model = Gtk.ListStore()
        self.calibrate_parameter_choose_combobox.set_model(empty_type_model)

    def update_next_about(self, widget):
        self._is_update_all_dependencies_segment_choose = True
        self.clear_factors_scrolled_win()
        self.clear_calibrate_parameter_interval_combobox()
        self.update_calibrate_model()
        self.update_dependencies_list()
        self.update_dependencies_segment_choose()

    def update_calibrate_model(self):
        channel_index = self._presenter.load_channel_index()
        if channel_index != 2020:
            calibrate_parameter = self._presenter.load_chosen_calibrate_parameter()
            if calibrate_parameter == 2020:
                self.init_calibrate_model()
            else:
                calibrate_model = self._presenter.get_calibrate_model()
                self.model_display_label.set_text('校正类型{}'.format(calibrate_model))
        else:
            self.model_display_label.set_text('--请先选择校正参数--')

    def init_calibrate_model(self):
        self.model_display_label.set_text('--请先选择校正参数--')

    def update_dependencies_list(self):
        self.dependencies_list_scrolled_win.set_sensitive(True)
        channel_index = self._presenter.load_channel_index()
        tree_view = Gtk.TreeView()
        if channel_index != 2020:
            calibrate_parameter = self._presenter.load_chosen_calibrate_parameter()
            if calibrate_parameter != 2020:
                dependencies_list = self._presenter.get_dependencies_list()
                model = self.create_dependencies_list_model(dependencies_list)
                tree_view = self.create_dependencies_list_tree_view(model)
        tree_view.set_sensitive(False)
        self.dependencies_list_scrolled_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        child = self.dependencies_list_scrolled_win.get_child()
        if child:
            self.dependencies_list_scrolled_win.remove(child)
        self.dependencies_list_scrolled_win.add(tree_view)
        self.dependencies_list_scrolled_win.show_all()    # show_all() 才能显示其中内容

    def create_dependencies_list_model(self, depends_list):
        dependencies_list_model = Gtk.ListStore(int, str)
        for depend in depends_list:
            try:
                depend_name = self._parameter_dict[depend]
            except KeyError:
                depend_name = 'None'
            dependencies_list_model.append([depend, depend_name])
        return dependencies_list_model

    @staticmethod
    def create_dependencies_list_tree_view(model):
        tree_view = Gtk.TreeView()
        cell_renderer_text = Gtk.CellRendererText()
        tree_view_column_1 = Gtk.TreeViewColumn('依赖ID')
        tree_view_column_2 = Gtk.TreeViewColumn('依赖名')
        tree_view.append_column(tree_view_column_1)
        tree_view_column_1.pack_start(cell_renderer_text, True)
        tree_view_column_1.add_attribute(cell_renderer_text, 'text', 0)
        tree_view.append_column(tree_view_column_2)
        tree_view_column_2.pack_start(cell_renderer_text, True)
        tree_view_column_2.add_attribute(cell_renderer_text, 'text', 1)
        tree_view.set_model(model)
        return tree_view

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
        self.clear_calibrate_parameter_interval_combobox()
        self.clear_factors_scrolled_win()

        calibrate_parameter = self._presenter.load_chosen_calibrate_parameter()
        if calibrate_parameter == 2020:
            self.clear_dependencies_segment_choose()
            self.clear_calibrate_parameter_interval_combobox()
        else:
            child = self.dependencies_segment_choose_scrolled_win.get_child()
            if child:
                self.dependencies_segment_choose_scrolled_win.remove(child)
            depends_id = self._presenter.get_depends_id_in_main(calibrate_parameter)
            self._depends_id = depends_id
            viewport = Gtk.Viewport()
            main_box = Gtk.Box()
            main_box.set_orientation(Gtk.Orientation.VERTICAL)
            for value in depends_id:
                child_box = Gtk.Box()
                child_box.set_orientation(Gtk.Orientation.HORIZONTAL)
                label_id = Gtk.Label()
                label_id.set_text('{}'.format(value))
                child_box.pack_start(label_id, True, True, 0)
                child_combobox = Gtk.ComboBox()
                child_model = Gtk.ListStore()
                child_combobox.set_model(child_model)
                child_box.pack_start(child_combobox, True, True, 0)
                main_box.add(child_box)
            viewport.add(main_box)
            self.dependencies_segment_choose_scrolled_win.add(viewport)
            self.dependencies_segment_choose_scrolled_win.show_all()
            self.update_first_depend_segments()

    def update_first_depend_segments(self):
        calibrate_parameter = self._presenter.load_chosen_calibrate_parameter()

        viewport = self.dependencies_segment_choose_scrolled_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()
        first_box = boxes[0]
        first_box_children = first_box.get_children()
        first_combobox = first_box_children[1]
        first_combobox.clear()

        first_path = [[calibrate_parameter, None]]
        first_depend_id = self._depends_id[0]
        first_segments = self._presenter.get_depend_segments(first_path, first_depend_id)
        first_model = Gtk.ListStore(str, str)
        first_model.append(['[2020, 2020]', '--请先选择依赖区间--'])
        for segment in first_segments:
            lower_num = segment.lower
            upper_num = segment.upper
            first_model.append(['[{}, {}]'.format(lower_num, upper_num), '[{}, {}]'.format(lower_num, upper_num)])
        first_combobox.set_model(first_model)
        first_cell = Gtk.CellRendererText()
        first_combobox.pack_start(first_cell, True)
        first_combobox.add_attribute(first_cell, 'text', 1)
        if self._is_update_all_dependencies_segment_choose:
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

        focus_depend_id, focus_segment = self._presenter.load_focus_depend()
        default_segment = FloatInterval.closed(2020, 2020)
        focus_depend_id_index = self._depends_id.index(focus_depend_id)
        if focus_depend_id_index+1 < len(self._depends_id):
            next_parameter_id = self._depends_id[focus_depend_id_index+1]
            next_model = Gtk.ListStore(str, str)
            if focus_segment != default_segment:
                depend_path = self._presenter.load_depend_path(focus_depend_id)
                next_segments = self._presenter.get_depend_segments(depend_path, next_parameter_id)
                next_model.append(['[2020, 2020]', '--请先选择依赖区间--'])
                for segment in next_segments:
                    lower_num = segment.lower
                    upper_num = segment.upper
                    next_model.append(['[{}, {}]'.format(lower_num, upper_num), '[{}, {}]'.format(lower_num, upper_num)])
                next_box = boxes[focus_depend_id_index+1]
                next_label = next_box.get_children()[0]
                next_depend_id = int(next_label.get_text())
                next_combobox = next_box.get_children()[1]
                next_combobox.clear()
                next_combobox.set_model(next_model)
                current_cell = Gtk.CellRendererText()
                next_combobox.pack_start(current_cell, True)
                next_combobox.add_attribute(current_cell, 'text', 1)
                # next_combobox.set_active(0)   # 这里的set_active又会跳回去，陷入无限循环，有毒..
                if self._is_update_all_dependencies_segment_choose:
                    if next_depend_id == self._depends_id[-1]:
                        next_combobox.connect('changed', self.update_calibrate_parameter_interval_combobox)
                        self._is_update_all_dependencies_segment_choose = False
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

        last_segment = self._presenter.load_last_dependency_segment()
        default_segment = FloatInterval.closed(2020, 2020)
        if last_segment == default_segment:
            self.clear_calibrate_parameter_interval_combobox()
        else:
            try:
                parameter_segments = self._presenter.get_calibrate_parameter_segments()
            except ValueError:
                dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                           buttons=Gtk.ButtonsType.OK, text="提示")
                dialog.format_secondary_text("请先选择好各个依赖分段")
                dialog.run()
                dialog.destroy()
            else:
                self._parameter_segments = parameter_segments
                interval_model = Gtk.ListStore(int, str)
                interval_model.append([2020, '--请先选择校正参数区间--'])
                count = 0
                for segment in parameter_segments:
                    interval = segment[0]
                    lower_num = interval.lower
                    upper_num = interval.upper
                    interval_model.append([count, '[{}, {}]'.format(lower_num, upper_num)])
                    count += 1
                self.calibrate_parameter_interval_choose_combobox.set_model(interval_model)
                cell = Gtk.CellRendererText()
                self.calibrate_parameter_interval_choose_combobox.pack_start(cell, True)
                self.calibrate_parameter_interval_choose_combobox.add_attribute(cell, 'text', 1)
                self.calibrate_parameter_interval_choose_combobox.set_active(0)

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
        factors_text_view.set_sensitive(False)   # 滚动窗口的显示有较长延迟

        interval_index = self._presenter.load_chosen_parameter_interval_index()
        default_index = 2020
        if default_index == interval_index:
            self.clear_factors_scrolled_win()
        else:
            factors = self._parameter_segments[interval_index][1]
            factors_text_buffer.set_text('{}'.format(factors))
            factors_text_view.set_buffer(factors_text_buffer)
            self.factors_scrolled_win.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            child = self.factors_scrolled_win.get_child()
            if child:
                self.factors_scrolled_win.remove(child)
            self.factors_scrolled_win.add(factors_text_view)

        self.factors_scrolled_win.show_all()

    def init_all(self, filename):
        if not self._state:
            self.init_all_display_widget()
            self.init_display()
            self.init_edit_operate()
            self.update_channel_combobox()
            self.init_others()
            self._state = True
            title_bar = self.main_window.get_titlebar()
            title_bar.set_subtitle('{}'.format(filename))
        else:
            title_bar = self.main_window.get_titlebar()
            title_bar.set_title('校正文件编辑')
            title_bar.set_subtitle('{}'.format(filename))
            self.update_channel_combobox()

    def update_modified_factors_scrolled_win(self, new_factors):
        self._parameter_segments = self._presenter.get_calibrate_parameter_segments()
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

    def update_modified_interval(self, interval):
        model = self.calibrate_parameter_interval_choose_combobox.get_model()
        interval_activated = self.calibrate_parameter_interval_choose_combobox.get_active()
        _iter = model.get_iter_from_string('{}'.format(interval_activated))
        model.set_value(_iter, 1, '[{}, {}]'.format(interval.lower, interval.upper))

    def update_modified_depend_segment(self, dependency_id, lower_num, upper_num):
        viewport = self.dependencies_segment_choose_scrolled_win.get_child()
        main_box = viewport.get_child()
        boxes = main_box.get_children()
        for box in boxes:
            children = box.get_children()
            label = children[0]
            depend = int(label.get_text())
            if dependency_id == depend:
                combobox = children[1]
                segment_activated = combobox.get_active()
                model = combobox.get_model()
                _iter = model.get_iter_from_string('{}'.format(segment_activated))
                model.set_value(_iter, 0, '[{}, {}]'.format(lower_num, upper_num))
                model.set_value(_iter, 1, '[{}, {}]'.format(lower_num, upper_num))

    def update_file_name_state(self):
        title_bar = self.main_window.get_titlebar()
        title_bar.set_title('校正文件编辑*')

    def open_file(self, widget):
        dialog = Gtk.FileChooserDialog(title="文件选择", parent=self.main_window,
                                       action=Gtk.FileChooserAction.OPEN,
                                       buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            try:
                filename = dialog.get_filename()
                self._presenter.load_channels(filename)
                self.init_all(filename)
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

    def save(self, widget):
        title = self.main_window.get_title()
        has_already_modified = '校正文件编辑*'
        if title == has_already_modified:
            self._presenter.save()
            title_bar = self.main_window.get_titlebar()
            title_bar.set_title('校正文件编辑')
            dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("保存成功")
            dialog.run()
            dialog.destroy()
        else:
            dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("文件未做修改")
            dialog.run()
            dialog.destroy()

    def save_as_dialog(self):
        save_as_dialog = Gtk.FileChooserDialog("另存为",
                                               self.main_window, Gtk.FileChooserAction.SELECT_FOLDER,
                                               (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        extra_box = Gtk.Box()
        extra_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        file_name_entry = Gtk.Entry()
        file_name_entry.set_text('untitled')
        extra_box.pack_start(file_name_entry, True, True, 0)
        file_combobox = Gtk.ComboBox()
        file_type_model = Gtk.ListStore(str)
        file_type_model.append(['.json'])
        file_type_model.append(['.bin'])
        file_type_model.append(['.db'])
        file_combobox.set_model(file_type_model)
        cell = Gtk.CellRendererText()
        file_combobox.pack_start(cell, True)
        file_combobox.add_attribute(cell, 'text', 0)
        file_combobox.set_active(0)
        extra_box.pack_start(file_combobox, False, True, 0)

        save_as_dialog.set_extra_widget(extra_box)
        return save_as_dialog

    @staticmethod
    def get_whole_file_path(dialog):
        file_path = dialog.get_filename()

        extra_box = dialog.get_extra_widget()
        children = extra_box.get_children()
        file_name = children[0].get_text()
        combobox = children[1]
        model = combobox.get_model()
        _iter = combobox.get_active_iter()
        file_type = model.get_value(_iter, 0)

        file = file_name + file_type
        whole_file_path = os.path.join(file_path, file)
        return whole_file_path

    def save_as(self, widget):
        if not self._state:
            dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("当前无文件")
            dialog.run()
            dialog.destroy()
        else:
            self.show_save_as()

    def show_save_as(self):
        save_as_dialog = self.save_as_dialog()
        extra_box = save_as_dialog.get_extra_widget()
        extra_box.show_all()
        while True:
            response = save_as_dialog.run()
            if response == Gtk.ResponseType.OK:
                whole_file_path = self.get_whole_file_path(save_as_dialog)
                if not os.path.exists(whole_file_path):
                    self._presenter.save_as(whole_file_path)
                    dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                               buttons=Gtk.ButtonsType.OK, text="提示")
                    dialog.format_secondary_text("保存成功")
                    dialog.run()
                    dialog.destroy()
                    save_as_dialog.destroy()
                    break
                else:
                    dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                               buttons=Gtk.ButtonsType.OK, text="提示")
                    dialog.format_secondary_text("文件已存在")
                    dialog.run()
                    dialog.destroy()
                    continue
            elif response == Gtk.ResponseType.CANCEL:
                save_as_dialog.destroy()
                break

    def show_calibrate_tree_edit_ui(self, widget):
        try:
            if not self._senior_ui.state:
                self._senior_ui.parameter_dict = self._parameter_dict
                self._senior_ui.update_available_parameters()
                self._senior_ui.window.show_all()
                self._senior_ui.state = True
            else:
                self._senior_ui.hide_()
                self._senior_ui.state = False
        except Exception as ex:
            print(ex)
            dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择有效通道")
            dialog.run()
            dialog.destroy()

    def show_merge_file_ui(self, widget):
        if not self._merge_ui.state:
            self._merge_ui.update_merged_file_channel_choose()
            self._merge_ui.clear_all_other_file_widget()
            self._merge_ui.window.show_all()
            self._merge_ui.state = True
        else:
            self._merge_ui.hide_()
            self._merge_ui.state = False

    def show_dependencies_edit_ui(self, widget):
        try:
            if not self._dependencies_segment_ui.state:
                self._dependencies_segment_ui.update_dependencies_choose()
                self._dependencies_segment_ui.window.show_all()
                self._dependencies_segment_ui.state = True
            else:
                self._dependencies_segment_ui.window.hide()
                self._dependencies_segment_ui.state = False
        except Exception as ex:
            print(ex)
            dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择好依赖分段")
            dialog.run()
            dialog.destroy()

    def show_parameter_intervals_edit_ui(self, widget):
        try:
            if not self._parameter_interval_ui.state:
                interval = self._presenter.load_chosen_parameter_interval()
                self._parameter_interval_ui.update_current_interval_display(interval)
                self._parameter_interval_ui.window.show_all()
                self._parameter_interval_ui.state = True
            else:
                self._parameter_interval_ui.window.hide()
                self._parameter_interval_ui.state = False
        except Exception as ex:
            print(ex)
            dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择出系数区间")
            dialog.run()
            dialog.destroy()

    def show_factors_edit_ui(self, widget):
        try:
            if not self._factors_edit_ui.state:
                factors = self._presenter.load_current_factors()
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
            self._presenter.show_factors_curve()
            if not self.curve.is_show:
                self.curve.update_img()
                self.curve.window.show_all()
                self.curve.is_show = True
            else:
                self.curve.window.hide()
                self.curve.is_show = False
        except Exception as ex:
            print(ex)
            dialog = Gtk.MessageDialog(parent=self.main_window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="提示")
            dialog.format_secondary_text("请先选择出校正系数")
            dialog.run()
            dialog.destroy()
        # self._presenter.show_factors_curve()  # 先检查系数是否为空 AttributeError


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
        self.image.set_from_file(r"view\image\factors_curve.png")
        self.window.add(self.image)

    def set_window_header(self):
        header = Gtk.HeaderBar(title='校正系数曲线')
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


def main():
    main_window = MainUI()
    main_window.init_file_operate()
    Gtk.main()

# if __name__ == '__main__':
#     main()
#  设置控件比例(grid)、get_path
