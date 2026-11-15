"""Pequeña librería CSG sobre manifold3d (equivalente a OpenSCAD en Python)."""
import math
import os

import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold

FN = 64


def box(x, y, z, center=False):
    return Manifold.cube((x, y, z), center)


def cbox(x, y, z):
    """caja centrada en X/Y, apoyada en Z=0"""
    return Manifold.cube((x, y, z), True).translate((0, 0, z / 2))


def cyl(h, r, r2=None, center=False, fn=FN):
    return Manifold.cylinder(h, r, r if r2 is None else r2, fn, center)


def cyl_y(h, r, center=True, fn=FN):
    """cilindro a lo largo del eje Y"""
    return cyl(h, r, center=center, fn=fn).rotate((90, 0, 0))


def cyl_x(h, r, center=True, fn=FN):
    return cyl(h, r, center=center, fn=fn).rotate((0, 90, 0))


def rrect(w, d, r):
    """sección rectangular con esquinas redondeadas, centrada (w en X, d en Y)"""
    r = max(0.01, min(r, w / 2 - 0.01, d / 2 - 0.01))
    return CrossSection.square((w - 2 * r, d - 2 * r), True).offset(r, circular_segments=FN)


def rbox(x, y, z, r):
    """caja con aristas verticales redondeadas, centrada en XY, base en Z=0"""
    return Manifold.extrude(rrect(x, y, r), z)


def hull(*ms):
    return Manifold.batch_hull(list(ms))


def union(*ms):
    return Manifold.batch_boolean(list(ms), manifold3d_op("add"))


def manifold3d_op(name):
    from manifold3d import OpType
    return {"add": OpType.Add, "sub": OpType.Subtract}[name]


def hex_nut(s, h):
    """prisma hexagonal: s = entre caras"""
    r = s / 2 / math.cos(math.pi / 6) + 0.2
    return cyl(h, r, fn=6)


# tornillería métrica: (diám. paso, entre caras tuerca, alto tuerca, diám. cabeza)
M = {
    4: (4.4, 7.0, 3.4, 7.6),
    5: (5.4, 8.0, 4.2, 9.0),
    6: (6.5, 10.0, 5.2, 11.0),
    8: (8.5, 13.0, 6.8, 14.0),
    10: (10.5, 16.0, 8.4, 17.0),
    12: (12.6, 18.0, 10.4, 19.0),
}


def export(m, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mesh = m.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts), process=True)
    # apoyar en la cama
    tm.apply_translation((0, 0, -tm.bounds[0][2]))
    tm.export(path)
    ext = tm.bounds[1] - tm.bounds[0]
    return ext, abs(tm.volume)
