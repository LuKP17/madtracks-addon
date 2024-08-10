# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    object_in
Purpose: Imports objects (.ini descriptors)

Description:
Objects include geometry with added properties, lights, cameras, pickups, game zones...

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(madini)
    imp.reload(ldo_in)

# from mathutils import Color, Vector
from . import common
from . import madini
from . import ldo_in

from .common import *
from .madini import *
from .ldo_in import *


def import_file(filepath, scene):
    """
    Imports a descriptor .ini file.
    Returns a Blender object with geometry data and added Mad Tracks properties.
    """
    props = scene.madtracks
    with open(filepath, 'r') as file:
        # read the .ini file
        ini = INI(file).as_dict()

        # import the .ldo found or "node.ldo" and retrieve the Blender object
        if "Filename" in ini['object'].keys():
            ldoFilename = ini['object']['Filename'].split("/", 1)[1] # strip useless "geometry/"
        else:
            ldoFilename = "node.ldo"
        obj = ldo_in.import_file(props.madtracks_dir + LDO_PATH + ldoFilename, scene)
        
        # transfer properties from object to Blender object
        obj.madtracks.descriptor = filepath.split("\\")[-1]
        if "ObjectType" in ini['object'].keys() and (ini['object']['ObjectType'] in ["trackpart", "start", "startfinish", "checkpoint", "finish", "looping"]):
            obj.madtracks.is_trackpart = True
            if "Invert" in ini['object'].keys():
                obj.madtracks.invert = ini['object']['Invert']

    return obj
