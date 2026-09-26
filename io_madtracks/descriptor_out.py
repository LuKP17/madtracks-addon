# Copyright (C) 2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
#  Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    descriptor_out
Purpose: Imports Descriptor INI files

Description:
Descriptors include a LDO with a separate collision mesh, lights, cameras, pickups, game zones...

"""

if "bpy" in locals():
    import imp
    imp.reload(common)

import os
import bpy

from math import degrees

from . import common

from .common import *


def export_file(filepath, context):
    """
    Exports selected Blender objects each as a descriptor .ini file.
    """
    scene = context.scene
    props = scene.madtracks

    for obj in context.selected_objects:
        # export INI file taking the descriptor property as the filename
        filename = obj.madtracks.descriptor
        if not filename:
            set_error('exporting INI descriptor', "No descriptor set for object {}".format(obj.name))
            return
        if obj.type != 'LAMP':
            set_error('exporting INI descriptor', "Only lights descriptors are supported for export")
            return
        with open(os.path.dirname(filepath) + os.path.sep + filename, 'w') as fini:
            # write the .ini file
            fini.write("[object]\n")
            fini.write("ObjectType = \"light\"\n")
            # NOTE saving on object custom properties, this prop will need to be changed manually
            fini.write("LightingMethod = 0\n")
            fini.write("LightShape = ")
            if obj.data.type == 'SUN':
                fini.write(str(LIGHT_SHAPE_DIRECTIONAL) + '\n')
                fini.write("RGBColor = {}\n".format(vector_format(to_madtracks_color(obj.data.color))))
            elif obj.data.type == 'AREA':
                fini.write(str(LIGHT_SHAPE_AMBIENT) + '\n')
                fini.write("RGBColor = {}\n".format(vector_format(to_madtracks_color(scene.world.horizon_color))))
            elif obj.data.type == 'POINT':
                fini.write(str(LIGHT_SHAPE_POINT) + '\n')
                fini.write("Radius = {}\n".format(int(obj.data.distance)))
                fini.write("RGBColor = {}\n".format(vector_format(to_madtracks_color(obj.data.color))))
            elif obj.data.type == 'SPOT':
                if obj.data.energy == 1.0:
                    fini.write(str(LIGHT_SHAPE_SPOT) + '\n')
                else:
                    fini.write(str(LIGHT_SHAPE_SPOTSOFT) + '\n')
                fini.write("ConeAngle = {}\n".format(int(degrees(obj.data.spot_size) // 2)))
                fini.write("Radius = {}\n".format(int(obj.data.distance)))
                fini.write("RGBColor = {}\n".format(vector_format(to_madtracks_color(obj.data.color))))
            if obj.madtracks.cast_shadows == False:
                fini.write("DontCastShadow = 1\n")
        dprint("Exported {}".format(filename))