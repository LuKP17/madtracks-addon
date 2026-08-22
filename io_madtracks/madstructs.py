# Copyright (C) 2024-2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original author: Marvin Thiel
#-----------------------------------------------------------------------------

"""
Name:    madstructs
Purpose: Reading and writing Mad Tracks binary files

See docs/ for file formats specifications.

The following data structures have been reconstructed from scratch,
by analyzing binary files in a hex editor, with the help of debug messages
thrown by the game when messing around with byte values.

Files can be successfully read or written with the current understanding
of Mad Tracks's file formats, but some classes names or attributes can be wrong.
Especially since some values appeared in only one data file and required guess work.
"""

import struct
from math import ceil, sqrt
from .common import *

import numpy as np

MAT_FLAG_RGBA =          1
MAT_FLAG_UNKNOWN =       4
MAT_FLAG_DIFFUSE =       8
MAT_FLAG_BRIGHTNESS =    64
MAT_FLAG_ENVMAP =        128

class LDO:
    """
    Handles .ldo files and contains all sub-structures
    """
    def __init__(self):
        self.atomic_cnt = 0
        
        self.atomics = []

    def read(self, file, debug=False):
        # Header
        file.seek(4, 1) # skip versions
        self.atomic_cnt = struct.unpack("<h", file.read(2))[0]
        
        # Use a function to keep the actual processing clear and maintain it easier.
        # Call it before reading the next parts to have debug prints in the right order.
        if debug:
            self.dbg_print()

        # Atomics
        for _ in range(self.atomic_cnt):
            atomic = Atomic()
            atomic.read(file, debug)
            self.atomics.append(atomic)

    def write(self, file, debug=False):
        # Header
        file.write(struct.pack("<4B", 0x01, 0x03, 0x02, 0x03))
        file.write(struct.pack("<H", self.atomic_cnt))
        
        if debug:
            self.dbg_print()
        
        # Atomics
        for i in range(self.atomic_cnt):
            self.atomics[i].write(file, debug)

    def __repr__(self):
        return "LDO"

    def as_dict(self):
        dic = {"atomic_cnt": self.atomic_cnt,
               "atomics": self.atomics,
        }
        return dic
    
    def dbg_print(self):
        print("==================== LDO DEBUG INFO ====================")
        print("atomic_cnt: {}\n".format(self.atomic_cnt))


class Atomic:
    """
    Handles a LDO atomic
    """
    def __init__(self):
        self.mesh_cnt = 0
        self.material_cnt = 0
        self.dummy_cnt = 0
        self.is_empty = False

        self.meshes = []
        self.materials = []
        self.dummies = []
        self.name = ""  # used for LDO with multiple atomics

    def __repr__(self):
        return "Atomic"

    def read(self, file, debug=False):
        # Atomic header
        self.mesh_cnt = struct.unpack("<h", file.read(2))[0]
        self.material_cnt = struct.unpack("<h", file.read(2))[0]
        data = file.read(1)[0]
        if (data == 0x01):
            self.is_empty = True
            if debug:
                self.dbg_print()
            return
        file.seek(1, 1)  # skip ~anim
        file.seek(16, 1)  # skip ~visibility
        
        if debug:
            self.dbg_print()

        # Materials
        for _ in range(self.material_cnt):
            material = Material()
            material.read(file, debug)
            self.materials.append(material)
        
        # Meshes
        for _ in range(self.mesh_cnt):
            mesh = Mesh()
            mesh.read(file, debug)
            self.meshes.append(mesh)
        
        # Dummies
        file.seek(10, 1)  # skip usual 10 bytes
        name_len = file.read(1)[0]
        self.dummy_cnt = file.read(1)[0]
        file.seek(8, 1)  # skip usual 8 bytes
        self.name = struct.unpack("<%ds" % name_len, file.read(name_len))[0].decode("utf-8")
        for _ in range(self.dummy_cnt):
            dummy = Dummy()
            dummy.read(file, debug)
            self.dummies.append(dummy)
            

    def write(self, file, debug=False):
        # Atomic header
        file.write(struct.pack("<H", self.mesh_cnt))
        file.write(struct.pack("<H", self.material_cnt))
        file.write(struct.pack("<B", self.is_empty))
        if self.is_empty:
            if debug:
                self.dbg_print()
            return
        file.write(struct.pack("<B", 0x00))  # ~anim
        file.write(struct.pack(">4I", 0x00000036, 0x03002040, 0xffffef40, 0x305c4841))  # ~visibility taken from Amorce_15.ldo
        
        if debug:
            self.dbg_print()
            
        # Materials
        for i in range(self.material_cnt):
            self.materials[i].write(file, debug)

    def as_dict(self):
        dic = { "mesh_cnt": self.mesh_cnt,
                "material_cnt": self.material_cnt,
                "dummy_cnt": self.dummy_cnt,
                "is_empty": self.is_empty,
                "meshes": self.meshes,
                "materials": self.materials,
                "dummies": self.dummies,
                "name": self.name
        }
        return dic
    
    def dbg_print(self):
        print("------------------ ATOMIC DEBUG INFO -------------------")
        print("is_empty: {}  mesh_cnt: {}  material_cnt: {}\n".format(self.is_empty, self.mesh_cnt, self.material_cnt))


