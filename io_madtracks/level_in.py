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
These files contain geometry instances (.ldo files) from Gfx\models\Geometry
and objects instances (.ini descriptors) from Bin\Descriptors, making a level.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(ldo_in)
    imp.reload(object_in)
    imp.reload(madstructs)
    imp.reload(madini)
    imp.reload(trackparts)

import os
import bpy
import bmesh
from . import common
from . import ldo_in
from . import object_in
from . import madstructs
from . import madini
from . import trackparts

from .common import *
from .ldo_in import *
from .object_in import *
from .madstructs import *
from .madini import *
from .trackparts import *

# EASIER SOLUTION
# - get the filled .ini file structure
# - import_file() can go through the .ini once to import .ldo sections and all .ini sections
# - if the returned object after has "is_trackpart" set to True, add its name to a list with the current section treated
# - call an auxiliary function import_trackparts() that takes the (obj_name, ini_section) list
#   and edits Blender's trackpart objects properties (the list will be in orer so doable)

# OTHER SOLUTION (allows to easily disable trackparts import)
# - get the filled .ini file structure
# - import_file() can go through the .ini once to import .ldo sections and .ini sections that are not trackparts
#   (we know if an object is a trackpart by using the is_trackpart() function in object_in.py, but each descriptor will be read twice...)
# - call an auxiliary function import_trackparts() to import .ini sections that are trackparts
# BUT THIS SOLUTION IS NOT VERY CLEAN AND GOING THROUGH THE SECTIONS A SECOND TIME ISN'T NECESSARY

# BETTER SOLUTION (maintainable code, great logic splitting, small performance impact)
# - get the filled .ini file structure
# - while loop through sections with index "si"
# - if the section is .ldo, call import_geometry_instance() with the current section
# - if the section is .ini, read the descriptor to see if it is a trackpart (will lead to an additional read of the descriptor, but if that's the cost for a manageable code then I'll take it)
#       - if not a trackpart, call import_object_instance() with the current section
#       - if a trackpart, call import_trackpart_sequence() with the ini structure and "si" as it will take care of multiple sections
# note: import_geometry_instance() and import_object_instance() will share some code, make auxiliary functions

