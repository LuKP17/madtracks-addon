# Copyright (C) 2024  Lucas Pottier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: __init__.py
# Original author: Marvin Thiel
#
# File first modified on 02/27/24
# Author: Lucas Pottier
#-----------------------------------------------------------------------------


"""
Name:    init
Purpose: Init file for the Blender Add-On

"""

import bpy
# import os
# import os.path
import imp
# from bpy.app.handlers import persistent  # For the scene update handler

from . import (
    common,
#     layers,
    operators,
#     texanim,
#     tools,
)

from .props import (
#     props_mesh,
    props_obj,
    props_scene,
)

from .ui import (
#   menu_add,
    headers,
#     faceprops,
    trackparts,
#     light,
#     hull,
    object,
#     scene,
#     vertex,
#     texanim,
#     helpers,
#     settings,
)

# # Reloads potentially changed modules on reload (F8 in Blender)
imp.reload(common)
# imp.reload(layers)
# imp.reload(props_mesh)
imp.reload(props_obj)
imp.reload(props_scene)
imp.reload(operators)
# imp.reload(texanim)
# imp.reload(tools)

# Reloads ui
# imp.reload(menu_add)
imp.reload(headers)
# imp.reload(faceprops)
imp.reload(trackparts)
# imp.reload(light)
# imp.reload(hull)
imp.reload(object)
# imp.reload(scene)
# imp.reload(vertex)
# imp.reload(texanim)
# imp.reload(helpers)
# imp.reload(settings)

# Reloaded here because it's used in a class which is instanced here
# if "fin_in" in locals():
#     imp.reload(fin_in)
# if "fin_out" in locals():
#     imp.reload(fin_out)
# if "hul_in" in locals():
#     imp.reload(hul_in)
# if "hul_out" in locals():
#     imp.reload(hul_out)
if "img_in" in locals():
    imp.reload(img_in)
if "ldo_in" in locals():
    imp.reload(ldo_in)
if "object_in" in locals():
    imp.reload(object_in)
if "level_in" in locals():
    imp.reload(level_in)
if "level_out" in locals():
    imp.reload(level_out)
if "trackpart" in locals():
    imp.reload(trackpart)
# if "prm_out" in locals():
#     imp.reload(prm_out)
# if "ncp_in" in locals():
#     imp.reload(ncp_in)
# if "ncp_out" in locals():
#     imp.reload(ncp_out)
# if "parameters_in" in locals():
#     imp.reload(parameters_in)
# if "ta_csv_in" in locals():
#     imp.reload(ta_csv_in)
# if "ta_csv_out" in locals():
#     imp.reload(ta_csv_out)
# if "w_in" in locals():
#     imp.reload(w_in)
# if "w_out" in locals():
#     imp.reload(w_out)
# if "rim_in" in locals():
#     imp.reload(rim_in)
# if "rim_out" in locals():
#     imp.reload(rim_out)


# Makes common variables and classes directly accessible
from .common import *
# from .props.props_mesh import *
from .props.props_obj import *
from .props.props_scene import *
# from .texanim import *

bl_info = {
"name": "Mad Tracks",
"author": "Lucas Pottier, original author: Marvin Thiel",
"version": (19, 12, 30),
"blender": (2, 79, 0),
"location": "File > Import-Export",
"description": "Import and export Mad Tracks file formats.",
"wiki_url": "https://github.com/LuKP17/madtracks-addon",
"tracker_url": "https://github.com/LuKP17/madtracks-addon/issues",
"support": 'COMMUNITY',
"category": "Import-Export"
}

# @persistent
# def edit_object_change_handler(scene):
#     """Makes the edit mode bmesh available for use in GUI panels."""
#     obj = scene.objects.active
#     if obj is None:
#         return
#     # Adds an instance of the edit mode mesh to the global dict
#     if obj.mode == 'EDIT' and obj.type == 'MESH':
#         bm = dic.setdefault(obj.name, bmesh.from_edit_mesh(obj.data))
#         return

#     dic.clear()


def menu_func_import(self, context):
    """Import function for the user interface."""
    self.layout.operator("import_scene.madtracks", text="Mad Tracks")


def menu_func_export(self, context):
    """Export function for the user interface."""
    self.layout.operator("export_scene.madtracks", text="Mad Tracks")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.madtracks = bpy.props.PointerProperty(
        type=MadSceneProperties
    )
    bpy.types.Object.madtracks = bpy.props.PointerProperty(
        type=MadObjectProperties
    )
    # bpy.types.Mesh.revolt = bpy.props.PointerProperty(
    #     type=RVMeshProperties
    # )

    bpy.types.INFO_MT_file_import.prepend(menu_func_import)
    bpy.types.INFO_MT_file_export.prepend(menu_func_export)
    # bpy.types.INFO_MT_add.append(menu_add.menu_func_add)

    # bpy.app.handlers.scene_update_pre.append(edit_object_change_handler)
    # bpy.app.handlers.scene_update_post.append(edit_object_change_handler)


def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.madtracks
    del bpy.types.Object.madtracks
    # del bpy.types.Mesh.revolt

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    # bpy.types.INFO_MT_add.remove(menu_add.menu_func_add)

if __name__ == "__main__":
    register()
