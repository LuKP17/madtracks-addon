# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: instances.py
# Original author: Marvin Thiel
#
# File first modified on 03/23/24
# Author: Lucas Pottier
#-----------------------------------------------------------------------------

"""
Name:    trackparts
Purpose: Trackpart position and rotation.

Description:
TODO Explain why its needed. Used for level import and export.
Also used for level editing to greatly improve the experience.

"""

import bpy
from ..common import *

class MadTracksTrackpartsPanel(bpy.types.Panel):
    bl_label = "Trackparts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Mad Tracks"

    # @classmethod
    # def poll(self, context):
    #     return context.object and len(context.selected_objects) >= 1 and context.object.type == "MESH"

    def draw_header(self, context):
        self.layout.label("", icon="OUTLINER_OB_SURFACE")

    def draw(self, context):
        props = context.scene.madtracks
        layout = self.layout

        layout.label("Active Trackpart:")
        row = layout.row()
        row.prop(props, "trackpart_category", text="")
        row = layout.row()
        if props.trackpart_category == "S":
            row.prop(props, "trackpart_small", text="")
        elif props.trackpart_category == "M":
            row.prop(props, "trackpart_medium", text="")
        else:
            row.prop(props, "trackpart_golf", text="")

        layout.label("Active Sequence:")
        row = layout.row()
        row.operator("trackpart_sequence.append")
        row = layout.row()
        row.operator("trackpart_sequence.remove")
        row = layout.row()
        row.operator("trackpart_sequence.new")
