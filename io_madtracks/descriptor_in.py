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
        ini = INI(file)
        ini_dic = ini.as_dict()
        obj = None

        filename = None
        if "filename" in ini_dic['object'].keys():
            filename = ini_dic['object']['filename']
            if ".ldo" in filename:
                ldoname = None
                for p in ini.sections[0].params:
                    if p.name.lower() == "filename":
                        ldoname = p.value.split("/", 1)[1] # strip "geometry/"
                # Handle .ldo filenames that differ between the descriptor parameter and the actual filename
                # TODO the "_High" suffix needs to be automatically searched by the .ldo importer
                if ldoname.lower() == "ant_out_sea.ldo":
                    ldoname = "ANT_Out_Sea_High.ldo"
                elif ldoname.lower() == "ger_eau.ldo":
                    ldoname = "GER_Eau_High.ldo"
                elif ldoname.lower() == "ger_eau_puit.ldo":
                    ldoname = "GER_Eau_Puit_High.ldo"
                elif ldoname.lower() == "ant_eau.ldo":
                    ldoname = "ANT_Eau_high.ldo"

                # import LDO
                ldo_in.import_file(props.settings_madtracks_dir + LDO_PATH + ldoname, scene, lightmap)
                obj = bpy.context.active_object
                if "objecttype" in ini_dic['object'].keys() and ini_dic['object']['objecttype'] in trackpart_types:
                    # assign trackpart properties
                    obj.madtracks.is_trackpart = True
                    if "invert" in ini_dic['object'].keys():
                        obj.madtracks.invert = ini_dic['object']['invert']

        if not obj and "objecttype" in ini_dic['object'].keys():
            # no LDO, create a Blender object matching the type
            object_type = ini_dic['object']['objecttype']
            if object_type == "minimap":
                # Image Empty as Linux doesn't have Images as Planes
                filename = ini_dic['object']['filename'].split("/")[-1]
                bpy.ops.object.empty_add(type='IMAGE')
                imagepath = filepath_insensitive(props.settings_madtracks_dir + HUD_PATH + filename)
                filename = imagepath.rsplit(os.path.sep, 1)[-1]
                bpy.ops.image.open(filepath=imagepath, directory=props.settings_madtracks_dir + HUD_PATH, files=[{"name":filename, "name":filename}])
                obj = bpy.context.active_object
                obj.data = bpy.data.images[filename]
            elif object_type == "light":
                # Lamp
                bpy.ops.object.lamp_add(type='POINT')
                import_light(ini_dic['object'], props)
            elif object_type in ["gamearea", "cameraarea"]:
                bpy.ops.object.empty_add(type='CUBE')
            else:
                # from primitive
                if "primitivetype" in ini_dic['object'].keys():
                    primitive_type = ini_dic['object']['primitivetype']
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

        # parse remaining parameters
        import_misc_params(ini_dic['object'], props)

        # set name and descriptor
        obj.madtracks.descriptor = filepath.rsplit(os.path.sep, 1)[1]
        obj.name = obj.madtracks.descriptor.split(".")[0]
        if lightmap:
            # reinstate lightmap suffix on the object to not be reused later
            obj.name = obj.name + "_lgt"
    
    dprint("Imported {}".format(os.path.basename(filepath)))

    return True


def import_misc_params(section, props):
    """
    Handle optional parameters and parameters shared between object types.
    """
    for param in section.keys():
        if param == "lengths":
            lengths = section[param]
            obj = bpy.context.active_object
            obj.dimensions[0] = to_blender_scale(lengths[0])
            obj.dimensions[1] = to_blender_scale(lengths[2])
            obj.dimensions[2] = to_blender_scale(lengths[1])
            # if not props.instance_mode:
                # TODO also import as metadata


LIGHT_SHAPE_DIRECTIONAL = 0
LIGHT_SHAPE_AMBIENT     = 1
LIGHT_SHAPE_POINT       = 2

LIGHT_METHOD_LIGHTMAP   = 3
def import_light(section, props):
    """
    Handle light specific parameters.
    Expects required parameters to be present (see _tutorial.txt in Descriptors game data folder)
    """
    obj = bpy.context.active_object

    # set Blender specific parameters
    obj.data.use_specular = False

    # light color
    rgb = section['rgbcolor']
    rgb = to_blender_color(rgb)

    # light type
    shape = section['lightshape']
    if shape == LIGHT_SHAPE_DIRECTIONAL:
        obj.data.type = 'SUN'
        obj.data.color = rgb
    elif shape == LIGHT_SHAPE_AMBIENT:
        # ambient light objects shouldn't emit light themselves 
        obj.data.energy = 0
        bpy.context.scene.world.light_settings.use_environment_light = True
        bpy.context.scene.world.light_settings.environment_color = 'SKY_COLOR'
        # FIXME overwrites level world's sky color
        bpy.context.scene.world.horizon_color = rgb
        bpy.context.scene.world.zenith_color = rgb
    elif shape == LIGHT_SHAPE_POINT:
        obj.data.type = 'POINT'
        obj.data.color = rgb
        obj.data.distance = float(section['radius'])
    
    # light method
    method = section['lightingmethod']
    if method == LIGHT_METHOD_LIGHTMAP:
        # light only shows up in the lightmap image
        bpy.context.object.hide_render = True

    # optional light param
    bpy.context.object.data.shadow_method = 'RAY_SHADOW' # default
    if 'dontcastshadow' in section.keys():
        if section['dontcastshadow'] == 1:
            bpy.context.object.data.shadow_method = 'NOSHADOW'
