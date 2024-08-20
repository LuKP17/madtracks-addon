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
    "M_gris_amorce_15_out.ini" : {
        "pos_offset" : [0, 0, 15],
        "rot_offset" : [0, 0, 0],
        "pos_invert" : [0, 0, 15],
        "rot_invert" : [0, 180, 0]
    },
    "M_gris_amorce_30_out.ini" : {
        "pos_offset" : [0, 0, 30],
        "rot_offset" : [0, 0, 0],
        "pos_invert" : [0, 0, 30],
        "rot_invert" : [0, 180, 0]
    },
    "M_gris_rail_15.ini" : {
        "pos_offset" : [0, 0, 15],
        "rot_offset" : [0, 0, 0]
    },
    "M_gris_rail_50.ini" : {
        "pos_offset" : [0, 0, 50],
        "rot_offset" : [0, 0, 0]
    },
    "M_neon_rail_50.ini" : {
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
    "M_none_start.ini" : {
        "pos_offset" : [0, 0, 0],
        "rot_offset" : [0, 0, 0]
    },
    "M_none_checkpoint.ini" : {
        "pos_offset" : [0, 0, 0],
        "rot_offset" : [0, 0, 0]
    },
    "M_none_finish_50.ini" : {
        "pos_offset" : [0, 0, 0],
        "rot_offset" : [0, 0, 0]
    },
    "M_gris_to_S_50.ini" : {
        "pos_offset" : [0, 0, 50],
        "rot_offset" : [0, 0, 0],
        "pos_invert" : [0, 0, 50],
        "rot_invert" : [0, 180, 0]
    },
    "S_bleu_amorce_15_in.ini" : {
        "pos_offset" : [0, 0, 15],
        "rot_offset" : [0, 0, 0]
    },
    "S_bleu_amorce_15_out.ini" : {
        "pos_offset" : [0, 0, 15],
        "rot_offset" : [0, 0, 0],
        "pos_invert" : [0, 0, 15],
        "rot_invert" : [0, 180, 0]
    },
    "S_neon_rail_50.ini" : {
        "pos_offset" : [0, 0, 50],
        "rot_offset" : [0, 0, 0]
    },
    "S_neon_virage_45_left.ini" : {
        "pos_offset" : [8.7924, 0, 21.2076],
        "rot_offset" : [0, 45, 0]
    },
    "S_neon_virage_45_right.ini" : {
        "pos_offset" : [-8.7924, 0, 21.2076],
        "rot_offset" : [0, -45, 0],
        "pos_invert" : [-8.7924, 0, 21.2076],
        "rot_invert" : [0, 135, 0]
    },
    "S_raye_rampe_30_up.ini" : {
        "pos_offset" : [0, 10.1114, 37.3328],
        "rot_offset" : [-30, 0, 0]
    },
    "S_raye_rampe_30_down.ini" : {
        "pos_offset" : [0, -10.342, 37.2943],
        "rot_offset" : [30, 0, 0]
    },
    "S_gris_to_M_50.ini" : {
        "pos_offset" : [0, 0, 50],
        "rot_offset" : [0, 0, 0]
    },
    "S_raye_looping.ini" : {
        "pos_offset" : [29.6271, 0.229707, 4.7106],
        "rot_offset" : [0, 0, 0]
    },
    "G_none_checkpoint.ini" : {
        "pos_offset" : [0, 0, 0],
        "rot_offset" : [0, 0, 0]
    },
    "G_none_finish.ini" : {
        "pos_offset" : [0, 0, 0],
        "rot_offset" : [0, 0, 0]
    },
}

def append_to_new_sequence(scene, descriptor=None):
    props = scene.madtracks
    # get filepath of trackpart to import
    if descriptor == None:
        # use the active descriptor set in the trackpart editor
        if props.trackpart_category == "S":
            descriptor = props.trackpart_small
        elif props.trackpart_category == "M":
            descriptor = props.trackpart_medium
        elif props.trackpart_category == "G":
            descriptor = props.trackpart_golf
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

    return trackpart

