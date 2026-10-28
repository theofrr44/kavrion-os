"""KAVRION OS - collecte de métriques système RÉELLES (/proc et /sys).
Aucune donnée simulée : si une donnée est indisponible, la valeur est None ou la liste est vide."""
import glob
import os
import time

CLK_TCK = os.sysconf("SC_CLK_TCK")
PAGE = os.sysconf("SC_PAGE_SIZE")
REAL_FS = {"ext2", "ext3", "ext4", "btrfs", "xfs", "vfat", "ntfs", "ntfs3", "f2fs", "exfat", "fuseblk"}


def _read(path):
    try:
        with open(path, "r", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def parse_cpu_times(text):
    """Retourne (total, idle) depuis la ligne agrégée 'cpu' de /proc/stat."""
    for line in text.splitlines():
        if line.startswith("cpu "):
            v = [int(x) for x in line.split()[1:]]
            idle = v[3] + (v[4] if len(v) > 4 else 0)
            return sum(v[:8]), idle
    raise ValueError("ligne cpu introuvable")


def parse_meminfo(text):
    d = {}
    for line in text.splitlines():
        k, _, rest = line.partition(":")
        if rest:
            d[k] = int(rest.split()[0]) * 1024
    total = d.get("MemTotal", 0)
    avail = d.get("MemAvailable", d.get("MemFree", 0))
    st, sf = d.get("SwapTotal", 0), d.get("SwapFree", 0)
    return {"total": total, "available": avail, "used": total - avail,
            "swap_total": st, "swap_used": st - sf}


def parse_net_dev(text):
    out = {}
    for line in text.splitlines()[2:]:
        name, _, rest = line.partition(":")
        name = name.strip()
        f = rest.split()
        if name and name != "lo" and len(f) >= 9:
            out[name] = (int(f[0]), int(f[8]))
    return out


def parse_proc_stat(text):
    """Retourne (nom, état, ticks_cpu, pages_rss) depuis /proc/PID/stat."""
    i, j = text.index("("), text.rindex(")")
    f = text[j + 2:].split()
    return text[i + 1:j], f[0], int(f[11]) + int(f[12]), int(f[21])


def disks():
    res, seen = [], set()
    for line in (_read("/proc/mounts") or "").splitlines():
        dev, mnt, fs = line.split()[:3]
        if fs in REAL_FS and dev not in seen:
            seen.add(dev)
            try:
                s = os.statvfs(mnt)
            except OSError:
                continue
            total, free = s.f_blocks * s.f_frsize, s.f_bavail * s.f_frsize
            if total:
                res.append({"device": dev, "mount": mnt, "fs": fs, "total": total, "used": total - free})
    return res


def temperatures():
    """Liste de (étiquette, °C) ; vide si aucun capteur n'est accessible."""
    out = []
    for hw in sorted(glob.glob("/sys/class/hwmon/hwmon*")):
        chip = (_read(hw + "/name") or "capteur").strip()
        for t in sorted(glob.glob(hw + "/temp*_input")):
            v = _read(t)
            if v and v.strip().lstrip("-").isdigit():
                lab = _read(t.replace("_input", "_label"))
                out.append(("%s %s" % (chip, (lab or os.path.basename(t)).strip()), int(v) / 1000.0))
    if not out:
        for z in sorted(glob.glob("/sys/class/thermal/thermal_zone*")):
            v, ty = _read(z + "/temp"), _read(z + "/type")
            if v and v.strip().lstrip("-").isdigit():
                out.append(((ty or "zone").strip(), int(v) / 1000.0))
    return out


def uptime_seconds():
    t = _read("/proc/uptime")
    return float(t.split()[0]) if t else None


def loadavg():
    t = _read("/proc/loadavg")
    return tuple(float(x) for x in t.split()[:3]) if t else None


def human(n, suffix="o"):
    n = float(n)
    for unit in ("", "K", "M", "G", "T"):
        if abs(n) < 1024 or unit == "T":
            return ("%d %s%s" % (n, unit, suffix)) if unit == "" else ("%.1f %s%s" % (n, unit, suffix))
        n /= 1024


def fmt_duration(sec):
    if sec is None:
        return "n/d"
    sec = int(sec)
    d, r = divmod(sec, 86400)
    h, r = divmod(r, 3600)
    return ("%dj " % d if d else "") + "%dh %02dmin" % (h, r // 60)


class Sampler:
    """Appeler sample() périodiquement ; les taux se calculent par différence entre deux appels."""

    def __init__(self):
        self._cpu = self._net = self._t = None
        self._procs = {}

    def sample(self, top=25):
        now = time.monotonic()
        dt = (now - self._t) if self._t else None
        self._t = now
        data = {}

        total, idle = parse_cpu_times(_read("/proc/stat"))
        if self._cpu and total > self._cpu[0]:
            data["cpu_percent"] = 100.0 * (1 - (idle - self._cpu[1]) / (total - self._cpu[0]))
        else:
            data["cpu_percent"] = None
        self._cpu = (total, idle)
        data["cpu_count"] = os.cpu_count()
        data["load"] = loadavg()
        data["mem"] = parse_meminfo(_read("/proc/meminfo"))

        net = parse_net_dev(_read("/proc/net/dev") or "")
        rx = tx = None
        if self._net is not None and dt:
            rx = max(0, sum(v[0] for v in net.values()) - sum(v[0] for v in self._net.values())) / dt
            tx = max(0, sum(v[1] for v in net.values()) - sum(v[1] for v in self._net.values())) / dt
        self._net = net
        data["net"] = {"interfaces": sorted(net), "rx_per_s": rx, "tx_per_s": tx}

        procs, cur = [], {}
        for p in glob.glob("/proc/[0-9]*"):
            try:
                name, state, ticks, rss = parse_proc_stat(_read(p + "/stat") or "")
            except (ValueError, IndexError):
                continue
            pid = int(os.path.basename(p))
            cur[pid] = ticks
            pct = None
            if pid in self._procs and dt:
                pct = 100.0 * (ticks - self._procs[pid]) / CLK_TCK / dt
            procs.append({"pid": pid, "name": name, "state": state, "cpu": pct, "rss": rss * PAGE})
        self._procs = cur
        procs.sort(key=lambda x: (x["cpu"] or 0, x["rss"]), reverse=True)
        data["processes"] = procs[:top]
        data["process_count"] = len(procs)
        data["disks"] = disks()
        data["temps"] = temperatures()
        data["uptime"] = uptime_seconds()
        return data