class Material:
    """
    Handles a LDO material
    """
    def __init__(self):
        self.name_len = 0
        self.name = ""
        self.flags = 0
        self.shader_tech = 0
        self.RGBA = ()
        self.diffuse_name_len = 0
        self.diffuse_name = ""
        self.brightness = 0.
        self.envmap_name_len = 0
        self.envmap_name = ""

    def __repr__(self):
        return "Material"

    def read(self, file, debug=False):
        # Material
        self.name_len = file.read(1)[0]
        self.name = struct.unpack("<%ds" % self.name_len, file.read(self.name_len))[0].decode("utf-8")
        file.seek(1, 1)  # skip null termination
        self.flags = struct.unpack("<h", file.read(2))[0]
        self.shader_tech = struct.unpack("<h", file.read(2))[0]
        if (bool(self.flags & MAT_FLAG_RGBA)):
            self.RGBA += (file.read(1)[0], file.read(1)[0], file.read(1)[0], file.read(1)[0],)
        if (bool(self.flags & MAT_FLAG_UNKNOWN)):
            file.seek(4, 1)  # skip unknown data
        if (bool(self.flags & MAT_FLAG_DIFFUSE)):
            self.diffuse_name_len = file.read(1)[0]
            self.diffuse_name = struct.unpack("<%ds" % self.diffuse_name_len, file.read(self.diffuse_name_len))[0].decode("utf-8")
            file.seek(1, 1)  # skip null termination
        if (bool(self.flags & MAT_FLAG_BRIGHTNESS)):
            self.brightness = struct.unpack("<f", file.read(4))[0]
        if (bool(self.flags & MAT_FLAG_ENVMAP)):
            file.seek(4, 1)  # skip unknown data
            self.envmap_name_len = file.read(1)[0]
            self.envmap_name = struct.unpack("<%ds" % self.envmap_name_len, file.read(self.envmap_name_len))[0].decode("utf-8")
            file.seek(1, 1)  # skip null termination

        if debug:
            self.dbg_print()
            
    def write(self, file, debug=False):
        file.write(struct.pack("<B", self.name_len))
        file.write(struct.pack("<%ds" % self.name_len, self.name.encode("utf-8")))
        file.write(struct.pack("<B", 0))  # null termination
        file.write(struct.pack("<H", self.flags))
        file.write(struct.pack("<H", self.shader_tech))
        if (bool(self.flags & MAT_FLAG_RGBA)):
            file.write(struct.pack("<4B", self.RGBA[0], self.RGBA[1], self.RGBA[2], self.RGBA[3]))
        if (bool(self.flags & MAT_FLAG_DIFFUSE)):
            file.write(struct.pack("<B", self.diffuse_name_len))
            file.write(struct.pack("<%ds" % self.diffuse_name_len, self.diffuse_name.encode("utf-8")))
            file.write(struct.pack("<B", 0))  # null termination
        if (bool(self.flags & MAT_FLAG_BRIGHTNESS)):
            file.write(struct.pack("<f", self.brightness))
        if (bool(self.flags & MAT_FLAG_ENVMAP)):
            file.write(struct.pack("<f", 0.4))  # <unknown2> taken from FrBis_Verre.ldo
            file.write(struct.pack("<B", self.envmap_name_len))
            file.write(struct.pack("<%ds" % self.envmap_name_len, self.envmap_name.encode("utf-8")))
            file.write(struct.pack("<B", 0))  # null termination
        
        if debug:
            self.dbg_print()
    
    def as_dict(self):
        dic = { "name_len": self.name_len,
                "name": self.name,
                "flags": self.flags,
                "shader_tech": self.shader_tech,
                "RGBA": self.RGBA,
                "diffuse_name_len": self.diffuse_name_len,
                "diffuse_name": self.diffuse_name,
                "brightness": self.brightness,
                "envmap_name_len": self.envmap_name_len,
                "envmap_name": self.envmap_name
        }
        return dic

    def dbg_print(self):
        print("----------------- MATERIAL DEBUG INFO ------------------")
        print("name: {}  shader_tech: {}".format(self.name, self.shader_tech))
        if (bool(self.flags & MAT_FLAG_RGBA)):
            red, green, blue, alpha = self.RGBA
            print("red: {}   green: {}   blue: {}   alpha: {}".format(red, green, blue, alpha))
        if (bool(self.flags & MAT_FLAG_DIFFUSE)):
            print("diffuse_name: {}".format(self.diffuse_name))
        if (bool(self.flags & MAT_FLAG_BRIGHTNESS)):
            print("brightness: {}".format(self.brightness))
        if (bool(self.flags & MAT_FLAG_ENVMAP)):
            print("envmap_name: {}".format(self.envmap_name))
        print()


