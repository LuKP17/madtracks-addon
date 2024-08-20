# Copyright (C) 2024  Lucas Pottier
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
Exports level files.

"""


if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(trackpart)

import bpy
import numpy as np

from . import common
from . import trackpart

from .common import *
from .trackpart import *


def export_file(filepath, scene):
    props = scene.madtracks

    with open(filepath, 'w') as fini:
        filename = os.path.basename(filepath)

        # export objects that are not trackparts
        for obj in bpy.data.objects:
            if not obj.madtracks.is_trackpart:
                export_object(fini, obj)
        
        # export trackpart sequences
        trackparts = get_all_trackparts()
        for trackpart in trackparts:
            obj = bpy.data.objects[trackpart[0]]
            export_object(fini, obj)

    print("Exported {}".format(filename))


def export_object(fini, obj):
    if obj.madtracks.descriptor != "None":
        name = obj.madtracks.descriptor
    else:
        name = "geometry/" + obj.name.rsplit(".ldo")[0] + ".ldo"

    fini.write("[" + name + "]\n")
    if not obj.madtracks.is_trackpart or obj.madtracks.num_trackpart == 0:
        fini.write("Position = " + float_format(-obj.location[0]) + "," + float_format(obj.location[2]) + "," + float_format(obj.location[1]) + "\n")
        euler_angles = obj.rotation_euler
        direction_vectors = euler_to_direction(euler_angles)
        fini.write("DirectionAT = " + float_format(-direction_vectors[0][0]) + "," + float_format(direction_vectors[0][2]) + "," + float_format(direction_vectors[0][1]) + "\n")
        fini.write("DirectionUp = " + float_format(-direction_vectors[1][0]) + "," + float_format(direction_vectors[1][2]) + "," + float_format(direction_vectors[1][1]) + "\n")
    fini.write("Filename = \"" + name + "\"\n\n")


def euler_to_direction(euler_angles):
    # Extract Euler angles
    angle_x, angle_y, angle_z = euler_angles

    # Initial direction vectors
    initial_directionAT = np.array([0, 1, 0])
    initial_directionUp = np.array([0, 0, 1])

    # Rotation matrices around X, Y, Z axes
    rotation_x = np.array([[1, 0, 0],
                           [0, np.cos(angle_x), -np.sin(angle_x)],
                           [0, np.sin(angle_x), np.cos(angle_x)]])

    rotation_y = np.array([[np.cos(angle_y), 0, np.sin(angle_y)],
                           [0, 1, 0],
                           [-np.sin(angle_y), 0, np.cos(angle_y)]])

    rotation_z = np.array([[np.cos(angle_z), -np.sin(angle_z), 0],
                           [np.sin(angle_z), np.cos(angle_z), 0],
                           [0, 0, 1]])

    # Apply rotations
    intermediate_directionAT = np.dot(rotation_x, initial_directionAT)
    intermediate_directionAT = np.dot(rotation_y, intermediate_directionAT)
    final_directionAT = np.dot(rotation_z, intermediate_directionAT)
    
    intermediate_directionUp = np.dot(rotation_x, initial_directionUp)
    intermediate_directionUp = np.dot(rotation_y, intermediate_directionUp)
    final_directionUp = np.dot(rotation_z, intermediate_directionUp)

    return final_directionAT, final_directionUp
