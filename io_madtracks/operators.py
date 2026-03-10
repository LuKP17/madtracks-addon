# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: operators.py
# Original author: Marvin Thiel
#
# File first modified on 02/28/24
# Author: Lucas Pottier
#-----------------------------------------------------------------------------

"""
Name:    operators
Purpose: Provides operators for importing and exporting and other buttons.

Description:
These operators are used for importing and exporting files, as well as
providing the functions behind the UI buttons.

"""

import bpy
import time

from . import object_in
from . import trackpart

from .common import *

"""
IMPORT AND EXPORT -------------------------------------------------------------
"""

class ImportMad(bpy.types.Operator):
    """
    Import Operator for all file types
    """
    bl_idname = "import_scene.madtracks"
    bl_label = "Import Mad Tracks Files"
    bl_description = "Import Mad Tracks game files"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        scene = context.scene
        props = scene.madtracks

        frmt = get_format(self.filepath)

        if props.settings_madtracks_dir == "":
            msg_box("No data directory specified.")
            return {'CANCELLED'}

        start_time = time.time()

        context.window.cursor_set("WAIT")

        dprint("Importing {}".format(self.filepath))

        if frmt == FORMAT_INI:
            # differentiate between .ini files based on filepath
            if DESCRIPTOR_PATH.split("\\")[-2] in self.filepath:
                frmt = FORMAT_OBJ_INI
            elif LEVEL_PATH.split("\\")[-2] in self.filepath:
                frmt = FORMAT_LVL_INI

        if frmt == FORMAT_UNK:
            msg_box("Unknown format.")
            return {'CANCELLED'}
        
        elif frmt == FORMAT_LDO:
            from . import ldo_in
            ldo_in.import_file(self.filepath, scene)

            # Disable debug info if user then imports a level for instance.
            # If user wants debug info when importing a level, check the LDO import option before selecting a level.
            props.ldo_debug_info = False
        
        elif frmt == FORMAT_OBJ_INI:
            if object_in.import_file(self.filepath, scene) == None:
                msg_box("Unsupported type of Object.")
                return {'CANCELLED'}
        
        elif frmt == FORMAT_LVL_INI:
            from . import level_in
            level_in.import_file(self.filepath, scene)
        
        else:
            msg_box("Format not yet supported: {}".format(FORMATS[frmt]))
            return {'CANCELLED'}

        end_time = time.time() - start_time

        # Gets any encountered errors
        errors = get_errors()

        # Defines the icon depending on the errors
        if errors == "Successfully completed.":
            ico = "FILE_TICK"
        else:
            ico = "ERROR"

        # Displays a message box with the import results
        msg_box(
            "Import of {} done in {:.3f} seconds.\n{}\n".format(
                FORMATS[frmt], end_time, errors),
            icon=ico
        )

        context.window.cursor_set("DEFAULT")

        return {"FINISHED"}

    def draw(self, context):
        props = context.scene.madtracks
        layout = self.layout
        space = context.space_data

        # Gets the format from the file path
        frmt = get_format(space.params.directory + space.params.filename)

        if frmt == -1 and not space.params.filename == "":
            layout.label("Format not supported", icon="ERROR")
        elif frmt != -1:
            if frmt == FORMAT_INI:
                # differentiate between .ini files based on filepath
                if DESCRIPTOR_PATH.split("\\")[-2] in space.params.directory:
                    frmt = FORMAT_OBJ_INI
                elif LEVEL_PATH.split("\\")[-2] in space.params.directory:
                    frmt = FORMAT_LVL_INI
            layout.label("Import {}:".format(FORMATS[frmt]))

        if frmt == FORMAT_LDO:
            box = layout.box()
            box.prop(props, "ldo_separate_atomics")
            box.prop(props, "ldo_debug_info")
        
        if frmt == FORMAT_LVL_INI:
            box = layout.box()
            box.prop(props, "level_import_trackparts")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExportMad(bpy.types.Operator):
    bl_idname = "export_scene.madtracks"
    bl_label = "Export Mad Tracks Files"
    bl_description = "Export Mad Tracks game files"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        scene = context.scene
        props = context.scene.madtracks

        start_time = time.time()
        context.window.cursor_set("WAIT")

        if self.filepath == "":
            msg_box("File not specified.", "ERROR")
            return {"FINISHED"}

        # Gets the format from the file path
        frmt = get_format(self.filepath)

        if frmt == FORMAT_UNK:
            msg_box("Not supported for export.", "INFO")
            return {"FINISHED"}
        else:
            # Turns off undo for better performance
            use_global_undo = bpy.context.user_preferences.edit.use_global_undo
            bpy.context.user_preferences.edit.use_global_undo = False

            if bpy.ops.object.mode_set.poll():
                bpy.ops.object.mode_set(mode="OBJECT")

            if frmt == FORMAT_INI:
                # for now don't differentiate between .ini files
                frmt = FORMAT_LVL_INI

            if frmt == FORMAT_LVL_INI:
                from . import level_out
                level_out.export_file(self.filepath, scene)
            
            else:
                msg_box("Format not yet supported: {}".format(FORMATS[frmt]))

            # Re-enables undo
            bpy.context.user_preferences.edit.use_global_undo = use_global_undo

        context.window.cursor_set("DEFAULT")

        # Gets any encountered errors
        errors = get_errors()

        # Defines the icon depending on the errors
        if errors == "Successfully completed.":
            ico = "FILE_TICK"
        else:
            ico = "ERROR"

        # Displays a message box with the import results
        end_time = time.time() - start_time
        msg_box(
            "Export to {} done in {:.3f} seconds.\n{}\n".format(
                FORMATS[frmt], end_time, errors),
            icon=ico
        )

        return {"FINISHED"}

    def draw(self, context):
        props = context.scene.madtracks
        layout = self.layout
        space = context.space_data

        # Gets the format from the file path
        frmt = get_format(space.params.filename)

        if frmt == -1 and not space.params.filename == "":
            layout.label("Format not supported", icon="ERROR")
        elif frmt != -1:
            layout.label("Export {}:".format(FORMATS[frmt]))
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


