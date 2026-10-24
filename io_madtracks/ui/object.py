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
    bl_label = "Mad Tracks Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        objprops = obj.madtracks
        sceneprops = context.scene.madtracks

        # level instance properties, naturally shows if there was an impact after editing object props
        layout.label("Level Instance Properties:")
        box = layout.box()
        # read-only properties
        box.label("Descriptor: {}".format(objprops.descriptor))
        box.label("LDO: {}".format(objprops.ldo))
        # special instance properties
        if objprops.is_trackpart:
            box.label("Trackpart Properties", icon="PARTICLE_PATH")
            box.prop(objprops, "nextt")
        if objprops.is_ainode:
            box.label("AI Node Properties", icon="PARTICLE_POINT")
            box.prop(objprops, "roadwidth")
            box.prop(objprops, "motivboost")
            box.prop(objprops, "speedexpected")
            box.prop(objprops, "nextt")
            box.prop(objprops, "prev")
        # all properties for object editing
        col = layout.column()
        col.prop(sceneprops, "edit_props")
        if sceneprops.edit_props:
            box = layout.box()
            box.prop(objprops, "descriptor")
            box.prop(objprops, "ldo")
            if objprops.descriptor and obj.type == 'LAMP':
                box.label("Light Properties", icon="LAMP_SPOT")
                box.prop(objprops, "cast_shadows")
