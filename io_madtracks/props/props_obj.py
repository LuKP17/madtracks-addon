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
    StringProperty,
    FloatVectorProperty,
)
from ..common import *

class MadObjectProperties(bpy.types.PropertyGroup):
    # Common
    is_instance = BoolProperty(
        name = "Is Instance",
        default = False,
        description = "Object is a level instance"
    )
    descriptor = StringProperty(
        name = "Descriptor",
        default = "",
        description = "Filename of the object's descriptor"
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
