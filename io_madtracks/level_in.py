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
            lightmap.read_instance()
        else:
            # give up on the lightmap
            lightmap_file.close()
            lightmap = None
        # world base mesh is a lightmap instance
        dam_filepath = filepath.replace(".ini", ".dam")
        with open_insensitive(dam_filepath, 'r') as settings_file:
            ini = INI(settings_file)
        world = int(ini.as_dict()['base']['world'])
        import_base_mesh(world, lightmap, scene)

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
                lightmap.read_instance()
    if not obj:
        # import LDO
        if lightmapped:
            ldo_in.import_file(props.madtracks_dir + LDO_PATH + filename, scene, lightmap)
            lightmap.read_instance()
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
                obj_copy = obj.copy()
                scene.objects.link(obj_copy)
                scene.objects.active = obj_copy
                if lightmapped:
                    # skip empty lightmap instance
                    lightmap.read_instance()
                # don't forget about potential children (like validation box)
                for child in obj.children:
                    child_copy = child.copy()
                    scene.objects.link(child_copy)
                    child_copy.parent = obj_copy
                obj = obj_copy
                obj.select = False
    if not obj:
        # import descriptor
        if lightmapped:
            if not descriptor_in.import_file(props.madtracks_dir + DESCRIPTOR_PATH + filename, scene, lightmap):
                return False
            lightmap.read_instance()
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
    if not props.level_import_lightmap or not lightmap:
        return False

    # add universal prefix for lightmaps
    filename = "geometry/" + filename
    print("Comparing LDO filename {} with LDL instance name {}...".format(filename.lower(), lightmap.current_name.lower()))
    return lightmap.current_name.lower() == filename.lower() or lightmap.current_name.lower() == "geometry/rampe_30.ldo"


def import_base_mesh(world_num, lightmap, scene):
    props = scene.madtracks
    filename = world_filenames[world_num]
    filepath = props.madtracks_dir + WORLD_PATH + filename

    with open_insensitive(filepath, 'r') as file:
        ini = INI(file)
        ini_dic = ini.as_dict()

    # import the world mesh with lightmap data
    if 'mesh' in ini_dic['base'].keys():
        ldo_filename = ini_dic['base']['mesh'].rsplit("/", 1)[1] # strip partial dirpath
        ldo_in.import_file(props.madtracks_dir + LDO_PATH + ldo_filename, scene, lightmap)
        lightmap.read_instance()
        obj = bpy.context.active_object
        # world doesn't cast shadows
        for mat in obj.data.materials:
            mat.use_cast_shadows = False
        # mark as world
        obj.madtracks.is_world = True
