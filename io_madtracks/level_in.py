# Copyright (C) 2024-2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    level_in
Purpose: Imports level .ini files.

Description:
Level files contain LDO level instances from Gfx\models\Geometry and
Object level instances from Bin\Descriptors.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(ldo_in)
    imp.reload(descriptor_in)
    imp.reload(madstructs)
    imp.reload(madini)
    imp.reload(trackpart)

import os
import bpy

import numpy as np

from . import common
from . import ldo_in
from . import descriptor_in
from . import madstructs
from . import madini
from . import trackpart

from .common import *
from .ldo_in import *
from .descriptor_in import *
from .madstructs import *
from .madini import *
from .trackpart import *

WORLD_FRA_BISTRO    = 0
WORLD_DEV_ONE       = 1  # dev test world
WORLD_DEV_TWO       = 2  # dev test world
WORLD_UK_MINIGOLF   = 3
WORLD_GER_BAL       = 4
WORLD_UK_STAIRS     = 5
WORLD_USA_ROOF      = 6
WORLD_GER_REMP      = 7
WORLD_USA_TOY       = 8
WORLD_FRA_MUSEE     = 9
WORLD_ANT           = 10
WORLD_DEV_LABO      = 11  # dev test world

world_filenames = [
    "FrBistrot.ini",
    "WorldTest.ini",
    "WorldTest.ini",
    "UkMiniGolf.ini",
    "GerBal.ini",
    "UkStairs.ini",
    "UsRoofs.ini",
    "GerRamparts.ini",
    "US_ToyStore.ini",
    "FR_Musee.ini",
    "Antartique.ini",
    "Labo.ini"
]


def import_file(filepath, scene):
    """
    Imports a level as Blender objects by reading the level .ini file.
    """
    props = scene.madtracks

    # enable instance mode
    instance_mode_save = props.instance_mode
    props.instance_mode = True

    lightmap = None
    if props.level_import_lightmap:
        # open lightmap file and read first instance
        filename = os.path.basename(filepath)
        filename = filename[:-3] + "ldl"
        lightmap_file = open(props.settings_madtracks_dir + LDL_PATH + filename, 'rb')
        lightmap = LDL(lightmap_file)
        success = lightmap.read_header()
        if success:
            lightmap.read_instance(props.lightmap_debug_info)
        else:
            # give up on the lightmap
            lightmap = None

    # import world
    dam_filepath = filepath.split(".", 1)[0] + ".dam"
    with open_insensitive(dam_filepath, 'r') as settings_file:
        ini = INI(settings_file)
        world = int(ini.as_dict()['base']['world'])
        import_world(world, lightmap, scene)

    with open_insensitive(filepath, 'r') as instance_file:
        filename = os.path.basename(filepath)
        # read and store level .ini file
        ini = INI(instance_file)

        si = 0
        while si < len(ini.sections):
            # get current section and its type
            section = ini.sections[si]
            ext = section.as_dict()['filename'].split(".", 1)[1]
            # import section
            if ext == "ldo":
                success = import_LDO_instance(section, lightmap, scene)
            elif ext == "ini":
                success = import_descriptor_instance(section, lightmap, scene)
            # go to next section or stop there
            if not success:
                set_error('importing a level', "Import of level instance failed")
                return
            si += 1
    
    if lightmap:
        lightmap_file.close()
        if lightmap.instance_cnt > 0:
            set_error('importing a level', "Missed %d lightmap instances" % lightmap.instance_cnt)

    # reinstate old instance mode
    props.instance_mode = instance_mode_save

    print("Imported {}".format(filename))


