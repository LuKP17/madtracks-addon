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
    imp.reload(camera)

import bpy

from . import common
from . import ldo_in
from . import img_in
from . import madini
from . import camera

from .common import *
from .ldo_in import *
from .img_in import *
from .madini import *
from .camera import *


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
    filepath = props.work_dir + WORLD_PATH + filename

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
            image = img_in.import_file(props.work_dir + TEXTURE_PATH + texture_name, reuse=False)
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
        ldo_in.import_file(props.work_dir + LDO_PATH + ldo_filename, scene)
        obj = bpy.context.active_object
        # world doesn't cast shadows
        for mat in obj.data.materials:
            mat.use_cast_shadows = False
        # mark as world
        obj.madtracks.is_world = True


def import_cameras(ini_dic, scene):
    camera.create_spec_cams(scene, ini_dic['camera'])
    cam = scene.objects['Camera_Intro']
    camera.setup_spec_cam(cam, ini_dic['spectator_camera'], scene)
    cam = scene.objects['Camera_Outro']
    camera.setup_spec_cam(cam, ini_dic['spectator_camera_2'], scene)
