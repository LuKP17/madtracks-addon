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

##############################################################################
# CURRENT STATE OF THE PROJECT
#
# - defined new bpy type "MadMeshProperties" containing a material number
#   to assign to each face of a mesh
#
# - enabled Mad Tracks 3D view panel in object mode and import function
#
# - implemented .ldo import, good enough for now
#   MAD TRACKS ENGINE ISSUE:
#   Only one UV coordinate is assigned per vertex,
#   instead of assigning a list of UV coordinates per polygon.
#   So the vertex needs to be duplicated if it's shared by 2 polygons mapped to
#   different regions of the texture.
#   => it doubles the vertex count for every model in the game
#   => it makes Blender's "Lightmap Pack" impossible to use, since it considers that UV-mapping
#   is assigned per polygon and gives vertices multiple UV coordinates.
#   Meaning I need to find another solution for .ldl file export!
#
# - started implementing level .ini import
#   MAD TRACKS FILE FORMAT ISSUE:
#   Level .ini files do not seem to respect the file specification,
#   as they contain duplicate sections and their order matter because of trackparts.
#   => it makes Python's configparser and other .ini readers impossible to use, since they
#   consider that sections are unique and their order is irrelevant.
#   Meaning I need to write a dedicated level .ini reader!
#
# - started implementing a trackpart editor
#
##################################################################################
#   CLEANER CODE! MORE SMALL FUNCTIONS! MORE DEBUG PRINTING! MORE COMMENTS!
##################################################################################
# TODO
#
# - 
#
# - fix trackpart_in.update_anchor()
# >> fix anchor calculations when making a turn while being banked (apply rotation offsets in the object's local frame)
# >> use Blender operators? How to compute the axis parameter?
# bpy.ops.transform.rotate(value=0.528511, axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
# bpy.ops.transform.rotate(value=-0.782533, axis=(0, -0.504248, 0.863559), constraint_axis=(False, False, True), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
# >> create rotate_vector() utility function, used by update_anchor but also by export tools in the future
#
# - keep populating trackparts dictionary, offsets are known by selecting the endpoint vertex and looking at the object's LOCAL location
# - better code: New and Append operators look remarkably similar...
# - when we remove the last and only trackpart of the sequence, delete the group as well, otherwise the next new sequence will have a huge number
#
# - point out in the installation part of the repo that the madtracks_dir variable needs to be set
#   to be able to import/export files.
##############################################################################

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
if "trackpart_in" in locals():
    imp.reload(trackpart_in)
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


# def menu_func_export(self, context):
#     """Export function for the user interface."""
#     self.layout.operator("export_scene.revolt", text="Re-Volt")


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
    # bpy.types.INFO_MT_file_export.prepend(menu_func_export)
    # bpy.types.INFO_MT_add.append(menu_add.menu_func_add)

    # bpy.app.handlers.scene_update_pre.append(edit_object_change_handler)
    # bpy.app.handlers.scene_update_post.append(edit_object_change_handler)


def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.madtracks
    del bpy.types.Object.madtracks
    # del bpy.types.Mesh.revolt

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    # bpy.types.INFO_MT_file_export.remove(menu_func_export)
    # bpy.types.INFO_MT_add.remove(menu_add.menu_func_add)

if __name__ == "__main__":
    register()
