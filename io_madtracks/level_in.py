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

# world numbers in game's files
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
        filename = filename.replace(".ini", ".ldl")
        lightmap_file = open_insensitive(props.madtracks_dir + LDL_PATH + filename, 'rb')
        lightmap = LDL(lightmap_file)
        success = lightmap.read_header()
        if success:
            lightmap.read_instance(props.lightmap_debug_info)
        else:
            # give up on the lightmap
            lightmap_file.close()
            lightmap = None

    # import world
    dam_filepath = filepath.replace(".ini", ".dam")
    with open_insensitive(dam_filepath, 'r') as settings_file:
        ini = INI(settings_file)
    world = int(ini.as_dict()['base']['world'])
    import_world(world, lightmap, scene)

    # import level .ini file
    with open_insensitive(filepath, 'r') as instance_file:
        ini = INI(instance_file)
    for section in ini.sections:
        ext = section.as_dict()['filename'].split(".", 1)[1]
        # import section
        if ext == "ldo":
            success = import_LDO_instance(section, lightmap, scene)
        elif ext == "ini":
            success = import_descriptor_instance(section, lightmap, scene)
        # abort level import on failure
        if not success:
            set_error('importing a level', "Import of level instance failed")
            return
    
    if lightmap:
        # make imported lightmap more visible over imported light objects
        bpy.context.scene.world.light_settings.environment_color = 'PLAIN'
        bpy.context.scene.world.light_settings.environment_energy = 1
        lightmap_file.close()
        if lightmap.instance_cnt > 0:
            set_error('importing a level', "Missed %d lightmap instances" % lightmap.instance_cnt)

    # reinstate old instance mode
    props.instance_mode = instance_mode_save


def import_LDO_instance(section, lightmap, scene):
    """
    Imports a LDO level instance from a .ini section.
    """
    props = scene.madtracks

    filename = section.as_dict()['filename'].rsplit("/", 1)[1] # strip partial dirpath
    lightmapped = is_lightmapped(lightmap, filename, props)

    obj = None
    if not lightmapped or lightmap.is_empty:
        # reuse already imported instances that don't have lightmap UVs
        obj_index = find_reusable_ldo(filename)
        if obj_index >= 0:
            obj = bpy.data.objects[obj_index]
            dprint("Copying Blender object {}...".format(obj.name))
            obj = obj.copy()
            scene.objects.link(obj)
            scene.objects.active = obj
            obj.select = False
            if lightmapped:
                obj.madtracks.is_lightmapped = True
                # skip empty lightmap instance
                lightmap.read_instance(props.lightmap_debug_info)
    if not obj:
        # import LDO
        if lightmapped:
            ldo_in.import_file(props.madtracks_dir + LDO_PATH + filename, scene, lightmap)
            lightmap.read_instance(props.lightmap_debug_info)
        else:
            ldo_in.import_file(props.madtracks_dir + LDO_PATH + filename, scene)
        obj = bpy.context.active_object

    # edit location and rotation of Blender object
    place_instance_object(section, obj)

    return True


def import_descriptor_instance(section, lightmap, scene):
    """
    Imports a Descriptor level instance from a .ini section.
    """
    props = scene.madtracks

    filename = section.as_dict()['filename']

    ldo_filename = None
    is_trackpart = False
    is_collectible = False
    with open_insensitive(props.madtracks_dir + DESCRIPTOR_PATH + filename, 'r') as file:
        descriptor = INI(file).as_dict()
        if "filename" in descriptor['object'].keys() and ".ldo" in descriptor['object']['filename']:
            ldo_filename = descriptor['object']['filename'].rsplit("/", 1)[1] # strip partial dirpath
        if "objecttype" in descriptor['object'].keys():
            if descriptor['object']['objecttype'] in trackpart_types:
                is_trackpart = True
            if descriptor['object']['objecttype'] in collectible_types:
                is_collectible = True

    obj = None
    lightmapped = False
    if ldo_filename:
        lightmapped = is_lightmapped(lightmap, ldo_filename, props)
        if not props.level_import_raceline and (is_trackpart or is_collectible):
            # don't import descriptor
            if lightmapped:
                lightmap.read_instance()
            return True  
        if not lightmapped or lightmap.is_empty:
            # reuse already imported instances that don't have lightmap UVs
            obj_index = find_reusable_descriptor(filename)
            if obj_index >= 0:
                obj = bpy.data.objects[obj_index]
                dprint("Copying Blender object {}...".format(obj.name))
                obj = obj.copy()
                scene.objects.link(obj)
                scene.objects.active = obj
                obj.select = False
                if lightmapped:
                    obj.madtracks.is_lightmapped = True
                    # skip empty lightmap instance
                    lightmap.read_instance(props.lightmap_debug_info)
    if not obj:
        # import descriptor
        if lightmapped:
            if not descriptor_in.import_file(props.madtracks_dir + DESCRIPTOR_PATH + filename, scene, lightmap):
                return False
            lightmap.read_instance(props.lightmap_debug_info)
        else:
            if not descriptor_in.import_file(props.madtracks_dir + DESCRIPTOR_PATH + filename, scene):
                return False
        obj = bpy.context.active_object
        
    # edit location and rotation of Blender object
    place_instance_object(section, obj)

    if is_trackpart:
        if len(section.params) > 1:
            # new trackpart sequence
            trackpart.add(scene, obj)
            # keep the current trackpart selected to retrieve it at the next iteration
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
        elif len(section.params) == 1:
            # add to trackpart sequence
            prev = bpy.context.selected_objects[0]
            trackpart.add(scene, obj, prev)
            # set parent relation which requires operator not to break the placement
            obj.select = True
            scene.objects.active = prev
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
            # keep the current trackpart selected to retrieve it at the next iteration
            prev.select = False

    return True


