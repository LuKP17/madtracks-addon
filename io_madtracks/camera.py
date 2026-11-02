# Copyright (C) 2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    camera
Purpose: Handle spectator (intro/outro) level cameras.

Description:

"""

if "bpy" in locals():
    import imp
    imp.reload(common)

from . import common

from .common import *

from math import radians, sqrt

# default DAM settings when creating spectator cameras
settings = {
    'farclip': 2500,
    'nearclip': 0.1,
    'rotcenter': (0, 0, 12.5),
    'lookat': (0, 0, 10),
    'heigth': 30.0,
    'radius': 50.0,
    'uprange': 10.0,
    'rotspeed': 20.0,
    'upspeed': 0.0,
    'introlength': 60.0
}

def create_user(scene):
    # called shared method with DAM importer
    create_spec_cams(scene, settings)
    cam = scene.objects['Camera_Outro']
    setup_spec_cam(cam, settings, scene)
    cam.select = False
    cam = scene.objects['Camera_Intro']
    setup_spec_cam(cam, settings, scene)
    # select intro cam anchors for convenience
    cam.constraints["Pivot"].target.select = True
    cam.constraints["Track To"].target.select = True
    cam.select = False
    return


def create_spec_cams(scene, settings):
    # create spectator cameras
    bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, -1.570))
    cam_intro = scene.objects.active
    cam_intro.name = "Camera_Intro"
    cam_intro.data.name = "Spectator_camera"
    cam_intro.data.lens_unit = 'FOV'
    cam_intro.data.angle = 0.788889
    cam_intro.data.clip_start = settings['nearclip']
    cam_intro.data.clip_end = settings['farclip']
    cam_intro.data.sensor_width = 15
    cam_intro.data.draw_size = 10
    cam_intro.data.show_passepartout = False
    cam_outro = cam_intro.copy() # reuse camera data
    scene.objects.link(cam_outro)
    cam_outro.name = "Camera_Outro"
    

def setup_spec_cam(cam, settings, scene):
    # create anchor objects
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    rotcenter = scene.objects.active
    rotcenter.name = "RotCenter"
    rotcenter.location = to_blender_axis(settings['rotcenter'])
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    lookat = scene.objects.active
    lookat.name = "LookAt"
    lookat.location = to_blender_axis(settings['lookat'])

    # add camera constraints using anchor objects
    scene.objects.active = cam
    bpy.ops.object.constraint_add(type='PIVOT')
    cam.constraints["Pivot"].target = rotcenter
    cam.constraints["Pivot"].rotation_range = 'Y'
    bpy.ops.object.constraint_add(type='COPY_LOCATION')
    cam.constraints["Copy Location"].target = rotcenter
    cam.constraints["Copy Location"].use_offset = True
    cam.constraints["Copy Location"].owner_space = 'LOCAL'
    bpy.ops.object.constraint_add(type='TRACK_TO')
    cam.constraints["Track To"].target = lookat
    cam.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
    cam.constraints["Track To"].up_axis = 'UP_Y'

    # place camera
    bpy.ops.object.select_all(action='DESELECT')
    cam.select = True
    cam.location[0] = settings['radius']

    # set timeline, 60 fps requires fetching the correct script path using bpy (Blender vs user script path)
    fps = 24
    bpy.context.scene.frame_end = fps * settings['introlength']

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
    scene.frame_current = fps
    bpy.ops.transform.rotate(value=radians(settings['rotspeed']), axis=(0, 0, 1))
    bpy.ops.anim.keyframe_insert_menu(type='Rotation')
    scene.frame_current = 1
    bpy.context.area.type = 'GRAPH_EDITOR'
    bpy.ops.graph.extrapolation_type(type='LINEAR')
    bpy.context.area.type = 'VIEW_3D'


def reset_spec_cams(scene):
    for cam in bpy.data.cameras:
        if "Spectator_camera" in cam.name:
            cam.name = "trash"
    bpy.ops.object.select_pattern(pattern="Camera_*tro", extend=False)
    bpy.ops.object.select_pattern(pattern="LookAt*", extend=True)
    bpy.ops.object.select_pattern(pattern="RotCenter*", extend=True)
    bpy.ops.object.delete()
    create_user(scene)
    return


def export_spec_cams(scene):
    if not "Spectator_camera" in bpy.data.cameras.keys():
        set_error('exporting cameras', "No spectator camera found")
        return
    if not "Camera_Intro" in scene.objects.keys():
        set_error('exporting cameras', "No \"Camera_Intro\" object found")
        return
    if not "Camera_Outro" in scene.objects.keys():
        set_error('exporting cameras', "No \"Camera_Outro\" object found")
        return
    cam_data = bpy.data.cameras['Spectator_camera']
    intro_cam = scene.objects["Camera_Intro"]
    outro_cam = scene.objects["Camera_Outro"]
    # switch to text editor with new text file
    bpy.context.area.type = 'TEXT_EDITOR'
    bpy.ops.text.new()
    text = bpy.context.space_data.text
    text.write("[Spectator_camera]\n")
    write_spec_cam(text, intro_cam)
    text.write("\n[Spectator_camera_2]\n")
    write_spec_cam(text, outro_cam)
    return


def write_spec_cam(text, cam):
    rotcenter_pos = to_madtracks_axis(cam.constraints["Pivot"].target.location)
    lookat_pos = to_madtracks_axis(cam.constraints["Track To"].target.location)
    text.write("RotCenter = " + float_format(rotcenter_pos[0]) + "," + float_format(rotcenter_pos[1]) + "," + float_format(rotcenter_pos[2]) + "\n")
    text.write("LookAt = " + float_format(lookat_pos[0]) + "," + float_format(lookat_pos[1]) + "," + float_format(lookat_pos[2]) + "\n")
    text.write("Heigth = {}\n".format(float_format(to_madtracks_scale(cam.location[2]))))
    text.write("Radius = {}\n".format(float_format(to_madtracks_scale(sqrt(cam.location[0]**2 + cam.location[1]**2)))))
    text.write("UpRange = {}\n".format(float_format(settings['uprange'])))
    text.write("RotSpeed = {}\n".format(float_format(settings['rotspeed'])))
    text.write("UpSpeed = {}\n".format(float_format(settings['upspeed'])))
    text.write("IntroLength = {}\n".format(float_format(settings['introlength'])))