class Mesh:
    """
    Handles a LDO mesh
    """
    def __init__(self):
        self.vertex_cnt = 0
        self.tri_cnt = 0
        self.va_cnt = 0
        self.va = ()
        
        self.vertices = []
        self.tri_seq_cnt = 0
        self.tri_seq_mat = []
        self.tri_seq_len = []
        self.tris = []
            
    def __repr__(self):
        return "Mesh"
    
    def read(self, file, debug=False):
        # Mesh header
        self.vertex_cnt = struct.unpack("<i", file.read(4))[0]
        self.tri_cnt = struct.unpack("<i", file.read(4))[0]
        file.seek(8, 1)  # skip unknown data
        file.seek(16, 1)  # skip unknown data
        file.seek(4, 1)  # skip unknown data
        self.va_cnt = file.read(1)[0]
        self.va += (file.read(1)[0], file.read(1)[0], file.read(1)[0], file.read(1)[0],)

        # Vertices
        for _ in range(self.vertex_cnt):
            vertex = Vertex()
            vertex.read(file, self.va_cnt, self.va)
            self.vertices.append(vertex)
        
        # Tris header
        self.tri_seq_cnt = struct.unpack("<i", file.read(4))[0]
        # Tri sequences
        for _ in range(self.tri_seq_cnt):
            self.tri_seq_mat.append(struct.unpack("<i", file.read(4))[0])
            self.tri_seq_len.append(struct.unpack("<i", file.read(4))[0])
            for _ in range(self.tri_seq_len[-1]):
                tri = Tri(self.tri_seq_mat[-1])
                tri.read(file)
                self.tris.append(tri)
        
        if debug:
            self.dbg_print()
    
    def as_dict(self):
        dic = { "vertex_cnt": self.vertex_cnt,
                "tri_cnt": self.tri_cnt,
                "va_cnt": self.va_cnt,
                "va": self.va,
                "vertices": self.vertices,
                "tri_seq_cnt": self.tri_seq_cnt,
                "tri_seq_mat": self.tri_seq_mat,
                "tri_seq_len": self.tri_seq_len,
                "tris": self.tris
        }
        return dic
    
    def dbg_print(self):
        print("------------------- MESH DEBUG INFO --------------------")
        print("vertex_cnt: {}  tri_cnt: {}  tri_seq_mat: {}  tri_seq_len: {}".format(self.vertex_cnt, self.tri_cnt, self.tri_seq_mat, self.tri_seq_len))
        print("va_cnt: {}  va: {}".format(self.va_cnt, self.va))
        print()


