#!/usr/bin/env python3

import os
import sys
import time
import signal
import json

from subprocess import Popen, PIPE
from gi.repository import Gtk, GLib
from gi.repository import AppIndicator3 as appindicator


class Indicator:

    def __init__(self, root):
        self.app = root
        self.ind = appindicator.Indicator.new(
            self.app.name,
            'indicator-messages',
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


class ConfigWin(Gtk.Window):

    def __init__(self, root, conf=None):
        super().__init__()
        self.app = root
        self.set_title(self.app.name + ' Config')

    def on_show(self, widget, date=None):
        self.show_all()


class MainWin(Gtk.Window):

    __SPACE_1 = (False, False)
    __SPACE_2 = (True, False)
    __SPACE_3 = (False, True)
    __SPACE_4 = (True, True)
    SPACE = [__SPACE_1, __SPACE_2, __SPACE_3, __SPACE_4]

    def __init__(self, root):
        super().__init__()
        self.app = root

        self.set_title(self.app.name)
        self.set_size_request(300, 200)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_resizable(False)

        # Data
        self.total_time = 0
        self.is_started = False
        self.is_showed = False
        self.getoutput = lambda x: Popen(x, stdout=PIPE).communicate()[0]

        # View
        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.timer_label = Gtk.Label(justify=Gtk.Justification.CENTER,
                                     hexpand=True,
                                     vexpand=True,
                                     halign=Gtk.Align.FILL,
                                     valign=Gtk.Align.FILL)
        self.grid.attach(self.timer_label, 0, 0, 2, 1)

        self.start_button = Gtk.Button(label='Start')
        self.grid.attach_next_to(
            self.start_button, self.timer_label, Gtk.PositionType.BOTTOM, 1, 1)

        self.stop_button = Gtk.Button(label='Stop')
        self.grid.attach_next_to(
            self.stop_button, self.start_button, Gtk.PositionType.RIGHT, 1, 1)

        # Event
        self.connect('delete-event', self.on_hide)
        self.app.connect_update(self.on_update)
        self.start_button.connect('clicked', self.on_start_clicked)
        self.stop_button.connect('clicked', self.on_stop_clicked)

        # Init view
        self.on_update_clock(None, date=self.total_time)

    def _get_viewport_position(self):
        # get the position of the current workspace
        return list(int(i.strip(b',')) for i in self.getoutput(('xprop', '-root',
                                                                '-notype', '_NET_DESKTOP_VIEWPORT', )).split()[-2:])

    def on_start_clicked(self, widget, date=None):
        self.is_started = True
        return True

    def on_stop_clicked(self, widget, date=None):
        self.is_started = False
        self.total_time = 0
        self.on_update_clock(None, date=self.total_time)
        return True

    def get_space(self):
        pos = self._get_viewport_position()
        return (pos[0] > 0, pos[1] > 0)

    def format_time(self, total):
        hour = int(total / (60 * 60))
        total -= (hour * (60 * 60))
        mint = int(total / 60)
        total -= (mint * 60)
        sec = int(total)
        return (hour, mint, sec)

    def on_update_clock(self, widget, date=None):
        t = self.format_time(date)
        markup = '<span font="60">' + \
            str(t[0]) + ':' + str(t[1]) + ':' + str(t[2]) + '</span>'
        self.timer_label.set_markup(markup)
        return True

    def on_update(self, now, duration):
        if not self.get_space() == MainWin.SPACE[3]:
            return

        if self.is_started:
            duration = duration / 1000
            self.total_time += duration

        if not self.is_showed:
            return

        self.on_update_clock(None, date=self.total_time)

    def on_show(self, widget, date=None):
        self.is_showed = True
        return self.show_all()

    def on_hide(self, widget, date=None):
        self.is_showed = False
        return self.hide_on_delete()


class Worktime(Gtk.Application):

    def __init__(self):
        super().__init__()
        self.name = 'Worktime'
        self.update_func_list = []
        self.session = Session()

        # create config dir
        config_dir = os.environ['HOME'] + '/.config/worktime'
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # dump default config.json
        config_name = 'config.json'
        filename = os.path.join(config_dir, config_name)

        # Data
        self.duration = 1000  # 1s = 1000ms

        # View
        self.main_win = MainWin(self)
        # self.conf_win = ConfigWin(self, config)
        self.indicator = Indicator(self)

        # Event
        GLib.timeout_add(self.duration, self.on_timeout)
        GLib.unix_signal_add(GLib.PRIORITY_HIGH,
                             signal.SIGINT, self.on_quit, None)

    def connect_update(self, update_func):
        self.update_func_list.append(update_func)

    def on_timeout(self):
        now = time.time()
        for func in self.update_func_list:
            func(now, self.duration)
        return True

    def run(self):
        Gtk.main()

    def on_quit(self, widget, data=None):
        Gtk.main_quit()


if __name__ == '__main__':
    app = Worktime()
    app.run()
