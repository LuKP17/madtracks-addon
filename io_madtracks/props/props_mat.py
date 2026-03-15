# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    props_mat
Purpose: Provides the material data class for Mad Tracks materials.

Description:
Materials in Mad Tracks have toggleable properties and custom shader properties.

"""

import bpy

from bpy.props import (
    BoolProperty,
)
from ..common import *

class MadMaterialProperties(bpy.types.PropertyGroup):
    has_rgba = BoolProperty(
        name = "RGBA",
        default = False,
        description = "Use diffuse color and alpha of the material")
    has_brightness = BoolProperty(
        name = "Brightness",
        default = False,
        description = "Use diffuse intensity of the material")
