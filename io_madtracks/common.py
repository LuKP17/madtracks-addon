# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: common.py
# Original author: Marvin Thiel
#
# File first modified on 02/27/24
# Author: Lucas Pottier
#-----------------------------------------------------------------------------

"""
Name:    common
Purpose: Providing variables and functions available for all modules

Description:
Contains values that are specific to Mad Tracks, functions for converting units
and helper functions for Blender. 

"""

# Prevents the global dict from being reloaded
if "bpy" not in locals():
    dic = {}  # dict to hold the mesh for edit mode

import bpy
import bmesh
import os

# from math import sqrt
# from mathutils import Color, Matrix
# from .carinfo import read_parameters

# Relative paths from the user's Mad Tracks data folder
LDO_PATH = "\\Gfx\\models\\Geometry\\"
TEXTURE_PATH = "\\Graph\\maps\\High\\"
DESCRIPTOR_PATH = "\\Bin\\Descriptors\\"
LEVEL_PATH = "\\Bin\\Levels\\"

# Global dictionaries
global ERRORS
ERRORS = {}  # Dictionary that holds error messages
PARAMETERS = {}  # Glocal dict to hold parameters


# If True, more debug messages will be printed
DEBUG =             True # TODO disable for release version!

SCALE =             1

# TEX_PAGES_MAX =     64
# TEX_ANIM_MAX =      1024
MAT_MAX =           256   # not the actual limit

MAT_RGBA =          1
MAT_FLOAT3 =        4
MAT_TEXTURE =       8
MAT_BRIGHTNESS =    64
MAT_REFLECTION =    128

DUMMY_FLOAT3 =      64
DUMMY_FLOAT12 =     128

DUMMY_TYPE_MASK =   15
DUMMY_TYPE_WORLD =  5
DUMMY_TYPE_NUM =    6
DUMMY_TYPE_OUT =    9
DUMMY_TYPE_ROOF =   10
DUMMY_TYPE_BONUS =  11

# FACE_QUAD =         1       # 0x1
# FACE_DOUBLE =       2       # 0x2
# FACE_TRANSLUCENT =  4       # 0x4
# FACE_MIRROR =       128     # 0x80
# FACE_TRANSL_TYPE =  256     # 0x100
# FACE_TEXANIM =      512     # 0x200
# FACE_NOENV =        1024    # 0x400
# FACE_ENV =          2048    # 0x800
# FACE_CLOTH =        4096    # 0x1000
# FACE_SKIP =         8192    # 0x2000

# NCP_QUAD =          1
# NCP_DOUBLE =        2
# NCP_OBJECT_ONLY =   4
# NCP_CAMERA_ONLY =   8
# NCP_NON_PLANAR =    16
# NCP_NO_SKID =       32
# NCP_OIL =           64
# NCP_NOCOLL =        128

# FIN_ENV =           1
# FIN_HIDE =          2
# FIN_NO_MIRROR =     4
# FIN_NO_LIGHTS =     8
# FIN_SET_MODEL_RGB = 16
# FIN_NO_OBJECT_COLLISION = 32
# FIN_NO_CAMERA_COLLISION = 64

# NCP_PROP_MASK = (
#     NCP_DOUBLE |
#     NCP_OBJECT_ONLY |
#     NCP_CAMERA_ONLY |
#     NCP_NON_PLANAR |
#     NCP_NO_SKID |
#     NCP_OIL
# )

# # Used to unmask unsupported flags (FACE_SKIP)
# FACE_PROP_MASK = (
#     FACE_DOUBLE |
#     FACE_TRANSLUCENT |
#     FACE_MIRROR |
#     FACE_TRANSL_TYPE |
#     FACE_TEXANIM |
#     FACE_NOENV |
#     FACE_ENV |
#     FACE_CLOTH
# )

# FACE_PROPS = [
#     FACE_QUAD,
#     FACE_DOUBLE,
#     FACE_TRANSLUCENT,
#     FACE_MIRROR,
#     FACE_TRANSL_TYPE,
#     FACE_TEXANIM,
#     FACE_NOENV,
#     FACE_ENV,
#     FACE_CLOTH,
#     FACE_SKIP
# ]

