# Copyright (C) 2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    ldl_in
Purpose: Imports .ldl files.

Description:
A LDL file is made of a sequence of game models with lightmap image UV data.
Although not handled here, these models are matched with the associated level INI instances
in order when loading a level, with a few exceptions for collectibles or moving/animated instances.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(ldo_in)
    imp.reload(madstructs)

import os
import bpy

from . import common
from . import ldo_in
from . import madstructs

from .common import *
from .ldo_in import *
from .madstructs import *


def import_file(filepath, scene):
    """
    Imports a lightmap as Blender objects by reading the .ldl file.
    """
    props = scene.madtracks

    props.as_instance = True
    props.reuse_data = True

    # open lightmap file and read instances
    filename = os.path.basename(filepath)
    with open_insensitive(filepath, 'rb') as file:
        lightmap = LDL(file)
        success = lightmap.read_header()
        if success:
            props.lightmap_bitdepth = lightmap.bit_depth
        else:
            set_error('importing lightmap', "Invalid lightmap file")
            return
        for _ in range(lightmap.instance_cnt):
            lightmap.read_instance(debug=True)
            ldoname = lightmap.current_name.split("/", 1)[1]
            if ldoname == "rampe_30.ldo":
                ldoname = "rampe_30_up.ldo"
            if not lightmap.is_empty:
                ldo_in.import_file(props.madtracks_dir + LDO_PATH + ldoname, scene, lightmap)
            # make lightmap UV layer active
            obj = scene.objects.active
            obj.data.uv_textures.active = obj.data.uv_textures["LightMap"]
    
    bpy.ops.object.select_all(action='DESELECT')
