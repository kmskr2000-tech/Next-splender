"""Stage-1 tiger cub test render (procedural, code-only modeling).

Run: python tiger_cub.py <out.png>
Needs the `bpy` module (pip install bpy). CPU Cycles + Freestyle outlines.
"""
import math
import sys

import bpy
from mathutils import Vector

OUT = sys.argv[-1] if sys.argv[-1].endswith(".png") else "/tmp/tiger_cub.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links


def principled(nodes):
    return nodes.get("Principled BSDF") or nodes.new("ShaderNodeBsdfPrincipled")


def flat_mat(name, color, rough=0.9, metal=0.0):
    m, nodes, _ = mat(name)
    p = principled(nodes)
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    return m


# ---------- fur material: white base, indigo-black stripes, cream belly/muzzle ----------
fur, n, l = mat("Fur")
p = principled(n)
p.inputs["Roughness"].default_value = 0.95
tc = n.new("ShaderNodeTexCoord")
noise = n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 2.5
noise.inputs["Detail"].default_value = 3
wave = n.new("ShaderNodeTexWave")
wave.wave_type = "BANDS"
wave.bands_direction = "Z"
wave.inputs["Scale"].default_value = 3.2
wave.inputs["Distortion"].default_value = 9.0
wave.inputs["Detail"].default_value = 2.0
l.new(tc.outputs["Object"], wave.inputs["Vector"])
ramp = n.new("ShaderNodeValToRGB")  # thin dark bands
ramp.color_ramp.interpolation = "CONSTANT"
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.05, 0.06, 0.16, 1)
ramp.color_ramp.elements[1].position = 0.18
ramp.color_ramp.elements[1].color = (0.92, 0.90, 0.85, 1)
l.new(wave.outputs["Fac"], ramp.inputs["Fac"])
# cream mask on front of chest / muzzle (object -Y side, low on body)
sep = n.new("ShaderNodeSeparateXYZ")
l.new(tc.outputs["Object"], sep.inputs["Vector"])
front = n.new("ShaderNodeMapRange")
front.inputs["From Min"].default_value = -0.25
front.inputs["From Max"].default_value = -0.55
l.new(sep.outputs["Y"], front.inputs["Value"])
mix = n.new("ShaderNodeMix")
mix.data_type = "RGBA"
l.new(front.outputs["Result"], mix.inputs["Factor"])
l.new(ramp.outputs["Color"], mix.inputs["A"])
mix.inputs["B"].default_value = (0.98, 0.95, 0.88, 1)
# slight warm tint variation for painted feel
tint = n.new("ShaderNodeMix")
tint.data_type = "RGBA"
tint.blend_type = "MULTIPLY"
tint.inputs["Factor"].default_value = 0.25
l.new(mix.outputs["Result"], tint.inputs["A"])
cr = n.new("ShaderNodeValToRGB")
cr.color_ramp.elements[0].color = (0.85, 0.82, 0.9, 1)
cr.color_ramp.elements[1].color = (1.0, 0.93, 0.8, 1)
l.new(noise.outputs["Fac"], cr.inputs["Fac"])
l.new(cr.outputs["Color"], tint.inputs["B"])
l.new(tint.outputs["Result"], p.inputs["Base Color"])

# ---------- body: metaballs merge into one organic blob ----------
mb = bpy.data.metaballs.new("CubBody")
mb.resolution = 0.03
mb.render_resolution = 0.02
mb.threshold = 0.6
body = bpy.data.objects.new("CubBody", mb)
scene.collection.objects.link(body)
mb.materials.append(fur)


def ball(co, r, kind="BALL", size=(1, 1, 1), stiff=2.0):
    e = mb.elements.new(type=kind)
    e.co = Vector(co)
    e.radius = r
    e.stiffness = stiff
    if kind == "ELLIPSOID":
        e.size_x, e.size_y, e.size_z = size
    return e


ball((0, 0.25, 0.62), 0.62, "ELLIPSOID", (0.75, 0.85, 1.0))   # torso, upright
ball((-0.36, 0.42, 0.34), 0.48)                               # haunches
ball((0.36, 0.42, 0.34), 0.48)
ball((0, -0.05, 1.32), 0.72, "ELLIPSOID", (1.0, 0.9, 0.85))   # big cub head
ball((-0.32, -0.12, 1.22), 0.34)                              # cheek ruff
ball((0.32, -0.12, 1.22), 0.34)
ball((0, -0.52, 1.18), 0.30, "ELLIPSOID", (1.0, 0.8, 0.7))    # muzzle
for sx in (-1, 1):
    for t in range(4):                                        # front legs
        ball((sx * 0.21, -0.12 - 0.04 * t, 0.62 - 0.15 * t), 0.2)
    ball((sx * 0.23, -0.3, 0.09), 0.25, "ELLIPSOID", (1.0, 1.4, 0.6))  # big paws
    ball((sx * 0.52, 0.12, 0.08), 0.22, "ELLIPSOID", (1.0, 1.5, 0.6))  # hind paws

# ---------- ears ----------
ear_m = flat_mat("EarInner", (0.9, 0.62, 0.6))
for sx in (-1, 1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(sx * 0.42, 0.0, 1.78))
    ear = bpy.context.object
    ear.scale = (1.0, 0.45, 1.0)
    ear.rotation_euler = (0.2, 0, -sx * 0.35)
    ear.data.materials.append(fur)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(sx * 0.42, -0.08, 1.76))
    inner = bpy.context.object
    inner.scale = (0.9, 0.3, 0.9)
    inner.rotation_euler = (0.2, 0, -sx * 0.35)
    inner.data.materials.append(ear_m)