def append_to_sequence(scene, groupName, groupSize, descriptor=None):
    props = scene.madtracks
    # get filepath of trackpart to import
    if descriptor == None:
        # use the active descriptor set in the trackpart editor
        if props.trackpart_category == "S":
            descriptor = props.trackpart_small
        elif props.trackpart_category == "M":
            descriptor = props.trackpart_medium
        elif props.trackpart_category == "G":
            descriptor = props.trackpart_golf
    filepath = props.madtracks_dir + DESCRIPTOR_PATH + descriptor
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
    for i in range(0, groupSize):
        next = get_trackpart(groupName, i)
        pos_offset = to_blender_axis(trackparts[next.madtracks.descriptor]['pos_offset'])
        bpy.ops.transform.translate(value=(pos_offset[0], pos_offset[1], pos_offset[2]), constraint_axis=(pos_offset[0]!=0, pos_offset[1]!=0, pos_offset[2]!=0), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        rot_offset = to_blender_axis(trackparts[next.madtracks.descriptor]['rot_offset'])
        trackpart.rotation_euler.rotate_axis("X", radians(rot_offset[0]))
        trackpart.rotation_euler.rotate_axis("Y", radians(rot_offset[1]))
        trackpart.rotation_euler.rotate_axis("Z", radians(rot_offset[2]))

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
    # It can be ignored and it will still work at export though (maybe color the inverted trackparts in the viewport to say "Hey it's not this way in reality").

    # As a simple solution I added "position_invert" and "rotation_invert" attributes to update in the viewport.
    if trackpart.madtracks.invert:
        pos_invert = to_blender_axis(trackparts[trackpart.madtracks.descriptor]['pos_invert'])
        bpy.ops.transform.translate(value=(pos_invert[0], pos_invert[1], pos_invert[2]), constraint_axis=(pos_invert[0]!=0, pos_invert[1]!=0, pos_invert[2]!=0), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        rot_invert = to_blender_axis(trackparts[trackpart.madtracks.descriptor]['rot_invert'])
        trackpart.rotation_euler.rotate_axis("X", radians(rot_invert[0]))
        trackpart.rotation_euler.rotate_axis("Y", radians(rot_invert[1]))
        trackpart.rotation_euler.rotate_axis("Z", radians(rot_invert[2]))
    
    # give the trackpart the same sequence number as the first trackpart of the sequence
    trackpart.madtracks.num_sequence = first.madtracks.num_sequence

    # select group to make the sequence "active" again
    bpy.ops.object.select_grouped(type='GROUP')

def set_sequence_ID(scene, groupName, groupSize, ID=None):
    props = scene.madtracks
    if ID == None:
        # use sequence ID set in the trackpart editor
        ID = props.sequence_ID
    for i in range(0, groupSize):
        next = get_trackpart(groupName, i)
        next.madtracks.num_sequence = ID

def get_trackpart(groupName, number):
    """
    Returns the trackpart of the sequence at the given number.
    """
    trackpart = None
    i = 0
    while not trackpart and i < len(bpy.data.objects):
        ob = bpy.data.objects[i]
        # since we loop through all objects, handle non-trackparts or trackparts imported without using the editor
        if ob.madtracks.is_trackpart and len(ob.users_group) > 0 and ob.users_group[0].name == groupName and ob.madtracks.num_trackpart == number:
            trackpart = ob
        i += 1
    
    return trackpart

def get_all_trackparts():
    """
    Returns a list of all the trackpart sequences in order.
    Each element of the list is a list that contains [name, num_sequence, num_trackpart].
    """
    sequences = []
    for obj in bpy.data.objects:
        if obj.madtracks.is_trackpart:
            sequences.append([obj.name, obj.madtracks.num_sequence, obj.madtracks.num_trackpart])
    sequences.sort(key=lambda sequences: (sequences[1], sequences[2]))
    
    return sequences
