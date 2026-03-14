# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
#  Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    ldo_out
Purpose: Exports .ldo files

Description:
Export Blender objects as atomics in a .ldo file.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(madstructs)

import os
import bpy
import bmesh

from . import common
from . import madstructs

from .madstructs import *
from .common import *


def export_file(filepath, scene):
    """
    Exports Blender objects in a .ldo file
    Each Blender object is exported as an atomic,
    and their meshes as atomic meshes.
    """
    props = scene.madtracks
    
    ldo = LDO()
    
    # no data relation found between Blender's objects and meshes
    for obj, mesh in zip(bpy.data.objects, bpy.data.meshes):
        object_to_atomic(obj, mesh, ldo)
        ldo.atomic_cnt += 1

    # export LDO data
    with open(filepath, 'wb') as file:
        filename = os.path.basename(filepath)
        # write the .ldo file
        ldo.write(file, props.ldo_debug_info)

    dprint("Exported {}".format(filename))


def object_to_atomic(obj, mesh, ldo):
    """
    Converts a Blender object's data into atomic data
    and stores it in a LDO structure.
    """
    atomic = Atomic()
    atomic.mesh_cnt = 1
    atomic.material_cnt = len(mesh.materials)
    
    ldo.atomics.append(atomic)
