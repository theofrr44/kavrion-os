#!/usr/bin/env python3
"""Génère les PNG de marque (logo, icône, écran d'accueil) sans dépendance externe. Dessin original."""
import struct, sys, zlib

def png(path, w, h, px):
    raw = b"".join(b"\x00" + b"".join(bytes(px(x, y)) for x in range(w)) for y in range(h))
    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))

def in_poly(x, y, pts):
    ins = False
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins

def logo(size):
    s = size / 256.0
    K = [[(70, 56), (104, 56), (104, 200), (70, 200)],
         [(104, 132), (178, 56), (222, 56), (140, 140), (104, 150)],
         [(122, 138), (222, 200), (178, 200), (104, 150)]]
    K = [[(x * s, y * s) for x, y in poly] for poly in K]
    r = 48 * s
    def px(x, y):
        cx, cy = min(max(x, r), size - 1 - r), min(max(y, r), size - 1 - r)
        if (x - cx) ** 2 + (y - cy) ** 2 > r * r:
            return (0, 0, 0, 0)
        if any(in_poly(x + .5, y + .5, p) for p in K):
            return (34, 211, 238, 255)
        t = (x + y) / (2.0 * size)
        return (int(5 + 11 * t), int(8 + 25 * t), int(15 + 48 * t), 255)
    return px

def welcome(w, h):
    lg = logo(180)
    def px(x, y):
        if 40 <= x < 220 and 60 <= y < 240:
            p = lg(x - 40, y - 60)
            if p[3]:
                return p
        t = x / w
        return (int(5 + 8 * t), int(8 + 18 * t), int(15 + 40 * t), 255)
    return px

out = sys.argv[1]
png(out + "/logo.png", 256, 256, logo(256))
png(out + "/icon.png", 64, 64, logo(64))
png(out + "/welcome.png", 640, 300, welcome(640, 300))
print("PNG générés dans", out)
