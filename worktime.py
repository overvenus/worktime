#!/usr/bin/env python3

import sys
import time

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
                    ('Conf', self.app.conf_win.on_show),
                    ('Quit', self.app.on_quit)]
        for text, callback in itemlist:
            item = Gtk.MenuItem(text)
            item.connect('activate', callback, '')
            menu.append(item)
        menu.show_all()
        return menu


class ConfigWin(Gtk.Window):
    def __init__(self, root):
        super().__init__()
        self.app = root
        self.set_title(self.app.name + ' Config Window')

    def on_show(self, w, data):
        self.show()


class MainWin(Gtk.Window):
    def __init__(self, root):
        super().__init__()
        self.app = root

        self.set_title(self.app.name)
        self.set_size_request(300, 200)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_resizable(False)

        # View
        self.box = Gtk.Box(spacing=6)
        self.add(self.box)

        self.timer_label = Gtk.Label(justify=Gtk.Justification.CENTER,
                                     hexpand=True,
                                     vexpand=True,
                                     halign=Gtk.Align.FILL,
                                     valign=Gtk.Align.FILL)
        self.box.pack_start(self.timer_label, True, True, 0)

        # Event
        self.connect('delete-event', self.on_hide)
        self.app.connect_update(self.on_update)

    def on_update(self, now):
        ctime = time.ctime(now)
        markup = '<span font="60">{}</span>'.format(ctime.split(' ')[-2])
        self.timer_label.set_markup(markup)

    def on_show(self, w, data):
        return self.show_all()

    def on_hide(self, w, data):
        return self.hide_on_delete()


class Worktime(Gtk.Application):
    def __init__(self):
        super().__init__()
        self.name = 'Worktime'
        self.getoutput = lambda x: Popen(x, stdout=PIPE).communicate()[0]
        self.update_func_list = []
        self.main_win = MainWin(self)
        self.conf_win = ConfigWin(self)
        self.indicator = Indicator(self)

        # Update event
        GLib.timeout_add(1000, self.on_timeout)
        self.connect_update(self.on_update)

    def connect_update(self, update_func):
        self.update_func_list.append(update_func)

    def get_viewport_position(self):
        # get the position of the current workspace
        return list(int(i.strip(b',')) for i in self.getoutput(('xprop', '-root',
            '-notype', '_NET_DESKTOP_VIEWPORT', )).split()[-2:])

    def on_update(self, now):
        print(self.get_viewport_position())

    def on_timeout(self):
        now = time.time()
        for func in self.update_func_list:
            func(now)
        return True

    def run(self):
        Gtk.main()

    def on_quit(self, w, data):
        Gtk.main_quit()


if __name__ == '__main__':
    app = Worktime()
    app.run()