# NCP_PROPS = [
#     NCP_QUAD,
#     NCP_DOUBLE,
#     NCP_OBJECT_ONLY,
#     NCP_CAMERA_ONLY,
#     NCP_NON_PLANAR,
#     NCP_NO_SKID,
#     NCP_OIL,
#     NCP_NOCOLL
# ]

TRACKPART_CATEGORIES = (
    # ("X", "Control", "Starts, checkpoints, finishes", ?),
    ("S", "Small", "Small trackparts", 0),
    ("M", "Medium", "Medium trackparts", 1),
    # ("W", "Wood", "Wood trackparts", ?),
    # ("B", "Bobsleigh", "Bobsleigh trackparts", ?),
    # ("C", "Croquet", "Croquet trackparts", ?),
    ("G", "Golf", "Golf trackparts", 2),
    # ("V", "Vent", "Vent trackparts", ?),
    # ("A", "Antartica", "Antartica trackparts", ?),
)
TRACKPARTS_SMALL = (
    ("S_bleu_amorce_15_in.ini", "Amorce 15 In", "Small amorce in", 0),
    ("S_bleu_amorce_15_out.ini", "Amorce 15 Out", "Small amorce out", 1),
    ("S_neon_rail_50.ini", "Straight Neon 50", "Small neon straight", 2),
    ("S_neon_virage_45_left.ini", "Left 45", "Small left turn", 3),
    ("S_neon_virage_45_right.ini", "Right 45", "Small right turn", 4),
    ("S_raye_rampe_30_up.ini", "Up 30", "Small up ramp", 5),
    ("S_raye_rampe_30_down.ini", "Down 30", "Small down ramp", 6),
    ("S_gris_to_M_50.ini", "S to M 50", "Small to medium transition", 7),
    ("S_raye_looping.ini", "Looping", "Small looping", 8),
)
TRACKPARTS_MEDIUM = (
    ("M_gris_amorce_05_in.ini", "Amorce 05 In", "Medium amorce in", 0),
    ("M_gris_amorce_15_in.ini", "Amorce 15 In", "Medium amorce in", 1),
    ("M_gris_amorce_15_out.ini", "Amorce 15 Out", "Medium amorce out", 2),
    ("M_gris_amorce_30_in.ini", "Amorce 30 In", "Medium amorce in", 3),
    ("M_gris_amorce_30_out.ini", "Amorce 30 Out", "Medium amorce out", 4),
    ("M_gris_rail_15.ini", "Straight 15", "Medium straight", 5),
    ("M_gris_rail_50.ini", "Straight 50", "Medium straight", 6),
    ("M_neon_rail_50.ini", "Straight Neon 50", "Medium neon straight", 7),
    ("M_gris_virage_45_left.ini", "Left 45", "Medium left turn", 8),
    ("M_gris_virage_45_right.ini", "Right 45", "Medium right turn", 9),
    ("M_gris_rampe_30_up.ini", "Up 30", "Medium up ramp", 10),
    ("M_gris_rampe_30_down.ini", "Down 30", "Medium down ramp", 11),
    ("M_none_start.ini", "Start", "Medium start", 12),
    ("M_none_checkpoint.ini", "Checkpoint", "Medium checkpoint", 13),
    ("M_none_finish_50.ini", "Finish", "Medium finish", 14),
    ("M_gris_to_S_50.ini", "M to S 50", "Medium to small transition", 15),
)
TRACKPARTS_GOLF = (
    ("G_none_checkpoint.ini", "Checkpoint", "Golf checkpoint", 0),
    ("G_none_finish.ini", "Finish", "Golf finish", 1),
)

