# -*- coding: utf-8 -*-
"""Скамейка v7: исправлен наклон стоек, доски спинки ставятся двумя способами.

РЕЖИМ (env MODE):
  A  — доски спинки ВПУСК между стойками: длина уложена между внутренними
       гранями стоек, передняя плоскость доски заподлицо с передней плоскостью
       стойки. Стойки видны по краям как рама.
  B  — доски спинки СНАРУЖИ, со стороны наблюдателя: лежат на передних гранях
       стоек по всей длине, у каждой стойки — круглая шляпка винта.

Наклон стоек: ось уходит назад с высотой (−X), локальный «верх» = (−sin T, 0, cos T),
поэтому поворот (0, −T, 0). Ранее стояло (0, +T, 0) — стойки уходили ВПЕРЁД,
и доски на разных высотах попадали то внутрь стойки, то наружу.

Окружение: OUT, MODE, RESX, RESY, SAMPLES, CAMH, CX, CY, TZ, LENS.
"""
import math
import os

import bpy
from mathutils import Vector

E = os.environ
OUT = E.get("OUT", "bench7.png")
MODE = E.get("MODE", "B").upper()
RESX = int(E.get("RESX", "3000"))
RESY = int(E.get("RESY", "1800"))
SAMPLES = int(E.get("SAMPLES", "120"))
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
T = math.radians(10.0)
LEG = 0.072
BACK_X = -SEAT_DEPTH / 2 + 0.035
POST_Y = L / 2 - 0.075          # ось стойки по Y
BSW = 0.100                     # высота доски спинки

for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
scene = bpy.context.scene


def mat(name, rgb, rough=0.70, spec=0.18, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    for key in ("Specular IOR Level", "Specular"):
        if key in b.inputs:
            b.inputs[key].default_value = spec
            break
    m.diffuse_color = (*rgb, 1.0)
    return m


M_WOOD = mat("paint_green", (0.100, 0.165, 0.115))
M_IRON = mat("iron", (0.048, 0.050, 0.048), rough=0.60)
M_BOLT = mat("bolt", (0.42, 0.43, 0.44), rough=0.35, metallic=1.0)


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
    """ось стойки: с высотой уходит назад (−X)."""
    return BACK_X - z * math.tan(T)


# u — единичная нормаль к плоскости спинки, смотрит на наблюдателя (+X, чуть +Z)
def u_off(off, z):
    return (leg_x(z) + off * math.cos(T), z + off * math.sin(T))


# --- сиденье: 4 доски вдоль Y ----------------------------------------------
NS, SW = 4, 0.112
gap = (SEAT_DEPTH - NS * SW) / (NS - 1)
for i in range(NS):
    x = -SEAT_DEPTH / 2 + SW / 2 + i * (SW + gap)
    box("seat%d" % i, (SW, L, SLAT_T), (x, 0.0, SEAT_Z - SLAT_T / 2), material=M_WOOD)

# --- спинка ----------------------------------------------------------------
if MODE == 'A':
    # между стойками, заподлицо с их передней плоскостью
    slat_len = 2.0 * (POST_Y - LEG / 2) - 0.004
    off = (LEG - SLAT_T) / 2.0
else:
    # на передних гранях стоек, по всей длине
    slat_len = L
    off = (LEG + SLAT_T) / 2.0

print("MODE", MODE, "slat_len %.3f" % slat_len, "off %.3f" % off)
for i, z in enumerate((0.560, 0.695, 0.830)):
    x, zz = u_off(off, z)
    box("back%d" % i, (SLAT_T, slat_len, BSW), (x, 0.0, zz), rot=(0, -T, 0),
        material=M_WOOD)

# шляпки винтов: спинка — на стойках, сиденье — на перекладинах под досками
if MODE == 'B':
    R, D = 0.0115, 0.007
    for i, z in enumerate((0.560, 0.695, 0.830)):
        x, zz = u_off(off + SLAT_T / 2.0 + D / 2.0 - 0.001, z)
        for sy in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=R, depth=D,
                                                location=(x, sy * POST_Y, zz))
            ob = bpy.context.object
            ob.name = "boltB%d_%d" % (i, sy)
            ob.rotation_euler = (0.0, math.pi / 2.0 - T, 0.0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            ob.data.materials.append(M_BOLT)
            bpy.ops.object.shade_smooth()

    # сиденье: винты сверху, в перекладины (по две на доску, у каждой стойки)
    for i in range(NS):
        x = -SEAT_DEPTH / 2 + SW / 2 + i * (SW + gap)
        for sy in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=R, depth=D,
                                                location=(x, sy * POST_Y,
                                                          SEAT_Z + D / 2.0 - 0.001))
            ob = bpy.context.object
            ob.name = "boltS%d_%d" % (i, sy)
            ob.data.materials.append(M_BOLT)
            bpy.ops.object.shade_smooth()

# --- ножки и перекладины ---------------------------------------------------
seat_under = SEAT_Z - SLAT_T
for sy in (-1, 1):
    y = sy * POST_Y
    box("legF%d" % sy, (LEG, LEG, seat_under),
        (SEAT_DEPTH / 2 - LEG / 2, y, seat_under / 2), material=M_IRON)
    h = BACK_TOP / math.cos(T)
    box("legB%d" % sy, (LEG, LEG, h), (leg_x(BACK_TOP / 2), y, BACK_TOP / 2),
        rot=(0, -T, 0), material=M_IRON)
    x0 = leg_x(seat_under - 0.07)
    x1 = SEAT_DEPTH / 2 - LEG / 2
    box("rail%d" % sy, (x1 - x0, LEG * 0.8, 0.062),
        ((x0 + x1) / 2, y, seat_under - 0.062 / 2 - 0.004), material=M_IRON)

# --- камера и свет ---------------------------------------------------------
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
bg.inputs[0].default_value = (0.80, 0.86, 0.96, 1.0)
bg.inputs[1].default_value = 1.30

sun_d = bpy.data.lights.new("sun", type='SUN')
sun_d.energy = 2.0
sun_d.angle = math.radians(14)
sun = bpy.data.objects.new("sun", sun_d)
scene.collection.objects.link(sun)
sun.location = (-2.0, -2.5, 4.0)
sun.rotation_euler = (math.radians(50), 0.0, math.radians(-40))

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 4
scene.cycles.transparent_max_bounces = 4
scene.render.film_transparent = True
scene.render.resolution_x = RESX
scene.render.resolution_y = RESY
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = os.path.abspath(OUT)
scene.view_settings.view_transform = 'Standard'
bpy.ops.render.render(write_still=True)
print("RENDERED", scene.render.filepath, MODE)
