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
        filename = os.path.basename(filepath)

        # export objects that are not trackparts
        for obj in bpy.data.objects:
            if not obj.madtracks.is_trackpart:
                export_instance(fini, obj, obj.location, obj.matrix_world)
        
        # export trackpart sequences
        for group in bpy.data.groups:
            for obj in group.objects:
                if obj.madtracks.is_trackpart:
                    if obj.parent == None:
                        export_instance(fini, obj, obj.location, obj.matrix_world)
                    else:
                        export_instance(fini, obj)
    
    # reinstate old instance mode
    props.instance_mode = instance_mode_save

    print("Exported {}".format(filename))


def export_instance(fini, obj, location=None, matrix_world=None):
    """
    Writes a Blender object as a level instance in the level file.
    Handles trackpart sequences, which are Object instances without position/rotation parameters,
    since they are automatically computed by Mad Tracks' engine.
    """
    if obj.madtracks.descriptor != '':
        name = obj.madtracks.descriptor
    else:
        if "_lgt" in obj.name:
            name = "geometry/" + obj.name.split("_lgt")[0] + ".ldo"
        else:
            name = "geometry/" + obj.name.split(".")[0] + ".ldo"

    fini.write("[" + name + "]\n")
    if location:
        pos = to_madtracks_axis(location)
        fini.write("Position = " + float_format(pos[0]) + "," + float_format(pos[1]) + "," + float_format(pos[2]) + "\n")
    if matrix_world:
        rot = to_madtracks_matrix(matrix_world)
        fini.write("DirectionAT = " + float_format(rot[0][0]) + "," + float_format(rot[0][1]) + "," + float_format(rot[0][2]) + "\n")
        fini.write("DirectionUp = " + float_format(rot[1][0]) + "," + float_format(rot[1][1]) + "," + float_format(rot[1][2]) + "\n")
    fini.write("Filename = \"" + name + "\"\n\n")

    print("Exported {}".format(obj.name))