# THIS SKELETON RUNS, IMPLEMENT BIT BY BIT USING DEBUG MESSAGES AND TEST FILES PLEASE!
def import_file(filepath, scene):
    """
    Imports a level.
    """
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
                        si = import_trackpart_sequence(ini, si, num_sequence, scene)
                        num_sequence += 1
                    else:
                        import_object_instance(section, scene)
            # go to next section
            si += 1

    # reinstate old separate atomics property
    props.separate_atomics = separate_atomics_save

    print("Imported {}".format(filename))

            # # the filename parameter is guaranteed, import it and retrieve the Blender object(s)
            # fname = section.as_dict()['Filename']
            # ext = fname.split(".", 1)[1]
            # if ext == "ldo":
            #     obj = ldo_in.import_file(props.madtracks_dir + LDO_PATH + fname.split("/", 1)[1], scene)
            # elif ext == "ini":
            #     obj = object_in.import_file(props.madtracks_dir + DESCRIPTOR_PATH + fname, scene)
                
            # # edit location and rotation of Blender objects
            # if obj.madtracks.is_trackpart == False:
            #     # object is not a trackpart, use section parameters
            #     bpy.context.object.name = obj.name
            #     bpy.context.object.rotation_mode = 'AXIS_ANGLE'
            #     obj.location = to_blender_coord(section.as_dict()['Position'])
            #     # compute rotation matrix from directions
            #     rotation_matrix = rotation_matrix_from_directions(section.as_dict()['DirectionAT'], section.as_dict()['DirectionUp'])
            #     # convert rotation matrix to axis-angle representation
            #     axis, angle = axis_angle_from_rotation_matrix(rotation_matrix)
            #     axis = to_blender_axis(axis)
            #     obj.rotation_axis_angle[0] = angle
            #     obj.rotation_axis_angle[1] = axis[0]
            #     obj.rotation_axis_angle[2] = axis[1]
            #     obj.rotation_axis_angle[3] = axis[2]
            # else:
            #     # object is a trackpart
            #     if "Position" in section.as_dict().keys():
            #         # beginning of a new trackpart sequence
            #         num_sequence += 1
            #         num_trackpart = 0
            #         # FIXME DUPLICATED CODE use section parameters
            #         bpy.context.object.name = obj.name
            #         bpy.context.object.rotation_mode = 'AXIS_ANGLE'
            #         position = section.as_dict()['Position']
            #         obj.location = to_blender_coord(position)
            #         # compute rotation matrix from directions
            #         rotation_matrix = rotation_matrix_from_directions(section.as_dict()['DirectionAT'], section.as_dict()['DirectionUp'])
            #         # convert rotation matrix to axis-angle representation
            #         axis, angle = axis_angle_from_rotation_matrix(rotation_matrix)
            #         axis = to_blender_axis(axis)
            #         obj.rotation_axis_angle[0] = angle
            #         obj.rotation_axis_angle[1] = axis[0]
            #         obj.rotation_axis_angle[2] = axis[1]
            #         obj.rotation_axis_angle[3] = axis[2]
            #         # assign object properties
            #         obj.madtracks.num_sequence = num_sequence
            #         obj.madtracks.num_trackpart = num_trackpart
            #         # set next trackpart anchors
            #         if fname in trackparts.keys():
            #             anchorPos[0] = position[0] + trackparts[fname]['pos_offset'][0]
            #             anchorPos[1] = position[1] + trackparts[fname]['pos_offset'][1]
            #             anchorPos[2] = position[2] + trackparts[fname]['pos_offset'][2]
            #             # HACK to avoid converting from axis-angle to euler in code
            #             rotation_euler = to_madtracks_axis(obj.rotation_euler)
            #             anchorRot[0] = rotation_euler[0] + trackparts[fname]['rot_offset'][0]
            #             anchorRot[1] = rotation_euler[1] + trackparts[fname]['rot_offset'][1]
            #             anchorRot[2] = rotation_euler[2] + trackparts[fname]['rot_offset'][2]
            #     else:
            #         # next trackpart in the current sequence
            #         num_trackpart += 1
            #         # FIXME DUPLICATED CODE use trackpart anchors
            #         bpy.context.object.name = obj.name
            #         bpy.context.object.rotation_mode = 'XYZ'
            #         obj.location = to_blender_coord(anchorPos)
            #         obj.rotation_euler = to_blender_axis(anchorRot)
            #         # assign object properties
            #         obj.madtracks.num_sequence = num_sequence
            #         obj.madtracks.num_trackpart = num_trackpart
            #         # set next trackpart anchors
            #         if fname in trackparts.keys():
            #             anchorPos[0] = anchorPos[0] + trackparts[fname]['pos_offset'][0]
            #             anchorPos[1] = anchorPos[1] + trackparts[fname]['pos_offset'][1]
            #             anchorPos[2] = anchorPos[2] + trackparts[fname]['pos_offset'][2]
            #             # HACK to avoid converting from axis-angle to euler in code
            #             rotation_euler = to_madtracks_axis(obj.rotation_euler)
            #             anchorRot[0] = anchorRot[0] + trackparts[fname]['rot_offset'][0]
            #             anchorRot[1] = anchorRot[1] + trackparts[fname]['rot_offset'][1]
            #             anchorRot[2] = anchorRot[2] + trackparts[fname]['rot_offset'][2]


def import_geometry_instance(section, scene):
    props = scene.madtracks

    # create Blender object
    fname = section.as_dict()['Filename']
    obj = ldo_in.import_file(props.madtracks_dir + LDO_PATH + fname.split("/", 1)[1], scene)

    # edit location and rotation of Blender object
    place_blender_object(section, obj)

    return


def import_object_instance(section, scene):
    props = scene.madtracks

    # create Blender object
    fname = section.as_dict()['Filename']
    obj = object_in.import_file(props.madtracks_dir + DESCRIPTOR_PATH + fname, scene)

    # edit location and rotation of Blender object
    place_blender_object(section, obj)

    return obj


# - manage trackparts Blender properties
# - call functions in trackparts.py to do the anchor computation for us
def import_trackpart_sequence(ini, si, num_sequence, scene):
    """
    Returns the last section imported.
    """
    props = scene.madtracks
    
    num_trackpart = 0
    anchorPos = [0, 0, 0]
    anchorRot = [0, 0, 0]
    if props.load_trackparts:
        # TODO call trackparts.append_trackpart(ini.sections[si], num_sequence) instead?
        obj = import_object_instance(ini.sections[si], scene)
        obj.madtracks.num_sequence = num_sequence
        obj.madtracks.num_trackpart = num_trackpart
        num_trackpart += 1
    si += 1
    while si < len(ini.sections) and len(ini.sections[si].params) == 1:
        if props.load_trackparts:
            # TODO call trackparts.append_trackpart(ini.sections[si], num_sequence)?
            # update num_trackpart
            pass
        # go to next trackpart
        si += 1
    
    return si - 1


