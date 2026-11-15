"""Miniaturas PNG de cada STL (para el manual)."""
import glob, os, sys
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "docs", "img", "piezas")
COL = {"01": "#ef6c00", "02": "#1e88e5", "03": "#43a047", "04": "#8e24aa", "00": "#757575"}
os.makedirs(OUT, exist_ok=True)
for f in sorted(glob.glob(os.path.join(ROOT, "stl", "**", "*.stl"), recursive=True)):
    m = trimesh.load(f)
    base = matplotlib.colors.to_rgb(COL[os.path.basename(os.path.dirname(f))[:2]])
    fig = plt.figure(figsize=(2.4, 2.4))
    ax = fig.add_subplot(111, projection="3d")
    light = np.clip(m.face_normals @ np.array([0.35, -0.55, 0.76]), 0, 1) * 0.65 + 0.35
    cols = np.clip(np.outer(light, base) + 0.08, 0, 1)
    ax.add_collection3d(Poly3DCollection(m.vertices[m.faces], facecolors=cols, edgecolor="none"))
    b = m.bounds; c = b.mean(0); r = (b[1] - b[0]).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.view_init(28, -55); ax.set_axis_off()
    plt.subplots_adjust(0, 0, 1, 1)
    plt.savefig(os.path.join(OUT, os.path.basename(f)[:-4] + ".png"), dpi=110, transparent=True)
    plt.close(fig)
print("ok")