# MATERIALS = (
#     ("-1", "NONE", "No material. Faces with this material will not be exported.", "POTATO", -1),
#     ("0", "DEFAULT",            "Default material", "POTATO", 0),
#     ("1", "MARBLE",             "Marble material", "POTATO", 1),
#     ("2", "STONE",              "Stone material", "POTATO", 2),
#     ("3", "WOOD",               "Wood material", "POTATO", 3),
#     ("4", "SAND",               "Sand material", "POTATO", 4),
#     ("5", "PLASTIC",            "Plastic material", "POTATO", 5),
#     ("6", "CARPETTILE",         "Carpet Tile material", "POTATO", 6),
#     ("7", "CARPETSHAG",         "Carpet Shag material", "POTATO", 7),
#     ("8", "BOUNDARY",           "Boundary material", "POTATO", 8),
#     ("9", "GLASS",              "Glass material", "POTATO", 9),
#     ("10", "ICE1",              "Most slippery ice material", "FREEZE", 10),
#     ("11", "METAL",             "Metal material", "POTATO", 11),
#     ("12", "GRASS",             "Grass material", "POTATO", 12),
#     ("13", "BUMPMETAL",         "Bump metal material", "POTATO", 13),
#     ("14", "PEBBLES",           "Pebbles material", "POTATO", 14),
#     ("15", "GRAVEL",            "Gravel material", "POTATO", 15),
#     ("16", "CONVEYOR1",         "First conveyor material", "POTATO", 16),
#     ("17", "CONVEYOR2",         "Second conveyor material", "POTATO", 17),
#     ("18", "DIRT1",             "First dirt material", "POTATO", 18),
#     ("19", "DIRT2",             "Second dirt material", "POTATO", 19),
#     ("20", "DIRT3",             "Third dirt material", "POTATO", 20),
#     ("21", "ICE2",              "Medium slippery ice material", "FREEZE", 21),
#     ("22", "ICE3",              "Least slippery ice material", "FREEZE", 22),
#     ("23", "WOOD2",             "Second wood material", "POTATO", 23),
#     ("24", "CONVEYOR_MARKET1",  "First supermarket conveyor", "POTATO", 24),
#     ("25", "CONVEYOR_MARKET2",  "Second supermarket conveyor", "POTATO", 25),
#     ("26", "PAVING",            "Paving material", "POTATO", 26),
# )


def dprint(*str):
    """ Debug print: only prints if debug is enabled """
    if DEBUG:
        print(*str)


# def rgb(r, g, b):
#     """ Workaround so I can use a color picker """
#     return (r/255, g/255, b/255)


# COLORS = (
#     rgb(153, 153, 153),     # DEFAULT
#     rgb(130, 91, 91),       # MARBLE
#     rgb(56, 56, 56),        # STONE
#     rgb(119, 76, 35),       # WOOD
#     rgb(244, 193, 127),     # SAND
#     rgb(22, 22, 22),        # PLASTIC
#     rgb(170, 20, 0),        # CARPETTILE
#     rgb(135, 45, 33),       # CARPETSHAG
#     rgb(255, 0, 255),       # BOUNDARY
#     rgb(255, 255, 255),     # GLASS
#     rgb(184, 255, 242),     # ICE1
#     rgb(135, 153, 163),     # METAL
#     rgb(45, 91, 12),        # GRASS
#     rgb(56, 61, 51),        # BUMPMETAL
#     rgb(140, 140, 124),     # PEBBLES
#     rgb(201, 196, 193),     # GRAVEL
#     rgb(56, 0, 128),        # CONVEYOR1
#     rgb(51, 38, 61),        # CONVEYOR2
#     rgb(135, 99, 73),       # DIRT1
#     rgb(91, 66, 48),        # DIRT2
#     rgb(66, 40, 25),        # DIRT3
#     rgb(132, 181, 178),     # ICE2
#     rgb(102, 136, 134),     # ICE3
#     rgb(119, 76, 43),       # WOOD2
#     rgb(0, 20, 56),         # CONVEYOR_MARKET1
#     rgb(25, 33, 51),        # CONVEYOR_MARKET2
#     rgb(142, 127, 114),     # PAVING
#     rgb(255, 0, 0)          # NONE (-1)
# )

