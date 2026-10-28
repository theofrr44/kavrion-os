#!/usr/bin/env python3
"""KAVRION Moniteur - affiche des données réelles (CPU, RAM, disques, processus, réseau, températures)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk
from kavrion_sysinfo import Sampler, human, fmt_duration


def pct(v):
    return "n/d" if v is None else "%.0f %%" % v


class Monitor(Gtk.Window):
    def __init__(self):
        super().__init__(title="KAVRION Moniteur")
        self.set_default_size(760, 520)
        self.sampler = Sampler()
        nb = Gtk.Notebook()
        self.add(nb)
        self.summary = Gtk.Label(xalign=0, yalign=0, margin=16)
        self.summary.set_selectable(True)
        nb.append_page(self.summary, Gtk.Label(label="Résumé"))
        self.procs = Gtk.ListStore(int, str, str, str, str)
        tv = Gtk.TreeView(model=self.procs)
        for i, t in enumerate(("PID", "Processus", "État", "CPU", "Mémoire")):
            tv.append_column(Gtk.TreeViewColumn(t, Gtk.CellRendererText(), text=i))
        sw = Gtk.ScrolledWindow()
        sw.add(tv)
        nb.append_page(sw, Gtk.Label(label="Processus"))
        self.sampler.sample()
        self.refresh()
        GLib.timeout_add_seconds(2, self.refresh)

    def refresh(self):
        d = self.sampler.sample()
        m = d["mem"]
        lines = ["CPU : %s sur %s cœur(s)" % (pct(d["cpu_percent"]), d["cpu_count"])]
        if d["load"]:
            lines.append("Charge moyenne : %.2f  %.2f  %.2f" % d["load"])
        lines.append("Mémoire : %s utilisés / %s (%s disponibles)" % (human(m["used"]), human(m["total"]), human(m["available"])))
        if m["swap_total"]:
            lines.append("Swap : %s / %s" % (human(m["swap_used"]), human(m["swap_total"])))
        lines.append("Temps de fonctionnement : %s   |   Processus : %d" % (fmt_duration(d["uptime"]), d["process_count"]))
        lines.append("")
        lines.append("Stockage :")
        for x in d["disks"] or []:
            lines.append("  %s (%s) sur %s : %s / %s" % (x["device"], x["fs"], x["mount"], human(x["used"]), human(x["total"])))
        n = d["net"]
        lines.append("")
        if n["interfaces"]:
            r = "n/d" if n["rx_per_s"] is None else human(n["rx_per_s"], "o/s")
            t = "n/d" if n["tx_per_s"] is None else human(n["tx_per_s"], "o/s")
            lines.append("Réseau (%s) : ↓ %s  ↑ %s" % (", ".join(n["interfaces"]), r, t))
        else:
            lines.append("Réseau : aucune interface détectée")
        lines.append("")
        if d["temps"]:
            lines.append("Températures :")
            lines += ["  %s : %.0f °C" % (a, b) for a, b in d["temps"]]
        else:
            lines.append("Températures : aucun capteur accessible sur cette machine")
        self.summary.set_text("\n".join(lines))
        self.procs.clear()
        for p in d["processes"]:
            self.procs.append([p["pid"], p["name"], p["state"], pct(p["cpu"]), human(p["rss"])])
        return True


if __name__ == "__main__":
    w = Monitor()
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()
