# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    level_in
Purpose: Imports level .ini files.

Description:
Level files contain Geometry instances (.ldo files) from Gfx\models\Geometry
and Object instances (.ini descriptors) from Bin\Descriptors.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(ldo_in)
    imp.reload(object_in)
    imp.reload(madstructs)
    imp.reload(madini)
    imp.reload(trackpart)

import os
import bpy
import bmesh
from . import common
from . import ldo_in
from . import object_in
from . import madstructs
from . import madini
from . import trackpart

from .common import *
from .ldo_in import *
from .object_in import *
from .madstructs import *
from .madini import *
from .trackpart import *


def import_file(filepath, scene):
    """
    Imports a level as Blender objects by reading the level .ini file.
    """
# TODO Handle that when I'll start supporting more levels at import
#
# for s in descriptor.sections:
#   for p in s.params:
#       if p.name == "Filename":
#           ldoFound = True
#           filename = p.values.split("/", 1)[1]
#           # Keep searching for descriptors .ldo filenames that do not exist
#           # Maybe the "_High" suffix needs to be searched when importing an .ldo file?
#           if filename == "ANT_Out_Sea.ldo":
#               filename = "ANT_Out_Sea_High.ldo"
#           elif filename == "GER_Eau.ldo":
#               filename = "GER_Eau_High.ldo"
#           elif filename == "ANT_Eau.ldo":
#               filename = "ANT_Eau_High.ldo"
#           dprint("%s will be imported" % filename)

    props = scene.madtracks

    with open(filepath, 'r') as file:
        filename = os.path.basename(filepath)
        # disable separate atomics property
        separate_atomics_save = props.separate_atomics
        props.separate_atomics = False
        # read and store level .ini file
        ini = INI(file)

        num_sequence = 0
        si = 0
        while si < len(ini.sections):
            # get current section and its type
            section = ini.sections[si]
            ext = section.as_dict()['Filename'].split(".", 1)[1]
            # import section
            if ext == "ldo":
                import_geometry_instance(section, scene)
            elif ext == "ini":
                descriptor_filename = props.madtracks_dir + DESCRIPTOR_PATH + section.as_dict()['Filename']
                # check object type (trackpart or not?)
                with open(descriptor_filename, 'r') as descriptor:
                    ini_descriptor = INI(descriptor).as_dict()
                    if "ObjectType" in ini_descriptor['object'].keys() and (ini_descriptor['object']['ObjectType'] in ["trackpart", "start", "startfinish", "checkpoint", "finish"]):
                        si = import_trackpart_sequence(ini, si, scene, num_sequence)
                        num_sequence += 1
                    else:
                        import_object_instance(section, scene)
            # go to next section
            si += 1

    # reinstate old separate atomics property
    props.separate_atomics = separate_atomics_save

    print("Imported {}".format(filename))


def import_geometry_instance(section, scene):
    """
    Imports a Geometry instance by reading a level .ini section.
    """
    props = scene.madtracks

    # create Blender object
    fname = section.as_dict()['Filename']
    obj = ldo_in.import_file(props.madtracks_dir + LDO_PATH + fname.split("/", 1)[1], scene)

    # edit location and rotation of Blender object
    place_blender_object(section, obj)

    return


def import_object_instance(section, scene):
    """
    Imports an Object instance by reading a level .ini section.
    """
    props = scene.madtracks

    # create Blender object
    fname = section.as_dict()['Filename']
    obj = object_in.import_file(props.madtracks_dir + DESCRIPTOR_PATH + fname, scene)

    # edit location and rotation of Blender object
    place_blender_object(section, obj)

    return obj


def import_trackpart_sequence(ini, si, scene, num_sequence):
    """
    Imports a sequence of trackparts by reading consecutive level .ini sections starting at index "si".
    Returns the index of the last level .ini section read and imported, which is the end of the sequence of trackparts.
    """
    props = scene.madtracks
    if props.import_trackparts:
        # create new trackpart sequence
        ob = trackpart.append_to_new_sequence(scene, ini.sections[si].as_dict()['Filename'])
        # place the first trackpart of the sequence with its INI coordinates
        place_blender_object(ini.sections[si], ob)
    si += 1
    while si < len(ini.sections) and len(ini.sections[si].params) == 1:
        if props.import_trackparts:
            # append to active trackpart sequence
            sequence = bpy.context.selected_objects[0].users_group[0]
            trackpart.append_to_sequence(scene, sequence.name, len(bpy.context.selected_objects), ini.sections[si].as_dict()['Filename'])
        # go to next trackpart
        si += 1
    if props.import_trackparts:
        # set sequence ID
        sequence = bpy.context.selected_objects[0].users_group[0]
        trackpart.set_sequence_ID(scene, sequence.name, len(bpy.context.selected_objects), num_sequence)

    # unselect objects
    bpy.ops.object.select_all(action='TOGGLE')
    
    return si - 1


