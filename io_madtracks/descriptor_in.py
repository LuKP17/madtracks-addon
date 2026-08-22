# Copyright (C) 2024-2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    descriptor_in
Purpose: Imports Descriptor INI files

Description:
Descriptors include a LDO with a separate collision mesh, lights, cameras, pickups, game zones...

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


def import_file(filepath, scene, lightmap=None):
    """
    Imports a descriptor .ini file as a Blender object.
    """
    props = scene.madtracks

    with open_insensitive(filepath, 'r') as file:
        # read the .ini file
        ini = INI(file).as_dict()
        obj = None

        filename = None
        if "filename" in ini['object'].keys():
            filename = ini['object']['filename']
            if ".ldo" in filename:
                ldoname = filename.split("/", 1)[1] # strip "geometry/"
                # Handle .ldo filenames that differ between the descriptor parameter and the actual filename
                # TODO the "_High" suffix needs to be automatically searched by the .ldo importer
                if ldoname == "ant_out_sea.ldo":
                    ldoname = "ant_out_sea_high.ldo"
                elif ldoname == "ger_eau.ldo":
                    ldoname = "ger_eau_high.ldo"
                elif ldoname == "ger_eau_puit.ldo":
                    ldoname = "ger_eau_puit_high.ldo"
                elif ldoname == "ant_eau.ldo":
                    ldoname = "ant_eau_high.ldo"

                # import LDO
                ldo_in.import_file(props.settings_madtracks_dir + LDO_PATH + ldoname, scene, lightmap)
                obj = bpy.context.active_object
                if "objecttype" in ini['object'].keys() and ini['object']['objecttype'] in trackpart_types:
                    # assign trackpart properties
                    obj.madtracks.is_trackpart = True
                    if "invert" in ini['object'].keys():
                        obj.madtracks.invert = ini['object']['invert']

        if not obj and "objecttype" in ini['object'].keys():
            # no LDO, create a Blender object matching the type
            object_type = ini['object']['objecttype']
            if object_type == "minimap":
                # Images as Planes
                filename = ini['object']['filename'].split("/")[-1]
                bpy.ops.import_image.to_plane(files=[{"name":filename, "name":filename}], directory=props.settings_madtracks_dir + HUD_PATH, align_axis='Z+', relative=False)
            elif object_type == "light":
                # Lamp
                bpy.ops.object.lamp_add(type='POINT')
                obj = bpy.context.active_object
                obj.data.energy = 0
            elif object_type in ["gamearea", "cameraarea"]:
                bpy.ops.object.empty_add(type='CUBE')
            else:
                # from primitive
                if "primitivetype" in ini['object'].keys():
                    primitive_type = ini['object']['primitivetype']
                    if primitive_type == "box":
                        bpy.ops.object.empty_add(type='CUBE')
                    elif primitive_type == "sphere":
                        bpy.ops.object.empty_add(type='SPHERE')
                    elif primitive_type == "capsule":
                        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1, depth=2)
                        obj = bpy.context.active_object
                        bpy.context.object.draw_type = 'WIRE'
                    else:
                        set_error('importing descriptor', "Unknown primitive type \"%s\" for %s" % (primitive_type, filepath))
                        return False
                else:
                    bpy.ops.object.empty_add(type='PLAIN_AXES')
            obj = bpy.context.active_object
            obj.select = False

        # parse descriptor parameters (see _tutorial.txt)
        parse_parameters(ini['object'], props)

        # set name and descriptor
        obj.madtracks.descriptor = filepath.split(os.path.sep)[1]
        obj.name = obj.madtracks.descriptor.rsplit(".")[0]
        if lightmap:
            # reinstate lightmap suffix on the object to not be reused later
            obj.name = obj.name + "_lgt"
    
    dprint("Imported {}".format(os.path.basename(filepath)))

    return True


def parse_parameters(section, props):
    for param in section.keys():
        if param == "lengths":
            lengths = section[param]
            obj = bpy.context.active_object
            obj.dimensions[0] = to_blender_scale(lengths[0])
            obj.dimensions[1] = to_blender_scale(lengths[2])
            obj.dimensions[2] = to_blender_scale(lengths[1])
            # if not props.instance_mode:
                # TODO also import as metadata
