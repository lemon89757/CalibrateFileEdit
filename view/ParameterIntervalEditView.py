import gi
import os
import intervals
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from presenter.ParameterIntervalEditPresenter import ParameterIntervalEditPresenter


class ParameterIntervalEditView:
    def __init__(self):
        self._presenter = ParameterIntervalEditPresenter()
        self._presenter.view = self
        self.state = False
        self.entries = []
        self.current_lower_label = None
        self.current_upper_label = None

        self.window = Gtk.Window()
        self.window.set_border_width(10)
        self.window.set_default_size(200, 100)
        self.ui = None
        self.get_all_widget()
        self.set_window_header()
        self.window.add(self.ui)

    @property
    def presenter(self):
        return self._presenter

    @presenter.setter
    def presenter(self, value):
        self._presenter = value

    def get_all_widget(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(os.path.dirname(__file__), 'glade/EditCalibrateParameterIntervalUI.glade'))
        self.ui = builder.get_object('edit_calibrate_parameter_interval_grid')
        self.current_lower_label = builder.get_object('current_interval_lower_num_label')
        self.current_upper_label = builder.get_object('current_interval_upper_num_label')
        lower_num_entry = builder.get_object('interval_lower_num_entry')
        upper_num_entry = builder.get_object('interval_upper_num_entry')
        self.entries = [lower_num_entry, upper_num_entry]
        confirm_button = builder.get_object('confirm_button')
        confirm_button.connect('clicked', self.confirm)
        cancel_button = builder.get_object('cancel_button')
        cancel_button.connect('clicked', self.cancel)

    def update_current_interval_display(self, current_interval):
        lower_num = current_interval.lower
        upper_num = current_interval.upper
        self.current_lower_label.set_text('{}'.format(lower_num))
        self.current_upper_label.set_text('{}'.format(upper_num))

    def set_window_header(self):
        header = Gtk.HeaderBar(title='??????????????????')
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

    def confirm(self, widget):
        try:
            self._presenter.modify_parameter_interval()
            self._presenter.update_modified_parameter_interval()
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="??????")
            dialog.format_secondary_text("????????????")
            dialog.run()
            dialog.destroy()
            self.hide_()
        except ValueError:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="??????")
            dialog.format_secondary_text("????????????????????????"
                                         "???????????????????????????")
            dialog.run()
            dialog.destroy()
        except intervals.exc.RangeBoundsException:
            dialog = Gtk.MessageDialog(parent=self.window, flags=0, message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.OK, text="??????")
            dialog.format_secondary_text("????????????????????????"
                                         "??????????????????")
            dialog.run()
            dialog.destroy()

    def cancel(self, widget):
        for entry in self.entries:
            entry.delete_text(0, -1)
        self.state = False
        self.window.hide()

