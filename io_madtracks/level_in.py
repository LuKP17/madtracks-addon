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
            props.lightmap_bitdepth = lightmap.bit_depth
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
    import_cameras(ini.as_dict(), scene)

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
        lightmap_file.close()
        if lightmap.instance_cnt > 0:
            set_error('importing a level', "Missed %d lightmap instances" % lightmap.instance_cnt)
        # remove all influences on lightmap
        bpy.context.scene.world.light_settings.environment_color = 'PLAIN'
        bpy.context.scene.world.light_settings.environment_energy = 1
        for obj in scene.objects:
            if obj.type == 'LAMP':
                obj.hide = True
                obj.hide_render = True
    
    bpy.ops.object.select_all(action='DESELECT')

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

    if is_collectible:
        for mat in obj.data.materials:
            mat.use_shadeless = True
        
    # edit location and rotation of Blender object
    place_instance_object(section, obj)

    if is_trackpart:
        if len(section.params) > 1:
            trackpart.add(scene, obj)
        elif len(section.params) == 1:
            # part of a trackpart sequence
            prev = bpy.context.selected_objects[0]
            trackpart.add(scene, obj, prev)

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
                # world doesn't cast shadows
                material.use_cast_shadows = False
                material.use_shadeless = True
                # assign to faces
                obj.data.polygons[side].material_index = side
            # fix skybox texture rotation
            mat_up = bpy.data.materials[skybox_textures[5]]
            mat_up.texture_slots[0].scale = [-1, -1, 1]
            # mark as world
            obj.madtracks.is_world = True

        # import the optional world mesh
        if 'mesh' in ini_dic['base'].keys():
            ldo_filename = ini_dic['base']['mesh'].rsplit("/", 1)[1] # strip partial dirpath
            if is_lightmapped(lightmap, ldo_filename, props):
                ldo_in.import_file(props.madtracks_dir + LDO_PATH + ldo_filename, scene, lightmap)
                lightmap.read_instance(props.lightmap_debug_info)
            else:
                ldo_in.import_file(props.madtracks_dir + LDO_PATH + ldo_filename, scene)
            obj = bpy.context.active_object
            # world doesn't cast shadows
            for mat in obj.data.materials:
                mat.use_cast_shadows = False
            # mark as world
            obj.madtracks.is_world = True


def import_cameras(ini_dic, scene):
    # create camera to be used for the intro/outro
    bpy.ops.object.camera_add(rotation=(0, 0, -1.570))
    cam_intro = scene.objects.active
    cam_intro.name = "Camera_Intro"
    cam_intro.data.lens_unit = 'FOV'
    cam_intro.data.angle = 0.788889
    cam_intro.data.clip_start = ini_dic['camera']['nearclip']
    cam_intro.data.clip_end = ini_dic['camera']['farclip']
    cam_intro.data.sensor_width = 15
    cam_intro.data.draw_size = 10
    cam_intro.data.show_passepartout = False
    cam_outro = cam_intro.copy()
    scene.objects.link(cam_outro)
    cam_outro.name = "Camera_Outro"
    # setup intro/outro paths
    setup_spectator_camera(cam_intro, ini_dic['spectator_camera'], scene)
    setup_spectator_camera(cam_outro, ini_dic['spectator_camera_2'], scene)


def setup_spectator_camera(cam, settings, scene):
    # create anchor objects
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    rotcenter_obj = scene.objects.active
    rotcenter_obj.name = "RotCenter"
    rotcenter_obj.location = to_blender_axis(settings['rotcenter'])
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    lookat_obj = scene.objects.active
    lookat_obj.name = "LookAt"
    lookat_obj.location = to_blender_axis(settings['lookat'])

    # add camera constraints using anchor objects
    scene.objects.active = cam
    bpy.ops.object.constraint_add(type='PIVOT')
    cam.constraints["Pivot"].target = rotcenter_obj
    cam.constraints["Pivot"].rotation_range = 'Y'
    bpy.ops.object.constraint_add(type='COPY_LOCATION')
    cam.constraints["Copy Location"].target = rotcenter_obj
    cam.constraints["Copy Location"].use_offset = True
    cam.constraints["Copy Location"].owner_space = 'LOCAL'
    bpy.ops.object.constraint_add(type='TRACK_TO')
    cam.constraints["Track To"].target = lookat_obj
    cam.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    cam.constraints["Track To"].up_axis = 'UP_Y'

    # place camera
    bpy.ops.object.select_all(action='DESELECT')
    cam.select = True
    cam.location[0] = settings['radius']

    # set timeline
    bpy.ops.script.python_file_run(filepath="C:\\Program Files\\Blender 2.79b\\2.79\\scripts\\presets\\framerate\\60.py")
    bpy.context.scene.frame_end = 60 * settings['introlength']

    # create up-down-up height keyframes with cyclic extrapolation
    # FIXME up-down motion timing isn't 100% accurate
    if settings['upspeed'] > 0:
        uprange_frames = 180 / settings['upspeed']
        scene.frame_current = 90
        cam.location[2] = settings['heigth'] + (settings['uprange'])
        bpy.ops.anim.keyframe_insert_menu(type='Location')
        scene.frame_current += uprange_frames
        cam.location[2] = settings['heigth'] - (settings['uprange'])
        bpy.ops.anim.keyframe_insert_menu(type='Location')
        scene.frame_current += uprange_frames
        cam.location[2] = settings['heigth'] + (settings['uprange'])
        bpy.ops.anim.keyframe_insert_menu(type='Location')
        bpy.context.area.type = 'GRAPH_EDITOR'
        bpy.ops.graph.extrapolation_type(type='MAKE_CYCLIC')
        # lock up-down height channel
        bpy.ops.anim.channels_editable_toggle()
        bpy.context.area.type = 'VIEW_3D'
    else:
        cam.location[2] = settings['heigth']

    # create an initial and a linear rotation keyframe (linear extrapolation means infinite rotation beyond these two keyframes)
    scene.frame_current = 1
    bpy.ops.anim.keyframe_insert_menu(type='Rotation')
    # RotSpeed value is in degrees per second
    scene.frame_current = 60
    bpy.ops.transform.rotate(value=radians(settings['rotspeed']), axis=(0, 0, 1))
    bpy.ops.anim.keyframe_insert_menu(type='Rotation')
    scene.frame_current = 1
    bpy.context.area.type = 'GRAPH_EDITOR'
    bpy.ops.graph.extrapolation_type(type='LINEAR')
    bpy.context.area.type = 'VIEW_3D'


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
        if obj.type in ['CAMERA', 'LAMP']:
            # Blender spawns these object types facing down instead of forward
            bpy.ops.object.select_all(action='DESELECT')
            obj.select = True
            bpy.ops.transform.rotate(value=1.5708, constraint_axis=(True, False, False), constraint_orientation='LOCAL')
            obj.select = False
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
