# Copyright (C) 2024-2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    level_out
Purpose: Exports level .ini files.

Description:
Level files contain LDO level instances from Gfx\models\Geometry and
Object level instances from Bin\Descriptors.
This module reads all Blender objects in a scene to export them as instances in a level file.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(trackpart)

import bpy

from . import common
from . import trackpart

from .common import *
from .trackpart import *


def export_file(filepath, scene):
    """
    Exports a level from Blender objects by writing the level .ini file.
    """
    props = scene.madtracks

    with open(filepath, 'w') as fini:
        # empty line like the original levels
        fini.write("\n")
        # loop thru objects by creation order
        checkpoint_names = []
        for i in range(len(scene.objects), 0, -1):
            obj = scene.objects[i-1]
            if obj.madtracks.is_world:
                # skip world elements
                continue
            if obj.parent:
                # skip, can be pieces of a breakable object for example
                continue
            if obj.madtracks.object_type == "checkpoint" and props.level_use_checkpoint_names:
                # export in alphanumerical order instead
                checkpoint_names.append(obj.name)
                continue
            if obj.madtracks.prev:
                # skip, is part of a sequence
                continue
            export_instance(fini, obj, obj.location, obj.matrix_world)
            if obj.madtracks.is_trackpart:
                # loop thru trackpart sequence, protect from infinite loops in any case
                head = obj
                while obj.madtracks.nextt:
                    obj = obj.madtracks.nextt
                    if obj == head:
                        set_error('exporting trackpart sequences', "Infinite loop detected")
                        return
                    # object location/rotation calculated by the game engine
                    export_instance(fini, obj)

        if props.level_use_checkpoint_names:
            # export checkpoints in alphanumerical order
            for name in sorted(checkpoint_names):
                obj = scene.objects[name]
                export_instance(fini, obj, obj.location, obj.matrix_world)


def export_instance(fini, obj, location=None, matrix_world=None):
    """
    Writes a Blender object as a level instance in the level file.
    Handles trackpart sequences, which are Object instances without position/rotation parameters,
    since they are automatically computed by Mad Tracks' engine.
    """
    if not obj.madtracks.descriptor and not obj.madtracks.ldo:
        return

    if obj.madtracks.descriptor:
        name = obj.madtracks.descriptor
    else:
        name = "geometry/" + obj.madtracks.ldo

    fini.write("[" + name + "]\n")
    if location:
        pos = to_madtracks_axis(location)
        if obj.madtracks.invert:
            # undo inverted translation
            obj_pos = np.array(obj.location)
            obj_rot = np.array(obj.rotation_euler.to_matrix())
            dummy_pos = obj.madtracks.dummy_pos
            dummy_pos = np.matmul(dummy_pos, np.transpose(obj_rot))
            pos = to_madtracks_axis(np.add(obj_pos, dummy_pos))
        fini.write("Position = " + float_format(pos[0]) + "," + float_format(pos[1]) + "," + float_format(pos[2]) + "\n")
    if matrix_world:
        if obj.type in ['CAMERA', 'LAMP']:
            # temporarily undo additional rotation done during level import
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.ops.transform.rotate(value=-1.5708, constraint_axis=(True, False, False), constraint_orientation='LOCAL')
            rot = to_madtracks_matrix(matrix_world)
            bpy.ops.transform.rotate(value=1.5708, constraint_axis=(True, False, False), constraint_orientation='LOCAL')
            obj.select = False
        else:
            rot = to_madtracks_matrix(matrix_world)
            if obj.madtracks.invert:
                # temporarily undo inverted rotation
                dummy_rotmat = mathutils.Matrix([obj.madtracks.dummy_rot1, obj.madtracks.dummy_rot2, obj.madtracks.dummy_rot3, obj.madtracks.dummy_rot4])
                dummy_roteuler = dummy_rotmat.to_euler()
                if dummy_roteuler[2] > 0:
                    # left turn
                    obj.rotation_euler.rotate_axis("Z", -ANGLE_180 + dummy_roteuler[2])
                    rot = to_madtracks_matrix(obj.rotation_euler.to_matrix())
                    obj.rotation_euler.rotate_axis("Z", ANGLE_180 - dummy_roteuler[2])
                else:
                    # right turn
                    obj.rotation_euler.rotate_axis("Z", ANGLE_180 - dummy_roteuler[2])
                    rot = to_madtracks_matrix(obj.rotation_euler.to_matrix())
                    obj.rotation_euler.rotate_axis("Z", -ANGLE_180 + dummy_roteuler[2])
        fini.write("DirectionAT = " + float_format(rot[0][0]) + "," + float_format(rot[0][1]) + "," + float_format(rot[0][2]) + "\n")
        fini.write("DirectionUp = " + float_format(rot[1][0]) + "," + float_format(rot[1][1]) + "," + float_format(rot[1][2]) + "\n")
    fini.write("Filename = \"" + name + "\"\n\n")

    print("Exported {}".format(obj.name))
