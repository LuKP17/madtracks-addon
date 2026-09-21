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

    # enable instance mode
    instance_mode_save = props.instance_mode
    props.instance_mode = True

    with open(filepath, 'w') as fini:
        # empty line like the original levels
        fini.write("\n")

        if props.level_export_use_groups:
            # export trackparts from group last
            for i in range(len(scene.objects), 0, -1):
                obj = scene.objects[i-1]
                if obj.madtracks.is_world:
                    # skip world elements
                    continue
                if obj.madtracks.is_trackpart:
                    continue
                export_instance(fini, obj, obj.location, obj.matrix_world)
            # export trackparts sequences in the alphabetical group order (for checkpoints ordering)
            if "Tracks" in bpy.data.groups.keys():
                for name in sorted(bpy.data.groups['Tracks'].objects.keys()):
                    obj = bpy.data.objects[name]
                    export_instance(fini, obj, obj.location, obj.matrix_world)
                    if obj.madtracks.is_trackpart and obj.madtracks.nextt:
                        # loop thru trackpart sequence
                        while obj.madtracks.nextt:
                            if scene.objects.find(obj.madtracks.nextt.name) == -1:
                                # trackpart points to a deleted object
                                obj.madtracks.nextt = None
                                break
                            obj = obj.madtracks.nextt
                            # object location/rotation calculated by the game engine
                            export_instance(fini, obj)
        else:
            # loop thru objects by creation order
            in_sequence = False
            for i in range(len(scene.objects), 0, -1):
                obj = scene.objects[i-1]
                if obj.madtracks.is_world:
                    # skip world elements
                    continue
                if in_sequence:
                    # object location/rotation calculated by the game engine
                    export_instance(fini, obj)
                else:
                    export_instance(fini, obj, obj.location, obj.matrix_world)
                if obj.madtracks.is_trackpart:
                    if obj.madtracks.nextt:
                        in_sequence = True
                    else:
                        in_sequence = False
    
    # reinstate old instance mode
    props.instance_mode = instance_mode_save


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
        fini.write("DirectionAT = " + float_format(rot[0][0]) + "," + float_format(rot[0][1]) + "," + float_format(rot[0][2]) + "\n")
        fini.write("DirectionUp = " + float_format(rot[1][0]) + "," + float_format(rot[1][1]) + "," + float_format(rot[1][2]) + "\n")
    fini.write("Filename = \"" + name + "\"\n\n")

    print("Exported {}".format(obj.name))
