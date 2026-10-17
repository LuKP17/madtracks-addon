# Copyright (C) 2024-2026  Lucas Pottier
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
    imp.reload(descriptor_in)
    imp.reload(madstructs)
    imp.reload(madini)

from . import common
from . import ldo_in
from . import descriptor_in
from . import madstructs
from . import madini

from .common import *
from .ldo_in import *
from .descriptor_in import *
from .madstructs import *
from .madini import *

import numpy as np
import mathutils

TRACKPART_CATEGORIES = (
    ("C", "Control", "", 0),
    ("M", "Medium", "", 1),
    ("S", "Small", "", 2),
    ("W", "Wood", "", 3),
    # ("G", "Golf", "", 4),
    # ("U", "Custom", "Custom trackparts"),
    # ("B", "Bobsleigh", "Bobsleigh trackparts"),
    # ("Q", "Croquet", "Croquet trackparts"),
    # ("V", "Vent", "Vent trackparts"),
    # ("A", "Antartica", "Antartica trackparts"),
)
TRACKPARTS_CONTROL = (
    ("M_none_start.ini", "Start", ""),
    ("M_none_startfinish.ini", "Start/Finish", ""),
    ("M_none_checkpoint.ini", "Checkpoint", ""),
    ("M_none_finish_50.ini", "Finish", ""),
    ("S_none_startfinish.ini", "Small Start/Finish", ""),
    ("S_none_checkpoint.ini", "Small Checkpoint", ""),
    ("G_none_checkpoint.ini", "Large Checkpoint", ""),
    ("G_none_finish.ini", "Large Finish", ""),
    ("G_none_startfinish.ini", "Golf Start/Finish", ""),
)
TRACKPARTS_MEDIUM = (
    ("M_gris_amorce_15_in.ini", "None to Medium 15", ""),
    ("M_gris_amorce_15_out.ini", "Medium to None 15", ""),
    ("M_gris_amorce_30_in.ini", "None to Medium 30", ""),
    ("M_gris_amorce_30_out.ini", "Medium to None 30", ""),
    ("M_gris_rail_15.ini", "Straight 15", ""),
    ("M_gris_rail_50.ini", "Straight 50", ""),
    ("M_neon_rail_50.ini", "Straight Neon 50", ""),
    ("M_gris_virage_45_left.ini", "Left 45", ""),
    ("M_gris_virage_45_right.ini", "Right 45", ""),
    ("M_gris_rampe_30_up.ini", "Up 30", ""),
    ("M_gris_rampe_30_down.ini", "Down 30", ""),
    ("M_raye_virage_90_kit_right_in.ini", "Right Stripe In", ""),
    ("M_raye_virage_90_kit_right_out.ini", "Right Stripe Out", ""),
    ("M_gris_to_S_50.ini", "Medium to Small 50", ""),
    ("M_none_cache_out.ini", "Cache Out", ""),
    ("M_none_cache_in.ini", "Cache In", ""),
)
TRACKPARTS_SMALL = (
    ("S_bleu_amorce_15_in.ini", "None to Small 15", ""),
    ("S_bleu_amorce_15_out.ini", "Small to None 15", ""),
    ("S_neon_rail_50.ini", "Straight Neon 50", ""),
    ("S_neon_virage_45_left.ini", "Left Neon 45", ""),
    ("S_neon_virage_45_right.ini", "Right Neon 45", ""),
    ("S_raye_rampe_30_up.ini", "Up Stripe 30", ""),
    ("S_raye_rampe_30_down.ini", "Down Stripe 30", ""),
    ("S_gris_to_M_50.ini", "Small to Medium 50", ""),
    ("S_raye_looping.ini", "Looping", ""),
)
TRACKPARTS_WOOD = (
    ("P_amorce_in.ini", "None to Wood", ""),
    ("W_amorce_in.ini", "None to Wood Sides", ""),
    ("P_amorce_out.ini", "Wood to None", ""),
    ("W_amorce_out.ini", "Wood to None Sides", ""),
    ("P_rail_50.ini", "Straight 50", ""),
    ("W_rail_50.ini", "Straight Sides 50", ""),
    ("P_virage_90_left.ini", "Left 90", ""),
    ("P_virage_90_right.ini", "Right 90", ""),
    ("W_virage_90_right.ini", "Right Sides 90", ""),
    ("P_amorce_cache_in.ini", "Cache In", ""),
)

ANGLE_180 = 3.141592654


def from_dropdown(scene):
    props = scene.madtracks
    # use the active descriptor set in the trackpart editor
    if props.trackpart_category == "C":
        return props.trackpart_control
    elif props.trackpart_category == "M":
        return props.trackpart_medium
    elif props.trackpart_category == "S":
        return props.trackpart_small
    elif props.trackpart_category == "W":
        return props.trackpart_wood


def from_reference(scene):
    props = scene.madtracks
    # use the descriptor of the reference field set in the trackpart editor
    if not props.trackpart_ref:
        set_error('adding trackpart', "No exiting trackpart referenced")
        return None
    return props.trackpart_ref.madtracks.descriptor