# # Colors for debug objects
# COL_CUBE = Color(rgb(180, 20, 0))
# COL_BBOX = Color(rgb(0, 0, 40))
# COL_BCUBE = Color(rgb(0, 180, 20))
# COL_SPHERE = Color(rgb(60, 60, 80))
# COL_HULL = Color(rgb(0, 20, 180))

"""
Supported File Formats
"""
FORMAT_UNK = -1
FORMAT_LDO = 0
FORMAT_INI = 2
FORMAT_OBJ_INI = 3
FORMAT_LVL_INI = 4
# FORMAT_BMP = 0
# FORMAT_CAR = 1
# FORMAT_TA_CSV = 2
# FORMAT_FIN = 3
# FORMAT_FOB = 4
# FORMAT_HUL = 5
# FORMAT_LIT = 6
# FORMAT_NCP = 7
# FORMAT_PRM = 8
# FORMAT_RIM = 9
# FORMAT_RTU = 10
# FORMAT_TAZ = 11
# FORMAT_VIS = 12
# FORMAT_W = 13

FORMATS = {
    FORMAT_LDO: "Geometry (.ldo)",
    FORMAT_INI: "Unsupported (.ini)",
    FORMAT_OBJ_INI: "Object (.ini)",
    FORMAT_LVL_INI: "Level (.ini)",
#     FORMAT_BMP: "Bitmap (.bm*)",
#     FORMAT_CAR: "Car Parameters (.txt)",
#     FORMAT_TA_CSV: "Texture Animation Sheet (.ta.csv)",
#     FORMAT_FIN: "Instances (.fin)",
#     FORMAT_FOB: "Objects (.fob)",
#     FORMAT_HUL: "Hull (.hul)",
#     FORMAT_LIT: "Lights (.lit)",
#     FORMAT_NCP: "Collision (.ncp)",
#     FORMAT_PRM: "Mesh (.prm/.m)",
#     FORMAT_RIM: "Mirrors (.rim)",
#     FORMAT_RTU: "Track Editor (.rtu)",
#     FORMAT_TAZ: "Track Zones (.taz)",
#     FORMAT_VIS: "Visiboxes (.vis)",
#     FORMAT_W:   "World (.w)",
}


# """
# Constants for the tool shelf functions
# """

# BAKE_LIGHTS = [
#     ("None", "None", "", -1),
#     ("HEMI", "Soft", "", 0),
#     ("SUN", "Hard", "", 1)
# ]

# BAKE_LIGHT_ORIENTATIONS = [
#     ("X", "X (Horizontal)", "", 0),
#     ("Y", "Y (Horizontal)", "", 1),
#     ("Z", "Z (Vertical)", "", 2)
# ]
# BAKE_SHADOW_METHODS = [
#     ("ADAPTIVE_QMC", "Default (fast)", "", "ALIASED", 0),
#     ("CONSTANT_QMC", "Nicer (slow)", "", "ANTIALIASED", 1)
# ]

# TA_CSV_HEADER = "Slot,Frame,Texture,Delay,U0,V0,U1,V1,U2,V2,U3,V3"


"""
Conversion functions for Mad Tracks structures.
Axes are saved differently and many indices are saved in a different order.
"""

def to_blender_axis(vec):
    return [-vec[0], vec[2], vec[1]]


def to_blender_coord(vec):
    return [-vec[0] * SCALE, vec[2] * SCALE, vec[1] * SCALE]


def to_blender_scale(num):
    return num * SCALE


def to_madtracks_axis(vec):
    return [-vec[0], vec[2], vec[1]]


def to_madtracks_coord(vec):
    return [-vec[0] / SCALE, vec[2] / SCALE, vec[1] / SCALE]


def to_madtracks_scale(num):
    return num / SCALE

# def to_trans_matrix(matrix):
#     return Matrix((
#         ( matrix[0][0],  matrix[2][0], -matrix[1][0], 0),
#         ( matrix[0][2],  matrix[2][2], -matrix[1][2], 0),
#         (-matrix[0][1], -matrix[2][1],  matrix[1][1], 0),
#         (0, 0, 0, 1)
#         ))

