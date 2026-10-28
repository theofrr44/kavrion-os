#!/usr/bin/env python3
"""KAVRION Écrans - profils simple/double écran via xrandr (gestion native Linux/X11).
Usage : kavrion-displays apply|status|set single|dual|auto
Ne bloque jamais la session : toute erreur est ignorée et le code de sortie reste 0 pour 'apply'."""
import json, os, re, subprocess, sys

CONF = os.path.expanduser("~/.config/kavrion/display.json")


def outputs():
    try:
        out = subprocess.run(["xrandr", "--query"], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return []
    return [m.group(1) for m in re.finditer(r"^(\S+) connected", out, re.M)]


def load():
    try:
        with open(CONF) as f:
            return json.load(f).get("profile", "auto")
    except Exception:
        return "auto"


def save(profile):
    os.makedirs(os.path.dirname(CONF), exist_ok=True)
    with open(CONF, "w") as f:
        json.dump({"profile": profile}, f)


def run(args):
    subprocess.run(["xrandr"] + args, timeout=15)


def apply():
    outs = outputs()
    profile = load()
    if not outs:
        return
    if profile == "single" or len(outs) < 2:
        args = ["--output", outs[0], "--auto", "--primary"]
        for o in outs[1:]:
            args += ["--output", o, "--auto", "--right-of", outs[0]] if profile == "dual" else ["--output", o, "--off"]
        run(args)
    else:  # double écran (dual ou auto avec 2+ écrans) : bureau sur le 1er, tableau de bord sur le 2e
        run(["--output", outs[0], "--auto", "--primary", "--output", outs[1], "--auto", "--right-of", outs[0]])


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    if cmd == "set" and len(argv) > 2 and argv[2] in ("single", "dual", "auto"):
        save(argv[2]); apply()
    elif cmd == "apply":
        try:
            apply()
        except Exception as e:
            print("kavrion-displays: ignoré (%s)" % e, file=sys.stderr)
    elif cmd == "status":
        print("profil: %s ; écrans connectés: %s" % (load(), ", ".join(outputs()) or "aucun détecté"))
    else:
        print(__doc__); return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
