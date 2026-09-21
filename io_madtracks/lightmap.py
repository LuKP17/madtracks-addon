# Copyright (C) 2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    lightmap
Purpose: Handles lightmap bake and export.

Description:
TODO

"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(madstructs)
    imp.reload(madini)

from . import common
from . import madstructs
from . import madini

from .common import *
from .madstructs import *
from .madini import *


class LightInstance:
    def __init__(self, name, ldo, bake):
        self.name = name
        self.ldo = ldo
        self.bake = bake
    
    # add export uvs function
    def write(self, lightmesh, lightmesh_loop_offset, fldl, props):
        """
        - number of meshes, directly provided by LGT file
        - LDO name, easy with dict list
        - for each mesh:
            - number of vertices are directly provided by LGT file
            - vertex UVs are indirectly provided by LGT file
        """
        lgt_filepath = props.madtracks_dir + CACHE_PATH + self.ldo.replace("ldo", "lgt")
        with open(lgt_filepath, 'rb') as flgt:
            # allows to export LDO meshes in the correct order
            ldo_loop_count = struct.unpack("<i", flgt.read(4))[0]
            
            bmeshcnt = flgt.read(4)
            fldl.write(bmeshcnt)
            if "_high" in self.ldo.lower():
                # LDL files don't have this suffix
                self.ldo = self.ldo[:-9] + ".ldo"
            if self.ldo.lower() == "rampe_30_up.ldo":
                # old name of LDO present in LDL files
                self.ldo = "rampe_30.ldo"
            ldo_str = 'geometry/' + self.ldo
            ldo_str_len = len(ldo_str)
            fldl.write(struct.pack("<b", ldo_str_len))
            fldl.write(struct.pack("<%ds" % ldo_str_len, ldo_str.encode("utf-8")))
            fldl.write(struct.pack("<b", 0))
 
            if self.bake:
                # write lightmap UVs
                lgt_loop_offset = ldo_loop_count
                for mesh in range(struct.unpack("<i", bmeshcnt)[0]):
                    bvertcnt = flgt.read(4)
                    fldl.write(bvertcnt)
                    bloopcnt = flgt.read(4)
                    lgt_loop_offset -= struct.unpack("<i", bloopcnt)[0]
                    for vert in range(struct.unpack("<i", bvertcnt)[0]):
                        per_face_index = struct.unpack("<h", flgt.read(2))[0]
                        light_uv = lightmesh.data.uv_layers['LightMap'].data[lightmesh_loop_offset + lgt_loop_offset + per_face_index].uv # Affiches: 5550 + (342 - 6 - 24) = 5862 + per_face_index
                        light_uv = [light_uv[0], 1 - light_uv[1]]
                        # 16-bit, TODO add support for 32-bit
                        light_uv = np.array(light_uv, dtype='<f2')
                        fldl.write(light_uv.tobytes())
            else:
                # skip UVs
                for mesh in range(struct.unpack("<i", bmeshcnt)[0]):
                    fldl.write(struct.pack("<i", 0))

        if self.bake:
            return lightmesh_loop_offset + ldo_loop_count
        else:
            # instance wasn't merged to the lightmesh
            return lightmesh_loop_offset


def bakeable(obj):
    """ Returns whether a lightmap object can be present in the lightmap image """
    if obj.madtracks.animate or obj.madtracks.physics:
        # object will move and lightmap UVs won't fit in anymore
        return False

    for mat in obj.data.materials:
        for texslot in mat.texture_slots:
            if texslot and texslot.blend_type == 'SOFT_LIGHT':
                # I guess the world reflection will give an ugly effect on top of lightmap UVs?
                return False
    
    return True


