# Copyright (C) 2024-2026  Lucas Pottier
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
    
    for obj in bpy.data.objects:
        object_to_atomic(obj, ldo)
        ldo.atomic_cnt += 1

    # export LDO data
    with open_insensitive(filepath, 'wb') as file:
        filename = os.path.basename(filepath)
        # write the .ldo file
        ldo.write(file, props.ldo_debug_info)

    dprint("Exported {}".format(filename))


def object_to_atomic(obj, ldo):
    """
    Converts a Blender object's data into atomic data
    and stores it in a LDO structure.
    """
    mesh = obj.data
    atomic = Atomic()
    atomic.mesh_cnt = 1
    if not(mesh.vertices):
        atomic.is_empty = True
        ldo.atomics.append(atomic)
        return
    
    for material in mesh.materials:
        madmat = Material()
        madmat.name_len = len(material.name.split(".", 1)[0])
        madmat.name = material.name.split(".", 1)[0]
        
        if material.madtracks.has_rgba:
            madmat.flags |= MAT_FLAG_RGBA
            madmat.RGBA += (int(material.diffuse_color[0] * 255),
                            int(material.diffuse_color[1] * 255),
                            int(material.diffuse_color[2] * 255),
                            int(material.alpha * 255),)
        
        if material.madtracks.has_brightness:
            madmat.flags |= MAT_FLAG_BRIGHTNESS
            madmat.brightness = float(material.diffuse_intensity * 2 - 1)
        
        # allow for having textures in any slot and check for excessive textures
        for texslot in material.texture_slots:
            if not(texslot):
                continue
            elif texslot.blend_type != "SOFT_LIGHT" and madmat.diffuse_name_len == 0:
                madmat.diffuse_name_len = len(texslot.texture.name.split(".", 1)[0])
                madmat.diffuse_name = texslot.texture.name.split(".", 1)[0]
                madmat.flags |= MAT_FLAG_DIFFUSE
            elif texslot.blend_type == "SOFT_LIGHT" and madmat.envmap_name_len == 0:
                madmat.envmap_name_len = len(texslot.texture.name.split(".", 1)[0])
                madmat.envmap_name = texslot.texture.name.split(".", 1)[0]
                madmat.flags |= MAT_FLAG_ENVMAP
            else:
                print("WARNING: skipping excessive textures for Blender material {}.".format(material.name))
                print("Check that the material has only one diffuse texture and only one envmap texture (blend type \"Soft Light\")")
        
        atomic.materials.append(madmat)
        atomic.material_cnt += 1
        
    # mesh. ...
    # len(mesh.materials)
    # loop mesh.polygons
        # add poly to tri sequence corresponding to material assigned
    
    ldo.atomics.append(atomic)
