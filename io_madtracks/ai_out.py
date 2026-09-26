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
    # export level .gra file (underlying format is still the INI dialect)
    with open(filepath, 'w') as fgra:
        # empty line like the original levels
        fgra.write("\n")
        start_node = props.ai_startnode
        # export nodes
        if start_node and scene.objects.find(start_node.name) != -1 and start_node.madtracks.nextt:
            export_ai_node(fgra, start_node)
            node = start_node.madtracks.nextt
            while node and scene.objects.find(node.name) != -1:
                export_ai_node(fgra, node)
                node = node.madtracks.nextt
        else:
            set_error('exporting AI paths', "Invalid start node")
            return

        # export edges
        export_ai_edges(fgra, start_node)
        node = start_node.madtracks.nextt
        while node and scene.objects.find(node.name) != -1:
            export_ai_edges(fgra, node)
            node = node.madtracks.nextt


def export_ai_node(fgra, node):
    """ Writes a Blender empty object as a node in the level AI file. """
    fgra.write("[Node]\n")
    fgra.write("ID = " + node.name.split('-', 1)[0] + "\n")
    position = to_madtracks_axis(node.location)
    fgra.write("Position = " + float_format(position[0]) + "," + float_format(position[1]) + "," + float_format(position[2]) + "\n")
    if node.madtracks.roadwidth > 0.0:
        fgra.write("RoadWidth = " + float_format(node.madtracks.roadwidth) + "\n")
    if node.madtracks.motivboost > 0.0:
        fgra.write("MotivBoost = " + float_format(node.madtracks.motivboost) + "\n")
    fgra.write("\n")


def export_ai_edges(fgra, obj):
    """ Writes a Blender empty object as edges in the level AI file. """
    if '-' in obj.name and obj.name[-1] != '-':
        in_node = obj.name.split('-', 1)[0]
        if obj.name[-1] == ',':
            obj.name = obj.name[:-1]
        out_nodes = obj.name.split('-', 1)[1].split(',')
        for out_node in out_nodes:
            fgra.write("[Edge]\n")
            fgra.write("In = " + in_node + "\n")
            fgra.write("Out = " + out_node + "\n\n")