# ---------- face: amber eyes, nose, forehead mark ----------
amber = flat_mat("Amber", (0.95, 0.55, 0.08), rough=0.3)
pupil = flat_mat("Pupil", (0.02, 0.02, 0.03), rough=0.2)
for sx in (-1, 1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(sx * 0.24, -0.58, 1.42))
    e = bpy.context.object
    e.scale = (1, 0.6, 1.1)
    e.data.materials.append(amber)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(sx * 0.24, -0.66, 1.43))
    pp = bpy.context.object
    pp.scale = (0.7, 0.4, 1.2)
    pp.data.materials.append(pupil)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.025, location=(sx * 0.21, -0.69, 1.48))
    bpy.context.object.data.materials.append(flat_mat("Glint", (1, 1, 1), rough=0.1))
nose = flat_mat("Nose", (0.75, 0.38, 0.38))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(0, -0.83, 1.2))
bpy.context.object.scale = (1.3, 0.8, 0.8)
bpy.context.object.data.materials.append(nose)

# ---------- tail (bezier curve with bevel) + pale gold ring ----------
cd = bpy.data.curves.new("Tail", "CURVE")
cd.dimensions = "3D"
cd.bevel_depth = 0.09
cd.bevel_resolution = 4
sp = cd.splines.new("BEZIER")
pts = [(0.5, 0.75, 0.2), (1.0, 0.6, 0.35), (1.15, 0.2, 0.75), (0.95, -0.05, 1.0)]
sp.bezier_points.add(len(pts) - 1)
for bp, co in zip(sp.bezier_points, pts):
    bp.co = co
    bp.handle_left_type = bp.handle_right_type = "AUTO"
sp.bezier_points[-1].radius = 0.8
tail = bpy.data.objects.new("Tail", cd)
scene.collection.objects.link(tail)
cd.materials.append(fur)
gold = flat_mat("PaleGold", (0.95, 0.8, 0.45), rough=0.35, metal=1.0)
bpy.ops.mesh.primitive_torus_add(location=(1.13, 0.32, 0.62), major_radius=0.11, minor_radius=0.035)
ring = bpy.context.object
ring.rotation_euler = (math.radians(70), 0, math.radians(30))
ring.data.materials.append(gold)

# ---------- jade ribbon + red knot ----------
jade = flat_mat("Jade", (0.12, 0.55, 0.42), rough=0.7)
red = flat_mat("Knot", (0.75, 0.1, 0.08), rough=0.7)
bpy.ops.mesh.primitive_torus_add(location=(0, -0.05, 0.93), major_radius=0.42, minor_radius=0.045)
rib = bpy.context.object
rib.scale = (1, 1, 0.7)
rib.rotation_euler = (math.radians(-12), 0, 0)
rib.data.materials.append(jade)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0.0, -0.47, 0.86))
bpy.context.object.data.materials.append(red)
for sx in (-1, 1):
    bpy.ops.mesh.primitive_cube_add(size=0.12, location=(sx * 0.07, -0.5, 0.74))
    t = bpy.context.object
    t.scale = (0.4, 0.15, 1.2)
    t.rotation_euler = (0, sx * 0.3, 0)
    t.data.materials.append(red)

# ---------- mossy rock ----------
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1.4, location=(0.1, 0.4, -1.1))
rock = bpy.context.object
rock.scale = (1.5, 1.2, 0.8)
tex = bpy.data.textures.new("RockNoise", "CLOUDS")
tex.noise_scale = 0.6
disp = rock.modifiers.new("D", "DISPLACE")
disp.texture = tex
disp.strength = 0.35
rm, rn, rl = mat("Rock")
rp = principled(rn)
rp.inputs["Roughness"].default_value = 1.0
geo = rn.new("ShaderNodeNewGeometry")
sxyz = rn.new("ShaderNodeSeparateXYZ")
rl.new(geo.outputs["Normal"], sxyz.inputs["Vector"])
rr = rn.new("ShaderNodeValToRGB")  # moss on top-facing faces, grey on sides
rr.color_ramp.elements[0].position = 0.45
rr.color_ramp.elements[0].color = (0.42, 0.42, 0.4, 1)
rr.color_ramp.elements[1].position = 0.7
rr.color_ramp.elements[1].color = (0.28, 0.45, 0.18, 1)
rl.new(sxyz.outputs["Z"], rr.inputs["Fac"])
rl.new(rr.outputs["Color"], rp.inputs["Base Color"])
rock.data.materials.append(rm)

# ---------- world: soft misty green ----------
world = bpy.data.worlds.new("Mist")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.55, 0.68, 0.55, 1)
bg.inputs["Strength"].default_value = 0.9
scene.world = world

# ---------- light & camera ----------
sun_d = bpy.data.lights.new("Sun", "SUN")
sun_d.energy = 3.2
sun_d.color = (1.0, 0.9, 0.75)
sun_d.angle = math.radians(8)
sun = bpy.data.objects.new("Sun", sun_d)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
scene.collection.objects.link(sun)

cam_d = bpy.data.cameras.new("Cam")
cam_d.lens = 70
cam = bpy.data.objects.new("Cam", cam_d)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = (2.6, -6.6, 2.0)
target = Vector((0.15, 0.1, 0.85))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()

# ---------- render ----------
r = scene.render
r.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 48
scene.cycles.use_denoising = True
r.resolution_x, r.resolution_y = 768, 1024
r.film_transparent = False
scene.view_settings.view_transform = "Standard"
r.use_freestyle = True
r.line_thickness_mode = "ABSOLUTE"
r.line_thickness = 2.2
fs = scene.view_layers[0].freestyle_settings
ls = fs.linesets[0] if fs.linesets else fs.linesets.new("Outline")
if ls.linestyle is None:
    ls.linestyle = bpy.data.linestyles.new("Ink")
ls.linestyle.color = (0.12, 0.08, 0.08)
r.filepath = OUT
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
