# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: prm_in.py
# Original author: Marvin Thiel
#
# File first modified on 02/28/24
# Author: Lucas Pottier
#-----------------------------------------------------------------------------

"""
Name:    ldo_in
Purpose: Imports .ldo files

Description:
Import atomics contained in a .ldo file as Blender objects.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(madstructs)
    imp.reload(img_in)

import os
import bpy
import bmesh

from . import common
from . import madstructs
from . import img_in

from .madstructs import *
from .common import *


def import_file(filepath, scene):
    """
    Imports a .ldo file as Blender objects
    """
    props = scene.madtracks

    # import LDO data
    with open(filepath, 'rb') as file:
        filename = os.path.basename(filepath)
        # read the .ldo file
        ldo = LDO()
        ldo.read(file, props.ldo_debug_info)
        # check for EOF
        if len(file.read(1)) != 0:
            dprint("WARNING: End of file %s wasn't reached!" % filepath)

    # create Blender meshes from LDO atomics
    meshes = []
    for atomic in ldo.atomics:
        meshes.append(atomic_to_mesh(atomic, scene, filepath, props))
    
    # create Blender objects
    if props.ldo_separate_atomics:
        # one Blender object per mesh
        for mesh in meshes:
            dprint("Creating Blender object for {}...".format(filename))
            ob = bpy.data.objects.new(filename, mesh)
            scene.objects.link(ob)
            scene.objects.active = ob
    else:
        # one Blender object with all meshes merged
        merged_mesh = bpy.data.meshes.new(filename)
        bm = bmesh.new()
        for mesh in meshes:
            bm.from_mesh(mesh)
        bm.to_mesh(merged_mesh)
        dprint("Creating Blender object for {}...".format(filename))
        ob = bpy.data.objects.new(filename, merged_mesh)
        scene.objects.link(ob)
        scene.objects.active = ob

    dprint("Imported {} ({} atomics)".format(filename, ldo.atomic_cnt))

    # for the level importer, won't work if we separate atomics in multiple Blender objects
    return ob


def atomic_to_mesh(atomic, scene, filepath, props):
    """
    Creates a Blender mesh from a LDO atomic and returns it.
    All the meshes contained in the atomic will be merged into a single Blender mesh.
    """
    filename = os.path.basename(filepath)

    # new Blender mesh
    # /!\ don't use filename after that as a suffix can be added to the mesh name
    mesh = bpy.data.meshes.new(filename)
    
    # new bmesh
    bm = bmesh.new()
    bm.loops.layers.uv.new("UVMap")
    bm.faces.layers.tex.new("UVMap")
    
    # fill bmesh with atomic meshes
    vertex_offset = 0
    for atomic_mesh in atomic.meshes:
        bmesh_add_atomic_mesh(bm, atomic_mesh, scene, vertex_offset)
        # 2026: why not call it vertex_offset already?
        vertex_offset += atomic_mesh.vertex_count

    # fill Blender mesh with bmesh
    bm.to_mesh(mesh)
    bm.free()
    
    # assign atomic materials to mesh (idk if it works when atomics are not split in separate objects)
    for atomic_mat in atomic.materials:
        # new Blender material
        # /!\ don't use atomic_mat.name after that as a suffix can be added to the material name
        material = bpy.data.materials.new(atomic_mat.name)
        
        # new Blender texture
        texslot = material.texture_slots.add()
        texture = bpy.data.textures.new(atomic_mat.diffuse_name, "IMAGE")
        image = None
        image_path = props.settings_madtracks_dir + TEXTURE_PATH + atomic_mat.diffuse_name + ".dds"
        for img in bpy.data.images:
            if img.filepath == image_path:
                image = img
        if not image:
            image = img_in.import_file(image_path)
        texture.image = image
        texslot.texture = texture
        
        # link the material to the merged mesh
        mesh.materials.append(material)
    
    # assign material to mesh faces
    poly_offset = 0
    for atomic_mesh in atomic.meshes:
        # rely on the fact the mesh vertices and materials are created in the LDO order
        for ti in range(atomic_mesh.polygon_count):
            mesh.polygons[ti + poly_offset].material_index = atomic_mesh.polygons[ti].material_index
        poly_offset += atomic_mesh.polygon_count

    return mesh


def bmesh_add_atomic_mesh(bm, atomic_mesh, scene, vertex_offset=0):
    """
    Adds an atomic mesh to an existing bmesh. Returns the resulting bmesh.
    """
    props = scene.madtracks
    uv_layer = bm.loops.layers.uv["UVMap"]
    tex_layer = bm.faces.layers.tex["UVMap"]

    for vert in atomic_mesh.vertices:
        position = to_blender_coord(vert.position.data)
        normal = to_blender_axis(vert.normal.data)

        # Creates vertices
        vert = bm.verts.new(Vector(data=(position[0], position[1], position[2])))
        vert.normal = Vector(data=(normal[0], normal[1], normal[2]))

        # Ensures lookup table (potentially puts out an error otherwise)
        bm.verts.ensure_lookup_table()

    for poly in atomic_mesh.polygons:
        num_loops = 3 # Mad tracks only uses tris
        indices = poly.vertex_indices

        verts = (bm.verts[indices[0] + vertex_offset], bm.verts[indices[1] + vertex_offset],
                 bm.verts[indices[2] + vertex_offset])

        uvs = []
        for i in indices:
            uvs.append(atomic_mesh.vertices[i].uvcoords)

        # Tries to create a face and yells at you when the face already exists
        try:
            face = bm.faces.new(verts)
        except Exception as e:
            print(e)
            continue  # Skips this face

        # Assigns the texture to the face (/!\ once materials are supported the texture won't be linked)
        #material = atomic_mesh.atomic.materials[poly.material_index]
        #if (bool(material.flags & MAT_FLAG_DIFFUSE)):
        #    texture = None
        #    texture_path = props.settings_madtracks_dir + TEXTURE_PATH + material.diffuse_name + ".dds"
        #    for image in bpy.data.images:
        #        if image.filepath == texture_path:
        #            texture = image
        #    if not texture:
        #        texture = img_in.import_file(texture_path)
        #    face[tex_layer].image = texture

        # Assigns the UV mapping TODO prevent UVs from leaving boundaries (see Bistrot.ldo door)
        for l in range(num_loops):
            face.loops[l][uv_layer].uv = (uvs[l].u, 1 - uvs[l].v)

        # Enables smooth shading for that face
        face.smooth = True