def setup_scene(scene):
    """
    Work with a list of dictionaries that keep track of the object names along with their LDO name and a "merged" boolean.
    This list will be constructed in level INI order to keep track of objects to export as instances in the LDL file,
    while marking the objects to include in the lightmap image.
    Collectibles are not to be added in this list as they are ignored in all lightmap files.
    Join objects to be included in the lightmap image to a single object called "Lightmesh".
    The Lightmesh can then be unwrapped for the lightmap baking step.
    Finally write the LDL file using the list of dictionaries and companion LGT files ("merged" is true when an instance has its vertices in the UV map).

    LDL:
    - bitmap depth easy with scene property
    - number of instances easy with dict list
    - instances
    """
    props = scene.madtracks
    
    bpy.ops.object.select_all(action='DESELECT')

    light_instances = []
    for i in range(len(scene.objects), 0, -1):
        obj = scene.objects[i-1]
        if obj.madtracks.is_world and obj.madtracks.ldo:
            # world mesh is always first
            light_instances.insert(0, LightInstance(obj.name, obj.madtracks.ldo, bakeable(obj)))
            continue
        if obj.madtracks.is_trackpart and obj.madtracks.previous:
            # skip sequence trackpart
            continue
        if obj.madtracks.ldo and not obj.madtracks.is_collectible:
            light_instances.append(LightInstance(obj.name, obj.madtracks.ldo, bakeable(obj)))
        if obj.madtracks.is_trackpart and obj.madtracks.nextt:
            # loop thru trackpart sequence
            while obj.madtracks.nextt:
                obj = obj.madtracks.nextt
                light_instances.append(LightInstance(obj.name, obj.madtracks.ldo, bakeable(obj)))
    
    for instance in light_instances:
        dprint("Instance: {} {} bake: {}".format(instance.name, instance.ldo, instance.bake))
    
    # first bakeable object becomes the lightmesh
    for instance in light_instances:
        if instance.bake:
            lightmesh = bpy.data.objects[instance.name]
            break
    # ensure this object doesn't use a shared mesh as it would duplicate the mesh of all its users when joining
    if lightmesh.data.users > 1:
        lightmesh.data = lightmesh.data.copy()
    lightmesh.data.name = "lightmesh"
    lightmesh.name = "Lightmesh"
    # make it active for the remainder of the routine
    scene.objects.active = lightmesh

    # join objects in INI order, relying on Blender data concetenation
    for i in range(1, len(light_instances)):
        instance = light_instances[i]
        if instance.bake:
            bpy.data.objects[instance.name].select = True
            lightmesh.select = True
            bpy.ops.object.join()
            lightmesh.select = False
    
    # unwrap lightmesh in lightmap UV layer
    uv_map = lightmesh.data.uv_textures.new("LightMap")
    lightmesh.data.uv_textures.active = uv_map
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.unwrap()
    bpy.ops.uv.pack_islands(margin=0.00025)
    bpy.ops.object.editmode_toggle()

    # write LDL
    ldl_filepath = props.madtracks_dir + LDL_PATH + "LevelName.ldl"
    with open(ldl_filepath, 'wb') as fldl:
        bit_depth = props.lightmap_bitdepth
        if bit_depth not in [16, 32]:
            set_error('writing LDL header', "Bit depth %d unsupported" % bit_depth)
            return
        fldl.write(struct.pack("<4b", bit_depth, 0, 0, 0))
        fldl.write(struct.pack("<i", len(light_instances)))
        # fetch UVs from lightmesh data using an offset into its global array
        lightmesh_loop_offset = 0
        for instance in light_instances:
            lightmesh_loop_offset = instance.write(lightmesh, lightmesh_loop_offset, fldl, props)
    
    # create lightmap texture and materials slot (done here as to not repeat it)
    lightex = bpy.data.textures.new("lightmap", "IMAGE")
    for mat in lightmesh.data.materials:
        texslot = mat.texture_slots.add()
        texslot.texture = lightex
        texslot.blend_type = "MULTIPLY"
        texslot.uv_layer = "LightMap"
        texslot.use = False


def bake_preview(scene):
    props = scene.madtracks

    obj_index = scene.objects.find("Lightmesh")
    if obj_index == -1:
        set_error('baking lightmap', "No lightmesh object found, was the scene setup?")
        return
    lightmesh = scene.objects[obj_index]

    # FIXME doesn't prevent preview from breaking if a different object was selected beforehand
    bpy.ops.object.select_all(action='DESELECT')
    lightmesh.select = True

    # ensure lighting is correct
    for obj in scene.objects:
        if obj != lightmesh and obj.type == 'MESH' and (obj.madtracks.animate or obj.madtracks.physics):
            obj.hide_render = True
    for lamp in bpy.data.lamps:
        lamp.use_diffuse = True
    scene.world.light_settings.environment_color = 'SKY_COLOR'

    # set up materials for baking
    for mat in lightmesh.data.materials:
        if mat.madtracks.has_rgba:
            mat.madtracks.rgba_save = (mat.diffuse_color[0], mat.diffuse_color[1], mat.diffuse_color[2], mat.alpha)
        mat.diffuse_color = (1.0, 1.0, 1.0)
        mat.alpha = 1.0
        for i in range(len(mat.texture_slots)):
            mat.use_textures[i] = False
    
    # set up bake context
    lightmesh.data.uv_textures.active = lightmesh.data.uv_textures["LightMap"]
    lightmesh.data.uv_textures["LightMap"].active_render = True
    scene.render.bake_margin = 12
    scene.render.use_bake_clear = False

    # generate a new active image each time to be able to compare with previous ones
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.select_all(action='SELECT')
    bpy.context.area.type = 'IMAGE_EDITOR'
    bpy.ops.image.new(name="LevelName_lgt0000", width=8192, height=8192, color=(0.5, 0.5, 0.5, 1.0), alpha=False, generated_type='BLANK', float=False, gen_context='NONE', use_stereo_3d=False)
    lightmap_img = bpy.context.space_data.image
    bpy.ops.object.bake_image()
    bpy.context.area.type = 'VIEW_3D'
    bpy.ops.object.editmode_toggle()

    # update lightmap texture with baked image
    tex_idx = bpy.data.textures.find("lightmap")
    if tex_idx == -1:
        set_error('previewing lightmap', "No lightmap texture found, was the scene setup?")
    lightex = bpy.data.textures[tex_idx]
    lightex.image = lightmap_img

    # set up materials for preview
    for mat in lightmesh.data.materials:
        if mat.madtracks.has_rgba:
            mat.diffuse_color = mat.madtracks.rgba_save[:3]
            mat.alpha = mat.madtracks.rgba_save[3]
        for i in range(len(mat.texture_slots)):
            mat.use_textures[i] = True
    
    # setup lighting for preview
    for lamp in bpy.data.lamps:
        lamp.use_diffuse = False
    scene.world.light_settings.environment_color = 'PLAIN'

    for obj in scene.objects:
        if obj != lightmesh and obj.type == 'MESH':
            obj.hide_render = False