# def to_or_matrix(matrix):
#     return [
#         (matrix[0][0], -matrix[2][0],  matrix[1][0]),
#         (-matrix[0][2],  matrix[2][2], -matrix[1][2]),
#         (matrix[0][1], -matrix[2][1],  matrix[1][1])
#     ]


# def rvbbox_from_bm(bm):
#     """ The bbox of Blender objects has all edge coordinates. RV just stores the
#     mins and max for each axis. """
#     return rvbbox_from_verts(bm.verts)


# def rvbbox_from_verts(verts):
#     xlo = min(v.co[0] for v in verts) / SCALE
#     xhi = max(v.co[0] for v in verts) / SCALE
#     ylo = -max(v.co[2] for v in verts) / SCALE
#     yhi = -min(v.co[2] for v in verts) / SCALE
#     zlo = min(v.co[1] for v in verts) / SCALE
#     zhi = max(v.co[1] for v in verts) / SCALE
#     return(xlo, xhi, ylo, yhi, zlo, zhi)


# def get_distance(v1, v2):
#     return sqrt((v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)


# def center_from_rvbbox(rvbbox):
#     return (
#         (rvbbox[0] + rvbbox[1]) / 2,
#         (rvbbox[2] + rvbbox[3]) / 2,
#         (rvbbox[4] + rvbbox[5]) / 2,
#     )


# def radius_from_bmesh(bm, center):
#     """ Gets the radius measured from the furthest vertex."""
#     radius = max(
#         [get_distance(center, to_revolt_coord(v.co)) for v in bm.verts]
#     )
#     return radius


# def reverse_quad(quad, tri=False):
#     if tri:
#         return quad[2::-1]
#     else:
#         return quad[::-1]


# def texture_to_int(string):
#     # Assigns texture A to cars
#     if "car.bmp" in string:
#         return 0

#     if ".bmp" in string:
#         base, ext = string.split(".", 1)
#         try:
#             num = int(base)
#         except:
#             # Checks if the last letter of the file name matches old naming convention
#             if base[-1].isalpha():
#                 num = ord(base[-1]) - 97
#             else:
#                 return -1

#         # Returns texture A if it's not a fitting track texture
#         if num >= TEX_PAGES_MAX or num < 0:
#             return 0

#         return num

#     # .bmp is not in the texture name, assumes no texture
#     else:
#         return -1


# def int_to_texture(tex_num, name=""):
#     suffix = chr(tex_num % 26 + 97)
#     suffix2 = (tex_num // 26 )
#     if suffix2 > 0:
#         suffix += chr(suffix2 + 96) 
#     return name + suffix + ".bmp"

# def create_material(name, diffuse, alpha):
#     """ Creates a material, mostly used for debugging objects """
#     mat = bpy.data.materials.new(name)
#     mat.diffuse_color = diffuse
#     mat.diffuse_intensity = 1.0
#     mat.alpha = alpha
#     if alpha:
#         mat.use_transparency = True
#     return mat


# """
# Blender helpers
# """

# def get_active_face(bm):
#     if bm.select_history:
#         elem = bm.select_history[-1]
#         if isinstance(elem, bmesh.types.BMFace):
#             return elem
#     return None


# def get_edit_bmesh(obj):
#     try:
#         bm = dic[obj.name]
#         bm.faces.layers.int.get("Type")
#         return bm
#     except Exception as e:
#         dprint("Bmesh is gone, creating new one...")
#         del dic[obj.name]
#         bm = dic.setdefault(obj.name, bmesh.from_edit_mesh(obj.data))
#         return bm


# def apply_trs(obj, bm, transform=False):
#         # Removes the parent for exporting and applies transformation
#         parent = obj.parent
#         if parent:
#             mat = obj.matrix_world.copy()
#             old_mat = obj.matrix_basis.copy()
#             obj.parent = None
#             obj.matrix_world = mat

