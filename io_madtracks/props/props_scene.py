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

def check_ref(self, context):
    scene = context.scene
    obj = scene.madtracks.trackpart_ref
    if obj and not obj.madtracks.is_trackpart:
        scene.madtracks.trackpart_ref = None
        msg_box("Object isn't a trackpart", icon='ERROR')


class MadSceneProperties(bpy.types.PropertyGroup):
    # General
    madtracks_dir = StringProperty(
        name = "Mad Tracks Directory",
        default = "",
        description = "Extracted Mad Tracks data.zip folder path. Needed for import/export"
    )

    # Import/Export
    ini_io_type = EnumProperty(
        name = "INI Type",
        description = "Select the INI category",
        items = INI_CATEGORIES
    )
    as_instance = BoolProperty(
        name = "As Level Instance",
        default = False,
        description = "Import objects in a lightmappable way, reusable by level importer and convenient for level editing"
    )
    reuse_data = BoolProperty(
        name = "Reuse Blender data",
        default = False,
        description = "Reuse already imported data to save on resources and improve performance"
    )
    ldo_debug_info = BoolProperty(
        name = "LDO Debug Info",
        default = False,
        description = "Enable all LDO debug info"
    )
    level_import_raceline = BoolProperty(
        name = "Import Raceline",
        default = True,
        description = "Import trackparts and collectibles"
    )
    level_import_lightmap = BoolProperty(
        name = "Cross-import Lightmap",
        default = False,
        description = "For visualization only. Import the associated LDL file at the same time, matching the instances from both files"
    )
    level_use_checkpoint_names = BoolProperty(
        name = "Use Checkpoint Names",
        default = True,
        description = "Checkpoints order is based on their names in alphanumerical order instead of creation date"
    )

    # Trackpart editor
    trackpart_category = EnumProperty(
        name = "Category",
        description = "Choose a trackpart category",
        items = TRACKPART_CATEGORIES
    )
    trackpart_control = EnumProperty(
        name = "Control",
        description = "Choose a trackpart",
        items = TRACKPARTS_CONTROL
    )
    trackpart_medium = EnumProperty(
        name = "Medium",
        description = "Choose a trackpart",
        items = TRACKPARTS_MEDIUM
    )
    trackpart_small = EnumProperty(
        name = "Small",
        description = "Choose a trackpart",
        items = TRACKPARTS_SMALL
    )
    trackpart_wood = EnumProperty(
        name = "Wood",
        description = "Choose a trackpart",
        items = TRACKPARTS_WOOD
    )
    trackpart_ref = PointerProperty(
        type = bpy.types.Object,
        name = "Trackpart Reference",
        description = "Reference an existing trackpart in the scene",
        update = check_ref
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

    # Object properties
    edit_props = BoolProperty(
        name = "Edit Object Properties",
        default = False,
        description = "Display all object properties and allow editing for object export"
    )
