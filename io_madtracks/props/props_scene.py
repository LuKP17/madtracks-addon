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
    PointerProperty,
)

from ..trackpart import *

# needed to allow exporting files outside of the extracted game folder
INI_CATEGORIES = (
    ("Level", "Level instances", "", 0),
    ("Desciptor", "Object descriptor", "", 1),
)

class MadSceneProperties(bpy.types.PropertyGroup):
    madtracks_dir = StringProperty(
        name = "Mad Tracks Directory",
        default = "",
        description = "Extracted Mad Tracks data.zip folder path"
    )

    instance_mode = BoolProperty(
        name = "Instance mode",
        default = False,
        description = "Import only necessary properties for level editing"
    )

    ldo_debug_info = BoolProperty(
        name = "LDO Debug Info",
        default = False,
        description = "Enable all LDO debug info"
    )

    ini_io_type = EnumProperty(
        name = "INI Type",
        description = "Select the INI category",
        items = INI_CATEGORIES
    )

    level_import_raceline = BoolProperty(
        name = "Import Raceline",
        default = True,
        description = "Import trackparts and collectibles"
    )
    level_import_lightmap = BoolProperty(
        name = "Import Lightmap",
        default = False,
        description = "Turn off level lights and import the level lightmap"
    )
    level_export_use_groups = BoolProperty(
        name = "Use Trackpart Groups",
        default = True,
        description = "Export trackpart sequences following \"Tracks\" group objects in alphabetical order (recommended)"
    )
    lightmap_debug_info = BoolProperty(
        name = "Lightmap Debug Info",
        default = False,
        description = "Enable lightmap instances debug info"
    )

    # Trackpart editor
    trackpart_category = EnumProperty(
        name = "Category",
        description = "Choose a trackpart category",
        items = TRACKPART_CATEGORIES
    )
    trackpart_small = EnumProperty(
        name = "Small",
        description = "Choose a trackpart",
        items = TRACKPARTS_SMALL
    )
    trackpart_medium = EnumProperty(
        name = "Medium",
        description = "Choose a trackpart",
        items = TRACKPARTS_MEDIUM
    )
    trackpart_golf = EnumProperty(
        name = "Golf",
        description = "Choose a trackpart",
        items = TRACKPARTS_GOLF
    )
    trackpart_ref = PointerProperty(
        type = bpy.types.Object,
        name = "Trackpart Reference",
        description = "Reference an existing trackpart in the scene"
    )

    # AI paths editor
    ai_startnode = PointerProperty(
        type = bpy.types.Object,
        name = "Start Node",
        description = "Start node for level export"
    )

    # Lightmap editor
    lightmap_bitdepth = IntProperty(
        name = "Bit depth",
        description = "Most lightmaps use 16-bit depth, with some using 32-bit",
        default = 16,
        min = 16,
        max = 32,
        step = 16 # not supported apparently
    )