#         spc = obj.matrix_basis
#         bmesh.ops.scale(
#             bm,
#             vec=obj.scale,
#             space=spc,
#             verts=bm.verts
#         )
#         if transform:
#             bmesh.ops.transform(
#                 bm,
#                 matrix=Matrix.Translation(obj.location),
#                 space=spc,
#                 verts=bm.verts
#             )
#         bmesh.ops.rotate(
#             bm,
#             cent=obj.location,
#             matrix=obj.rotation_euler.to_matrix(),
#             space=spc,
#             verts=bm.verts
#         )

#         # Restores the parent relationship
#         if parent and not obj.parent:
#             obj.parent = parent
#             obj.matrix_basis = old_mat


# def objects_to_bmesh(objs, transform=True):
#     """ Merges multiple objects into one bmesh for export """

#     # CAUTION: Removes/destroys custom layer props

#     # Creates the mesh used to merge the entire scene
#     bm_all = bmesh.new()

#     # Adds the objects" meshes to the bmesh
#     for obj in objs:
#         dprint("Preparing object {} for export...".format(obj.name))
#         # Creates a bmesh from the supplied object
#         bm = bmesh.new()
#         bm.from_mesh(obj.data)

#         # Makes sure all layers exist so values don't get lost while exporting
#         uv_layer = bm.loops.layers.uv.get("UVMap")
#         tex_layer = bm.faces.layers.tex.get("UVMap")
#         vc_layer = (bm.loops.layers.color.get("Col") or
#                     bm.loops.layers.color.new("Col"))
#         env_layer = (bm.loops.layers.color.get("Env") or
#                      bm.loops.layers.color.new("Env"))
#         env_alpha_layer = (bm.faces.layers.float.get("EnvAlpha") or
#                            bm.faces.layers.float.new("EnvAlpha"))
#         va_layer = (bm.loops.layers.color.get("Alpha") or
#                     bm.loops.layers.color.new("Alpha"))
#         texnum_layer = bm.faces.layers.int.get("Texture Number")
#         type_layer = (bm.faces.layers.int.get("Type") or
#                       bm.faces.layers.int.new("Type"))
#         material_layer = (bm.faces.layers.int.get("Material") or
#                           bm.faces.layers.int.new("Material"))

#         # Removes the parent for exporting and applies transformation
#         parent = obj.parent
#         if parent:
#             mat = obj.matrix_world.copy()
#             old_mat = obj.matrix_basis.copy()
#             obj.parent = None
#             obj.matrix_world = mat

#         spc = obj.matrix_basis
#         bmesh.ops.scale(
#             bm,
#             vec=obj.scale,
#             space=spc,
#             verts=bm.verts
#         )
#         if transform:
#             bmesh.ops.transform(
#                 bm,
#                 matrix=Matrix.Translation(obj.location),
#                 space=spc,
#                 verts=bm.verts
#             )
#         bmesh.ops.rotate(
#             bm,
#             cent=obj.location,
#             matrix=obj.rotation_euler.to_matrix(),
#             space=spc,
#             verts=bm.verts
#         )

#         # Restores the parent relationship
#         if parent and not obj.parent:
#             obj.parent = parent
#             obj.matrix_basis = old_mat

#         # Converts the transformed bmesh to mesh
#         new_mesh = bpy.data.meshes.new("ncp_export_temp")
#         bm.to_mesh(new_mesh)

#         # Adds the transformed mesh to the big bmesh
#         bm_all.from_mesh(new_mesh)

#         # Removes unused meshes
#         bpy.data.meshes.remove(new_mesh, do_unlink=True)
#         bm.free()

#     return bm_all


class DialogOperator(bpy.types.Operator):
    bl_idname = "madtracks.dialog"
    bl_label = "Mad Tracks Add-On Notification"

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        global dialog_message
        global dialog_icon
        row = self.layout.row()
        row.label("", icon=dialog_icon)
        column = row.column()
        for line in str.split(dialog_message, "\n"):
            column.label(line)


def msg_box(message, icon="INFO"):
    global dialog_message
    global dialog_icon
    print(message)
    dialog_message = message
    dialog_icon = icon
    bpy.ops.madtracks.dialog("INVOKE_DEFAULT")


