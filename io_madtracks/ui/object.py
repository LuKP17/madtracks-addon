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
                box.prop(objprops, "num_trackpart")

        # # NCP properties
        # box = layout.box()
        # box.label("NCP Properties:")
        # row = box.row()
        # row.prop(objprops, "ignore_ncp")

        # # Debug properties
        # if objprops.is_bcube:
        #     box = layout.box()
        #     box.label("BigCube Properties:")
        #     row = box.row()
        #     row.prop(objprops, "bcube_mesh_indices")
        
        # # Instance properties
        # box = layout.box()
        # box.label("Instance Properties:")
        # box.prop(objprops, "is_instance")

        # if objprops.is_instance:
        #     row = box.row(align=True)
        #     row.prop(context.object.revolt, "fin_model_rgb", text="Model Color")
        #     row.prop(context.object.revolt, "fin_col", text="")
        #     row = box.row(align=True)
        #     row.prop(context.object.revolt, "fin_env", text="EnvColor")
        #     row.prop(context.object.revolt, "fin_envcol", text="")
        #     box.prop(context.object.revolt, "fin_hide")
        #     box.prop(context.object.revolt, "fin_no_mirror")
        #     box.prop(context.object.revolt, "fin_no_lights")
        #     box.prop(context.object.revolt, "fin_no_cam_coll")
        #     box.prop(context.object.revolt, "fin_no_obj_coll")
        #     box.prop(context.object.revolt, "fin_priority")
        #     box.prop(context.object.revolt, "fin_lod_bias")

        # # Mirror properties
        # box = layout.box()
        # box.label("Mirror Properties:")
        # box.prop(objprops, "is_mirror_plane")

        # # InstanceHull properties
        # box = layout.box()
        # box.label("Hull Properties:")
        # box.prop(objprops, "is_hull_convex")
        # box.prop(objprops, "is_hull_sphere")