"""
TRACKPART EDITOR ------------------------------------------------------------------------
"""

class ButtonNewTrackpartSequence(bpy.types.Operator):
    bl_idname = "trackpart_sequence.new"
    bl_label = "New"
    bl_description = "Append the active trackpart to a new trackpart sequence"

    def execute(self, context):
        scene = context.scene
        trackpart.append_to_new_sequence(scene)
        # Enables texture mode after import
        # if props.enable_tex_mode:
        enable_any_tex_mode(context)
        return {"FINISHED"}


class ButtonAppendTrackpartSequence(bpy.types.Operator):
    bl_idname = "trackpart_sequence.append"
    bl_label = "Append"
    bl_description = "Append the active trackpart to the active trackpart sequence"

    def execute(self, context):
        scene = context.scene
        sequence = context.selected_objects[0].users_group[0]
        trackpart.append_to_sequence(scene, sequence.name, len(context.selected_objects))
        # Enables texture mode after import
        # if props.enable_tex_mode:
        enable_any_tex_mode(context)
        return {"FINISHED"}


class ButtonRemoveTrackpartSequence(bpy.types.Operator):
    bl_idname = "trackpart_sequence.remove"
    bl_label = "Remove Last"
    bl_description = "Remove the last trackpart of the active trackpart sequence"

    def execute(self, context):
        # get sequence group while trackparts are selected
        sequence = context.selected_objects[0].users_group[0]
        # get and remove the last trackpart of the sequence
        last = trackpart.get_trackpart(sequence.name, len(context.selected_objects) - 1)
        bpy.data.objects.remove(bpy.data.objects[last.name], do_unlink=True)
        # if the sequence is now empty, delete the Blender group
        if len(context.selected_objects) == 0:
            bpy.data.groups.remove(bpy.data.groups[sequence.name])

        # Enables texture mode after import
        # if props.enable_tex_mode:
        enable_any_tex_mode(context)
        return {"FINISHED"}


class ButtonSetSequenceID(bpy.types.Operator):
    bl_idname = "trackpart_sequence.setid"
    bl_label = "Set ID"
    bl_description = "Set the sequence ID for all trackparts in the active sequence"

    def execute(self, context):
        scene = context.scene
        # get sequence group while trackparts are selected
        sequence = context.selected_objects[0].users_group[0]
        # set sequence_number attribute of all trackparts of the sequence
        trackpart.set_sequence_ID(scene, sequence.name, len(context.selected_objects))

        return {"FINISHED"}
