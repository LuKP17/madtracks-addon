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
    ("M", "Medium", "", 0),
    ("S", "Small", "", 1),
    ("G", "Golf", "", 2),
    # ("U", "Custom", "Custom trackparts"),
    # ("X", "Control", "Starts, checkpoints, finishes"),
    # ("W", "Wood", "Wood trackparts"),
    # ("B", "Bobsleigh", "Bobsleigh trackparts"),
    # ("C", "Croquet", "Croquet trackparts"),
    # ("V", "Vent", "Vent trackparts"),
    # ("A", "Antartica", "Antartica trackparts"),
)
TRACKPARTS_SMALL = (
    ("S_bleu_amorce_15_in.ini", "Amorce In 15", ""),
    ("S_bleu_amorce_15_out.ini", "Amorce Out 15", ""),
    ("S_neon_rail_50.ini", "Neon Straight 50", ""),
    ("S_neon_virage_45_left.ini", "Neon Left 45", ""),
    ("S_neon_virage_45_right.ini", "Neon Right 45", ""),
    ("S_raye_rampe_30_up.ini", "Stripe Up 30", ""),
    ("S_raye_rampe_30_down.ini", "Stripe Down 30", ""),
    ("S_gris_to_M_50.ini", "Small to Medium 50", ""),
    ("S_raye_looping.ini", "Stripe Looping", ""),
)
TRACKPARTS_MEDIUM = (
    ("M_gris_amorce_05_in.ini", "Amorce In 05", ""),
    ("M_gris_amorce_15_in.ini", "Amorce In 15", ""),
    ("M_gris_amorce_15_out.ini", "Amorce Out 15", ""),
    ("M_gris_amorce_30_in.ini", "Amorce In 30", ""),
    ("M_gris_amorce_30_out.ini", "Amorce Out 30", ""),
    ("M_gris_rail_15.ini", "Straight 15", ""),
    ("M_gris_rail_50.ini", "Straight 50", ""),
    ("M_neon_rail_50.ini", "Neon Straight 50", ""),
    ("M_gris_virage_45_left.ini", "Left 45", ""),
    ("M_gris_virage_45_right.ini", "Right 45", ""),
    ("M_gris_rampe_30_up.ini", "Up 30", ""),
    ("M_gris_rampe_30_down.ini", "Down 30", ""),
    ("M_none_start.ini", "Start", ""),
    ("M_none_startfinish.ini", "Start/Finish", ""),
    ("M_none_checkpoint.ini", "Checkpoint", ""),
    ("M_none_finish_50.ini", "Finish", ""),
    ("M_gris_to_S_50.ini", "Medium to Small 50", ""),
    ("M_none_cache_out.ini", "Cache Out", ""),
    ("M_none_cache_in.ini", "Cache In", ""),
)
TRACKPARTS_GOLF = (
    ("G_none_checkpoint.ini", "Checkpoint", ""),
    ("G_none_finish.ini", "Finish", ""),
)


def from_dropdown(scene):
    props = scene.madtracks
    # use the active descriptor set in the trackpart editor
    if props.trackpart_category == "S":
        return props.trackpart_small
    elif props.trackpart_category == "M":
        return props.trackpart_medium
    elif props.trackpart_category == "G":
        return props.trackpart_golf


def add_user(scene, descriptor):
    """
    Used to handle trackparts selected by the user.
    """
    props = scene.madtracks
    filepath = props.settings_madtracks_dir + DESCRIPTOR_PATH + descriptor

    # look for a selected trackpart to append to
    prev = None
    sel = bpy.context.selected_objects
    if len(sel) == 1 and sel[0].madtracks.is_trackpart:
        prev = sel[0]
    elif len(sel) > 1:
        set_error('adding trackpart', "Please select one object at most")
        return
    # don't reuse already imported since it could be a custom modified version
    descriptor_in.import_file(filepath, scene)
    obj = bpy.context.active_object
    # call method shared with level importer
    add(scene, obj, prev)
    # move trackpart to 3D cursor if standalone
    if not prev:
        obj.location = bpy.context.scene.cursor_location
    # update selection
    if prev:
        prev.select = False
    obj.select = True


def add(scene, obj, prev=None):
    eps = 0.00001
    if not prev:
        # new trackpart sequence
        sequence = bpy.data.groups.new("Sequence")
        bpy.ops.object.group_link(group=sequence.name)
    else:
        # add to trackpart sequence
        bpy.ops.object.group_link(group=prev.users_group[0].name)
        # compute rotation
        dummy_rotmat = mathutils.Matrix([prev.madtracks.dummy_rot1, prev.madtracks.dummy_rot2, prev.madtracks.dummy_rot3, prev.madtracks.dummy_rot4])
        dummy_roteuler = dummy_rotmat.to_euler()
        obj.rotation_euler = prev.rotation_euler
        if prev.madtracks.invert:
            obj.rotation_euler.rotate_axis("Z", 3.141593)
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
    
    if obj.madtracks.invert:
        # all stock trackparts which are inverted either have no rotation offset or 90 Z rotation offset
        # maybe it was a hack to avoid making more models and fit in Xbox Live, just like having to compute every trackpart position
        # 1) apply additional rotation
        dummy_rotmat = mathutils.Matrix([obj.madtracks.dummy_rot1, obj.madtracks.dummy_rot2, obj.madtracks.dummy_rot3, obj.madtracks.dummy_rot4])
        dummy_roteuler = dummy_rotmat.to_euler()
        if abs(dummy_roteuler[2]) < eps:
            # a. no rotation offset, rotate 180 on Z
            obj.rotation_euler.rotate_axis("Z", 3.141593)
        else:
            # b. rotation offset, apply own endpoint rotation
            obj.rotation_euler.rotate_axis("Z", dummy_roteuler[2])
        # 2) apply inverse of own dummy position offset
        obj_pos = np.array(obj.location)
        obj_rot = np.array(obj.rotation_euler.to_matrix())
        dummy_pos = obj.madtracks.dummy_pos
        dummy_pos = np.matmul(dummy_pos, np.transpose(obj_rot))
        obj.location = np.add(obj_pos, -dummy_pos)
