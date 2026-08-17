# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: props_scene.py
# Original author: Marvin Thiel
#
# File first modified on 02/27/24
# Author: Lucas Pottier
#-----------------------------------------------------------------------------

"""
Name:    props_scene
Purpose: Provides the scene data class for Mad Tracks meshes.

Description:
The scene properties are misused for storing settings as well as 
level information.

"""

import bpy

from bpy.props import (
    BoolProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)

from ..trackpart import *

class MadSceneProperties(bpy.types.PropertyGroup):
    settings_madtracks_dir = StringProperty(
        name = "Mad Tracks Directory",
        default = "",
        description = "Manually define a folder containing extracted Mad Tracks data.zip files.\nNeeded for import/export"
    )

    instance_mode = BoolProperty(
        name = "Instance Mode",
        default = False,
        description = "Import files in a simplified way, marginally useful when importing levels."
    )

    ldo_debug_info = BoolProperty(
        name = "LDO Debug Info",
        default = False,
        description = "Enable all LDO debug info"
    )

    level_import_raceline = BoolProperty(
        name = "Import Raceline",
        default = True,
        description = "Import trackparts, pick-ups and other collectibles contained in the level"
    )
    level_import_lightmap = BoolProperty(
        name = "Import Lightmap",
        default = True,
        description = "Import the level lightmap (worse performance)"
    )
    lightmap_debug_info = BoolProperty(
        name = "Lightmap Debug Info",
        default = False,
        description = "Enable lightmap instances debug info"
    )

    # Trackpart editor
    # PROPERTIES CAN TAKE A "update" PARAMETERS WHICH IS THE FUNCTION CALLED WHEN THE VALUE CHANGES
    # CAN BE USEFUL
    trackpart_category = EnumProperty(
        name = "Category",
        description = "Select the trackpart category",
        items = TRACKPART_CATEGORIES
    )
    trackpart_small = EnumProperty(
        name = "Small",
        description = "Select the trackpart",
        items = TRACKPARTS_SMALL
    )
    trackpart_medium = EnumProperty(
        name = "Medium",
        description = "Select the trackpart",
        items = TRACKPARTS_MEDIUM
    )
    trackpart_golf = EnumProperty(
        name = "Golf",
        description = "Select the trackpart",
        items = TRACKPARTS_GOLF
    )
