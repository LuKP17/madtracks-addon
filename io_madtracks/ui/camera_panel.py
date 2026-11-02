# Copyright (C) 2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Author: Lucas Pottier
#-----------------------------------------------------------------------------

import bpy

class MadTracksCameraPanel(bpy.types.Panel):
    """
    Tool panel in the left sidebar of the viewport for editing spectator cameras.
    """
    bl_label = "Cameras"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Mad Tracks"

    def draw_header(self, context):
        self.layout.label("", icon="CAMERA_DATA")

    def draw(self, context):
        props = context.scene.madtracks
        layout = self.layout

        col = layout.column()
        if "Spectator_camera" in bpy.data.cameras.keys():
            col.operator("camera.reset_spec_cams", text="Reset Cameras", icon='FILE_REFRESH')
            col.operator("camera.export_spec_cams", text="Export Cameras", icon='SCRIPTPLUGINS')
        else:
            col.operator("camera.create_spec_cams", text="Create Cameras", icon='ZOOMIN')
