# Copyright (C) 2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

import bpy

class MadTracksLightmapPanel(bpy.types.Panel):
    """
    Tool panel in the left sidebar of the viewport for generating a lightmap.
    """
    bl_label = "Lightmap"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Mad Tracks"

    def draw_header(self, context):
        self.layout.label("", icon="FILE_IMAGE")

    def draw(self, context):
        props = context.scene.madtracks
        layout = self.layout

        # TODO remove the lightmap object selection operators once I have a pattern to detect them automatically
        # layout.label("Lightmap Objects:")
        # row = layout.row()
        # row.operator("lightmap.mark_sel", text="Mark", icon="ZOOMIN")
        # row.operator("lightmap.unmark_sel", text="Unmark", icon="ZOOMOUT")
        # row = layout.row()
        # row.operator("lightmap.select", text="Select Marked")
        # layout.label("Lightmap Generation:")
        row = layout.row()
        row.prop(props, "lightmap_bitdepth", text="Bit Depth")
        row = layout.row()
        row.operator("lightmap.setup_scene", text="Setup Scene", icon="SCENE_DATA")
        row = layout.row()
        row.operator("lightmap.bake_preview", text="Bake Lightmap", icon="RENDER_STILL")