def place_blender_object(section, obj):
    """
    Edits a Blender object location and rotation.
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
        # we never go there yet
        pass

    return


# def import_geometry(filename, position, directionAT, directionUp, scene):
#     """
#     Imports a piece of geometry in Blender at the desired position and rotation
#     to visualize a level instance or object.
#     """
#     props = scene.madtracks

#     # import using the LDO file
#     objs = ldo_in.import_file(props.madtracks_dir + LDO_PATH + filename, scene)

#     # FIXME Below is an attempt of a huge optimization (multiple seconds for a level import).
#     # The goal is to avoid reading a .ldo file multiple times, by copying the Blender object.
#     # But the mesh is still shared with the original object,
#     # and we can't identify all the atomics of a .ldo file yet.

#     # ob = None
#     # # check if geometry was already imported
#     # for object in bpy.data.objects:
#     #     if object.name == filename:
#     #         # duplicate the existing object
#     #         ob = object.copy()
#     #         scene.objects.link(ob)
#     #         scene.objects.active = ob
#     #         break
#     # if not ob:
#     #     # import using the LDO file
#     #     ob = ldo_in.import_file(props.madtracks_dir + LDO_PATH + filename, scene)
    
#     # if the model has multiple atomics, import all of them
#     for ob in objs:
#         bpy.context.object.name = ob.name
#         bpy.context.object.rotation_mode = 'AXIS_ANGLE'
#         # set object's position and rotation
#         ob.location = to_blender_coord(position)
#         # compute rotation matrix from directions
#         rotation_matrix = rotation_matrix_from_directions(directionAT, directionUp)
#         # convert rotation matrix to axis-angle representation
#         axis, angle = axis_angle_from_rotation_matrix(rotation_matrix)
#         axis = to_blender_axis(axis)
#         ob.rotation_axis_angle[0] = angle
#         ob.rotation_axis_angle[1] = axis[0]
#         ob.rotation_axis_angle[2] = axis[1]
#         ob.rotation_axis_angle[3] = axis[2]

#     return objs


# def import_section(section, scene, cur_pos=None, cur_rot=None):
#     """
#     Imports a section as a Blender object
#     """
#     props = scene.madtracks
    
#     # get section extension
#     isInstance = False
#     isObject = False
#     isTrackpart = False
#     ext = section.name.rsplit(".", 1)[1]
#     if (ext == "ldo"):
#         isInstance = True
#     elif (ext == "ini"):
#         if (len(section.params) > 1):
#             isObject = True
#         else:
#             isTrackpart = True
#     else:
#         print("Unknown section extension \"%s\"" % ext)

#     # Loop thru all parameters
#     position = None
#     directionAT = None
#     directionUp = None
#     filename = None
#     for p in section.params:
#         if p.name == "Position":
#             position = p.values
#         elif p.name == "DirectionAT":
#             directionAT = p.values
#         elif p.name == "DirectionUp":
#             directionUp = p.values
#         elif p.name == "Filename":
#             filename = p.values
#             if isInstance:
#                 filename = filename.split("/", 1)[1] # strip useless "geometry/"
#         else:
#             print("Unknown parameter \"%s\"" % p.name)

#     # Retrieve associated .ldo filename
#     if isInstance:
#         dprint("%s will be imported" % filename)
#     else:
#         ldoFound = False
#         fini = open(props.madtracks_dir + DESCRIPTOR_PATH + filename, "r")
#         descriptor = INI(fini)
#         fini.close()
#         # TODO implement INI.as_dict() to avoid searching for a parameter in loops
#         for s in descriptor.sections:
#             for p in s.params:
#                 if p.name == "Filename":
#                     ldoFound = True
#                     filename = p.values.split("/", 1)[1]
#                     # TODO keep searching for descriptors .ldo filenames that do not exist
#                     # Maybe the "_High" suffix needs to be searched when importing an .ldo file?
#                     if filename == "ANT_Out_Sea.ldo":
#                         filename = "ANT_Out_Sea_High.ldo"
#                     elif filename == "GER_Eau.ldo":
#                         filename = "GER_Eau_High.ldo"
#                     elif filename == "ANT_Eau.ldo":
#                         filename = "ANT_Eau_High.ldo"
#                     dprint("%s will be imported" % filename)
#         if not ldoFound:
#             filename = "node.ldo"
#             dprint("%s will be imported" % filename)
    
#     dprint("At position: ", position)
#     dprint("At directionAT: ", directionAT)
#     dprint("At directionUp: ", directionUp)
#     dprint()

