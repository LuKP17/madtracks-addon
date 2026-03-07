# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    object_in
Purpose: Imports Objects (.ini descriptors)

Description:
Objects include geometry with a different collision mesh, lights, cameras, pickups, game zones...
They are defined in .ini descriptors.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(madini)
    imp.reload(ldo_in)

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

        # import the .ldo found or node.ldo if the object doesn't have geometry attached to it
        if "Filename" in ini['object'].keys():
            if ".ldo" in ini['object']['Filename']:
                ldoFilename = ini['object']['Filename'].split("/", 1)[1] # strip useless "geometry/"
                # handle .ldo filenames that differ between the descriptor parameter and the actual filename
                # Keep searching for descriptors .ldo filenames that do not exist
                # Maybe the "_High" suffix needs to be automatically searched by the .ldo importer?
                if ldoFilename == "ANT_Out_Sea.ldo":
                    ldoFilename = "ANT_Out_Sea_High.ldo"
                elif ldoFilename == "GER_Eau.ldo":
                    ldoFilename = "GER_Eau_High.ldo"
                elif ldoFilename == "GER_Eau_Puit.ldo":
                    ldoFilename = "GER_Eau_Puit_High.ldo"
                elif ldoFilename == "ANT_Eau.ldo":
                    ldoFilename = "ANT_Eau_High.ldo"
            else:
                # the filename isn't a .ldo file
                ldoFilename = "node.ldo"
        else:
            # no filename in descriptor
            ldoFilename = "node.ldo"
        
        obj = ldo_in.import_file(props.madtracks_dir + LDO_PATH + ldoFilename, scene)
        
        # transfer properties from object to Blender object
        obj.madtracks.descriptor = filepath.split("\\")[-1]
        if "ObjectType" in ini['object'].keys() and (ini['object']['ObjectType'] in ["trackpart", "start", "startfinish", "checkpoint", "finish", "looping"]):
            obj.madtracks.is_trackpart = True
            if "Invert" in ini['object'].keys():
                obj.madtracks.invert = ini['object']['Invert']

    return obj