def place_blender_object(section, obj):
    """
    Edits a Blender object's location and rotation by reading a level .ini section's parameters.
    """
    bpy.context.object.name = obj.name
    bpy.context.object.rotation_mode = 'AXIS_ANGLE'

    if len(section.params) == 4:
        obj.location = to_blender_coord(section.as_dict()['Position'])
        # compute rotation matrix from directions
        rotation_matrix = rotation_matrix_from_directions(section.as_dict()['DirectionAT'], section.as_dict()['DirectionUp'])
        # convert rotation matrix to axis-angle representation
        axis, angle = axis_angle_from_rotation_matrix(rotation_matrix)
        axis = to_blender_axis(axis)
        obj.rotation_axis_angle[0] = angle
        obj.rotation_axis_angle[1] = axis[0]
        obj.rotation_axis_angle[2] = axis[1]
        obj.rotation_axis_angle[3] = axis[2]
    else:
        print("Object imported from level .ini file section doesn't have the usual number of parameters, skipping...")

    # this is important for how I handle trackparts in general
    bpy.context.object.rotation_mode = 'XYZ'

    return


"""
ChatGPT code to compute Blender objects rotation from the directionAT and directionUp parameters.
FIXME The rotation obtained sometimes isn't the one we want, maybe because of Gimbal lock.
"""

import numpy as np

def rotation_matrix_from_directions(directionAT, directionUp):
    # Compute the rotation matrix
    # Direction vector along Z-axis (standard orientation)
    standard_forward = np.array([0, 0, 1])

    # Compute rotation axis as the cross product of standard_forward and directionAT
    axis = np.cross(standard_forward, directionAT)
    axis_norm = np.linalg.norm(axis)
    
    # If directionAT is parallel to standard_forward, choose axis as directionUp
    if axis_norm < 1e-6:
        axis = directionUp
    else:
        axis = axis / axis_norm

    # Compute the rotation angle as the angle between standard_forward and directionAT
    angle = np.arccos(np.dot(standard_forward, directionAT))

    # Compute the rotation matrix
    rotation_matrix = rotation_matrix_from_axis_angle(axis, angle)

    return rotation_matrix

def rotation_matrix_from_axis_angle(axis, angle):
    # Convert axis-angle representation to rotation matrix
    axis = axis / np.linalg.norm(axis)
    c = np.cos(angle)
    s = np.sin(angle)
    t = 1 - c

    rotation_matrix = np.array([[t * axis[0]**2 + c, t * axis[0] * axis[1] - s * axis[2], t * axis[0] * axis[2] + s * axis[1]],
                                [t * axis[0] * axis[1] + s * axis[2], t * axis[1]**2 + c, t * axis[1] * axis[2] - s * axis[0]],
                                [t * axis[0] * axis[2] - s * axis[1], t * axis[1] * axis[2] + s * axis[0], t * axis[2]**2 + c]])

    return rotation_matrix

def axis_angle_from_rotation_matrix(rotation_matrix):
    # Convert rotation matrix to axis-angle representation
    epsilon = 1e-8
    angle = np.arccos((np.trace(rotation_matrix) - 1) / 2)

    axis = np.zeros(3)
    if abs(angle) < epsilon:
        axis = np.array([0, 0, 1])  # Rotation angle close to zero, axis is arbitrary
    elif abs(np.pi - angle) < epsilon:
        # Rotation angle close to pi, axis is sqrt(2) times the eigenvector corresponding to the eigenvalue 1
        eigvals, eigvecs = np.linalg.eig(rotation_matrix)
        idx = np.argmax(eigvals)
        axis = eigvecs[:, idx]
    else:
        # Normal case, compute axis from skew-symmetric part of the rotation matrix
        axis = np.array([rotation_matrix[2, 1] - rotation_matrix[1, 2],
                         rotation_matrix[0, 2] - rotation_matrix[2, 0],
                         rotation_matrix[1, 0] - rotation_matrix[0, 1]])
        axis = axis / np.linalg.norm(axis)

    return axis, angle