class Dummy:
    """
    Handles a LDO dummy
    """
    def __init__(self):
        self.flags = 0
        
        self.position = None
        self.rotmat = []
            
    def __repr__(self):
        return "Dummy"
    
    def read(self, file, debug=False):
        self.flags = struct.unpack("<h", file.read(2))[0]

        if (bool(self.flags & DUMMY_FLAG_POS)):
            self.position = Vector(file)
        if (bool(self.flags & DUMMY_FLAG_POSROT)):
            self.position = Vector(file)
            self.rotmat.append(Vector(file))
            self.rotmat.append(Vector(file))
            self.rotmat.append(Vector(file))

        file.seek(4, 1)  # skip dummy index
        file.seek(4, 1)  # skip usual 4 bytes

        # retrieve dummy type
        dummy_type = self.flags & DUMMY_MASK_TYPE

        if (dummy_type == DUMMY_TYPE_WORLD):
            file.seek(5, 1)  # skip "world"
        elif (dummy_type == DUMMY_TYPE_NUM):
            file.seek(6, 1)  # skip "Dummy#"
        elif (dummy_type == DUMMY_TYPE_OUT):
            file.seek(9, 1)  # skip "DUMMY_OUT"
        elif (dummy_type == DUMMY_TYPE_ROOF):
            file.seek(10, 1)  # skip "DUMMY ROOF"
        elif (dummy_type == DUMMY_TYPE_BONUS):
            file.seek(11, 1)  # skip "DUMMY BONUS"
        
        if debug:
            self.dbg_print()
    
    def as_dict(self):
        dic = { "flags": self.flags,
                "position": self.position,
                "rotation": self.rotmat
        }
        return dic
    
    def dbg_print(self):
        print("------------------- DUMMY DEBUG INFO --------------------")
        print("flags: {}".format(self.flags))
        if self.position:
            print("position: {}".format(self.position.as_dict()))
        if len(self.rotmat) == 3:
            print("rotmat: {} {} {}".format(self.rotmat[0].as_dict(), self.rotmat[1].as_dict(),self.rotmat[2].as_dict()))
        print()


class Vertex:
    """
    Handles a LDO vertex
    """
    def __init__(self):
        self.position = None
        self.normal = None
        self.uv = None

    def __repr__(self):
        return "Vertex"

    def read(self, file, va_cnt, va):
        # Vertex
        self.position = Vector(file)
        self.normal = Vector(file)
        self.uv = UV()
        self.uv.read4(file)
        if (va[2] == 0x0b):
            file.seek(4, 1)  # skip unknown data
        if (va_cnt > 3):
            file.seek(8, 1)  # skip unknown data
            if (va[3] == 0x0c):
                file.seek(4, 1)  # skip unknown data

    def as_dict(self):
        dic = {"position": self.position.as_dict(),
               "normal": self.normal.as_dict(),
               "uv": self.uv.as_dict()
               }
        return dic


class Tri:
    """
    Handles a LDO tri
    """
    def __init__(self, material_id):
        self.vertices_id = []
        self.material_id = material_id

    def __repr__(self):
        return "Tri"

    def read(self, file):
        self.vertices_id = struct.unpack("<3h", file.read(6))

    def as_dict(self):
        dic = { "vertices_id": self.vertices_id
        }
        return dic


class LDL:
    """
    Handles .ldl files to be read in conjunction with a level .ini file
    """
    def __init__(self, file):
        self.bit_depth = 0
        self.instance_cnt = 0
        self.file = file

        self.mesh_cnt = 0
        self.vertex_cnt = []
        self.current_name = None
        self.current_uvs = []

    def read_header(self):
        self.bit_depth = self.file.read(1)[0]
        if self.bit_depth not in [16, 32]:
            set_error('reading LDL header', "Bit depth %d unsupported" % self.bit_depth)
            return False
        self.file.seek(3, 1) # skip unknown, maybe part of bit depth
        self.instance_cnt = struct.unpack("<i", self.file.read(4))[0]
        return True

    def read_instance(self, debug=False):
        self.instance_cnt -= 1
        if self.instance_cnt < 0:
            # allow trying to read one instance past the file (need to read each instance in advance)
            if self.instance_cnt == -2:
                set_error('reading LDL instance', "No more instances to read")
            return
        self.mesh_cnt = struct.unpack("<i", self.file.read(4))[0]
        name_len = self.file.read(1)[0]
        self.current_name = struct.unpack("<%ds" % name_len, self.file.read(name_len))[0].decode("utf-8")
        self.file.seek(1, 1)  # skip null termination
        self.vertex_cnt = []
        self.current_uvs = []
        for _ in range(self.mesh_cnt):
            uvs = []
            vertex_cnt = struct.unpack("<i", self.file.read(4))[0]
            for _ in range(vertex_cnt):
                uv = UV()
                if self.bit_depth == 16:
                    uv.read2(self.file)
                if self.bit_depth == 32:
                    uv.read4(self.file)
                uvs.append(uv)
            self.vertex_cnt.append(vertex_cnt)
            self.current_uvs.append(uvs)

        if debug:
            self.dbg_print()

    def __repr__(self):
        return "LDL"
    
    def dbg_print(self):
        print("----------------- LIGHTMAP DEBUG INFO ------------------")
        print("current_name: {}  mesh_cnt: {}  vertex_cnt: {}".format(self.current_name, self.mesh_cnt, self.vertex_cnt))
        print()


