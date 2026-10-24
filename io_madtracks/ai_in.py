# Copyright (C) 2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    ai_in
Purpose: Imports level .gra files.

Description:

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


def import_file(filepath, scene):
    """
    Imports AI paths as Blender nodes by reading the level .gra file.
    """
    props = scene.madtracks
    # import level .gra file (underlying format is still the INI dialect)
    with open_insensitive(filepath, 'r') as file:
        ini = INI(file)
    import_ai_paths(ini, scene)


def import_ai_paths(ini, scene):
    node = None
    for section in ini.sections:
        if section.name.lower() == "node":
            ai.add_node(scene)
            node = scene.objects.active
            for param in section.params:
                if param.name.lower() == "id":
                    node.name = node.name + '_' + str(param.value)
                elif param.name.lower() == "position":
                    node.location = to_blender_axis(param.value)
                elif param.name.lower() == "motivboost":
                    node.madtracks.motivboost = param.value
                elif param.name.lower() == "roadwidth":
                    node.madtracks.roadwidth = param.value
                elif param.name.lower() == "speedexpected":
                    node.madtracks.speedexpected = param.value
        elif section.name.lower() == "edge":
            for param in section.params:
                if param.name.lower() == "in":
                    node = scene.objects["AInode_{}".format(param.value)]
                elif param.name.lower() == "out":
                    if not node.madtracks.nextt:
                        node.madtracks.nextt = scene.objects["AInode_{}".format(param.value)]
                    else:
                        # mark branching path with reverse links (can't assign multiple next nodes)
                        nextt = node.madtracks.nextt
                        nextt.madtracks.prev = node
                        scene.objects["AInode_{}".format(param.value)].madtracks.prev = node
