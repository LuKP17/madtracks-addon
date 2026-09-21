# Copyright (C) 2024-2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    ai
Purpose: AI paths operators.

Description:

"""

if "bpy" in locals():
    import imp
    imp.reload(common)

from . import common
from .common import *


def add_node(scene):
    if bpy.data.groups.find("Paths") == -1:
        bpy.data.groups.new("Paths")
    
    sel = bpy.context.selected_objects
    prev = None
    if len(sel) == 1:
        prev = sel[0]
    bpy.ops.object.empty_add(type='SPHERE', radius=2)
    bpy.ops.object.group_link(group="Paths")
    node = scene.objects.active
    node.name = "AINode"
    if prev:
        prev.madtracks.nextt = node


def link_nodes(start_node):
    node_id = 0
    reset_nodes()
    if start_node.madtracks.nextt:
        start_node.name = "{}-{}".format(str(node_id), str(node_id + 1))
        node_id += 1
        nextt = start_node.madtracks.nextt
        while nextt:
            nextt.name = str(node_id) + '-'
            if nextt.madtracks.nextt:
                if nextt.madtracks.nextt == start_node:
                    # closed loop
                    nextt.name = nextt.name + str(0)
                    break
                else:
                    nextt.name = nextt.name + str(node_id + 1)
            node_id += 1
            nextt = nextt.madtracks.nextt
    else:
        set_error('linking nodes', "Start node doesn't point to a next node")


def reset_nodes():
    """ Sometimes necessary when relinking nodes """
    for node in bpy.data.groups['Paths'].objects:
        node.name = "AINode"


# def draw_paths(scene, start_node):
#     bpy.ops.curve.primitive_bezier_curve_add(radius=1, location=start_node.location)
#     curve = scene.objects.active
#     curve.data.resolution_u = 1
#     # curve.data.splines[0].bezier_points[0].co is a local coordinate, use the curve object position to feed the node position in local coords 
