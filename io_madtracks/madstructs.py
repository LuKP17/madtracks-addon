# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: rvstruct.py
# Original author: Marvin Thiel
#
# File first modified on 02/28/24
# Author: Lucas Pottier
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

import os
import struct
from math import ceil, sqrt
from .common import *

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


DUMMY_TYPE_MASK =   15
DUMMY_TYPE_WORLD =  5
DUMMY_TYPE_NUM =    6
DUMMY_TYPE_OUT =    9
DUMMY_TYPE_ROOF =   10
DUMMY_TYPE_BONUS =  11
DUMMY_FLOAT3 =      64
DUMMY_FLOAT12 =     128

class Atomic:
    """
    Handles a LDO atomic
    """
    def __init__(self):
        self.mesh_cnt = 0
        self.material_cnt = 0
        self.is_empty = False

        self.meshes = []
        self.materials = []
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
        dummy_count = file.read(1)[0]
        file.seek(8, 1)  # skip usual 8 bytes
        self.name = struct.unpack("<%ds" % name_len, file.read(name_len))[0].decode("utf-8")
        for i in range(dummy_count):
            dummy_flags = struct.unpack("<h", file.read(2))[0]

            # retrieve dummy flags
            dflag_floats3 = bool(dummy_flags & DUMMY_FLOAT3)
            dflag_floats12 = bool(dummy_flags & DUMMY_FLOAT12)

            if (dflag_floats3):
                file.seek(12, 1)  # skip 3 floats
            if (dflag_floats12):
                file.seek(48, 1)  # skip 12 floats

            file.seek(4, 1)  # skip dummy index
            file.seek(4, 1)  # skip usual 4 bytes

            # retrieve dummy type
            dummy_type = dummy_flags & DUMMY_TYPE_MASK

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

    def write(self, file, debug=False):
        # Atomic header
        file.write(struct.pack("<H", self.mesh_cnt))
        file.write(struct.pack("<H", self.material_cnt))
        
        if debug:
            self.dbg_print()

    def as_dict(self):
        dic = { "mesh_cnt": self.mesh_cnt,
                "material_cnt": self.material_cnt,
                "is_empty": self.is_empty,
                "meshes": self.meshes,
                "materials": self.materials,
                "name": self.name
        }
        return dic
    
    def dbg_print(self):
        print("------------------ ATOMIC DEBUG INFO -------------------")
        print("mesh_cnt: {}  material_cnt: {}   is_empty: {}\n".format(self.mesh_cnt, self.material_cnt, self.is_empty))


MAT_FLAG_RGBA =          1
MAT_FLAG_UNKNOWN =       4
MAT_FLAG_DIFFUSE =       8
MAT_FLAG_BRIGHTNESS =    64
MAT_FLAG_ENVMAP =        128

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
                tri = Tri()
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
        self.uv = UV(file)
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
    def __init__(self):
        self.vertices_id = []

    def __repr__(self):
        return "Tri"

    def read(self, file):
        self.vertices_id = struct.unpack("<3h", file.read(6))

    def as_dict(self):
        dic = { "vertices_id": self.vertices_id
        }
        return dic


class UV:
    """
    Handles a LDO uv
    """
    def __init__(self, file=None):
        self.u = 0.0
        self.v = 0.0
        
        if file:
            self.read(file)

    def __repr__(self):
        return str(self.as_dict())

    def read(self, file):
        self.u = struct.unpack("<f", file.read(4))[0]
        self.v = struct.unpack("<f", file.read(4))[0]
        
        #if self.u < 0. or self.u > 1. or self.v < 0. or self.v > 1.:
            # do something about it?
            #print("Warning: UV coordinates out of bounds: ({};{})".format(self.u, self.v))

    def write(self, file):
        file.write(struct.pack("<f", self.u))
        file.write(struct.pack("<f", self.v))

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
