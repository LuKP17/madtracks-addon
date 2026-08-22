# Copyright (C) 2024-2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original author: Marvin Thiel
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

from . import descriptor_in
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
            if DESCRIPTOR_PATH.split(os.path.sep)[-2] in self.filepath:
                frmt = FORMAT_DESCRIPTOR
            elif LEVEL_PATH.split(os.path.sep)[-2] in self.filepath:
                frmt = FORMAT_LEVEL_INI

        if frmt == FORMAT_UNK:
            msg_box("Unknown format.")
            return {'CANCELLED'}
        
        elif frmt == FORMAT_LDO:
            from . import ldo_in
            ldo_in.import_file(self.filepath, scene)

            # Disable debug info if user then imports a level for instance.
            # If user wants debug info when importing a level, check the LDO import option before selecting a level.
            props.ldo_debug_info = False
        
        elif frmt == FORMAT_DESCRIPTOR:
            if not descriptor_in.import_file(self.filepath, scene):
                msg_box("Descriptor not supported.")
                return {'CANCELLED'}
        
        elif frmt == FORMAT_LEVEL_INI:
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

        # Enable backface culling for a closer in-game preview
        bpy.context.space_data.show_backface_culling = True

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
                if DESCRIPTOR_PATH.split(os.path.sep)[-2] in space.params.directory:
                    frmt = FORMAT_DESCRIPTOR
                elif LEVEL_PATH.split(os.path.sep)[-2] in space.params.directory:
                    frmt = FORMAT_LEVEL_INI
            layout.label("Import {}:".format(FORMATS[frmt]))

        if frmt == FORMAT_LDO:
            box = layout.box()
            box.prop(props, "ldo_debug_info")
        
        if frmt == FORMAT_LEVEL_INI:
            box = layout.box()
            box.prop(props, "level_import_raceline")
            box.prop(props, "level_import_lightmap")
            box.prop(props, "lightmap_debug_info")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExportMad(bpy.types.Operator):
    """
    Export Operator for all file types
    """
    bl_idname = "export_scene.madtracks"
    bl_label = "Export Mad Tracks Files"
    bl_description = "Export Mad Tracks game files"

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

        dprint("Exporting {}".format(self.filepath))
        
        if frmt == FORMAT_INI:
            # for now don't differentiate between .ini files
            frmt = FORMAT_LEVEL_INI

        if frmt == FORMAT_UNK:
            msg_box("Unknown format.")
            return {'CANCELLED'}
        
        else:
            # Turns off undo for better performance
            use_global_undo = bpy.context.user_preferences.edit.use_global_undo
            bpy.context.user_preferences.edit.use_global_undo = False

            if bpy.ops.object.mode_set.poll():
                bpy.ops.object.mode_set(mode="OBJECT")

            if frmt == FORMAT_LDO:
                from . import ldo_out
                ldo_out.export_file(self.filepath, scene)

                # Disable debug info if user then exports a level for instance.
                props.ldo_debug_info = False

            elif frmt == FORMAT_LEVEL_INI:
                from . import level_out
                level_out.export_file(self.filepath, scene)
            
            else:
                msg_box("Format not yet supported: {}".format(FORMATS[frmt]))

            # Re-enables undo
            bpy.context.user_preferences.edit.use_global_undo = use_global_undo

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
            "Export to {} done in {:.3f} seconds.\n{}\n".format(
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
        frmt = get_format(space.params.filename)

        if frmt == -1 and not space.params.filename == "":
            if frmt == FORMAT_INI:
                # for now don't differentiate between .ini files
                frmt = FORMAT_LEVEL_INI
            layout.label("Format not supported", icon="ERROR")
        elif frmt != -1:
            layout.label("Export {}:".format(FORMATS[frmt]))
            
        if frmt == FORMAT_LDO:
            box = layout.box()
            box.prop(props, "ldo_debug_info")
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


"""
TRACKPART EDITOR ------------------------------------------------------------------------
"""

class ButtonNewTrackpartSequence(bpy.types.Operator):
    bl_idname = "trackpart.add_dropdown"
    bl_label = "Add"
    bl_description = "Add the trackpart from the dropdown menu to a new sequence if no trackpart is selected, or appends it to the last selected one otherwise"

    def execute(self, context):
        scene = context.scene
        trackpart.add_user(scene, trackpart.from_dropdown(scene))

        # Gets any encountered errors
        errors = get_errors()
        if "uccess" not in errors:
            msg_box(
                "{}\n".format(errors),
                icon="ERROR"
            )
        context.window.cursor_set("DEFAULT")
        return {"FINISHED"}
