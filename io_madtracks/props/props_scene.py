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

from ..common import *

TRACKPART_CATEGORIES = (
    # ("X", "Control", "Starts, checkpoints, finishes", ?),
    ("S", "Small", "Small trackparts", 0),
    ("M", "Medium", "Medium trackparts", 1),
    # ("W", "Wood", "Wood trackparts", ?),
    # ("B", "Bobsleigh", "Bobsleigh trackparts", ?),
    # ("C", "Croquet", "Croquet trackparts", ?),
    ("G", "Golf", "Golf trackparts", 2),
    # ("V", "Vent", "Vent trackparts", ?),
    # ("A", "Antartica", "Antartica trackparts", ?),
)
TRACKPARTS_SMALL = (
    ("S_bleu_amorce_15_in.ini", "Amorce 15 In", "Small amorce in", 0),
    ("S_bleu_amorce_15_out.ini", "Amorce 15 Out", "Small amorce out", 1),
    ("S_neon_rail_50.ini", "Straight Neon 50", "Small neon straight", 2),
    ("S_neon_virage_45_left.ini", "Left 45", "Small left turn", 3),
    ("S_neon_virage_45_right.ini", "Right 45", "Small right turn", 4),
    ("S_raye_rampe_30_up.ini", "Up 30", "Small up ramp", 5),
    ("S_raye_rampe_30_down.ini", "Down 30", "Small down ramp", 6),
    ("S_gris_to_M_50.ini", "S to M 50", "Small to medium transition", 7),
    ("S_raye_looping.ini", "Looping", "Small looping", 8),
)
TRACKPARTS_MEDIUM = (
    ("M_gris_amorce_05_in.ini", "Amorce 05 In", "Medium amorce in", 0),
    ("M_gris_amorce_15_in.ini", "Amorce 15 In", "Medium amorce in", 1),
    ("M_gris_amorce_15_out.ini", "Amorce 15 Out", "Medium amorce out", 2),
    ("M_gris_amorce_30_in.ini", "Amorce 30 In", "Medium amorce in", 3),
    ("M_gris_amorce_30_out.ini", "Amorce 30 Out", "Medium amorce out", 4),
    ("M_gris_rail_15.ini", "Straight 15", "Medium straight", 5),
    ("M_gris_rail_50.ini", "Straight 50", "Medium straight", 6),
    ("M_neon_rail_50.ini", "Straight Neon 50", "Medium neon straight", 7),
    ("M_gris_virage_45_left.ini", "Left 45", "Medium left turn", 8),
    ("M_gris_virage_45_right.ini", "Right 45", "Medium right turn", 9),
    ("M_gris_rampe_30_up.ini", "Up 30", "Medium up ramp", 10),
    ("M_gris_rampe_30_down.ini", "Down 30", "Medium down ramp", 11),
    ("M_none_start.ini", "Start", "Medium start", 12),
    ("M_none_checkpoint.ini", "Checkpoint", "Medium checkpoint", 13),
    ("M_none_finish_50.ini", "Finish", "Medium finish", 14),
    ("M_gris_to_S_50.ini", "M to S 50", "Medium to small transition", 15),
)
TRACKPARTS_GOLF = (
    ("G_none_checkpoint.ini", "Checkpoint", "Golf checkpoint", 0),
    ("G_none_finish.ini", "Finish", "Golf finish", 1),
)

class MadSceneProperties(bpy.types.PropertyGroup):
    settings_madtracks_dir = StringProperty(
        name = "Mad Tracks Directory",
        default = "",
        description = "Manually define a folder containing extracted Mad Tracks data.zip files.\nNeeded for import/export"
    )

    ldo_separate_atomics = BoolProperty(
        name = "Separate Atomics",
        default = True,
        description = "Split atomics into separate objects"
    )
    ldo_debug_info = BoolProperty(
        name = "LDO Debug Info",
        default = False,
        description = "Enable all LDO debug info"
    )

    level_import_trackparts = BoolProperty(
        name = "Import Trackparts",
        default = True,
        description = "Import the trackparts contained in the level"
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
    sequence_ID = IntProperty(
        name = "Sequence ID",
        default = -1,
        min = -1,
        description = "ID for a trackpart sequence. Valid values start at 0"
    )