def import_LDO_instance(section, lightmap, scene, ldo_filename=None):
    """
    Imports a LDO level instance from a .ini section.
    """
    props = scene.madtracks

    filename = section.as_dict()['filename']
    lightmapped = is_lightmapped(lightmap, filename)
    ldoname = filename.split("/", 1)[1].split(".", 1)[0]
    
    if not lightmapped:
        # reuse already imported instances that are not lightmapped
        obj_index = bpy.data.objects.find(ldoname)
        if obj_index >= 0:
            obj = bpy.data.objects[obj_index]
            dprint("Copying Blender object {}...".format(obj.name))
            obj = obj.copy()
            scene.objects.link(obj)
            scene.objects.active = obj
            obj.select = False
        else:
            # import LDO without lightmap to be reused
            ldo_in.import_file(props.settings_madtracks_dir + LDO_PATH + ldoname + ".ldo", scene)
            obj = bpy.context.active_object
    else:
        # import LDO and consume lightmap data
        ldo_in.import_file(props.settings_madtracks_dir + LDO_PATH + ldoname + ".ldo", scene, lightmap)
        obj = bpy.context.active_object
        lightmap.read_instance(props.lightmap_debug_info)

    # edit location and rotation of Blender object
    place_instance_object(section, obj)

    return True


def import_descriptor_instance(section, lightmap, scene):
    """
    Imports a Descriptor level instance from a .ini section.
    """
    props = scene.madtracks

    filename = section.as_dict()['filename']
    descname = filename.split(".", 1)[0]

    ldo_filename = False
    is_trackpart = False
    is_collectible = False
    with open_insensitive(props.settings_madtracks_dir + DESCRIPTOR_PATH + filename, 'r') as file:
        descriptor = INI(file).as_dict()
        if "filename" in descriptor['object'].keys() and ".ldo" in descriptor['object']['filename']:
            ldo_filename = descriptor['object']['filename']
        if "objecttype" in descriptor['object'].keys():
            if descriptor['object']['objecttype'] in trackpart_types:
                is_trackpart = True
            if descriptor['object']['objecttype'] in collectible_types:
                is_collectible = True
    
    if not props.level_import_raceline and (is_trackpart or is_collectible):
        # don't import descriptor
        if is_lightmapped(lightmap, ldo_filename):
            lightmap.read_instance()
        return True
    
    if ldo_filename:
        if not is_lightmapped(lightmap, ldo_filename):
            # reuse already imported instances that are not lightmapped
            obj_index = bpy.data.objects.find(descname)
            if obj_index >= 0:
                obj = bpy.data.objects[obj_index]
                dprint("Copying Blender object {}...".format(obj.name))
                obj = obj.copy()
                scene.objects.link(obj)
                scene.objects.active = obj
                obj.select = False
            else:
                # import descriptor without lightmap to be reused
                if not descriptor_in.import_file(props.settings_madtracks_dir + DESCRIPTOR_PATH + filename, scene):
                    return False
                obj = bpy.context.active_object
        else:
            # import descriptor and consume lightmap data
            if not descriptor_in.import_file(props.settings_madtracks_dir + DESCRIPTOR_PATH + filename, scene, lightmap):
                return False
            obj = bpy.context.active_object
            lightmap.read_instance(props.lightmap_debug_info)
    else:
        # import descriptor which doesn't have a LDO
        if not descriptor_in.import_file(props.settings_madtracks_dir + DESCRIPTOR_PATH + filename, scene):
            return False
        obj = bpy.context.active_object
        
    # edit location and rotation of Blender object
    place_instance_object(section, obj)

    if is_trackpart:
        prev = None
        if len(section.params) > 1:
            # new trackpart sequence
            trackpart.add(scene, obj)
        elif len(section.params) == 1:
            # add to trackpart sequence
            prev = bpy.context.selected_objects[0]
            trackpart.add(scene, obj, prev)
        # select the trackpart to remember it at the next iteration as *prev*
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True

    return True


