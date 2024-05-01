# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: headers.py
# Original author: Marvin Thiel
#
# File first modified on 02/27/24
# Author: Lucas Pottier
#-----------------------------------------------------------------------------

import bpy
from ..common import *

# class EditModeHeader(bpy.types.Panel):
#     """
#     Fixes the tab at the top in edit mode.
#     """
#     bl_label = "Edit Mode Header"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "TOOLS"
#     bl_context = "mesh_edit"
#     bl_category = "Re-Volt"
#     bl_options = {"HIDE_HEADER"}

#     def draw(self, context):
#         props = context.scene.revolt
#         row  = self.layout.row()
#         # PRM/NCP toggle
#         row.prop(props, "face_edit_mode", expand=True)


class MadTracksIOToolPanel(bpy.types.Panel):
    """
    Tool panel in the left sidebar of the viewport for performing
    various operations
    """
    bl_label = "Import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Mad Tracks"
    
    def draw_header(self, context):
        self.layout.label("", icon="IMPORT")

    def draw(self, context):
        # i/o buttons
        props = context.scene.madtracks

        self.layout.label("Mad Tracks Data Directory:")
        box = self.layout.box()
        box.prop(props, "madtracks_dir", text="")
        if props.madtracks_dir == "":
            box.label("No directory specified", icon="ERROR")

        row = self.layout.row(align=True)
        row.operator("import_scene.madtracks", text="Import", icon="IMPORT")
        # row.operator("export_scene.revolt", text="Export", icon="EXPORT")
        # row.operator("export_scene.revolt_redo", text="", icon="FILE_REFRESH")