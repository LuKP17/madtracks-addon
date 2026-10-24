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

        start_time = time.time()
        context.window.cursor_set("WAIT")

        dprint("Importing {}".format(self.filepath))

        bpy.ops.object.select_all(action='DESELECT')

        if frmt == FORMAT_INI:
            # INI category determined by scene property
            if props.ini_io_type == "Level":
                frmt = FORMAT_LEVEL_INI
            else:
                frmt = FORMAT_DESCRIPTOR

        if frmt == FORMAT_UNK:
            msg_box("Unknown format.")
            return {'CANCELLED'}
        
        elif frmt == FORMAT_LDO:
            from . import ldo_in
            ldo_in.import_file(self.filepath, scene)
            # for convenience
            scene.objects.active.location = bpy.context.scene.cursor_location
            bpy.ops.object.select_all(action='DESELECT')
            scene.objects.active.select = True

            # Disable debug info if user then imports a level for instance.
            # If user wants debug info when importing a level, check the LDO import option before selecting a level.
            props.ldo_debug_info = False

        elif frmt == FORMAT_DESCRIPTOR:
            from . import descriptor_in
            if not descriptor_in.import_file(self.filepath, scene):
                msg_box("Descriptor not supported.")
                return {'CANCELLED'}
            # for convenience
            scene.objects.active.location = bpy.context.scene.cursor_location
            bpy.ops.object.select_all(action='DESELECT')
            scene.objects.active.select = True
        
        elif frmt == FORMAT_LEVEL_INI:
            from . import level_in
            level_in.import_file(self.filepath, scene)
        
        elif frmt == FORMAT_DAM:
            from . import dam_in
            dam_in.import_file(self.filepath, scene)
        
        elif frmt == FORMAT_GRA:
            from . import ai_in
            ai_in.import_file(self.filepath, scene)
        
        elif frmt == FORMAT_LDL:
            from . import ldl_in
            ldl_in.import_file(self.filepath, scene)
        
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

        # Visibility in viewport
        bpy.context.space_data.clip_end = 7000
        bpy.context.space_data.show_backface_culling = True
        scene.world.light_settings.use_environment_light = True

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
            return
        elif frmt != -1:
            if frmt == FORMAT_INI:
                # INI category determined by scene property
                box = layout.box()
                box.prop(props, "ini_io_type")
                if props.ini_io_type == "Level":
                    frmt = FORMAT_LEVEL_INI
                else:
                    frmt = FORMAT_DESCRIPTOR
            layout.label("Import {}:".format(FORMATS[frmt]))

        if frmt == FORMAT_LDO:
            box = layout.box()
            box.prop(props, "as_instance")
            box.prop(props, "reuse_data")
            box.prop(props, "ldo_debug_info")
        
        elif frmt == FORMAT_DESCRIPTOR:
            box = layout.box()
            box.prop(props, "as_instance")
            box.prop(props, "reuse_data")
        
        elif frmt == FORMAT_LEVEL_INI:
            box = layout.box()
            box.prop(props, "level_import_raceline")
            box.prop(props, "level_import_lightmap")
        
        else:
            box = layout.box()
            box.label("No options available.")

    def invoke(self, context, event):
        if context.scene.madtracks.madtracks_dir == "":
            msg_box("No data directory specified.", icon="ERROR")
        else:
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
            # INI category determined by scene property
            if props.ini_io_type == "Level":
                frmt = FORMAT_LEVEL_INI
            else:
                frmt = FORMAT_DESCRIPTOR

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
            
            elif frmt == FORMAT_DESCRIPTOR:
                from . import descriptor_out
                descriptor_out.export_file(self.filepath, context)

            elif frmt == FORMAT_LEVEL_INI:
                from . import level_out
                level_out.export_file(self.filepath, scene)
            
            elif frmt == FORMAT_GRA:
                from . import ai_out
                ai_out.export_file(self.filepath, scene)
            
            else:
                msg_box("Format not yet supported: {}".format(FORMATS[frmt]))
                return {'CANCELLED'}

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
            layout.label("Format not supported", icon="ERROR")
            return
        elif frmt != -1:
            if frmt == FORMAT_INI:
                # INI category determined by scene property
                box = layout.box()
                box.prop(props, "ini_io_type")
                if props.ini_io_type == "Level":
                    frmt = FORMAT_LEVEL_INI
                else:
                    frmt = FORMAT_DESCRIPTOR
            layout.label("Export {}:".format(FORMATS[frmt]))
            
        if frmt == FORMAT_LDO:
            box = layout.box()
            box.prop(props, "ldo_debug_info")
        
        if frmt == FORMAT_LEVEL_INI:
            box = layout.box()
            box.prop(props, "level_use_checkpoint_names")
        
        else:
            box = layout.box()
            box.label("No options available.")
    
    def invoke(self, context, event):
        if context.scene.madtracks.madtracks_dir == "":
            msg_box("No data directory specified.", icon="ERROR")
        else:
            context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


