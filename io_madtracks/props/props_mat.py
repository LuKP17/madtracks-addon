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
    FloatVectorProperty,
    BoolProperty,
)
from ..common import *

class MadMaterialProperties(bpy.types.PropertyGroup):
    has_rgba = BoolProperty(
        name = "Use RGBA",
        default = False,
        description = "Use diffuse color and alpha of the material"
    )
    has_brightness = BoolProperty(
        name = "Use Brightness",
        default = False,
        description = "Tied to material light emission"
    )
    rgba_save = FloatVectorProperty(
        name = "RGBA save",
        size = 4,
        default = (1.0, 1.0, 1.0, 1.0),
        description = "Save of diffuse color and alpha to restore after baking the lightmap"
    )
