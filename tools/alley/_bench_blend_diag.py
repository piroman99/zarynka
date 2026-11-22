# -*- coding: utf-8 -*-
"""Диагностический рендер: планки — красные, ножки/стойки — синие.

Нужен, чтобы цифрами проверить, что планки спинки действительно с ВНУТРЕННЕЙ
стороны стоек: где они перекрываются, на экране должен стоять красный (планка),
а не синий (стойка со стороны газона).
Геометрия ровно как в _bench_blend3.py.
"""
import math
import os

import bpy
from mathutils import Vector

E = os.environ
OUT = E.get("OUT", "diag.png")
RESX = int(E.get("RESX", "1200"))
RESY = int(E.get("RESY", "720"))
CAMH = float(E.get("CAMH", "0.872600"))
CX = float(E.get("CX", "1.8903"))
CY = float(E.get("CY", "-3.00"))
TZ = float(E.get("TZ", "0.45"))
LENS = float(E.get("LENS", "50"))

L = 1.80
SEAT_DEPTH = 0.56
SLAT_T = 0.034
SEAT_Z = 0.45
BACK_TOP = 0.90
BACK_TILT = math.radians(10.0)
LEG = 0.072
BACK_X = -SEAT_DEPTH / 2 + 0.035

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
scene = bpy.context.scene


def emissive(name, rgb, strength=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*rgb, 1.0)
    em.inputs[1].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


M_WOOD = emissive("wood_red", (1.0, 0.02, 0.02))
M_IRON = emissive("iron_blue", (0.02, 0.10, 1.0))


def box(name, size, loc, rot=(0, 0, 0), material=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    ob.rotation_euler = rot
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        ob.data.materials.append(material)
    bpy.ops.object.shade_flat()
    return ob


def leg_x(z):
    return BACK_X - z * math.tan(BACK_TILT)


NS, SW = 4, 0.112
gap = (SEAT_DEPTH - NS * SW) / (NS - 1)
for i in range(NS):
    x = -SEAT_DEPTH / 2 + SW / 2 + i * (SW + gap)
    box("seat%d" % i, (SW, L, SLAT_T), (x, 0.0, SEAT_Z - SLAT_T / 2), material=M_WOOD)

BSW = 0.100
BACK_SLAT_IN = (LEG + SLAT_T) / 2.0
for i, z in enumerate((0.560, 0.695, 0.830)):
    box("back%d" % i, (SLAT_T, L, BSW),
        (leg_x(z) + BACK_SLAT_IN * math.cos(BACK_TILT), 0.0,
         z - BACK_SLAT_IN * math.sin(BACK_TILT)),
        rot=(0, BACK_TILT, 0), material=M_WOOD)

seat_under = SEAT_Z - SLAT_T
for sy in (-1, 1):
    y = sy * (L / 2 - 0.075)
    box("legF%d" % sy, (LEG, LEG, seat_under),
        (SEAT_DEPTH / 2 - LEG / 2, y, seat_under / 2), material=M_IRON)
    h = BACK_TOP / math.cos(BACK_TILT)
    box("legB%d" % sy, (LEG, LEG, h), (leg_x(BACK_TOP / 2), y, BACK_TOP / 2),
        rot=(0, BACK_TILT, 0), material=M_IRON)
    x0 = leg_x(seat_under - 0.07)
    x1 = SEAT_DEPTH / 2 - LEG / 2
    box("rail%d" % sy, (x1 - x0, LEG * 0.8, 0.062),
        ((x0 + x1) / 2, y, seat_under - 0.062 / 2 - 0.004), material=M_IRON)

cam_data = bpy.data.cameras.new("cam")
cam_data.lens = LENS
cam_data.sensor_width = 36.0
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
cam.location = Vector((CX, CY, CAMH))
cam.rotation_euler = (Vector((0.0, 0.0, TZ)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

world = bpy.data.worlds[0] if bpy.data.worlds else bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
bg.inputs[1].default_value = 0.0

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = int(E.get("SAMPLES", "24"))
scene.cycles.use_denoising = False
scene.render.film_transparent = True
scene.render.resolution_x = RESX
scene.render.resolution_y = RESY
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = os.path.abspath(OUT)
scene.view_settings.view_transform = 'Standard'
bpy.ops.render.render(write_still=True)
print("RENDERED", scene.render.filepath)
