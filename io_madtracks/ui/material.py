# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

import bpy
from ..common import *

class MadTracksMaterialPanel(bpy.types.Panel):
    """
    Panel in the Material Properties tab to view material properties.
    """
    bl_label = "Mad Tracks Material Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {"HIDE_HEADER"}


    def draw(self, context):
        layout = self.layout
        mat = context.object.active_material
        matprops = mat.madtracks

        layout.label("Mad Tracks Properties")

        box = layout.box()
        box.prop(matprops, "has_rgba")
        box.prop(matprops, "has_brightness")