def import_world(world_num, lightmap, scene):
    props = scene.madtracks
    filename = world_filenames[world_num]
    filepath = props.madtracks_dir + WORLD_PATH + filename

    with open_insensitive(filepath, 'r') as file:
        dprint("Reading world file %s..." % filename)
        ini = INI(file)
        ini_dic = ini.as_dict()

        # import the sky color
        sky_color = ini_dic['base']['skycolor']
        bpy.data.worlds[0].horizon_color = to_blender_color(sky_color)

        # import the optional skybox
        if 'skybox' in ini_dic.keys():
            skybox_pos = to_blender_coord(ini_dic['skybox']['position'])
            skybox_scale = to_blender_scale(ini_dic['skybox']['scale'])
            bpy.ops.mesh.primitive_cube_add(location=(skybox_pos[0], skybox_pos[1], skybox_pos[2]),
                                            radius=skybox_scale,
                                            enter_editmode=True)
            bpy.ops.mesh.flip_normals()
            bpy.ops.mesh.uv_texture_add()
            obj = bpy.context.edit_object
            bpy.ops.object.editmode_toggle()
            obj.data.name = "skybox"
            obj.name = "Skybox"
            obj.madtracks.is_world = True
            # rotate the skybox to the right orientation
            bpy.context.object.rotation_euler[2] = 7.85398
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

            # assign skybox textures
            skybox_textures = [ini_dic['skybox']['back'],
                               ini_dic['skybox']['right'],
                               ini_dic['skybox']['front'],
                               ini_dic['skybox']['left'],
                               ini_dic['skybox']['down'],
                               ini_dic['skybox']['up']
                            ]
            for side in range(6):
                texture_name = skybox_textures[side]
                material = bpy.data.materials.new(texture_name)
                texslot = material.texture_slots.add()
                texture = bpy.data.textures.new(texture_name, "IMAGE")
                image = img_in.import_file(props.madtracks_dir + TEXTURE_PATH + texture_name, reuse=False)
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
        if 'mesh' in ini_dic['base'].keys():
            ldo_filename = ini_dic['base']['mesh'].rsplit("/", 1)[1] # strip partial dirpath
            if is_lightmapped(lightmap, ldo_filename, props):
                ldo_in.import_file(props.madtracks_dir + LDO_PATH + ldo_filename, scene, lightmap)
                lightmap.read_instance(props.lightmap_debug_info)
            else:
                ldo_in.import_file(props.madtracks_dir + LDO_PATH + ldo_filename, scene)
            obj = bpy.context.active_object
            obj.madtracks.is_world = True


def place_instance_object(section, obj):
    """
    Edit an instance object's location and rotation by reading a level .ini section's parameters.
    """
    if len(section.params) == 4:
        section_dic = section.as_dict()
        directionAT = section_dic['directionat']
        directionUp = section_dic['directionup']
        directionRight = np.cross(directionAT, directionUp)
        directionLeft = -directionRight

        mat = [
            (directionAT[0], directionAT[1], directionAT[2]),
            (directionUp[0], directionUp[1], directionUp[2]),
            (directionLeft[0], directionLeft[1], directionLeft[2]),
        ]

        bmat = to_blender_matrix(mat)
        obj.rotation_euler = bmat.to_euler()
        obj.location = to_blender_coord(section_dic['position'])


def is_lightmapped(lightmap, filename, props):
    """
    Return True if the LDO to import is present in the LDL file, although it can have no UV data to import
    """
    if not lightmap:
        return False

    # add universal prefix for lightmaps
    filename = "geometry/" + filename
    if props.lightmap_debug_info:
        print("Comparing LDO filename {} with LDL instance name {}...".format(filename.lower(), lightmap.current_name.lower()))
    return lightmap.current_name.lower() == filename.lower() or lightmap.current_name.lower() == "geometry/rampe_30.ldo"

