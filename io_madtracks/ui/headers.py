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


class MadTracksIOToolPanel(bpy.types.Panel):
    """
    Tool panel in the left sidebar of the viewport for performing
    various operations
    """
    bl_label = "Import/Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Mad Tracks"
    bl_options = {"HIDE_HEADER"}

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
        row.operator("export_scene.madtracks", text="Export", icon="EXPORT")
