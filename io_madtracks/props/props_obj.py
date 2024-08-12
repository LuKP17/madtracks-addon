# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: props_obj.py
# Original author: Marvin Thiel
#
# File first modified on 03/17/24
# Author: Lucas Pottier
#-----------------------------------------------------------------------------

"""
Name:    props_obj
Purpose: Provides the object data class for Mad Tracks meshes

Description:
Objects in Mad Tracks can be of different types or used for debugging only.

"""

import bpy

from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
    CollectionProperty,
    IntVectorProperty,
    FloatVectorProperty,
    PointerProperty
)
from ..common import *

class MadObjectProperties(bpy.types.PropertyGroup):
    descriptor = StringProperty(
        name = "Descriptor",
        default = "None",
        description = "Filename of the object's descriptor"
    )
    # Trackparts
    is_trackpart = BoolProperty(
        name = "Is Trackpart",
        default = False,
        description = "Object is a trackpart"
    )
    num_sequence = IntProperty(
        name = "Sequence",
        default = -1,
        min = -1,
        description = "Which trackpart sequence the trackpart belongs to. Valid values start at 0"
    )
    num_trackpart = IntProperty(
        name = "Number",
        default = -1,
        min = -1,
        description = "Where in the trackpart sequence the trackpart is. Valid values start at 0"
    )
    invert = BoolProperty(
        name = "Invert",
        default = False,
        description = "If the trackpart is inverted"
    )

    # # Debug Objects
    # is_bcube = BoolProperty(
    #     name = "Object is a BigCube",
    #     default = False,
    #     description = "Makes BigCube properties visible for this object"
    # )
    # is_cube = BoolProperty(
    #     name = "Object is a Cube",
    #     default = False,
    #     description = "Makes Cube properties visible for this object"
    # )
    # is_bbox = BoolProperty(
    #     name = "Object is a Boundary Box",
    #     default = False,
    #     description = "Makes BoundBox properties visible for this object"
    # )
    # ignore_ncp = BoolProperty(
    #     name = "Ignore Collision (.ncp)",
    #     default = False,
    #     description = "Ignores the object when exporting to NCP"
    # )
    # bcube_mesh_indices = StringProperty(
    #     name = "Mesh indices",
    #     default = "",
    #     description = "Indices of child meshes"
    # )

    # # Hull

    # is_hull_sphere = BoolProperty(
    #     name = "Is Interior Sphere",
    #     default = False,
    #     description = ""
    # )
    # is_hull_convex = BoolProperty(
    #     name = "Is Convex Hull",
    #     default = False,
    #     description = ""
    # )

    # # Instances

    # is_instance = BoolProperty(
    #     name = "Is Instance",
    #     default = False,
    #     description = "Object is an instanced mesh"
    # )

    # fin_col = FloatVectorProperty(
    #    name="Model Color",
    #    subtype='COLOR',
    #    default=(0.5, 0.5, 0.5),
    #    min=0.0, max=1.0,
    #    description="Model RGB color to be added/subtracted:\n1.0: Bright, overrides vertex colors\n"
    #        "0.5: Default, leaves vertex colors intact\n"
    #        "0.0: Dark"
    # )
    # fin_envcol = FloatVectorProperty(
    #    name="Env Color",
    #    subtype='COLOR',
    #    default=(1.0, 1.0, 1.0, 1.0),
    #    min=0.0, max=1.0,
    #    description="Color of the EnvMap",
    #    size=4
    # )
    # fin_priority = IntProperty(
    #     name="Priority",
    #     default=1,
    #     description="Priority for instance. Instance will always be shown if set to 1."
    # )
    # fin_env = BoolProperty(
    #     name="Use Environment Map",
    #     default=True
    # )
    # fin_model_rgb = BoolProperty(
    #     name="Use Model Color",
    #     default=False
    # )
    # fin_hide = BoolProperty(
    #     name="Hide",
    #     default=False
    # )
    # fin_no_mirror = BoolProperty(
    #     name="Don't show in Mirror Mode",
    #     default=False
    # )
    # fin_no_lights = BoolProperty(
    #     name="Is affected by Light",
    #     default=False
    # )
    # fin_no_cam_coll = BoolProperty(
    #     name="No Camera Collision",
    #     default=False
    # )
    # fin_no_obj_coll = BoolProperty(
    #     name="No Object Collision",
    #     default=False
    # )
    # fin_lod_bias = IntProperty(
    #     name="LoD Bias",
    #     default = 1024,
    #     description = "Unused"
    # )

    # # Mirrors

    # is_mirror_plane = BoolProperty(
    #     name = "Is Mirror Plane",
    #     default = False,
    #     description = "Object is a mirror plane (.rim)"
    # )
    
    # # Zones
    # is_track_zone = BoolProperty(
    #     name = "Is Track Zone",
    #     default = False,
    #     description = "This object is a track zone box"
    # )
