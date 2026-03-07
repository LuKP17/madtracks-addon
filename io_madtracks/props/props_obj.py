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
)
from ..common import *

class MadObjectProperties(bpy.types.PropertyGroup):
    # Common
    descriptor = StringProperty(
        name = "Descriptor",
        default = "",
        description = "Filename of the object's descriptor"
    )

    # Trackparts
    is_trackpart = BoolProperty(
        name = "Is Trackpart",
        default = False,
        description = "Is the object a trackpart"
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
        description = "Is the trackpart inverted"
    )