# def export_uvs(lgt_filepath, fldl, lightmesh, loop_instance_offset, scene):
#     with open(lgt_filepath, 'rb') as flgt:
#         # allows to export LDO meshes in the correct order
#         loop_count = struct.unpack("<i", flgt.read(4))[0]
#         loop_index = loop_count
#         print("instance loop count: {}".format(loop_index))
#         # read mesh count for HACK below
#         bmeshcnt = flgt.read(4)
#         mesh_cnt = struct.unpack("<i", bmeshcnt)[0]
#         name_len = flgt.read(1)[0]
#         flgt.seek(name_len + 1, 1) # account for null character
#         vertex_cnt = flgt.read(4)
#         while vertex_cnt != b'':
#             # HACK read inside the loop to bail or make code still correct if no bail, brain completely fried for hours, no work no more
#             # read vertex count from LDL in addition to LGT as it can become 0 if not eligible for lightmap
#             ldl_vertex_cnt = struct.unpack("<i", fldl.read(4))[0]
#             if ldl_vertex_cnt == 0:
#                 # FIXME skip all meshes, ignores potential non-empty LDO meshes after this mesh
#                 for _ in range(mesh_cnt - 1):
#                     fldl.seek(4, 1)
#                 return 0 # we read an instance which was potentially uneligible, so not present in the lightmesh global
#             mesh_loop_cnt = struct.unpack("<i", flgt.read(4))[0]
#             loop_index -= mesh_loop_cnt
#             for _ in range(struct.unpack("<i", vertex_cnt)[0]):
#                 per_face_index = struct.unpack("<h", flgt.read(2))[0]
#                 light_uv = lightmesh.data.uv_layers['LightMap'].data[loop_instance_offset + loop_index + per_face_index].uv # Affiches: 5550 + (342 - 6 - 24) = 5862 + per_face_index
#                 light_uv = [light_uv[0], 1 - light_uv[1]]
#                 # 16-bit, TODO add support for 32-bit
#                 light_uv = np.array(light_uv, dtype='<f2')
#                 fldl.write(light_uv.tobytes())
#             vertex_cnt = flgt.read(4)
#     return loop_count


# def export_metadata(obj, fldl, props, export_uvs=True):
#     loop_index = len(obj.data.loops)
#     ldo_filename = obj.madtracks.ldo
#     lgt_filepath = props.madtracks_dir + ".cache" + os.path.sep + ldo_filename.replace(".ldo", ".lgt")
#     with open(lgt_filepath, 'rb') as flgt:
#         print("reading LGT")
#         # skip total loop count which is only for export_uvs function to work
#         flgt.seek(4, 1)
#         # transfer LDO light cache bytes
#         bmeshcnt = flgt.read(4)
#         mesh_cnt = struct.unpack("<i", bmeshcnt)[0]
#         fldl.write(bmeshcnt) # LDO mesh count
#         name_len = flgt.read(1)[0]
#         bmeshname = flgt.read(name_len)
#         mesh_name = struct.unpack("<%ds" % name_len, bmeshname)[0].decode("utf-8")
#         if mesh_name.lower() == "geometry/rampe_30_up.ldo":
#             # this trackpart has its old name in original lightmaps
#             fldl.write(struct.pack("<b", 21))
#             fldl.write(struct.pack("<21s", "geometry/rampe_30.ldo".encode("utf-8")))
#         else:
#             fldl.write(struct.pack("<b", name_len))
#             fldl.write(bmeshname)
#         fldl.write(flgt.read(1))
#         if not export_uvs:
#             # signify this LDO shouldn't be lightmapped
#             for _ in range(mesh_cnt):
#                 fldl.write(struct.pack("<i", 0))
#             return
#         vertex_cnt = flgt.read(4)
#         while vertex_cnt != b'':
#             print("reading mesh metadata")
#             fldl.write(vertex_cnt)
#             flgt.seek(4, 1) # skip loop count
#             for _ in range(struct.unpack("<i", vertex_cnt)[0]):
#                 flgt.seek(2, 1) # skip vertex loop index
#                 # write zeroes to replace with UV coords of unwrapped lightmesh
#                 if props.lightmap_bitdepth == 16:
#                     print("writing mesh metadata")
#                     fldl.write(struct.pack("<4b", 0, 0, 0, 0))
#                 elif props.lightmap_bitdepth == 32:
#                     print("writing mesh metadata")
#                     fldl.write(struct.pack("<8b", 0, 0, 0, 0, 0, 0, 0, 0))
#             vertex_cnt = flgt.read(4)