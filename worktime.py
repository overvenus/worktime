#!/usr/bin/env python3

import os
import time
import signal
import yaml
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib, GdkPixbuf
from gi.repository import AppIndicator3 as appindicator

# custom build module
import where_


class Indicator:

    def __init__(self, root):
        self.app = root
        self.ind = appindicator.Indicator.new(
            self.app.name,
            self.app.conf_win.icons['stop'],
            appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.menu = self.make_menu()

        self.ind.set_menu(self.menu)

    def make_menu(self):
        menu = Gtk.Menu()
        itemlist = [('Show', self.app.main_win.on_show),
                    ('Hide', self.app.main_win.on_hide),
                    # ('Conf', self.app.conf_win.on_show),
                    ('Quit', self.app.on_quit)]
        for text, callback in itemlist:
            item = Gtk.MenuItem(text)
            item.connect('activate', callback, '')
            menu.append(item)
        menu.show_all()
        return menu

    def on_start(self, widget, data=None):
        self.ind.set_icon(app.conf_win.icons['start'])
        return True

    def on_stop(self, widget, data=None):
        self.ind.set_icon(app.conf_win.icons['stop'])
        return True


class ConfigWin(Gtk.Window):

    def __init__(self, root, config_dir, config_name):
        super().__init__()
        self.app = root
        self.set_title(self.app.name + ' Config')
        self.config_dir = config_dir
        self.config_name = config_name
        self.config = None
        with open(os.path.join(config_dir, config_name)) as f:
            self.config = yaml.load(f.read())

        for k in self.config['icons']:
            self.config['icons'][k] = os.path.abspath(
                os.path.join(self.config_dir, self.config['icons'][k]))

    def on_show(self, widget, data=None):
        self.show_all()

    @property
    def duration(self):
        return self.config['duration']

    @property
    def space(self):
        return self.config['space']

    @property
    def icons(self):
        return self.config['icons']


class MainWin(Gtk.Window):

    __SPACE_1 = (False, False)
    __SPACE_2 = (True, False)
    __SPACE_3 = (False, True)
    __SPACE_4 = (True, True)
    SPACE = [__SPACE_1, __SPACE_2, __SPACE_3, __SPACE_4]

    TIME_FORMATER = '<span font="50">{:02d}:{:02d}</span> <span font="40">{:02d}</span>'
    STATUS_FOTMATER = '<span size="x-large">{}</span>'

    def __init__(self, root):
        super().__init__()
        self.app = root

        self.set_default_icon(GdkPixbuf.Pixbuf.new_from_file(
            self.app.conf_win.icons['window']))
        self.set_title(self.app.name)
        self.set_size_request(300, 200)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_resizable(False)

        # Data
        self.total_time = 0
        self.is_started = False
        self.is_showed = False

        # View
        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.timer_label = Gtk.Label(justify=Gtk.Justification.CENTER,
                                     hexpand=True,
                                     vexpand=True,
                                     halign=Gtk.Align.FILL,
                                     valign=Gtk.Align.FILL)
        self.grid.attach(self.timer_label, 0, 0, 2, 1)

        self.status_label = Gtk.Label(justify=Gtk.Justification.CENTER,
                                      hexpand=True,
                                      vexpand=True,
                                      halign=Gtk.Align.FILL,
                                      valign=Gtk.Align.FILL)
        self.grid.attach(self.status_label, 0, 1, 2, 1)

        self.start_button = Gtk.Button(label='Start')
        self.grid.attach_next_to(
            self.start_button, self.status_label, Gtk.PositionType.BOTTOM, 1, 1)

        self.stop_button = Gtk.Button(label='Stop')
        self.grid.attach_next_to(
            self.stop_button, self.start_button, Gtk.PositionType.RIGHT, 1, 1)

        # Event
        self.connect('delete-event', self.on_hide)
        self.app.connect_update(self.on_update)
        self.start_button.connect('clicked', self.on_start_clicked)
        self.stop_button.connect('clicked', self.on_stop_clicked)

        # Init view
        self.on_update_clock(None, data=self.total_time)
        self.status_label.set_markup(self.STATUS_FOTMATER.format('Stop'))
        self.on_show(None)

    @staticmethod
    def _get_viewport_position():
        # get the position of the current workspace
        return where_.cardinal()

    def on_start_clicked(self, widget, data=None):
        if not self.is_started:
            self.is_started = True
            self.total_time = 0
            self.status_label.set_markup(
                self.STATUS_FOTMATER.format('Recording'))
            self.app.indicator.on_start(widget, data)
        return True

    def on_stop_clicked(self, widget, data=None):
        if self.is_started:
            self.is_started = False
            self.status_label.set_markup(self.STATUS_FOTMATER.format('Stop'))
            self.app.indicator.on_stop(widget, data)
        return True

    def get_space(self):
        pos = self._get_viewport_position()
        return pos[0] > 0, pos[1] > 0

    @staticmethod
    def format_time(total):
        hour = int(total / (60 * 60))
        total -= (hour * (60 * 60))
        mint = int(total / 60)
        total -= (mint * 60)
        sec = int(total)
        return hour, mint, sec

    def on_update_clock(self, widget, data=None):
        t = self.format_time(data)
        markup = self.TIME_FORMATER.format(t[0], t[1], t[2])
        self.timer_label.set_markup(markup)
        return True

    def on_update(self, now, duration):
        space = self.app.conf_win.space
        if self.get_space() not in [MainWin.SPACE[i - 1] for i in space]:
            return

        if self.is_started:
            duration /= 1000
            self.total_time += duration

        if not self.is_showed:
            return

        self.on_update_clock(None, data=self.total_time)

    def on_show(self, widget, data=None):
        self.is_showed = True
        self.on_update_clock(None, data=self.total_time)
        return self.show_all()

    def on_hide(self, widget, data=None):
        self.is_showed = False
        return self.hide_on_delete()


class Worktime(Gtk.Application):

    def __init__(self):
        super().__init__()
        self.name = 'Worktime'
        self.update_func_list = []

        # create config dir
        config_dir = os.environ['HOME'] + '/.config/worktime'
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        config_name = 'config.yaml'

        # View
        self.conf_win = ConfigWin(self, config_dir, config_name)
        self.main_win = MainWin(self)
        self.indicator = Indicator(self)

        # Event
        GLib.timeout_add(self.conf_win.duration, self.on_timeout)
        GLib.unix_signal_add(GLib.PRIORITY_HIGH,
                             signal.SIGINT, self.on_quit, None)

    def connect_update(self, update_func):
        self.update_func_list.append(update_func)

    def on_timeout(self):
        now = time.time()
        duration = self.conf_win.duration
        for func in self.update_func_list:
            func(now, duration)
        return True

    def run(self):
        Gtk.main()

    def on_quit(self, widget, data=None):
        Gtk.main_quit()


if __name__ == '__main__':
    app = Worktime()
    app.run()
