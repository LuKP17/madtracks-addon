# Copyright (C) 2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    dam_in
Purpose: Imports .dam files.

Description:
DAM files contain level settings, the base mesh, skybox, intro/outro cameras.
The underlying format is the custom Mad Tracks INI dialect.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(ldo_in)
    imp.reload(img_in)
    imp.reload(madini)

import bpy

from . import common
from . import ldo_in
from . import img_in
from . import madini

from .common import *
from .ldo_in import *
from .img_in import *
from .madini import *

from math import radians


def import_file(filepath, scene):
    """
    Imports a level as Blender objects by reading the level .ini file.
    """
    props = scene.madtracks

    with open_insensitive(filepath, 'r') as file:
        ini = INI(file)
    world = int(ini.as_dict()['base']['world'])
    import_world(world, scene)
    import_cameras(ini.as_dict(), scene)


def import_world(world_num, scene):
    props = scene.madtracks
    filename = world_filenames[world_num]
    filepath = props.madtracks_dir + WORLD_PATH + filename

    with open_insensitive(filepath, 'r') as file:
        dprint("Reading world file %s..." % filename)
        ini = INI(file)
    ini_dic = ini.as_dict()

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
