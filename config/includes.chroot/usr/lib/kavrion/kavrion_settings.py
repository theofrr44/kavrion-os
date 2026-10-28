#!/usr/bin/env python3
"""KAVRION Paramètres - thème, fond d'écran, mode léger, écrans, applications au démarrage.
Les réglages sont persistants : xfconf (bureau) et ~/.config/kavrion, ~/.config/autostart."""
import glob, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import kavrion_displays as kd

AUTOSTART_USER = os.path.expanduser("~/.config/autostart")


def xf(channel, prop, *vals, typ=None):
    cmd = ["xfconf-query", "-c", channel, "-p", prop]
    if vals:
        cmd += ["-n", "-t", typ, "-s", vals[0]] if typ else ["-s", vals[0]]
    return subprocess.run(cmd, capture_output=True, text=True)


def autostart_entries():
    items = {}
    for path in sorted(glob.glob("/etc/xdg/autostart/*.desktop")) + sorted(glob.glob(AUTOSTART_USER + "/*.desktop")):
        name = os.path.basename(path)
        label, hidden = name, False
        for line in open(path, errors="replace"):
            if line.startswith("Name=") and label == name:
                label = line.split("=", 1)[1].strip()
            if line.strip() == "Hidden=true":
                hidden = True
        items[name] = (label, not hidden)
    return items


def set_autostart(name, enabled):
    os.makedirs(AUTOSTART_USER, exist_ok=True)
    target = os.path.join(AUTOSTART_USER, name)
    if enabled and os.path.exists(target) and "Hidden=true" in open(target).read():
        os.remove(target)
    elif not enabled:
        with open(target, "w") as f:
            f.write("[Desktop Entry]\nType=Application\nHidden=true\n")


class Settings(Gtk.Window):
    def __init__(self):
        super().__init__(title="KAVRION Paramètres")
        self.set_default_size(520, 520)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=18)
        self.add(box)

        box.pack_start(Gtk.Label(label="<b>Apparence</b>", use_markup=True, xalign=0), False, False, 0)
        self.dark = Gtk.Switch(active=(xf("xsettings", "/Net/ThemeName").stdout.strip() or "Arc-Dark").endswith("Dark"))
        self.dark.connect("notify::active", self.on_theme)
        box.pack_start(self.row("Thème sombre", self.dark), False, False, 0)
        pick = Gtk.FileChooserButton(title="Choisir un fond d'écran", action=Gtk.FileChooserAction.OPEN)
        pick.set_current_folder("/usr/share/kavrion/wallpapers")
        pick.connect("file-set", self.on_wallpaper)
        box.pack_start(self.row("Fond d'écran", pick), False, False, 0)

        box.pack_start(Gtk.Label(label="<b>Performances</b>", use_markup=True, xalign=0), False, False, 0)
        comp = xf("xfwm4", "/general/use_compositing").stdout.strip()
        self.light = Gtk.Switch(active=(comp == "false"))
        self.light.connect("notify::active", self.on_light)
        box.pack_start(self.row("Mode léger (sans effets ni animations)", self.light), False, False, 0)

        box.pack_start(Gtk.Label(label="<b>Écrans</b>", use_markup=True, xalign=0), False, False, 0)
        self.prof = Gtk.ComboBoxText()
        for key, lab in (("auto", "Automatique"), ("single", "Simple écran"), ("dual", "Double écran + tableau de bord")):
            self.prof.append(key, lab)
        self.prof.set_active_id(kd.load())
        self.prof.connect("changed", lambda c: kd.save(c.get_active_id()) or kd.apply())
        box.pack_start(self.row("Profil d'affichage", self.prof), False, False, 0)

        box.pack_start(Gtk.Label(label="<b>Applications au démarrage</b>", use_markup=True, xalign=0), False, False, 0)
        sw = Gtk.ScrolledWindow(); sw.set_vexpand(True)
        lb = Gtk.ListBox(); sw.add(lb)
        for name, (label, on) in autostart_entries().items():
            s = Gtk.Switch(active=on)
            s.connect("notify::active", lambda w, _p, n=name: set_autostart(n, w.get_active()))
            lb.add(self.row(label, s))
        box.pack_start(sw, True, True, 0)

    @staticmethod
    def row(text, widget):
        b = Gtk.Box(spacing=12)
        b.pack_start(Gtk.Label(label=text, xalign=0), True, True, 0)
        b.pack_end(widget, False, False, 0)
        return b

    def on_theme(self, sw, _p):
        dark = sw.get_active()
        xf("xsettings", "/Net/ThemeName", "Arc-Dark" if dark else "Arc", typ="string")
        xf("xfwm4", "/general/theme", "Arc-Dark" if dark else "Arc", typ="string")

    def on_wallpaper(self, btn):
        path = btn.get_filename()
        props = subprocess.run(["xfconf-query", "-c", "xfce4-desktop", "-l"], capture_output=True, text=True).stdout.split()
        for p in props:
            if p.endswith("/last-image"):
                xf("xfce4-desktop", p, path, typ="string")

    def on_light(self, sw, _p):
        on = sw.get_active()
        xf("xfwm4", "/general/use_compositing", "false" if on else "true", typ="bool")


if __name__ == "__main__":
    w = Settings()
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()