class UV:
    """
    Handles a LDO uv
    """
    def __init__(self):
        self.u = 0.0
        self.v = 0.0

    def __repr__(self):
        return str(self.as_dict())

    def read2(self, file):
        self.u = np.frombuffer(file.read(2), dtype='<f2')[0]
        self.v = np.frombuffer(file.read(2), dtype='<f2')[0]

    def read4(self, file):
        self.u = struct.unpack("<f", file.read(4))[0]
        self.v = struct.unpack("<f", file.read(4))[0]
        
        #if self.u < 0. or self.u > 1. or self.v < 0. or self.v > 1.:
            # do something about it?
            #print("Warning: UV coordinates out of bounds: ({};{})".format(self.u, self.v))

    def as_dict(self):
        dic = {"u": self.u,
               "v": self.v
               }
        return dic

    def from_dict(self, dic):
        self.u = dic["u"]
        self.v = dic["v"]


class Vector:
    """
    A very simple vector class
    """
    def __init__(self, file=None, data=None):
        if data:
            self.data = [data[0], data[1], data[2]]
        else:
            self.data = [0, 0, 0]

        if file:
            self.read(file)

    def read(self, file):
        # Reads the coordinates
        self.data = [c for c in struct.unpack("<3f", file.read(12))]

    def write(self, file):
        # Writes all coordinates
        file.write(struct.pack("<3f", *self.data))

    def get_distance_to(self, v):
        return sqrt((self.x - v.x)**2 + (self.y - v.y)**2 + (self.z - v.z)**2)

    def scalar(self, v):
        """ Returns the dot/scalar product with v """
        if len(v.data) != len(self.data):
            print("MADSTRUCTS ERROR: Vectors are of different lengths.")
            return None
        return sum([v[x] * self[x] for x in range(len(self.data))])

    dot = scalar

    def cross(self, v):
        """ Returns the cross product with v """
        s1, s2, s3 = (
            self[1] * v[2] - self[2] * v[1],
            self[2] * v[0] - self[0] * v[2],
            self[0] * v[1] - self[1] * v[0]
        )
        return Vector(data=(s1, s2, s3))

    def scale(self, a):
        return Vector(data=(self.x * a, self.y * a, self.z * a))

    def magnitude(self):
        return sqrt(sum([self[i] * self[i] for i in range(len(self))]))

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return self
        for i in range(len(self)):
            self[i] /= mag
        return self

    def as_dict(self):
        dic = {"x": self.x,
               "y": self.y,
               "z": self.z
               }
        return dic

    def __add__(self, v):
        return Vector(data=(self[0] + v[0], self[1] + v[1], self[2] + v[2]))

    def __sub__(self, v):
        return Vector(data=(self[0] - v[0], self[1] - v[1], self[2] - v[2]))

    def __truediv__(self, a):
        return Vector(data=(self.x / a, self.y / a, self.z / a))

    def __mul__(self, a):
        return Vector(data=(self.x * a, self.y * a, self.z * a))

    __rmul__ = __mul__

    def __iter__(self):
        for elem in self.data:
            yield elem

    def __getitem__(self, i):
        return self.data[i]

    def __repr__(self):
        return "Vector"

    def __len__(self):
        return len(self.data)

    def __setitem__(self, i, value):
        self.data[i] = value

    @property
    def x(self):
        return self[0]
    @property
    def y(self):
        return self[1]
    @property
    def z(self):
        return self[2]
