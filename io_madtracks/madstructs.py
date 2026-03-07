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

Supported Formats:
- .ldo (Geometry)

Missing Formats:
- .ldl (Lightmap)

/!\ DISCLAIMER

The following data structures have been reconstructed from scratch,
by analyzing binary files in a hex editor, with the help of debug messages
thrown by the game when messing around with byte values.

Files can be successfully read or written with the current understanding
of Mad Tracks's file formats, but some classes names or attributes can be wrong.
Especially since some values appeared in only one data file and required guesswork.
Feel free to suggest clarifications for unknown attributes.
"""

import os
import struct
from math import ceil, sqrt
from .common import *

MAT_RGBA =          1
MAT_FLOAT3 =        4
MAT_TEXTURE =       8
MAT_BRIGHTNESS =    64
MAT_REFLECTION =    128

DUMMY_TYPE_MASK =   15
DUMMY_TYPE_WORLD =  5
DUMMY_TYPE_NUM =    6
DUMMY_TYPE_OUT =    9
DUMMY_TYPE_ROOF =   10
DUMMY_TYPE_BONUS =  11
DUMMY_FLOAT3 =      64
DUMMY_FLOAT12 =     128

class LDO:
    """
    Reads a .ldo file and stores all sub-structures.
    If an opened file is supplied, it immediately starts reading from it.
    A .ldo file contains one or multiple atomics (models) that make up a 3D object.
    """
    def __init__(self, file=None):
        self.atomic_count = 0           # amount of Atomic objects
        self.atomics = []               # sequence of Atomic structures

        # Immediately starts reading if an opened file is supplied
        if file:
            self.read(file)

    def read(self, file):
        # Reads the HEADER
        file.seek(4, 1) # skip version bytes
        self.atomic_count = struct.unpack("<h", file.read(2))[0]

        # Reads the atomics
        for atomic in range(self.atomic_count):
            self.atomics.append(Atomic(file))

    def __repr__(self):
        return "LDO"

    def as_dict(self):
        dic = {"atomic_count": self.atomic_count,
               "atomics": self.atomics,
        }
        return dic


class Atomic:
    """
    Reads the Atomics found in .ldo files from an opened file.
    The name "Atomic" was inferred from some debug messages.
    It represents a model made of meshes and materials.
    """
    def __init__(self, file=None):
        self.is_empty = False    # if the atomic is empty

        self.mesh_count = 0      # amount of Mesh objects
        self.mat_count = 0       # amount of Material objects

        self.meshes = []         # sequence of Mesh structures
        self.materials = []      # sequence of Material structures

        self.name = "UNNAMED"    # used for files with multiple atomics

        # FIXME the atomic dummies are missing on purpose.
        # Read the data and add the attributes here once a use for them is found.

        if file:
            self.read(file)

    def __repr__(self):
        return "Atomic"

    def read(self, file):
        # Reads the ATOMIC HEADER
        self.mesh_count = struct.unpack("<h", file.read(2))[0]
        self.mat_count = struct.unpack("<h", file.read(2))[0]

        data = file.read(1)[0]
        if (data == 0x01):
            self.is_empty = True
            return
        
        file.seek(1, 1) # skip suspected isAtomicAnimated boolean
        file.seek(16, 1) # skip visibility floats

        # Reads all materials
        for i in range(self.mat_count):
            self.materials.append(Material(file))
        
        # Reads all meshes
        for i in range(self.mesh_count):
            self.meshes.append(Mesh(file, self))
        
        # Skips all dummies
        file.seek(10, 1) # skip usual 10 bytes
        name_len = file.read(1)[0]
        dummy_count = file.read(1)[0]
        file.seek(8, 1) # skip usual 8 bytes
        self.name = struct.unpack("<%ds" % name_len, file.read(name_len))[0].decode("utf-8")
        for i in range(dummy_count):
            dummy_flags = struct.unpack("<h", file.read(2))[0]

            # retrieve dummy flags
            dflag_floats3 = bool(dummy_flags & DUMMY_FLOAT3)
            dflag_floats12 = bool(dummy_flags & DUMMY_FLOAT12)

            if (dflag_floats3):
                file.seek(12, 1) # skip 3 floats
            if (dflag_floats12):
                file.seek(48, 1) # skip 12 floats

            file.seek(4, 1) # skip dummy index
            file.seek(4, 1) # skip usual 4 bytes

            # retrieve dummy type
            dummy_type = dummy_flags & DUMMY_TYPE_MASK

            if (dummy_type == DUMMY_TYPE_WORLD):
                file.seek(5, 1) # skip "world"
            elif (dummy_type == DUMMY_TYPE_NUM):
                file.seek(6, 1) # skip "Dummy#"
            elif (dummy_type == DUMMY_TYPE_OUT):
                file.seek(9, 1) # skip "DUMMY_OUT"
            elif (dummy_type == DUMMY_TYPE_ROOF):
                file.seek(10, 1) # skip "DUMMY ROOF"
            elif (dummy_type == DUMMY_TYPE_BONUS):
                file.seek(11, 1) # skip "DUMMY BONUS"

    def as_dict(self):
        dic = { "is_empty": self.is_empty,
                "mesh_count": self.mesh_count,
                "mat_count": self.mat_count,
                "meshes": self.meshes,
                "materials": self.materials,
                "name": self.name
        }
        return dic


class Material:
    """
    Reads the Materials found in .ldo files from an opened file.
    """
    def __init__(self, file=None):
        self.name = ""                  # name of the material

        # shader flags
        self.sflag_RGBA = False         # RGBA color channels, from 0 to 255

        self.sflag_float3 = False       # FIXME 3 unknown floats

        self.sflag_texture = False      # uses a texture
        self.tex_name = ""              # name of the texture

        self.sflag_brightness = False   # material "brightness", from -1 to 1

        self.sflag_reflection = False   # uses a reflection texture
        self.refltex_name = ""          # name of the reflection texture

        if file:
            self.read(file)
    
    def read(self, file):
        # Reads the MATERIAL
        name_len = file.read(1)[0]
        self.name = struct.unpack("<%ds" % name_len, file.read(name_len))[0].decode("utf-8")
        file.seek(1, 1) # skip string termination

        shader_flags = struct.unpack("<h", file.read(2))[0]
        file.seek(2, 1) # skip shader technique

        # retrieve shader flags (there are 16 flags, but the rest of them doesn't affect file reading)
        self.sflag_RGBA = bool(shader_flags & MAT_RGBA)
        self.sflag_float3 = bool(shader_flags & MAT_FLOAT3)
        self.sflag_texture = bool(shader_flags & MAT_TEXTURE)
        self.sflag_brightness = bool(shader_flags & MAT_BRIGHTNESS)
        self.sflag_reflection = bool(shader_flags & MAT_REFLECTION)

        if (self.sflag_RGBA):
            file.seek(4, 1) # skip RGBA color channels

        if (self.sflag_float3):
            file.seek(4, 1) # FIXME skip 3 unknown floats

        if (self.sflag_texture):
            tex_name_len = file.read(1)[0]
            self.tex_name = struct.unpack("<%ds" % tex_name_len, file.read(tex_name_len))[0].decode("utf-8")
            file.seek(1, 1) # skip string termination

        if (self.sflag_brightness):
            file.seek(4, 1) # skip brightness

        if (self.sflag_reflection):
            file.seek(4, 1) # FIXME skip unknown byte
            refltex_name_len = file.read(1)[0]
            self.refltex_name = struct.unpack("<%ds" % refltex_name_len, file.read(refltex_name_len))[0].decode("utf-8")
            file.seek(1, 1) # skip string termination
    
    def as_dict(self):
        dic = { "name": self.name,
                "sflag_RGBA": self.sflag_RGBA,
                "sflag_float3": self.sflag_float3,
                "tex_name": self.tex_name,
                "sflag_brightness": self.sflag_brightness,
                "sflag_reflection": self.sflag_reflection,
                "refltex_name": self.refltex_name
        }
        return dic


class Mesh:
    """
    Reads the Meshes found in .ldo files from an opened file.
    """
    def __init__(self, file=None, atomic=None):
        self.atomic = atomic        # atomic it belongs to
        self.vertex_count = 0       # amount of Vertex objects
        self.polygon_count = 0      # amount of Polyon objects

        self.vert_attrib_count = 0  # amount of vertex attributes
        self.vert_data_size = 0     # FIXME dictates what is contained in a vertex, but what does each byte represent?
        self.vertices = []          # sequence of Vertex objects

        self.nb_materials = 0       # amount of materials used
        self.polygons = []          # sequence of Polygon objects

        if file:
            self.read(file)
    
    def read(self, file):
        # Reads the MESH HEADER
        self.vertex_count = struct.unpack("<i", file.read(4))[0]
        self.polygon_count = struct.unpack("<i", file.read(4))[0]

        file.seek(4, 1) # FIXME skip unknown vertex property
        file.seek(4, 1) # FIXME skip idk what this is, or if they are 2 byte values

        file.seek(16, 1) # skip visibility bytes

        file.seek(4, 1) # FIXME skip unknown index

        self.vert_attrib_count = file.read(1)[0]
        self.vert_data_size = file.read(self.vert_attrib_count)

        # Reads the MESH VERTICES
        for i in range(self.vertex_count):
            self.vertices.append(Vertex(file, self.vert_attrib_count, self.vert_data_size))
        
        # Reads the MESH TRIS
        self.nb_materials = struct.unpack("<i", file.read(4))[0]
        for i in range(self.nb_materials):
            mat_idx = struct.unpack("<i", file.read(4))[0] # material index to use
            nb_tris = struct.unpack("<i", file.read(4))[0] # number of tris that use this material
            for j in range(nb_tris):
                self.polygons.append(Polygon(file, mat_idx))
    
    def as_dict(self):
        dic = { "vertex_count": self.vertex_count,
                "polygon_count": self.polygon_count,
                "vert_attrib_count": self.vert_attrib_count,
                "vert_data_size": self.vert_data_size,
                "vertices": self.vertices,
                "nb_materials": self.nb_materials,
                "polygons": self.polygons
        }
        return dic


class Polygon:
    """
    Reads a Polygon structure and stores it.
    """
    def __init__(self, file=None, mat_idx=0):
        self.material_index = mat_idx
        self.vertex_indices = []

        if file:
            self.read(file)

    def __repr__(self):
        return "Polygon"

    def read(self, file):
        self.vertex_indices = struct.unpack("<3h", file.read(6))

    def as_dict(self):
        dic = { "material_index": self.material_index,
                "vertex_indices": self.vertex_indices
        }
        return dic


class Vertex:
    """
    Reads a Vertex structure and stores it
    """
    def __init__(self, file=None, attrib_count=None, data_size=None):
        self.position = None    # Vector
        self.normal = None      # Vector
        self.uvcoords = None    # UV structure

        # TODO in Mad Tracks a vertex can also have additional attributes
        # skip them for now using parameters in the read() method
        if file:
            self.read(file, attrib_count, data_size)

    def __repr__(self):
        return "Vertex"

    def read(self, file, attrib_count, data_size):
        # Stores position and normal as a vector
        self.position = Vector(file)
        self.normal = Vector(file)

        # Stores UV coordinates as a UV structure
        self.uvcoords = UV(file)

        if (data_size[2] == 0x0b):
            file.seek(4, 1) # FIXME skip unknown additional float

        if (attrib_count > 3):
            file.seek(8, 1) # FIXME skip 2 unknown floats
            if (data_size[3] == 0x0c):
                file.seek(4, 1) # FIXME skip unknown additional float

    def as_dict(self):
        dic = {"position": self.position.as_dict(),
               "normal": self.normal.as_dict(),
               "uvcoords": self.uvcoords.as_dict()
               }
        return dic


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


class UV:
    """
    Reads UV-map structure and stores it
    """
    def __init__(self, file=None, uv=None):
        if uv:
            self.u, self.v = uv
        else:
            self.u = 1.0
            self.v = 0.0

        if file:
            self.read(file)

    def __repr__(self):
        return str(self.as_dict())

    def read(self, file):
        # Reads the uv coordinates
        self.u = struct.unpack("<f", file.read(4))[0]
        self.v = struct.unpack("<f", file.read(4))[0]

    def write(self, file):
        # Writes the uv coordinates
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
