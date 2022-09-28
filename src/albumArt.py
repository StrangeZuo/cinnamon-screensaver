#!/usr/bin/python3

from gi.repository import Gio, Gtk

from util import trackers, settings
from baseWindow import BaseWindow
from floating import Floating
from widgets.framedImage import FramedImage

import singletons
import status

class AlbumArt(Floating, BaseWindow):
    """
    AlbumArt

    It is a child of the Stage's GtkOverlay, and its placement is
    controlled by the overlay's child positioning function.

    When not Awake, it positions itself around all monitors
    using a timer which randomizes its halign and valign properties
    as well as its current monitor.
    """
    def __init__(self, away_message=None, initial_monitor=0):
        super(AlbumArt, self).__init__(initial_monitor)
        self.get_style_context().add_class("albumart")
        self.set_halign(Gtk.Align.END)

        if not settings.get_show_albumart():
            return

        self.watcher = singletons.MediaPlayerWatcher
        self.player = self.watcher.get_best_player()

        self.current_url = None

        self.image = FramedImage(status.screen.get_low_res_mode(), scale_up=True)
        self.image.show()
        self.image.set_opacity(0.0)
        self.add(self.image)

        trackers.con_tracker_get().connect(self.image,
                                           "surface-changed",
                                           self.on_surface_changed)

        if self.player != None:
            trackers.con_tracker_get().connect(self.player,
                                               "metadata-changed",
                                               self.on_metadata_changed)
            self.on_metadata_changed(self.player)

    def on_surface_changed(self, image, surface):
        if surface != None:
            self.image.set_opacity(1.0)
        else:
            self.image.set_opacity(0.0)

    def on_metadata_changed(self, player):
        self.update_image()

    def update_image(self):
        url = self.player.get_albumart_url()

        if self.player.get_identity() == "spotify":
            url = url.replace("open.spotify.com", "i.scdn.co");

        if url == self.current_url:
            return

        self.current_url = url

        if url == "":
            self.image.clear_image()

        f = Gio.File.new_for_uri(url)

        if f.get_uri_scheme() == "file":
            self.image.set_from_path(f.get_path())
        elif f.get_uri_scheme() == "http":
            self.image.set_from_file(f)
