# Copyright (C) 2024-2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original author: Marvin Thiel
#-----------------------------------------------------------------------------

"""
Name:    ldo_in
Purpose: Imports LDO files

Description:
Import atomics contained in a LDO file as Blender objects.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(madstructs)
    imp.reload(img_in)

import os
import bpy
import bmesh

import numpy as np
import mathutils

from . import common
from . import madstructs
from . import img_in

from .madstructs import *
from .common import *


def import_file(filepath, scene, lightmap=None):
    props = scene.madtracks
    filename = os.path.basename(filepath)
    ldoname = filename.rsplit(".", 1)[0]

    with open_insensitive(filepath, 'rb') as file:
        # read the file
        dprint("Reading LDO file %s..." % filename)
        ldo = LDO()
        ldo.read(file, props.ldo_debug_info)
        # check for EOF
        if len(file.read(1)) != 0:
            dprint("End of file %s wasn't reached." % filename)

    # create Blender meshes from LDO atomics
    meshes = ldo_to_meshes(ldo, ldoname, scene, props, lightmap)
    
    # create Blender objects
    parent = None
    if len(meshes) > 1:
        # create a parent object
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        parent = bpy.context.active_object
        parent.name = ldoname

    for i in range(len(meshes)):
        dprint("Creating Blender object for {}...".format(meshes[i].name))
        obj = bpy.data.objects.new(meshes[i].name, meshes[i])
        scene.objects.link(obj)
        if lightmap:
            # add lightmap suffixes to not be reused later
            obj.name = obj.name + "_lgt"
            obj.data.name = obj.data.name + "_lgt"
        if parent:
            obj.parent = parent
            scene.objects.active = parent
        else:
            scene.objects.active = obj
        obj.madtracks.is_instance = props.instance_mode
        for dummy in ldo.atomics[i].dummies:
            # store dummy data in the object
            if (bool(dummy.flags & DUMMY_FLAG_POSROT)):
                dummy_rot = to_blender_matrix(dummy.rotmat)
                obj.madtracks.dummy_rot1 = dummy_rot[0]
                obj.madtracks.dummy_rot2 = dummy_rot[1]
                obj.madtracks.dummy_rot3 = dummy_rot[2]
                obj.madtracks.dummy_rot4 = dummy_rot[3]
            if (bool(dummy.flags & DUMMY_FLAG_POS) or bool(dummy.flags & DUMMY_FLAG_POSROT)):
                obj.madtracks.dummy_pos = to_blender_axis(dummy.position)
    
    # the parent object could have been selected
    if parent:
        parent.select = False

    dprint("Imported {} ({} atomics)".format(filename, ldo.atomic_cnt))


def ldo_to_meshes(ldo, ldoname, scene, props, lightmap=None):
    """
    Create Blender meshes from a LDO and return them.
    All the meshes contained in one atomic will always be merged into a single Blender mesh.
    All the atomics will be merged into a single Blender mesh if instance mode is enabled.
    """
    meshes = []
    
    if not props.instance_mode:
        # separate atomics in separate meshes
        for atomic in ldo.atomics:
            if atomic.is_empty:
                continue
            # atomic Blender mesh
            if ldo.atomic_cnt > 1:
                meshname = atomic.name
            else:
                meshname = ldoname
            mesh = bpy.data.meshes.new(meshname)

            bm = bmesh.new()
            bm.loops.layers.uv.new("UVMap")
            bm.faces.layers.tex.new("UVMap")
            
            # fill bmesh with atomic meshes
            vertex_offset = 0
            for atomic_mesh in atomic.meshes:
                bmesh_add_atomic_mesh(bm, atomic, atomic_mesh, scene, vertex_offset)
                vertex_offset += atomic_mesh.vertex_cnt

            # fill Blender mesh with bmesh
            bm.to_mesh(mesh)
            bm.free()
            
            mesh_assign_materials(ldo.atomic_cnt, atomic, mesh, props)

            meshes.append(mesh)
    else:
        # merge all atomics into a single mesh
        mesh = bpy.data.meshes.new(ldoname)

        bm = bmesh.new()
        bm.loops.layers.uv.new("UVMap")
        if lightmap:
            bm.loops.layers.uv.new("LightMap")
        bm.faces.layers.tex.new("UVMap")

        # fill bmesh with all atomics meshes
        vertex_offset = 0
        for atomic in ldo.atomics:
            if atomic.is_empty:
                continue
            i = atomic.mesh_cnt - 1 # meshes are stored in reverse order in the LDO, thanks for the rage Load xoxo
            for atomic_mesh in atomic.meshes:
                if lightmap:
                    bmesh_add_atomic_mesh(bm, atomic, atomic_mesh, scene, vertex_offset, lightmap.current_uvs[i])
                else:
                    bmesh_add_atomic_mesh(bm, atomic, atomic_mesh, scene, vertex_offset)
                vertex_offset += atomic_mesh.vertex_cnt
                i -= 1

        # fill Blender mesh with bmesh
        bm.to_mesh(mesh)
        bm.free()

        # FIXME currently only assigns the last atomic materials
        mesh_assign_materials(ldo.atomic_cnt, atomic, mesh, props, lightmap)

        meshes.append(mesh)

    return meshes


def bmesh_add_atomic_mesh(bm, atomic, atomic_mesh, scene, vertex_offset=0, light_uvs=None):
    """
    Adds an atomic mesh to an existing bmesh. Returns the resulting bmesh.
    """
    props = scene.madtracks
    uv_layer = bm.loops.layers.uv["UVMap"]
    if light_uvs:
        light_layer = bm.loops.layers.uv["LightMap"]
    tex_layer = bm.faces.layers.tex["UVMap"]

    for vert in atomic_mesh.vertices:
        position = to_blender_coord(vert.position.data)
        normal = to_blender_axis(vert.normal.data)

        # create vertices
        vert = bm.verts.new(Vector(data=(position[0], position[1], position[2])))
        vert.normal = Vector(data=(normal[0], normal[1], normal[2]))

        # ensure lookup table (potentially puts out an error otherwise)
        bm.verts.ensure_lookup_table()

    for poly in atomic_mesh.tris:
        num_loops = 3 # Mad Tracks only uses tris
        indices = poly.vertices_id

        verts = (bm.verts[indices[0] + vertex_offset], bm.verts[indices[1] + vertex_offset],
                 bm.verts[indices[2] + vertex_offset])

        # Tries to create a face and yells at you when the face already exists
        try:
            face = bm.faces.new(verts)
        except Exception as e:
            print(e)
            continue  # skip this face

        # Assigns the diffuse image to the face
        material = atomic.materials[poly.material_id]
        if (bool(material.flags & MAT_FLAG_DIFFUSE)):
           texture = None
           texture_path = props.settings_madtracks_dir + TEXTURE_PATH + material.diffuse_name + ".dds"
           for image in bpy.data.images:
               if image.filepath == texture_path:
                   texture = image
           if not texture:
               texture = img_in.import_file(texture_path)
           face[tex_layer].image = texture

        # Assigns the UV mapping, prevent UVs from leaving boundaries? (see Bistrot.ldo door)
        uvs = []
        for i in indices:
            uvs.append(atomic_mesh.vertices[i].uv)

        for l in range(num_loops):
            face.loops[l][uv_layer].uv = (uvs[l].u, 1 - uvs[l].v)
        
        if light_uvs:
            uvs = []
            for i in indices:
                uvs.append(light_uvs[i])

            # Assigns the lightmap UV mapping
            for l in range(num_loops):
                face.loops[l][light_layer].uv = (uvs[l].u, 1 - uvs[l].v)

        # Enables smooth shading for that face
        #face.smooth = True


def mesh_assign_materials(atomic_cnt, atomic, mesh, props, lightmap=None):
    # assign atomic materials to mesh
    for atomic_mat in atomic.materials:
        # reuse already imported lightmapped materials
        mat_index = bpy.data.materials.find(atomic_mat.name + "_lgt")
        if mat_index >= 0 and lightmap:
            material = bpy.data.materials[mat_index]
        else:
            # new Blender material
            material = bpy.data.materials.new(atomic_mat.name)

            if (bool(atomic_mat.flags & MAT_FLAG_RGBA)):
                material.madtracks.has_rgba = True
                material.diffuse_color = [float(atomic_mat.RGBA[0] / 255),
                                        float(atomic_mat.RGBA[1] / 255),
                                        float(atomic_mat.RGBA[2] / 255)]
                material.use_transparency = True
                material.alpha = float(atomic_mat.RGBA[3] / 255)
            if (bool(atomic_mat.flags & MAT_FLAG_BRIGHTNESS)):
                material.madtracks.has_brightness = True
                # Blender's default diffuse_intensity is 0.8
                material.diffuse_intensity = float((atomic_mat.brightness + 1) / 2)

            if atomic_mat.diffuse_name_len:
                texslot = material.texture_slots.add()

                # new Blender texture for diffuse
                texture = bpy.data.textures.new(atomic_mat.diffuse_name, "IMAGE")
                image = None
                filename = atomic_mat.diffuse_name + ".dds"
                # reuse shared images between atomics
                # FIXME this doesn't reload the image if another import loaded it before
                if atomic_cnt > 1 and bpy.data.images.find(filename) >= 0:
                    image = bpy.data.images[bpy.data.images.find(filename)]
                else:
                    image = img_in.import_file(props.settings_madtracks_dir + TEXTURE_PATH + filename)
                texture.image = image
                texslot.texture = texture

            if atomic_mat.envmap_name_len:
                texslot = material.texture_slots.add()

                # new Blender texture for envmap
                texture = bpy.data.textures.new(atomic_mat.envmap_name, "IMAGE")
                image = None
                filename = atomic_mat.envmap_name + ".dds"
                # reuse shared images between atomics
                if atomic_cnt > 1 and bpy.data.images.find(filename) >= 0:
                    image = bpy.data.images[bpy.data.images.find(filename)]
                else:
                    image = img_in.import_file(props.settings_madtracks_dir + TEXTURE_PATH + filename)
                texture.image = image
                texslot.texture = texture
                texslot.blend_type = "SOFT_LIGHT"
                texslot.diffuse_color_factor = 0.5
            
            if lightmap:
                # add a lightmap suffix to be reused later
                material.name = material.name + "_lgt"
                texslot = material.texture_slots.add()
                texture = None
                # reuse lightmap texture
                image_name = os.path.basename(lightmap.file.name)
                image_name = image_name.rsplit(".", 1)[0] + "_lgt0000"
                tex_index = bpy.data.textures.find(image_name)
                if tex_index >= 0:
                    texture = bpy.data.textures[tex_index]
                if not texture:
                    # new Blender texture for lightmap
                    texture = bpy.data.textures.new(image_name, "IMAGE")
                    filename = image_name + ".dds"
                    image = img_in.import_file(props.settings_madtracks_dir + LDL_PATH + filename)
                    texture.image = image
                texslot.texture = texture
                texslot.blend_type = "MULTIPLY"
                texslot.uv_layer = "LightMap"

            # other convenient material properties
            material.specular_intensity = 0

        mesh.materials.append(material)
    
    # assign material to mesh faces
    tri_offset = 0
    for atomic_mesh in atomic.meshes:
        # rely on the fact the mesh vertices and materials are created in the LDO order
        for material_id, sequence_len in zip(atomic_mesh.tri_seq_mat, atomic_mesh.tri_seq_len):
            for ti in range(sequence_len):
                mesh.polygons[ti + tri_offset].material_index = material_id
            tri_offset += sequence_len
