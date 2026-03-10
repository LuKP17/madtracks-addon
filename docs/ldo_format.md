# ldo Format

Geometry, rendering, texture mapping of one or multiple atomics (3D models)
of a game object.

FOR VALUES DIFFICULT TO FIGURE OUT BY HAND, WRITE A TAILORED SCANNER
TO RETRIEVE THEM FROM ALL FILES AND PRINT THE ONES THAT DO NOT HAVE
THE VALUE I EXPECT.
From the debug messages, the file contains a boolean named
“AnimatedParticles”

Command in case the game freezes when testing other values:
`taskkill /f /im MadTracks.exe`

## Overview

- HEADER, gives the number of atomics Z
- Z atomics, each containing:
    - ATOMIC HEADER, gives the number of meshes Y and materials X
    - X materials, each containing:
        - MATERIAL
    - Y meshes, each containing:
        - MESH HEADER
        - MESH VERTICES
        - MESH TRIS
    - ATOMIC DUMMY HEADER, gives the number of dummies D
    - D dummies, each containing:
        - DUMMY

### HEADER

```
    0       1       2       3       4       5    bytes
+-------+-------+-------+-------+---------------+
| obj-v | ato-v | msh-v | mat-v | atomic-cnt    |
+-------+-------+-------+-------+---------------+
```


| Field          | Description                                        |
|----------------|----------------------------------------------------|
| `obj-v`        | Object version, asserted to 0x01                   |
|                |                                                    |
| `ato-v`        | Atomic version, asserted to 0x03                   |
|                |                                                    |
| `msh-v`        | Mesh version, asserted to 0x02                     |
|                |                                                    |
| `mat-v`        | Material version, asserted to 0x03                 |
|                |                                                    |
| `atomic-cnt`   | Number of atomics                                  |
|                | Cars use 3 atomics: body, front wheel, rear wheel. |
|                | Breakable objects have one atomic for the whole    |
|                | model and one atomic per broken part.              |

### ATOMIC HEADER

The name "Atomic" was inferred from debug messages.
It represents a 3D model made of meshes and materials.

```
    0       1       2       3       4       5    bytes
+---------------+---------------+-------+-------+
| mesh-cnt      | material-cnt  | empty | ~anim |
+---------------+---------------+-------+-------+
| ~visibility1                  |
+-------------------------------+
| ~visibility2                  |
+-------------------------------+
| ~visibility3                  |
+-------------------------------+
| ~visibility4                  |
+-------------------------------+
```


| Field          | Description                                        |
|----------------|----------------------------------------------------|
| `mesh-cnt`     | Number of meshes                                   |
|                | TODO find stock atomics with multiple meshes.      |
|                | Is it related to a polygon limit?                  |
|                |                                                    |
| `material-cnt` | Number of materials                                |
|                |                                                    |
| `empty`        | 0x01 if the atomic is empty, 0x00 otherwise        |
|                |                                                    |
| `~anim`        | Maybe whether the atomic is animated               |
|                |                                                    |
| `~visibility1` |                                                    |
| `~visibility2` |                                                    |
| `~visibility3` |                                                    |
| `~visibility4` | Makes the atomic disappear when the camera looks   |
|                | at the center of the atomic from a certain angle   |
|                | and from a certain distance.                       |

### MATERIAL

```
    0       1       2       3       4       5       6       7    bytes
+-------+-------------------------------------------------------+
| str-l | mat-name-str
...                             | mat-flags     | shader-tech   |
+-------------------------------+---------------+---------------+
| red   | green | blue  | alpha | <unknown1>                    |
+-------+-------+-------+-------+-------------------------------+
| dif-l | dif-name-str                                  
...                             | brightness                    |
+-------------------------------+-------------------------------+
| <unknown2>                    | env-l | env-name-str
...                                                             |
| ???
+-------------------------------+-------------------------------+
```


| Field          | Description                                        |
|----------------|----------------------------------------------------|
| `str-l`        | Length of the material name string                 |
| `mat-name-str` | Material name string, null terminated despite      |
|                | having a string length to know where it ends.      |
|                |                                                    |
| `mat-flags`    | Flags for material properties.                     |
|                | Bit 0: has RGBA color channels ('A' needs testing) |
|                | Bit 3: has diffuse texture                         |
|                | Bit 6: has brightness                              |
|                | Bit 7: has environment map texture                 |
|                | Other bits are unclear or unused                   |
|                |                                                    |
| `shader-tech`  | Usually 0x0000                                     |
|                | 0x00002: "Technique to use 1 max ranged light for  |
|                | this shader is not implemented"                    |
|                | Higher values: "Technique not found"               |
|                |                                                    |
| `red`          |                                                    |
| `green`        |                                                    |
| `blue`         |                                                    |
| `alpha`        | (Only if has RGBA color channels)                  |
|                | Color channels from 0 to 255, `alpha` is a guess   |
|                |                                                    |
| `<unknown1>`   | (Only if flag bit 2 is set)                        |
|                |                                                    |
| `dif-l`        |                                                    |
| `dif-name-str` | (Only if has diffuse texture)                      |
|                | Diffuse texture name length and string,            |
|                | null terminated.                                   |
|                |                                                    |
| `brightness`   | (Only if has brightness)                           |
|                | Material brightness from -1 to 1                   |
|                |                                                    |
| `<unknown2>`   |                                                    |
| `env-l`        |                                                    |
| `env-name-str` | (Only if has environment map texture)              |
|                | Environment map texture name length and string,    |
|                | null terminated. The first 4 bytes are unknown.    |
|                |                                                    |
| `???`          | Unknown data from other flag bits                  |

