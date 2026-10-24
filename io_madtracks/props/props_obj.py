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
    # objects can either be trackparts or AI nodes
    obj = context.active_object
    nextt = obj.madtracks.nextt
    if not nextt:
        return
    if nextt == obj:
        obj.madtracks.nextt = None
        msg_box("Can't link an object with itself", icon='ERROR')
        return
    if obj.type == 'MESH' and not nextt.madtracks.is_trackpart:
        # trackparts always point to other trackparts
        obj.madtracks.nextt = None
        msg_box("Object isn't a trackpart", icon='ERROR')
        return
    if obj.type == 'EMPTY' and not nextt.madtracks.is_ainode:
        # AI nodes always point to other nodes
        obj.madtracks.nextt = None
        msg_box("Object isn't an AI node", icon='ERROR')
        return
    # check for sequence loop
    iterator = nextt
    while iterator:
        if iterator == obj:
            obj.madtracks.nextt = None
            msg_box("Sequence loops are not allowed", icon='ERROR')
            return
        iterator = iterator.madtracks.nextt
    if obj.madtracks.is_trackpart:
        # check for multiple links
        for scene_obj in scene.objects:
            if scene_obj != obj and scene_obj.madtracks.nextt == nextt:
                obj.madtracks.nextt = None
                msg_box("Trackpart is already linked", icon='ERROR')
                return
        # update other end of the link
        nextt.madtracks.prev = obj


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
    object_type = StringProperty(
        name = "Type",
        default = "",
        description = "Game object type"
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
        name = "Has Physics",
        default = False,
        description = "Object has physics"
    )
    animate = BoolProperty(
        name = "Is Animated",
        default = False,
        description = "Object is animated"
    )
    cast_shadows = BoolProperty(
        name = "Casts in-game shadows",
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
        name = "Is Inverted",
        default = False,
        description = "Trackpart is inverted"
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
    is_ainode = BoolProperty(
        name = "Is AI Node",
        default = False,
        description = "Object is an AI node"
    )
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

    nextt = PointerProperty(
        type = bpy.types.Object,
        name = "Next",
        description = "Next object in the sequence",
        update = nextt_update_func
    )
    # previous object in the sequence, but adapt name and tooltip for AI nodes since it's hidden otherwise
    prev = PointerProperty(
        type = bpy.types.Object,
        name = "Root",
        description = "Root node of branching path"
    )