#     # Create Blender object
#     ob = None
#     # check if instance was already imported
#     for object in bpy.data.objects:
#         if object.name == filename:
#             # duplicate the existing instance
#             # FIXME the mesh is still shared with the original instance
#             ob = object.copy()
#             scene.objects.link(ob)
#             scene.objects.active = ob
#             break
#     if not ob:
#         # import using the LDO file
#         ob = ldo_in.import_file(props.madtracks_dir + LDO_PATH + filename, scene)
    
#     bpy.context.object.name = ob.name
#     bpy.context.object.rotation_mode = 'AXIS_ANGLE'
#     # set object's position and rotation
#     # TODO rotation computation is wrong, an object with:
#     # directionAT = 0.000000,-0.035014,-0.999387
#     # directionUp = 0.000000,0.999387,-0.035014
#     # should have a close to 0 angle, but it has 178 degrees
#     if position:
#         ob.location = to_blender_coord(Vector(data=(float(position[0]), float(position[1]), float(position[2]))))
#     if directionAT and directionUp:
#         # Compute rotation matrix from directions
#         directionAT = np.array(Vector(data=(float(directionAT[0]), float(directionAT[1]), float(directionAT[2]))))
#         directionUp = np.array(Vector(data=(float(directionUp[0]), float(directionUp[1]), float(directionUp[2]))))
#         rotation_matrix = rotation_matrix_from_directions(directionAT, directionUp)
#         # Convert rotation matrix to axis-angle representation
#         axis, angle = axis_angle_from_rotation_matrix(rotation_matrix)
#         axis = to_blender_axis(axis)
#         ob.rotation_axis_angle[0] = angle
#         ob.rotation_axis_angle[1] = axis[0]
#         ob.rotation_axis_angle[2] = axis[1]
#         ob.rotation_axis_angle[3] = axis[2]
#     if isTrackpart and cur_pos and cur_rot:
#         ob.location = to_blender_coord(cur_pos)
#         ob.rotation_euler = to_blender_axis(cur_rot)
    
#     return ob


"""
ChatGPT code to compute Blender objects rotation from the directionAT and directionUp parameters.
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



"""    
    bpy.context.object.name = ob.name
    bpy.context.object.rotation_mode = 'QUATERINON'
    # set object's position and rotation
    # TODO rotation computation is wrong, an object with:
    # directionAT = 0.000000,-0.035014,-0.999387
    # directionUp = 0.000000,0.999387,-0.035014
    if position:
        ob.location = to_blender_axis(Vector(data=(float(position[0]), float(position[1]), float(position[2]))))
    if directionAT and directionUp:
        # Compute rotation matrix from directions
        directionAT = np.array(Vector(data=(float(directionAT[0]), float(directionAT[1]), float(directionAT[2]))))
        directionUp = np.array(Vector(data=(float(directionUp[0]), float(directionUp[1]), float(directionUp[2]))))
        quaternion = direction_to_quaternion(directionAT, directionUp)
        ob.rotation_quaternion[0] = quaternion[0]
        ob.rotation_quaternion[1] = -quaternion[1]
        ob.rotation_quaternion[2] = quaternion[3]
        ob.rotation_quaternion[3] = quaternion[2]


ChatGPT code to compute Blender objects rotation from the directionAT and directionUp parameters.

import numpy as np

def direction_to_quaternion(directionAT, directionUp):
    # Initial direction vector
    initial_vector = np.array([0, 0, 1])

    # Check if directionAT is parallel to initial_vector
    if np.allclose(directionAT, initial_vector):
        # Rotation around the X-axis, no need to compute axis
        axis = np.array([0, 0, 1])
        angle = np.arccos(np.dot(initial_vector, directionAT))

        # Compute the rotation quaternion
        quaternion_rotation = axis_angle_to_quaternion(axis, angle)
    else:
        # Compute the rotation matrix to align initial_vector with directionAT
        dot_product = np.dot(initial_vector, directionAT)
        angle = np.arccos(dot_product / (np.linalg.norm(initial_vector) * np.linalg.norm(directionAT)))
        axis = np.cross(initial_vector, directionAT)
        axis = axis / np.linalg.norm(axis)

        # Compute the rotation quaternion
        quaternion_rotation = axis_angle_to_quaternion(axis, angle)

    return quaternion_rotation

def axis_angle_to_quaternion(axis, angle):
    # Convert axis-angle representation to quaternion
    axis = axis / np.linalg.norm(axis)
    half_angle = angle / 2
    w = np.cos(half_angle)
    xyz = axis * np.sin(half_angle)
    quaternion = np.array([w, xyz[0], xyz[1], xyz[2]])

    return quaternion
"""