"""
TRACKPART EDITOR ------------------------------------------------------------------------
"""

class ButtonTrackpartAddDropdown(bpy.types.Operator):
    bl_idname = "trackpart.add_dropdown"
    bl_label = "Add Dropdown"
    bl_description = "Import the dropdown trackpart at the 3D cursor or link it after the trackpart selected in the 3D view"

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
    bl_description = "Import the referenced trackpart at the 3D cursor or link it after the trackpart selected in the 3D view"

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


class ButtonTrackpartSelectLinked(bpy.types.Operator):
    bl_idname = "trackpart.select_linked"
    bl_label = "Select Linked"
    bl_description = "Extend the selection to the end of the tracks"

    def execute(self, context):
        scene = context.scene
        trackpart.select_linked(scene, context.selected_objects)

        # Gets any encountered errors
        errors = get_errors()
        if "uccess" not in errors:
            msg_box(
                "{}\n".format(errors),
                icon="ERROR"
            )
        context.window.cursor_set("DEFAULT")
        return {"FINISHED"}


class ButtonTrackpartRecalculate(bpy.types.Operator):
    bl_idname = "trackpart.recalculate"
    bl_label = "Recalculate All"
    bl_description = "Clean up trackpart links and recalculate all trackparts placement"

    def execute(self, context):
        scene = context.scene
        trackpart.recalculate(scene)

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
    bl_description = "Add an AI node at the 3D cursor and link it to the selected node in the 3D view if there is one"

    def execute(self, context):
        scene = context.scene

        prev = None
        if len(context.selected_objects) == 1:
            prev = context.selected_objects[0]
        # call method shared with level importer
        ai.add_node(scene)
        # move node to 3D cursor
        obj = scene.objects.active
        obj.location = bpy.context.scene.cursor_location
        # link it to selection
        if prev and prev.madtracks.is_ainode:
            prev.madtracks.nextt = obj
        obj.select = True
        return {"FINISHED"}


class ButtonAIRenameNodes(bpy.types.Operator):
    bl_idname = "ai.rename_nodes"
    bl_label = "Rename Nodes"
    bl_description = "Rename all AI nodes with their IDs. Done automatically when exporting"

    def execute(self, context):
        scene = context.scene
        props = scene.madtracks

        ai.rename_nodes(scene)

        # Gets any encountered errors
        errors = get_errors()
        if "uccess" not in errors:
            msg_box(
                "{}\n".format(errors),
                icon="ERROR"
            )
        context.window.cursor_set("DEFAULT")
        return {"FINISHED"}


class ButtonAIDrawPaths(bpy.types.Operator):
    bl_idname = "ai.draw_paths"
    bl_label = "Draw Paths"
    bl_description = "Create a path object following links between nodes for edges visualization"

    def execute(self, context):
        scene = context.scene
        props = scene.madtracks

        ai.draw_paths(scene, context)
        
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
LIGHTMAP EDITOR ------------------------------------------------------------------------
"""

class ButtonLightmapBake(bpy.types.Operator):
    bl_idname = "lightmap.bake_preview"
    bl_label = "Bake Lightmap"
    bl_description = "Generate the lightmap image and apply it to the scene for preview"

    def execute(self, context):
        scene = context.scene
        
        obj_idx = scene.objects.find("Lightmesh")
        if obj_idx == -1:
            lightmap.setup_scene(scene)
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
        row.label("Baking may take a minute.", icon="INFO")
