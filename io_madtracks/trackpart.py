# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    trackpart
Purpose: Handles trackpart sequences.

Description:

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(ldo_in)
    imp.reload(object_in)
    imp.reload(madstructs)
    imp.reload(madini)

from . import common
from . import ldo_in
from . import object_in
from . import madstructs
from . import madini

from .common import *
from .ldo_in import *
from .object_in import *
from .madstructs import *
from .madini import *

from math import radians
import numpy as np

trackparts = {
    "M_gris_amorce_05_in.ini" : {
        "pos_offset" : [0, 0, 5],
        "rot_offset" : [0, 0, 0]
    },
    "M_gris_amorce_15_in.ini" : {
        "pos_offset" : [0, 0, 15],
        "rot_offset" : [0, 0, 0]
    },
    "M_gris_amorce_30_in.ini" : {
        "pos_offset" : [0, 0, 30],
        "rot_offset" : [0, 0, 0]
    },
    "M_gris_rail_15.ini" : {
        "pos_offset" : [0, 0, 15],
        "rot_offset" : [0, 0, 0]
    },
    "M_gris_rail_50.ini" : {
        "pos_offset" : [0, 0, 50],
        "rot_offset" : [0, 0, 0]
    },
    "M_gris_virage_45_left.ini" : {
        "pos_offset" : [17.5848, 0, 42.4152],
        "rot_offset" : [0, 45, 0]
    },
    "M_gris_virage_45_right.ini" : {
        "pos_offset" : [-17.5848, 0, 42.4152],
        "rot_offset" : [0, -45, 0]
    },
    "M_gris_rampe_30_up.ini" : {
        "pos_offset" : [0, 10.9245, 40.3482],
        "rot_offset" : [-30, 0, 0]
    },
    "M_gris_rampe_30_down.ini" : {
        "pos_offset" : [0, -10.7132, 40.4182],
        "rot_offset" : [30, 0, 0]
    },
    "M_none_checkpoint.ini" : {
        "pos_offset" : [0, 0, 0],
        "rot_offset" : [0, 0, 0]
    },
}

def append_to_new_sequence(scene):
    props = scene.madtracks
    # get filepath of trackpart to import
    if props.trackpart_category == "M":
        descriptor = props.trackpart_medium
        filepath = props.madtracks_dir + DESCRIPTOR_PATH + descriptor
    trackpart = object_in.import_file(filepath, scene)
    # set trackpart properties
    trackpart.madtracks.num_trackpart = 0
    # restrict rotation
    trackpart.lock_rotation[0] = True
    trackpart.lock_rotation[1] = True
    trackpart.lock_rotation[2] = False
    # create a new trackpart sequence
    sequence = bpy.data.groups.new("Sequence")
    bpy.ops.object.group_link(group=sequence.name)
    # select group to make the sequence "active"
    bpy.ops.object.select_grouped(type='GROUP')

    return sequence.name

