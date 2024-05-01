# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    trackpart_in
Purpose: Imports trackparts.

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
from . import madinix

from .common import *
from .ldo_in import *
from .object_in import *
from .madstructs import *
from .madini import *

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
        "pos_offset" : [0, -10.9245, 40.3482],
        "rot_offset" : [30, 0, 0]
    },
    "M_none_checkpoint.ini" : {
        "pos_offset" : [0, 0, 0],
        "rot_offset" : [0, 0, 0]
    },
}

def update_anchor(descriptor, anchorPos, anchorRot):
    """
    Given a trackpart descriptor name and it's anchor,
    return the updated anchor corresponding to the next trackpart's anchor.
    """
    # rotate pos_offset vector by trackpart's rotation
    pos_vec = to_blender_axis(trackparts[descriptor]["pos_offset"])
    rotation_x = np.array([[1, 0, 0],
                           [0, np.cos(anchorRot[0]), -np.sin(anchorRot[0])],
                           [0, np.sin(anchorRot[0]), np.cos(anchorRot[0])]])

    rotation_y = np.array([[np.cos(anchorRot[1]), 0, np.sin(anchorRot[1])],
                           [0, 1, 0],
                           [-np.sin(anchorRot[1]), 0, np.cos(anchorRot[1])]])

    rotation_z = np.array([[np.cos(anchorRot[2]), -np.sin(anchorRot[2]), 0],
                           [np.sin(anchorRot[2]), np.cos(anchorRot[2]), 0],
                           [0, 0, 1]])
    pos_vec = np.dot(rotation_x, pos_vec)
    pos_vec = np.dot(rotation_y, pos_vec)
    pos_vec = np.dot(rotation_z, pos_vec)
    
    # update anchorPos
    anchorPos = np.add(anchorPos, pos_vec)
    
    # update anchorRot
    rot_vec = to_blender_axis(trackparts[descriptor]["rot_offset"])
    rot_vec[0] = rot_vec[0]/180*np.pi
    rot_vec[1] = rot_vec[1]/180*np.pi
    rot_vec[2] = rot_vec[2]/180*np.pi
    anchorRot = np.add(anchorRot, rot_vec)
    
    return anchorPos, anchorRot
