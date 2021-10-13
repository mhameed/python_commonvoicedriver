import sys
import threading
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DictationCorrection(Gtk.Window):
    def __init__(self, on_abort_callback, on_play_callback, on_submit_callback):
        super(DictationCorrection, self).__init__(title="Dictation correction")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        hbox = Gtk.Box(spacing=6)
        self.add(vbox)

        label1 = Gtk.Label(label="Please enter the correct text:")
        label1.set_selectable(True)
        vbox.add(label1)
        self.entry = Gtk.Entry()
        vbox.add(self.entry)

        play = Gtk.Button(label="play audio")
        play.connect("clicked", on_play_callback)
        hbox.add(play)

        submit = Gtk.Button(label="submit correction")
        submit.connect("clicked", on_submit_callback)
        hbox.add(submit)

        abort = Gtk.Button(label="abort")
        abort.connect("clicked", on_abort_callback)
        hbox.add(abort)
        vbox.add(hbox)

    def on_abort(self, widget):
        print("aborting ...")
        self.set_visible(False)
        print("quitted.")

    def on_play_audio(self, widget):
        print("playing audio ...")

    def on_submit_correction(self, widget):
        print("hello world.")
        print(self.entry.get_text())

