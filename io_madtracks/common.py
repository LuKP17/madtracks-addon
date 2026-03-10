# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: common.py
# Original author: Marvin Thiel
#
# File first modified on 02/27/24
# Author: Lucas Pottier
#-----------------------------------------------------------------------------

"""
Name:    common
Purpose: Providing variables and functions available for all modules

Description:
Contains values that are specific to Mad Tracks, functions for converting units
and helper functions for Blender. 

"""

import bpy
import bmesh
import os

# Relative paths from the user's Mad Tracks data folder
LDO_PATH = "\\Gfx\\models\\Geometry\\"
TEXTURE_PATH = "\\Graph\\maps\\High\\"
DESCRIPTOR_PATH = "\\Bin\\Descriptors\\"
LEVEL_PATH = "\\Bin\\Levels\\"

# Global dictionaries
global ERRORS
ERRORS = {}  # Dictionary that holds error messages

# If True, more debug messages will be printed
# TODO disable for release version
DEBUG = True

SCALE = 1


def dprint(*str):
    """ Debug print: only prints if debug is enabled """
    if DEBUG:
        print(*str)


"""
Supported File Formats
"""
FORMAT_UNK = -1
FORMAT_LDO = 0
FORMAT_INI = 2
FORMAT_OBJ_INI = 3
FORMAT_LVL_INI = 4

FORMATS = {
    FORMAT_LDO: "LDO (.ldo)",
    FORMAT_INI: "Unsupported (.ini)",
    FORMAT_OBJ_INI: "Object (.ini)",
    FORMAT_LVL_INI: "Level (.ini)",
}


"""
Conversion functions for Mad Tracks structures.
Axes are saved differently and many indices are saved in a different order.
"""

def to_blender_axis(vec):
    return [-vec[0], vec[2], vec[1]]


def to_blender_coord(vec):
    return [-vec[0] * SCALE, vec[2] * SCALE, vec[1] * SCALE]


def to_blender_scale(num):
    return num * SCALE


def to_madtracks_axis(vec):
    return [-vec[0], vec[2], vec[1]]


def to_madtracks_coord(vec):
    return [-vec[0] / SCALE, vec[2] / SCALE, vec[1] / SCALE]


def to_madtracks_scale(num):
    return num / SCALE


class DialogOperator(bpy.types.Operator):
    bl_idname = "madtracks.dialog"
    bl_label = "Mad Tracks Add-On Notification"

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        global dialog_message
        global dialog_icon
        row = self.layout.row()
        row.label("", icon=dialog_icon)
        column = row.column()
        for line in str.split(dialog_message, "\n"):
            column.label(line)


def msg_box(message, icon="INFO"):
    global dialog_message
    global dialog_icon
    print(message)
    dialog_message = message
    dialog_icon = icon
    bpy.ops.madtracks.dialog("INVOKE_DEFAULT")


def get_errors():
    global ERRORS
    if ERRORS:
        errors = "The following errors have been encountered:\n\n"
        for error in ERRORS:
            errors += "~ ERROR while {}:\n     {}\n\n".format(error, ERRORS[error])
        errors += "Check the console for more information."
    else:
        errors = "Successfully completed."

    # Clears the error messages
    ERRORS = {}

    return errors


def redraw_3d():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
                break


def enable_any_tex_mode(context):
    """ Enables the preferred texture mode according to settings """
    enable_texture_mode()
    # props = context.scene.revolt
    # if props.prefer_tex_solid_mode:
    #     enable_textured_solid_mode()
    # else:
    #     enable_texture_mode()


def enable_texture_mode():
    """ Enables textured shading in the viewport """
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.viewport_shade = "TEXTURED"
    return


"""
Non-Blender helper functions
"""

def get_format(fstr):
    """
    Gets the format by the ending and returns an int
    """
    fstr = fstr.lower()  # support uppercase letters
    if os.sep in fstr:
        fstr = fstr.split(os.sep)[-1]
    try:
        fname, ext = fstr.split(".", 1)
    except:
        fname, ext = ("", "")

    if ext == "ldo":
        return FORMAT_LDO
    elif ext == "ini":
        return FORMAT_INI
    else:
        return FORMAT_UNK


def float_format(value):
    return '{:f}'.format(value)