def append_to_sequence(scene, groupName, groupSize):
    props = scene.madtracks
    # get filepath of trackpart to import
    if props.trackpart_category == "M":
        #descriptor = props.trackpart_medium
        #filepath = props.madtracks_dir + DESCRIPTOR_PATH + descriptor
        filepath = props.madtracks_dir + DESCRIPTOR_PATH + props.trackpart_medium
    trackpart = object_in.import_file(filepath, scene)
    # set trackpart properties
    trackpart.madtracks.num_trackpart = groupSize
    # restrict rotation
    trackpart.lock_rotation[0] = True
    trackpart.lock_rotation[1] = True
    trackpart.lock_rotation[2] = False
    # add to active trackpart sequence
    bpy.ops.object.group_link(group=groupName)
    # only select the trackpart to append
    bpy.ops.object.select_all()
    bpy.data.objects[trackpart.name].select = True

    # place the trackpart at the end of the sequence
    first = get_trackpart(groupName, 0)
    trackpart.location = first.location
    trackpart.rotation_euler = first.rotation_euler
    pos_vec = to_blender_axis(trackparts[first.madtracks.descriptor]['pos_offset'])
    bpy.ops.transform.translate(value=(pos_vec[0], pos_vec[1], pos_vec[2]), constraint_axis=(pos_vec[0]!=0, pos_vec[1]!=0, pos_vec[2]!=0), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
    rot_vec = to_blender_axis(trackparts[first.madtracks.descriptor]['rot_offset'])
    trackpart.rotation_euler.rotate_axis("X", radians(rot_vec[0]))
    trackpart.rotation_euler.rotate_axis("Y", radians(rot_vec[1]))
    trackpart.rotation_euler.rotate_axis("Z", radians(rot_vec[2]))
    for i in range(1, groupSize):
        next = get_trackpart(groupName, i)
        pos_vec = to_blender_axis(trackparts[next.madtracks.descriptor]['pos_offset'])
        bpy.ops.transform.translate(value=(pos_vec[0], pos_vec[1], pos_vec[2]), constraint_axis=(pos_vec[0]!=0, pos_vec[1]!=0, pos_vec[2]!=0), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        rot_vec = to_blender_axis(trackparts[next.madtracks.descriptor]['rot_offset'])
        trackpart.rotation_euler.rotate_axis("X", radians(rot_vec[0]))
        trackpart.rotation_euler.rotate_axis("Y", radians(rot_vec[1]))
        trackpart.rotation_euler.rotate_axis("Z", radians(rot_vec[2]))

    # select group to make the sequence "active" again
    bpy.ops.object.select_grouped(type='GROUP')
        

    # "Invert" descriptor flag for trackparts:
    # In the case of amorce_out, the model is rotated by 180°, not mirrored
    # "Invert" means: the other end of the trackpart is attached to the sequence

    # By analyzing the M_raye_virage_90_kit_left_in.ini and M_raye_virage_90_kit_left_out.ini descriptors
    # to make a 180 turn, "Invert" might just mean finding the other end of the trackpart and putting the object's origin there.
    # If I can't move the origin directly, try using the 3D cursor temporarily
    # Then move the trackpart at the end of the sequence, but for the rotation I might need to use the trackparts' rotation offsets in the dictionary.
    # I say that because a straight inverted trackpart need to be rotated 180° and a 90° turn inverted trackpart doesn't need to be rotated.

    # My trackparts dictionary works per descriptor, so if I already hardcode the anchor offsets,
    # I just apply the inversion by hand.
    # The challenge is to invert the trackpart in the viewport.
    # I NEED THAT because of the way I get the anchor (rotation of the second to last trackpart).
    # Or I change the way I get the anchor: work from the first trackpart and move it to the end of the sequence using the dictionary offsets.
    # It can be ignored and it will still work at export though (maybe color the inverted trackparts in the viewport to say "Hey it's not this way in reality").
    # As a simple solution I can maybe add "position_invert" and "rotation_invert" attributes to update in the viewport.
    # Does it depend on the current anchor though?

def get_trackpart(groupName, number):
    """
    Returns the trackpart of the sequence at the given number.
    """
    trackpart = None
    i = 0
    while not trackpart and i < len(bpy.data.objects):
        ob = bpy.data.objects[i]
        if ob.users_group[0].name == groupName and ob.madtracks.num_trackpart == number:
            trackpart = ob
        i += 1
    
    return trackpart

# def update_anchor(descriptor, anchorPos, anchorRot):
#     """
#     Given a trackpart descriptor name and an anchor,
#     return the updated anchor corresponding to the end of the trackpart.
#     """
#     # rotate pos_offset vector by trackpart's rotation
#     pos_vec = to_blender_axis(trackparts[descriptor]["pos_offset"])
#     rotation_x = np.array([[1, 0, 0],
#                            [0, np.cos(anchorRot[0]), -np.sin(anchorRot[0])],
#                            [0, np.sin(anchorRot[0]), np.cos(anchorRot[0])]])

#     rotation_y = np.array([[np.cos(anchorRot[1]), 0, np.sin(anchorRot[1])],
#                            [0, 1, 0],
#                            [-np.sin(anchorRot[1]), 0, np.cos(anchorRot[1])]])

#     rotation_z = np.array([[np.cos(anchorRot[2]), -np.sin(anchorRot[2]), 0],
#                            [np.sin(anchorRot[2]), np.cos(anchorRot[2]), 0],
#                            [0, 0, 1]])
#     pos_vec = np.dot(rotation_x, pos_vec)
#     pos_vec = np.dot(rotation_y, pos_vec)
#     pos_vec = np.dot(rotation_z, pos_vec)
    
#     # update anchorPos
#     anchorPos = np.add(anchorPos, pos_vec)

#     # update anchorRot
#     rot_vec = to_blender_axis(trackparts[descriptor]["rot_offset"])
#     rot_vec[0] = rot_vec[0]/180*np.pi
#     rot_vec[1] = rot_vec[1]/180*np.pi
#     rot_vec[2] = rot_vec[2]/180*np.pi
#     anchorRot = np.add(anchorRot, rot_vec)
    
#     return anchorPos, anchorRot
