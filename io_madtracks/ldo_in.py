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
Purpose: Imports geometry files (.ldo)

Description:
Import any Mad Tracks 3D model.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(madstructs)
    imp.reload(img_in)

import os
import bpy
import bmesh
# from mathutils import Color, Vector
from . import common
from . import madstructs
from . import img_in

from .madstructs import *
from .common import *


def import_file(filepath, scene):
    """
    Imports a .ldo file.
    Creates and returns a Blender object with geometry data.
    """
    props = scene.madtracks

    with open(filepath, 'rb') as file:
        filename = os.path.basename(filepath)
        # Read the .ldo file
        ldo = LDO(file)
        # Check for end of file
        if len(file.read(1)) != 0:
            dprint("WARNING: End of file %s wasn't reached!" % filepath)

    dprint("Imported {} ({} atomics)".format(filename, ldo.atomic_count))

    meshes = []
    for atomic in ldo.atomics:
        # get new Blender mesh from the atomic data
        meshes.append(import_atomic(atomic, scene, filepath))
    
    if props.separate_atomics:
        # create one Blender object per mesh
        for mesh in meshes:
            dprint("Creating Blender object for {}...".format(filename))
            ob = bpy.data.objects.new(filename, mesh)
            scene.objects.link(ob)
            scene.objects.active = ob
    else:
        # create one Blender object with all meshes merged
        merged_mesh = bpy.data.meshes.new(filename)
        bm = bmesh.new()
        for mesh in meshes:
            bm.from_mesh(mesh)
        bm.to_mesh(merged_mesh)
        dprint("Creating Blender object for {}...".format(filename))
        ob = bpy.data.objects.new(filename, merged_mesh)
        scene.objects.link(ob)
        scene.objects.active = ob

    return ob


def import_atomic(atomic, scene, filepath):
    """
    Creates a Blender mesh from an Atomic object and returns it.
    All the meshes contained in the atomic will be merged into a single Blender mesh.
    """
    filename = os.path.basename(filepath)

    me = bpy.data.meshes.new(filename)
    bm = bmesh.new()

    # props = bpy.context.scene.revolt
    bm.loops.layers.uv.new("UVMap")
    bm.faces.layers.tex.new("UVMap")
    # vc_layer = bm.loops.layers.color.new("Col")
    # env_layer = bm.loops.layers.color.new("Env")
    # env_alpha_layer = bm.faces.layers.float.new("EnvAlpha")
    # va_layer = bm.loops.layers.color.new("Alpha")
    # texnum_layer = bm.faces.layers.int.new("Texture Number")
    # type_layer = bm.faces.layers.int.new("Type")

    # add atomic data to bmesh
    poly_offset = 0
    for atomic_mesh in atomic.meshes:
        add_madmesh_to_bmesh(atomic_mesh, bm, filepath, scene, poly_offset)
        poly_offset += atomic_mesh.vertex_count

    bm.to_mesh(me)
    bm.free()

    return me


def add_madmesh_to_bmesh(atomic_mesh, bm, filepath, scene, poly_offset=0):
    """
    Adds Atomic data to an existing bmesh. Returns the resulting bmesh.
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

        verts = (bm.verts[indices[0] + poly_offset], bm.verts[indices[1] + poly_offset],
                 bm.verts[indices[2] + poly_offset])

        uvs = []
        for i in indices:
            uvs.append(atomic_mesh.vertices[i].uvcoords)

        # Tries to create a face and yells at you when the face already exists
        try:
            face = bm.faces.new(verts)
        except Exception as e:
            print(e)
            continue  # Skips this face

        # Assigns the texture to the face
        material = atomic_mesh.atomic.materials[poly.material_index]
        if material.sflag_texture:
            texture = None
            texture_path = props.madtracks_dir + TEXTURE_PATH + material.tex_name + ".dds"
            for image in bpy.data.images:
                if image.filepath == texture_path:
                    texture = image
            if not texture:
                texture = img_in.import_file(texture_path)
            face[tex_layer].image = texture

        # # Assigns the face properties (bit field, one int per face)
        # face[type_layer] = poly.type
        # face[texnum_layer] = poly.texture

        # # Assigns env alpha to face. Colors are on a vcol layer
        # if envlist and (poly.type & FACE_ENV):
        #     env_col_alpha = envlist[props.envidx].alpha
        #     face[env_alpha_layer] = float(env_col_alpha) / 255

        # Assigns the UV mapping, colors and alpha
        for l in range(num_loops):
            # Converts the colors to float (req. by Blender)
            # alpha = 1-(float(colors[l].alpha) / 255)
            # color = [float(c) / 255 for c in colors[l].color]
            # if envlist and (poly.type & FACE_ENV):
            #     env_col = [float(c) / 255 for c in envlist[props.envidx].color]
            #     face.loops[l][env_layer][0] = env_col[0]
            #     face.loops[l][env_layer][1] = env_col[1]
            #     face.loops[l][env_layer][2] = env_col[2]

            face.loops[l][uv_layer].uv = (uvs[l].u, 1 - uvs[l].v)

            # face.loops[l][vc_layer][0] = color[0]
            # face.loops[l][vc_layer][1] = color[1]
            # face.loops[l][vc_layer][2] = color[2]

            # face.loops[l][va_layer][0] = alpha
            # face.loops[l][va_layer][1] = alpha
            # face.loops[l][va_layer][2] = alpha

        # Enables smooth shading for that face
        face.smooth = True
        # if envlist and (poly.type & FACE_ENV):
        #     props.envidx += 1
