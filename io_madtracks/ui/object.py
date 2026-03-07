# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: object.py
# Original author: Marvin Thiel
#
# File first modified on 03/17/24
# Author: Lucas Pottier
#-----------------------------------------------------------------------------

import bpy
from ..common import *

class MadTracksObjectPanel(bpy.types.Panel):
    """
    Panel in the Object Properties tab to view object properties.
    """
    bl_label = "Mad Tracks Object Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {"HIDE_HEADER"}


    def draw(self, context):
        layout = self.layout
        obj = context.object
        objprops = obj.madtracks

        layout.label("Mad Tracks Properties")

        # Debug properties
        if DEBUG:
            box = layout.box()
            box.prop(objprops, "descriptor")
        if objprops.is_trackpart:
            box = layout.box()
            box.label("Trackpart:")
            box.prop(objprops, "num_sequence")
            if DEBUG:
                box.prop(objprops, "num_trackpart")
                box.prop(objprops, "invert")
