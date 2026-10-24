# Copyright (C) 2026  Lucas Pottier
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
GRA level files contain nodes and edges for AI navigation.
The file is loaded sequentially in-game, the only rule is to load an edge after loading the In and Out nodes.
Start nodes aren't a thing. The main path doesn't need to loop even for lap races, and closing the loop won't
make the AI cars loop smoothly.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)

from . import common

from .common import *


def add_node(scene):
    bpy.ops.object.empty_add(type='SPHERE', radius=2)
    node = scene.objects.active
    node.name = "AInode"
    node.madtracks.is_ainode = True


def rename_nodes(scene):
    """
    Nodes IDs are defined in their names.
    """
    # reset all node names to avoid .00X suffixes
    for obj in scene.objects:
        if obj.madtracks.is_ainode:
            obj.name = "AInode_"
    node_id = 0
    # add node ID in the name, looping in reverse creation date
    for i in range(len(scene.objects)-1, -1, -1):
        obj = scene.objects[i]
        if obj.madtracks.is_ainode:
            obj.name = "AInode_" + str(node_id)
            node_id += 1


def draw_paths(scene, context):
    """ Draw edges that will be exported for preview. """
    # clear previous edges
    bpy.ops.object.select_pattern(pattern="AIedges", extend=False)
    bpy.ops.object.delete()
    bpy.ops.curve.primitive_nurbs_path_add(location=(0,0,0))
    edges = scene.objects.active
    edges.name = "AIedges"
    edges.data.show_handles = False
    # create paths in edit mode to group them into a single object
    bpy.ops.object.editmode_toggle()
    for i in range(len(scene.objects)-1, -1, -1):
        obj = scene.objects[i]
        if obj.madtracks.is_ainode:
            if obj.madtracks.prev:
                # reverse link for branching paths (transform to forward link)
                add_path(edges, obj.madtracks.prev.location, obj.location)
            if obj.madtracks.nextt:
                # forward link, export if no reverse link
                if not obj.madtracks.nextt.madtracks.prev == obj:
                    add_path(edges, obj.location, obj.madtracks.nextt.location)
    bpy.ops.curve.select_all(action="SELECT")
    bpy.ops.object.editmode_toggle()
    # remove base spline created with the object
    edges.data.splines.remove(edges.data.splines[0])
    # set normal size higher for convenience
    scene.tool_settings.normal_size = 2


def add_path(obj, pos_in, pos_out):
    bpy.ops.curve.primitive_nurbs_path_add(location=(0,0,0))
    path = obj.data.splines[len(obj.data.splines)-1]
    path.points[0].select = False
    path.points[1].select = False
    bpy.ops.curve.delete(type='VERT')
    path.points[0].co[0] = pos_in[0]
    path.points[0].co[1] = pos_in[1]
    path.points[0].co[2] = pos_in[2]
    path.points[0].co[3] = 1
    path.points[1].co[0] = pos_out[0]
    path.points[1].co[1] = pos_out[1]
    path.points[1].co[2] = pos_out[2]
    path.points[1].co[3] = 1