# def queue_error(action, error_message):
#     """ Adds an error message to the error dict """
#     global ERRORS
#     print("Error while {}: {}".format(action, error_message))
#     ERRORS[action] = error_message


def get_errors():
    global ERRORS
    if ERRORS:
        errors = "The following errors have been encountered:\n\n"
        for error in ERRORS:
            errors += "~ ERROR while {}:\n     {}\n\n".format(error, ERRORS[error])
        errors += "Check the console for more information."
    else:
        errors = "Successfully completed."

    # Clears the error messages
    ERRORS = {}

    return errors


# def redraw():
#     redraw_3d()
#     redraw_uvedit()


def redraw_3d():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
                break


# def redraw_uvedit():
#     for window in bpy.context.window_manager.windows:
#         screen = window.screen
#         for area in screen.areas:
#             if area.type == "IMAGE_EDITOR":
#                 area.tag_redraw()
#                 break


def enable_any_tex_mode(context):
    """ Enables the preferred texture mode according to settings """
    enable_texture_mode()
    # props = context.scene.revolt
    # if props.prefer_tex_solid_mode:
    #     enable_textured_solid_mode()
    # else:
    #     enable_texture_mode()


def enable_texture_mode():
    """ Enables textured shading in the viewport """
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.viewport_shade = "TEXTURED"
    return

# def enable_textured_solid_mode():
#     """ Enables solid mode and enables textured solid shading """
#     for area in bpy.context.screen.areas:
#         if area.type == "VIEW_3D":
#             for space in area.spaces:
#                 if space.type == "VIEW_3D":
#                     space.viewport_shade = "SOLID"
#                     space.show_textured_solid = True
#     return

# def enable_solid_mode():
#     """ Enables solid mode """
#     for area in bpy.context.screen.areas:
#         if area.type == "VIEW_3D":
#             for space in area.spaces:
#                 if space.type == "VIEW_3D":
#                     space.viewport_shade = "SOLID"
#                     space.show_textured_solid = False
#     return


# def texture_mode_enabled():
#     """ Returns true if texture mode or textured solid mode is enabled """
#     for area in bpy.context.screen.areas:
#         if area.type == "VIEW_3D":
#             for space in area.spaces:
#                 if space.type == "VIEW_3D":
#                     if space.viewport_shade == "TEXTURED":
#                         return True
#                     elif (space.viewport_shade == "SOLID" and
#                           space.show_textured_solid):
#                         return True
#     return False


# def get_all_lod(namestr):
#     """ Gets all LoD meshes belonging to a mesh (including that mesh) """
#     meshes = []
#     for me in bpy.data.meshes:
#         if "|q" in me.name and namestr in me.name:
#             meshes.append(me)
#     return meshes


# def triangulate_ngons(bm):
#     """ Triangulates faces for exporting """
#     triangulate = []
#     for face in bm.faces:
#         if len(face.verts) > 4:
#             triangulate.append(face)
#     if triangulate:
#         bmesh.ops.triangulate(bm, faces=triangulate,
#                               quad_method=0, ngon_method=0)
#     return len(triangulate)


# def check_for_export(obj):
#     if not obj:
#         msg_box("Please select an object first.")
#         return False
#     if not obj.data:
#         msg_box("The selected object does not have any data.")
#         return False
#     if not obj.type == "MESH":
#         msg_box("The selected object does not have any mesh.")
#         return False
#     return True


"""
Non-Blender helper functions
"""

# def is_track_folder(path):
#     for f in os.listdir(path):
#         if ".inf" in f:
#             return True
#     return False


def get_format(fstr):
    """
    Gets the format by the ending and returns an int
    """
    fstr = fstr.lower()  # support uppercase letters
    if os.sep in fstr:
        fstr = fstr.split(os.sep)[-1]
    try:
        fname, ext = fstr.split(".", 1)
    except:
        fname, ext = ("", "")

    if ext == "ldo":
        return FORMAT_LDO
    elif ext == "ini":
        return FORMAT_INI
    else:
        return FORMAT_UNK


def float_format(value):
    return '{:f}'.format(value)
