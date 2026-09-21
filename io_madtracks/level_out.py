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

    with open_insensitive(filepath, 'w') as fini:
        # empty line like the original levels
        fini.write("\n")

        if props.level_export_use_groups:
            # export objects from groups last
            for i in range(len(bpy.data.scenes[0].objects), 0, -1):
                obj = bpy.data.scenes[0].objects[i-1]
                if obj.madtracks.is_world:
                    # skip world elements
                    continue
                if len(obj.users_group) > 0:
                    # skip group objects
                    continue
                export_instance(fini, obj, obj.location, obj.matrix_world) 
            for group in bpy.data.groups:
                for name in sorted(group.objects.keys()):
                    obj = bpy.data.objects[name]
                    if obj.madtracks.is_trackpart and obj.madtracks.previous:
                        # skip sequence trackpart
                        continue
                    export_instance(fini, obj, obj.location, obj.matrix_world)
                    if obj.madtracks.is_trackpart and obj.madtracks.nextt:
                        # loop thru trackpart sequence
                        while obj.madtracks.nextt:
                            obj = obj.madtracks.nextt
                            export_instance(fini, obj)
        else:
            # loop thru objects by creation order
            for i in range(len(bpy.data.scenes[0].objects), 0, -1):
                obj = bpy.data.scenes[0].objects[i-1]
                if obj.madtracks.is_world:
                    # skip world elements
                    continue
                if obj.madtracks.is_trackpart and obj.madtracks.previous:
                    # skip sequence trackpart
                    continue
                export_instance(fini, obj, obj.location, obj.matrix_world)
                if obj.madtracks.is_trackpart and obj.madtracks.nextt:
                    # loop thru trackpart sequence
                    while obj.madtracks.nextt:
                        obj = obj.madtracks.nextt
                        export_instance(fini, obj)
    
    with open_insensitive(filepath.replace(".ini", ".gra"), 'w') as fgra:
        # empty line like the original levels
        fgra.write("\n")
        start_node = props.ai_startnode
        # export nodes
        if not start_node.parent and start_node.children[0]:
            export_ai_node(fgra, start_node)
            node = start_node.children[0]
            while node:
                export_ai_node(fgra, node)
                node = node.children[0] if node.children else None
        else:
            set_error('linking nodes', "Invalid start node")

        # export edges
        export_ai_edges(fgra, start_node)
        node = start_node.children[0]
        while node:
            export_ai_edges(fgra, node)
            node = node.children[0] if node.children else None
    
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


def export_ai_node(fgra, node):
    """ Writes a Blender empty object as a node in the level AI file. """
    fgra.write("[Node]\n")
    fgra.write("ID = " + node.name.split('-', 1)[0] + "\n")
    position = to_madtracks_axis(node.location)
    fgra.write("Position = " + float_format(position[0]) + "," + float_format(position[1]) + "," + float_format(position[2]) + "\n")
    if node.madtracks.roadwidth > 0.0:
        fgra.write("RoadWidth = " + float_format(node.madtracks.roadwidth) + "\n")
    if node.madtracks.motivboost > 0.0:
        fgra.write("MotivBoost = " + float_format(node.madtracks.motivboost) + "\n")
    fgra.write("\n")


def export_ai_edges(fgra, obj):
    """ Writes a Blender empty object as edges in the level AI file. """
    if '-' in obj.name and obj.name[-1] != '-':
        in_node = obj.name.split('-', 1)[0]
        if obj.name[-1] == ',':
            obj.name = obj.name[:-1]
        out_nodes = obj.name.split('-', 1)[1].split(',')
        for out_node in out_nodes:
            fgra.write("[Edge]\n")
            fgra.write("In = " + in_node + "\n")
            fgra.write("Out = " + out_node + "\n\n")
