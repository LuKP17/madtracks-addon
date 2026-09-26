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
            box.prop(objprops, "ldo")
            box.prop(objprops, "is_collectible")
            box.prop(objprops, "is_world")
            if objprops.descriptor:
                box = layout.box()
                box.label("Object:")
                box.prop(objprops, "animate")
                box.prop(objprops, "physics")
                if objprops.physics:
                    box.prop(objprops, "mass")
                if obj.type == 'LAMP':
                    box.prop(objprops, "cast_shadows")
            if objprops.is_trackpart:
                box = layout.box()
                box.label("Trackpart:")
                box.prop(objprops, "invert")
            if len(obj.users_group) > 0 and bpy.data.groups.find("Paths") != -1 and obj.users_group[0] == bpy.data.groups['Paths']:
                box = layout.box()
                box.label("AI Node:")
                box.prop(objprops, "roadwidth")
                box.prop(objprops, "motivboost")
                box.prop(objprops, "speedexpected")
            if objprops.is_trackpart or (len(obj.users_group) > 0 and bpy.data.groups.find("Paths") != -1 and obj.users_group[0] == bpy.data.groups['Paths']):
                box.prop(objprops, "nextt")
