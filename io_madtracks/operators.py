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
from . import ai
from . import lightmap

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

        if props.madtracks_dir == "":
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
        
        # ensure correct scene ligthing
        scene.display_settings.display_device = "None"
        scene.view_settings.use_curve_mapping = True
        scene.view_settings.curve_mapping.white_level = (0.9, 0.9, 0.9)

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
        
        if props.madtracks_dir == "":
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

class ButtonTrackpartDropdown(bpy.types.Operator):
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


class ButtonTrackpartReference(bpy.types.Operator):
    bl_idname = "trackpart.add_existing"
    bl_label = "Add Existing"
    bl_description = "Add the trackpart from the reference field to a new sequence if no trackpart is selected, or appends it to the last selected one otherwise"

    def execute(self, context):
        scene = context.scene
        trackpart.add_user(scene, trackpart.from_reference(scene))

        # Gets any encountered errors
        errors = get_errors()
        if "uccess" not in errors:
            msg_box(
                "{}\n".format(errors),
                icon="ERROR"
            )
        context.window.cursor_set("DEFAULT")
        return {"FINISHED"}


"""
AI PATHS EDITOR ------------------------------------------------------------------------
"""

class ButtonAIAddNode(bpy.types.Operator):
    bl_idname = "ai.add_node"
    bl_label = "Add Node"
    bl_description = "Add an AI node with properties"

    def execute(self, context):
        scene = context.scene

        # call method shared with level importer
        ai.add_node(scene)

        # move node to 3D cursor
        obj = scene.objects.active
        obj.location = bpy.context.scene.cursor_location
        return {"FINISHED"}


class ButtonAILinkNodes(bpy.types.Operator):
    bl_idname = "ai.link_nodes"
    bl_label = "Link Nodes"
    bl_description = "Rename AI nodes following edges naming convention for export"

    def execute(self, context):
        scene = context.scene
        props = scene.madtracks

        ai.link_nodes(props.ai_startnode)

        # Gets any encountered errors
        errors = get_errors()
        if "uccess" not in errors:
            msg_box(
                "{}\n".format(errors),
                icon="ERROR"
            )
        context.window.cursor_set("DEFAULT")
        return {"FINISHED"}


# class ButtonAIResetNodes(bpy.types.Operator):
#     bl_idname = "ai.reset_nodes"
#     bl_label = "Reset Nodes"
#     bl_description = "Rename AI nodes to remove edges naming convention"

#     def execute(self, context):
#         scene = context.scene
#         props = scene.madtracks

#         ai.reset_nodes()
#         return {"FINISHED"}


"""
LIGHTMAP EDITOR ------------------------------------------------------------------------
"""

class ButtonLightmapSetup(bpy.types.Operator):
    bl_idname = "lightmap.setup_scene"
    bl_label = "Setup Lightmap Scene"
    bl_description = "DESTRUCTIVE scene setup, merges selected objects into a lightmap object and exports the LDL file"

    def execute(self, context):
        scene = context.scene
       
        lightmap.setup_scene(scene)

        # Gets any encountered errors
        errors = get_errors()
        if "uccess" not in errors:
            msg_box(
                "{}\n".format(errors),
                icon="ERROR"
            )
        context.window.cursor_set("DEFAULT")
        return {"FINISHED"}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout.row()
        row.label("Merging and unwrapping may take a few minutes.", icon="INFO")


class ButtonLightmapBake(bpy.types.Operator):
    bl_idname = "lightmap.bake_preview"
    bl_label = "Bake Lightmap"
    bl_description = "Generates the lightmap image and applies it to the lightmap object for preview"

    def execute(self, context):
        scene = context.scene
        lightmap.bake_preview(scene)

        # Gets any encountered errors
        errors = get_errors()
        if "uccess" not in errors:
            msg_box(
                "{}\n".format(errors),
                icon="ERROR"
            )
        context.window.cursor_set("DEFAULT")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        row = self.layout.row()
        row.label("Baking may take a few minutes.", icon="INFO")