def add_user(scene, descriptor):
    """
    Used to handle trackparts selected by the user.
    """
    props = scene.madtracks

    if not descriptor:
        set_error('adding trackpart', "No trackpart set")
        return
    filepath = props.madtracks_dir + DESCRIPTOR_PATH + descriptor

    # look for a selected trackpart to append to
    prev = None
    sel = bpy.context.selected_objects
    if len(sel) == 1 and sel[0].madtracks.is_trackpart:
        prev = sel[0]
    elif len(sel) > 1:
        set_error('adding trackpart', "Please select one existing trackpart at most")
        return
    # don't reuse already imported since it could be a custom modified version
    descriptor_in.import_file(filepath, scene)
    obj = bpy.context.active_object
    if prev:
        skip_link = False
        # allow appending a control object to a trackpart for convenience
        if obj.madtracks.object_type in control_types:
            skip_link = True
        append(scene, obj, prev, skip_link)
    else:
        # move trackpart to 3D cursor
        obj.location = bpy.context.scene.cursor_location
        obj.select = True
    if obj.madtracks.invert:
        invert(scene, obj)


def append(scene, obj, prev, skip_link=False):
    """
    Shared method with level importer to append and optionally link
    a trackpart to another one.
    """
    # compute rotation
    dummy_rotmat = mathutils.Matrix([prev.madtracks.dummy_rot1, prev.madtracks.dummy_rot2, prev.madtracks.dummy_rot3, prev.madtracks.dummy_rot4])
    dummy_roteuler = dummy_rotmat.to_euler()
    obj.rotation_euler = prev.rotation_euler
    if prev.madtracks.invert:
        obj.rotation_euler.rotate_axis("Z", ANGLE_180)
    else:
        obj.rotation_euler.rotate_axis("X", dummy_roteuler[0])
        obj.rotation_euler.rotate_axis("Y", dummy_roteuler[1])
        obj.rotation_euler.rotate_axis("Z", dummy_roteuler[2])
    # calculate location
    if prev.madtracks.invert:
        # use prev origin instead of its dummy
        obj.location = prev.location
    else:
        prev_pos = np.array(prev.location)
        prev_rot = np.array(prev.rotation_euler.to_matrix())
        dummy_pos = prev.madtracks.dummy_pos
        dummy_pos = np.matmul(dummy_pos, np.transpose(prev_rot))
        obj.location = np.add(prev_pos, dummy_pos)

    if not skip_link:
        obj.select = True
        prev.select = False
        # set prev as active for nextt_update_func to link both trackparts
        scene.objects.active = prev
        prev.madtracks.nextt = obj
        scene.objects.active = obj


def invert(scene, obj):
    """
    All stock trackparts which are inverted have a left-right rotation offset which can be zero.
    Inverted trackparts are a way to avoid making more models by applying an additional transformation.
    """
    # apply additional rotation
    dummy_rotmat = mathutils.Matrix([obj.madtracks.dummy_rot1, obj.madtracks.dummy_rot2, obj.madtracks.dummy_rot3, obj.madtracks.dummy_rot4])
    dummy_roteuler = dummy_rotmat.to_euler()
    if dummy_roteuler[2] > 0:
        # left turn
        obj.rotation_euler.rotate_axis("Z", ANGLE_180 - dummy_roteuler[2])
    else:
        # right turn
        obj.rotation_euler.rotate_axis("Z", -ANGLE_180 + dummy_roteuler[2])
    # apply inverse of own dummy position offset
    obj_pos = np.array(obj.location)
    obj_rot = np.array(obj.rotation_euler.to_matrix())
    dummy_pos = obj.madtracks.dummy_pos
    dummy_pos = np.matmul(dummy_pos, np.transpose(obj_rot))
    obj.location = np.add(obj_pos, -dummy_pos)


def select_linked(scene, trackparts):
    for obj in trackparts:
        if obj.madtracks.is_trackpart:
            nextt = obj.madtracks.nextt
            # safe loop
            while nextt and scene.objects.find(nextt.name) != -1 and nextt != obj:
                nextt.select = True
                nextt = nextt.madtracks.nextt


def recalculate(scene):
    bpy.ops.object.select_all(action='DESELECT')
    # first pass to fix trackpart links
    for obj in scene.objects:
        if obj.madtracks.prev:
            # check prev link
            prev = obj.madtracks.prev
            if scene.objects.find(prev.name) == -1:
                # prev object was deleted
                obj.madtracks.prev = None
            elif prev.madtracks.nextt != obj:
                # prev object points to another trackpart
                obj.madtracks.prev = None
        if obj.madtracks.nextt:
            if scene.objects.find(obj.madtracks.nextt.name) == -1:
                # next object doesn't exist
                obj.madtracks.nextt = None
    # second pass to recalculate trackparts position
    for obj in scene.objects:
        if not obj.madtracks.prev:
            while obj.madtracks.nextt:
                # move the next trackpart after this one
                append(scene, obj.madtracks.nextt, obj, skip_link=True)
                obj = obj.madtracks.nextt
                if obj.madtracks.invert:
                    invert(scene, obj)
