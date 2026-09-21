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
    group_idx = bpy.data.groups.find("Paths")
    if group_idx == -1:
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
        scene.objects.active = prev
        prev.select = True
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        prev.select = False
        scene.objects.active = node


def link_nodes(start_node):
    node_id = 0
    reset_nodes()
    if not start_node.parent and start_node.children[0]:
        start_node.name = str(node_id) + '-'
        node_id += 1
        nextt = start_node.children[0]
        while nextt:
            nextt.name = str(node_id) + '-'
            nextt.parent.name = nextt.parent.name.split('.', 1)[0] + str(node_id)
            node_id += 1
            nextt = nextt.children[0] if nextt.children else None
    else:
        set_error('linking nodes', "Invalid start node")


def reset_nodes():
    """ Sometimes necessary when relinking nodes """
    for node in bpy.data.groups['Paths'].objects:
        node.name = "AINode"
