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
import imp

from . import (
    common,
    operators,
)

from .props import (
    props_obj,
    props_scene,
)

from .ui import (
    headers,
    trackpart_editor,
    object,
)

# Reloads potentially changed modules on reload (F8 in Blender)
imp.reload(common)
imp.reload(operators)
imp.reload(props_obj)
imp.reload(props_scene)
imp.reload(headers)
imp.reload(trackpart_editor)
imp.reload(object)

# Reloaded here because it's used in a class which is instanced here
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


# Makes common variables and classes directly accessible
from .common import *
from .props.props_obj import *
from .props.props_scene import *

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

    bpy.types.INFO_MT_file_import.prepend(menu_func_import)
    bpy.types.INFO_MT_file_export.prepend(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.madtracks
    del bpy.types.Object.madtracks

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
