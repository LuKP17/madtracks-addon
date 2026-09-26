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
Purpose: Provides the object data class for Mad Tracks meshes.

Description:
Objects in Mad Tracks can be of different types or used for debugging only.

"""

import bpy

from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    StringProperty,
    FloatVectorProperty,
    PointerProperty
)
from ..common import *


def nextt_update_func(self, context):
    scene = context.scene
    nextt = context.active_object.madtracks.nextt
    if nextt:
        bpy.data.groups['Tracks'].objects.unlink(nextt)


class MadObjectProperties(bpy.types.PropertyGroup):
    # Common
    descriptor = StringProperty(
        name = "Descriptor",
        default = "",
        description = "Filename of the object's descriptor"
    )
    ldo = StringProperty(
        name = "LDO",
        default = "",
        description = "Filename of the object's LDO"
    )
    is_instance = BoolProperty(
        name = "Is Instance",
        default = False,
        description = "Object is imported as an instance"
    )
    is_collectible = BoolProperty(
        name = "Is Collectible",
        default = False,
        description = "Object is a collectible"
    )
    is_world = BoolProperty(
        name = "Is World",
        default = False,
        description = "Object is part of the world"
    )

    # Descriptor
    physics = BoolProperty(
        name = "Physics",
        default = False,
        description = "Object has physics"
    )
    animate = BoolProperty(
        name = "Animation",
        default = False,
        description = "Object has animation"
    )
    mass = IntProperty(
        name = "Mass",
        default = 0,
        description = "Object mass"
    )
    cast_shadows = BoolProperty(
        name = "Cast car shadows",
        default = False,
        description = "Cast in-game shadows used by cars"
    )

    # Trackparts
    is_trackpart = BoolProperty(
        name = "Is Trackpart",
        default = False,
        description = "Object is a trackpart"
    )
    invert = BoolProperty(
        name = "Invert",
        default = False,
        description = "Trackpart is inverted"
    )
    nextt = PointerProperty(
        type = bpy.types.Object,
        name = "Next",
        description = "Next trackpart in the sequence",
        update = nextt_update_func
    )
    dummy_pos = FloatVectorProperty(
        name = "Dummy position",
        default = (0.0, 0.0, 0.0),
        description = "Dummy position"
    )
    dummy_rot1 = FloatVectorProperty(
        name = "Dummy rotation matrix row 1",
        size = 4,
        default = (1.0, 0.0, 0.0, 0.0),
        description = "First row of dummy rotation matrix"
    )
    dummy_rot2 = FloatVectorProperty(
        name = "Dummy rotation matrix row 2",
        size = 4,
        default = (0.0, 1.0, 0.0, 0.0),
        description = "Second row of dummy rotation matrix"
    )
    dummy_rot3 = FloatVectorProperty(
        name = "Dummy rotation matrix row 3",
        size = 4,
        default = (0.0, 0.0, 1.0, 0.0),
        description = "Third row of dummy rotation matrix"
    )
    dummy_rot4 = FloatVectorProperty(
        name = "Dummy rotation matrix row 4",
        size = 4,
        default = (0.0, 0.0, 0.0, 1.0),
        description = "Fourth row of dummy rotation matrix"
    )

    # AI Nodes
    roadwidth = FloatProperty(
        name = "Road Width",
        default = 0.0,
        min = 0.0,
        description = "Exceeding this lateral distance from the node makes the car out of bounds (...Lost ?)"
    )
    motivboost = FloatProperty(
        name = "Motiv Boost",
        default = 0.0,
        min = 0.0,
        description = "30 is a good value to encourage AI to use a boost"
    )
    speedexpected = FloatProperty(
        name = "Speed Expected",
        default = 0.0,
        min = 0.0,
        description = "10 is a good value to encourage AI to slow down"
    )
