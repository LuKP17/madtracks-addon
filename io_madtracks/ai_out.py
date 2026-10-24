# Copyright (C) 2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    ai_out
Purpose: Exports level .gra files.

Description:
GRA level files contain nodes and edges for AI navigation.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(madini)
    imp.reload(ai)

import bpy

from . import common
from . import madini
from . import ai

from .common import *
from .madini import *
from .ai import *


def export_file(filepath, scene):
    """
    Imports AI paths as Blender nodes by reading the level .gra file.
    """
    props = scene.madtracks
    # ensure node names are correct
    ai.rename_nodes(scene)
    # export level .gra file (underlying format is still the INI dialect)
    with open(filepath, 'w') as fgra:
        # empty line like the original levels
        fgra.write("\n")
        # export nodes
        for i in range(len(scene.objects)-1, -1, -1):
            obj = scene.objects[i]
            if obj.madtracks.is_ainode:
                export_ai_node(fgra, obj)
        # export edges
        for i in range(len(scene.objects)-1, -1, -1):
            obj = scene.objects[i]
            if obj.madtracks.is_ainode:
                if obj.madtracks.prev:
                    # reverse link for branching paths (transform to forward link)
                    export_ai_edge(fgra, obj.madtracks.prev, obj)
                if obj.madtracks.nextt:
                    # forward link, export if no reverse link
                    if not obj.madtracks.nextt.madtracks.prev == obj:
                        export_ai_edge(fgra, obj, obj.madtracks.nextt)


def export_ai_node(fgra, node):
    """ Writes a Blender empty object as a node in the level AI file. """
    fgra.write("[Node]\n")
    node_id = node.name.split('_', 1)[-1]
    # nodes can have .00X suffix if a node with the same name was deleted from the scene while pointed by other nodes
    node_id = node_id.split('.', 1)[0]
    fgra.write("ID = " + str(node_id) + "\n")
    position = to_madtracks_axis(node.location)
    fgra.write("Position = " + float_format(position[0]) + "," + float_format(position[1]) + "," + float_format(position[2]) + "\n")
    if node.madtracks.roadwidth > 0.0:
        fgra.write("RoadWidth = " + float_format(node.madtracks.roadwidth) + "\n")
    if node.madtracks.motivboost > 0.0:
        fgra.write("MotivBoost = " + float_format(node.madtracks.motivboost) + "\n")
    if node.madtracks.speedexpected > 0.0:
        fgra.write("SpeedExpected = " + float_format(node.madtracks.speedexpected) + "\n")
    fgra.write("\n")


def export_ai_edge(fgra, in_node, out_node):
    """ Writes a Blender empty object as edges in the level AI file. """
    fgra.write("[Edge]\n")
    in_id = in_node.name.split('_', 1)[-1]
    out_id = out_node.name.split('_', 1)[-1]
    # nodes can have .00X suffix if a node with the same name was deleted from the scene while pointed by other nodes
    in_id = in_id.split('.', 1)[0]
    out_id = out_id.split('.', 1)[0]
    fgra.write("In = " + in_id + "\n")
    fgra.write("Out = " + out_id + "\n\n")
