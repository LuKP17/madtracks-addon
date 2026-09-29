# Copyright (C) 2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

import bpy

class MadTracksAIPanel(bpy.types.Panel):
    """
    Tool panel in the left sidebar of the viewport for AI paths.
    """
    bl_label = "AI Paths"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Mad Tracks"

    def draw_header(self, context):
        self.layout.label("", icon="PARTICLE_POINT")

    def draw(self, context):
        props = context.scene.madtracks
        layout = self.layout

        row = layout.row()
        row.label("Start Node:")
        row = layout.row()
        row.prop(props, "ai_startnode", text="")
        row = layout.row()
        row.operator("ai.add_node", text="Add Node", icon="ZOOMIN")
        row = layout.row()
        row.operator("ai.link_nodes", text="Link Nodes", icon="LINKED")
        # row = layout.row()
        # row.operator("ai.draw_paths", text="Draw Paths", icon="CURVE_PATH")
