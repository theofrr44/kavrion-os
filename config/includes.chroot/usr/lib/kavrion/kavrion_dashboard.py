#!/usr/bin/env python3
"""KAVRION Tableau de bord - plein écran sur le SECOND moniteur uniquement.
Si aucun second écran n'est présent, le programme se termine proprement (code 0)."""
import os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk
from kavrion_sysinfo import Sampler, human, fmt_duration

CSS = b"""
window { background: #0b1220; }
label { color: #d7e3f4; font-family: sans-serif; }
.big { font-size: 64px; font-weight: bold; color: #22d3ee; }
.date { font-size: 24px; color: #7aa2f7; }
.title { font-size: 18px; color: #7aa2f7; }
.val { font-size: 30px; }
progressbar trough { min-height: 14px; background: #162238; border-radius: 7px; }
progressbar progress { min-height: 14px; background: #22d3ee; border-radius: 7px; }
"""
SERVICES = ("NetworkManager", "lightdm", "cron", "systemd-timesyncd")


def svc_state(name):
    try:
        return subprocess.run(["systemctl", "is-active", name], capture_output=True, text=True, timeout=3).stdout.strip() or "inconnu"
    except Exception:
        return "inconnu"


class Dash(Gtk.Window):
    def __init__(self, geo):
        super().__init__(title="KAVRION Tableau de bord")
        self.move(geo.x, geo.y)
        self.set_default_size(geo.width, geo.height)
        self.set_decorated(False)
        self.fullscreen()
        self.sampler = Sampler()
        grid = Gtk.Grid(column_spacing=40, row_spacing=14, margin=48, column_homogeneous=True)
        self.add(grid)
        self.clock = Gtk.Label(xalign=0); self.clock.get_style_context().add_class("big")
        self.date = Gtk.Label(xalign=0); self.date.get_style_context().add_class("date")
        grid.attach(self.clock, 0, 0, 2, 1); grid.attach(self.date, 0, 1, 2, 1)
        self.bars, self.vals = {}, {}
        for row, key in enumerate(("CPU", "Mémoire", "Stockage"), start=2):
            t = Gtk.Label(label=key, xalign=0); t.get_style_context().add_class("title")
            v = Gtk.Label(xalign=1); v.get_style_context().add_class("val")
            b = Gtk.ProgressBar()
            grid.attach(t, 0, row * 2, 1, 1); grid.attach(v, 1, row * 2, 1, 1); grid.attach(b, 0, row * 2 + 1, 2, 1)
            self.bars[key], self.vals[key] = b, v
        self.info = Gtk.Label(xalign=0, yalign=0); self.info.set_line_wrap(True)
        grid.attach(self.info, 0, 12, 2, 1)
        self.sampler.sample()
        self.tick()
        GLib.timeout_add_seconds(2, self.tick)

    def tick(self):
        d = self.sampler.sample(top=8)
        self.clock.set_text(time.strftime("%H:%M:%S"))
        self.date.set_text(time.strftime("%A %d %B %Y"))
        c = d["cpu_percent"]
        self.bars["CPU"].set_fraction((c or 0) / 100); self.vals["CPU"].set_text("n/d" if c is None else "%.0f %%" % c)
        m = d["mem"]
        f = m["used"] / m["total"] if m["total"] else 0
        self.bars["Mémoire"].set_fraction(f); self.vals["Mémoire"].set_text("%s / %s" % (human(m["used"]), human(m["total"])))
        root = next((x for x in d["disks"] if x["mount"] == "/"), d["disks"][0] if d["disks"] else None)
        if root:
            self.bars["Stockage"].set_fraction(root["used"] / root["total"])
            self.vals["Stockage"].set_text("%s / %s" % (human(root["used"]), human(root["total"])))
        n = d["net"]
        net = ", ".join(n["interfaces"]) or "aucune interface"
        if n["rx_per_s"] is not None:
            net += "  ↓ %s ↑ %s" % (human(n["rx_per_s"], "o/s"), human(n["tx_per_s"], "o/s"))
        lines = ["Réseau : " + net, "Actif depuis : " + fmt_duration(d["uptime"]) + "   |   %d processus" % d["process_count"], ""]
        lines.append("Services : " + "   ".join("%s: %s" % (s, svc_state(s)) for s in SERVICES))
        lines.append("")
        lines.append("Top processus :")
        lines += ["  %-22s %6s  %s" % (p["name"][:22], "n/d" if p["cpu"] is None else "%.0f%%" % p["cpu"], human(p["rss"])) for p in d["processes"]]
        if d["temps"]:
            lines += ["", "Température max : %.0f °C" % max(t for _, t in d["temps"])]
        self.info.set_text("\n".join(lines))
        return True


def second_monitor_geometry():
    disp = Gdk.Display.get_default()
    if disp is None or disp.get_n_monitors() < 2:
        return None
    primary = disp.get_primary_monitor()
    for i in range(disp.get_n_monitors()):
        mon = disp.get_monitor(i)
        if mon != primary:
            return mon.get_geometry()
    return None


if __name__ == "__main__":
    geo = second_monitor_geometry()
    if geo is None:
        sys.exit(0)  # pas de second écran : on ne fait rien, la session continue normalement
    prov = Gtk.CssProvider(); prov.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    w = Dash(geo)
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()
