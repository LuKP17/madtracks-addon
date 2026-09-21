# Copyright (C) 2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    lightmap_out
Purpose: Exports level .ldl file and generates the lightmap image.

Description:
Script to be executed in Blender 2.8 which supports multi-edit mode,
needed to unwrap objects while preserving their attributes.
Exports a LDL file and generates a lightmap image to be saved from the
"Image Editor" Blender window, as you will need to convert it into DDS in another software.
The 3D viewport gives an in-game preview in case you want to adjust the lightmap before saving.

You will need to select all objects to include in the lightmap beforehand.
If this script is executed after importing a level with lightmap to do a re-bake,
you can simply enter the following command in Blender's "Python console" window:
`
for obj in bpy.data.objects: obj.select = True if obj.madtracks.is_lightmapped else False
`
"""

import bpy
import os
import struct

import numpy as np

#------------------------------------------------------------------------------------
# NEW 2.79b Blender workflow from no imported lightmap, from imported lightmap will require an alternate path with non-lightmapped materials
#
# HEAVILY OUTDATED
# 1) setup the scene (UI button)
#   - the world mesh object or the first object in LDL order will act as the merged lightmap mesh ("Lightmesh")
#   - select the lightmesh and the next object to bake following INI order
#   - everytime an object is about to be joined to the lightmesh, write the LDL instance using LGT files with zeroes to fill in UVs after unwrapping
#   - mark the lightmesh as active and join both objects
#   - repeat until the lightmesh is complete
#   - create a lightmap UV layer ("LightMap") for the lightmesh
#   - create a lightmap material ("Lightmat") with a lightmap texture ("Lightex") using the LightMap layer and a new lightmap image ("LevelName_lgt0000")
#   - unwrap lightmesh, maybe "Pack Islands" can be interesting
#   - fill in UVs in LDL file using the pre-filled LDL, LGTs and a object loop count offset into the lightmesh LightMap layer array
#
# 2) bake and result preview (UI button)
#   - select LightMap and mark it as active render
#   - for all materials of the lightmesh, disable the use of its textures as to not bake them and to avoid a circular reference error when adjusting the lightmap afterwards
#   - mark lightex and lightmat as active
#   - maybe set the bake margin to a standard value which works for the general case
#   - execute bake operator (I still don't understand how it selects the lightmap image as output, I made it first try by hand without assigning the texture top the faces and now trying everything doesnt work)
#   - for all materials of the lightmesh, enable the use of its textures and add a lightex in multiply blend mode
#
# If the user wants to adjust the lightmap afterwards (only lighting adjustments), redo step 2) after changes are done.
# The 2) button should be available only after executing 1), which can be handles by a scene variable "lightmapped" to True and can never be switched to False
#------------------------------------------------------------------------------------

def setup_scene():
    # set up lightmap texture
    texture = None
    tex_index = bpy.data.textures.find("lightmap")
    if tex_index == -1:
        # create lightmap texture for baking
        texture = bpy.data.textures.new("lightmap", "IMAGE")
        image = bpy.data.images.new("LevelName_lgt0000.dds", 1024, 1024, alpha=True)
        texture.image = image
    else:
        # use existing lightmap texture for re-baking
        texture = bpy.data.textures[tex_index]

    # set up objects, meshes and materials
    for obj in bpy.context.selected_objects:
        if not obj.madtracks.is_lightmapped and obj.data.users > 1:
            # copy mesh to create a lightmapped version (one mesh = unique lightmap UV layer)
            obj.data = bpy.data.meshes[obj.data.name].copy()
            obj.data.name = obj.data.name.split(".")[0] + "_lgt"

        # set up lightmap UV layer
        if "LightMap" in obj.data.uv_textures.keys():
            # use existing lightmap UVs for re-baking
            uv_map = obj.data.uv_textures["LightMap"]
            obj.data.uv_textures.active = uv_map
            obj.data.uv_textures["LightMap"].active_render = True
        else:
            if not obj.madtracks.is_lightmapped:
                # create lightmap UVs for baking
                uv_map = obj.data.uv_textures.new("LightMap")
                obj.data.uv_textures.active = uv_map
                obj.data.uv_textures["LightMap"].active_render = True
                # object will become lightmapped
                obj.madtracks.is_lightmapped = True
            # else: object is lightmapped but doesn't have UVs to export

        # setup materials, looping with indices because the array may be modified here
        for i in range(len(obj.data.materials)):
            material = obj.data.materials[i]
            # TODO enable render backface culling, on 2.8, if geometry node can be automated with "Backfacing" input and Mix shader node
            if not "_lgt" in material.name:
                # switch material with lightmapped version, preserving shared materials
                mat_index = bpy.data.materials.find(material.name + "_lgt")
                if mat_index > -1:
                    # use existing lightmapped version
                    material = bpy.data.materials[mat_index]
                else:
                    # copy material to create a lightmapped version
                    material = bpy.data.materials[material.name].copy()
                    texslot = material.texture_slots.add()
                    texslot.texture = texture
                    texslot.blend_type = "MULTIPLY"
                    texslot.uv_layer = "LightMap" # works even if user doesn't have a lightmap UV layer
                    material.name = material.name.split(".")[0] + "_lgt"  
                obj.data.materials[i] = material
            # else: use existing lightmapped material for re-baking
            # set lightmap texture as active
            for s in range(len(material.texture_slots)):
                if material.texture_slots[s].texture.name == "lightmap":
                    material.active_texture_index = s
                    break


def unwrap_objects(props):
    # remove objects without lightmap UV layer from the selection (they were needed when setting up LDL export)
    instance_cnt = len(bpy.context.selected_objects)
    for obj in bpy.context.selected_objects:
        if not "LightMap" in obj.data.uv_textures.keys():
            obj.select = False
    # "make sure any pinned UVMap UVs are unpinned" => already the case as I don't pin them when importing
    # select objects to be unwrapped and keep them selected
    # TODO 2.8 call unwrap operator in multi-edit and select all faces in UV editor, "Pack Islands" can be interesting

    # return original number of objects to write in LDL
    return instance_cnt


def bake_image():
    print("TODO")
    # some Blender 2.8 requirements
    # - objects that are going to be baked are the ones selected
    # - all materials used by these objects must have an extra image texture containing the lightmap image that is selected
    # /!\ the lightmap image shouldn't be in use by any materials or I will get a circular reference error message, if not using the node editor,
    # Blender 2.79b has a "use_textures" property which might be it, although testing still gave the error message
    # - all lightmap UV layers of these objects must be selected and set as render active
    # TODO 2.8 call bake operator
    # TODO do what's needed to show the generated image in the lightmap texture so that it applies to all its users


def export_LDL(instance_cnt, props):
    """
    Write scene objects marked as lightmapped in a level .ldl file in the same format than the original ones.
    """
    filepath = props.madtracks_dir + os.path.join("Gfx", "Lightmaps") + os.path.sep + "LevelName.ldl"
    with open(filepath, 'wb') as fldl:
        # TODO a scene property is probably required to retrieve the lightmap bit depth
        fldl.write(struct.pack("<4b", 16, 0, 0, 0))
        fldl.write(struct.pack("<i", instance_cnt))
        # loop thru scene objects matching the level INI order
        for i in range(len(bpy.context.scene.objects), 0, -1):
            obj = bpy.context.scene.objects[i-1]
            if obj.madtracks.is_trackpart and obj.parent:
                # skip sequence trackpart
                continue
            if obj.madtracks.is_lightmapped:
                export_instance(obj, fldl, props)
            if obj.madtracks.is_trackpart and obj.children:
                # loop thru trackpart sequence
                while obj.children:
                    obj = obj.children[0]
                    if obj.madtracks.is_lightmapped:
                        export_instance(obj, fldl, props)


def export_instance(obj, fldl, props):
    print("Writing LDL instance {}...".format(obj.data.name))
    loop_index = len(obj.data.loops)
    ldo_filename = obj.madtracks.ldo
    lgt_filepath = props.madtracks_dir + ".cache" + os.path.sep + ldo_filename.replace(".ldo", ".lgt")
    with open(lgt_filepath, 'rb') as flgt:
        # transfer LDO light cache bytes, replacing lightmap UV indices with their actual value
        bmeshcnt = flgt.read(4)
        mesh_cnt = struct.unpack("<i", bmeshcnt)[0]
        fldl.write(bmeshcnt) # LDO mesh count
        name_len = flgt.read(1)[0]
        bmeshname = flgt.read(name_len)
        mesh_name = struct.unpack("<%ds" % name_len, bmeshname)[0].decode("utf-8")
        if mesh_name.lower() == "geometry/rampe_30_up.ldo":
            # this trackpart has its old name in original lightmaps
            fldl.write(struct.pack("<b", 21))
            fldl.write(struct.pack("<21s", "geometry/rampe_30.ldo".encode("utf-8")))
        else:
            fldl.write(struct.pack("<b", name_len))
            fldl.write(bmeshname)
        fldl.write(flgt.read(1))
        if not "LightMap" in obj.data.uv_layers:
            # object doesn't have lightmap data to export
            for _ in range(mesh_cnt):
                fldl.write(struct.pack("<i", 0))
            return
        vertex_cnt = flgt.read(4)
        while vertex_cnt != b'':
            fldl.write(vertex_cnt)
            mesh_loop_cnt = struct.unpack("<i", flgt.read(4))[0]
            # TODO should be initialized at the sum of the number of loops of all LDO meshes
            loop_index -= mesh_loop_cnt
            for _ in range(struct.unpack("<i", vertex_cnt)[0]):
                per_face_index = struct.unpack("<h", flgt.read(2))[0]
                light_uv = obj.data.uv_layers['LightMap'].data[loop_index + per_face_index].uv
                light_uv = [light_uv[0], 1 - light_uv[1]]
                # 16-bit, TODO add support for 32-bit
                light_uv = np.array(light_uv, dtype='<f2')
                fldl.write(light_uv.tobytes())
            vertex_cnt = flgt.read(4)

# main():
props = bpy.context.scene.madtracks
setup_scene()
instance_cnt = unwrap_objects(props)
bake_image()
export_LDL(instance_cnt, props)