def import_world(world, lightmap, scene):
    props = scene.madtracks
    filepath = props.settings_madtracks_dir + WORLD_PATH + world_filenames[world]

    with open_insensitive(filepath, 'r') as file:
        dprint("Reading world file %s..." % filepath)
        ini = INI(file)

        # import the sky color
        sky_color = ini.as_dict()['base']['skycolor']
        bpy.data.worlds[0].horizon_color = [float(sky_color[0] / 255),
                                            float(sky_color[1] / 255),
                                            float(sky_color[2] / 255)]

        # import the optional skybox
        if 'skybox' in ini.as_dict().keys():
            skybox_pos = to_blender_coord(ini.as_dict()['skybox']['position'])
            skybox_scale = to_blender_scale(ini.as_dict()['skybox']['scale'])
            bpy.ops.mesh.primitive_cube_add(location=(skybox_pos[0], skybox_pos[1], skybox_pos[2]),

                                            radius=skybox_scale,
                                            enter_editmode=True)
            bpy.ops.mesh.flip_normals()
            bpy.ops.mesh.uv_texture_add()
            obj = bpy.context.edit_object
            bpy.ops.object.editmode_toggle()
            obj.name = "Skybox"
            obj.data.name = "Skybox"
            # rotate the skybox to the right orientation
            bpy.context.object.rotation_euler[2] = 7.85398
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

            # assign skybox textures
            skybox_textures = [ini.as_dict()['skybox']['back'],
                               ini.as_dict()['skybox']['right'],
                               ini.as_dict()['skybox']['front'],
                               ini.as_dict()['skybox']['left'],
                               ini.as_dict()['skybox']['down'],
                               ini.as_dict()['skybox']['up']
                            ]
            for side in range(6):
                texture_name = skybox_textures[side]
                material = bpy.data.materials.new(texture_name)
                texslot = material.texture_slots.add()
                texture = bpy.data.textures.new(texture_name, "IMAGE")
                image = img_in.import_file(props.settings_madtracks_dir + TEXTURE_PATH + texture_name + ".dds")
                texture.image = image
                texslot.texture = texture
                # other convenient material properties
                material.specular_intensity = 0
                obj.data.materials.append(material)
                # assign to faces
                obj.data.polygons[side].material_index = side
            # fix skybox texture rotation
            mat_up = bpy.data.materials[skybox_textures[5]]
            mat_up.texture_slots[0].scale = [-1, -1, 1]

        # import the optional world mesh
        if 'mesh' in ini.as_dict()['base'].keys():
            filename = ini.as_dict()['base']['mesh']
            if is_lightmapped(lightmap, filename):
                obj = ldo_in.import_file(props.settings_madtracks_dir + LDO_PATH + filename.split("/", 1)[1], scene, lightmap)
                lightmap.read_instance(props.lightmap_debug_info)
            else:
                obj = ldo_in.import_file(props.settings_madtracks_dir + LDO_PATH + filename.split("/", 1)[1], scene)


def place_instance_object(section, obj):
    """
    Edit an instance object's location and rotation by reading a level .ini section's parameters.
    """
    if len(section.params) == 4:
        directionAT = section.as_dict()['directionat']
        directionUp = section.as_dict()['directionup']
        directionRight = np.cross(directionAT, directionUp)
        directionLeft = -directionRight

        mat = [
            (directionAT[0], directionAT[1], directionAT[2]),
            (directionUp[0], directionUp[1], directionUp[2]),
            (directionLeft[0], directionLeft[1], directionLeft[2]),
        ]

        bmat = to_blender_matrix(mat)
        obj.rotation_euler = bmat.to_euler()
        obj.location = to_blender_coord(section.as_dict()['position'])


def is_lightmapped(lightmap, filename):
    """
    Return True if the LDO to import is present in the LDL file and has lightmap data to import.
    Skip the LDL instance if it has no data to import.
    """
    if not lightmap:
        return False

    if lightmap.current_name.lower() == filename.lower() or lightmap.current_name.lower() == "geometry/rampe_30.ldo":
        if lightmap.mesh_cnt == 0 or lightmap.vertex_cnt[0] == 0:
            # skip the instance with no data to import
            lightmap.read_instance()
        else:
            return True

    return False
