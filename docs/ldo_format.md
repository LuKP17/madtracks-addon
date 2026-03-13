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
        - VERTICES
        - TRIS HEADER, gives the number of materials M used
        - M tri sequences, each containing:
            - TRI SEQUENCE
    - DUMMY HEADER, gives the number of dummies D
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


### MESH HEADER

```
    0       1       2       3       4       5       6       7    bytes
+-------------------------------+-------------------------------+
| vertex-cnt                    | tri-cnt                       |
+-------------------------------+-------------------------------+
| <unknown1>                    | <unknown2>                    |
+-------------------------------+-------------------------------+
| ~visibility1                  | ~visibility2                  |
+-------------------------------+-------------------------------+
| ~visibility3                  | ~visibility4                  |
+-------------------------------+-------+-------+-------+-------+
| <unknown3>                    | ~vacnt| <unk4>| <unk5>| <unk6>|
+-------+-----------------------+-------+-------+-------+-------+
| <unk7>|
+-------+
```

| Field          | Description                                        |
|----------------|----------------------------------------------------|
| `vertex-cnt`   | Number of vertices                                 |
|                |                                                    |
| `tri-cnt`      | Number of tris                                     |
|                |                                                    |
| `<unknown1>`   | Seems like a vertex property, maybe a size         |
|                |                                                    |
| `<unknown2>`   | Could either be one or two values                  |
|                |                                                    |
| `~visibility1` |                                                    |
| `~visibility2` |                                                    |
| `~visibility3` |                                                    |
| `~visibility4` | Seem like visibility related. Needs testing        |
|                |                                                    |
| `<unknown3>`   | A mysterious index: "_Index < m_CurrentSize"       |
|                |                                                    |
| `~vacnt`       | Behaves like a vertex attribute count.             |
|                | Indicates the number of the following bytes.       |
|                |                                                    |
| `<unk4>`       | Usually 0x00                                       |
| `<unk5>`       | Usually 0x01                                       |
| `<unk6>`       | Usually 0x07 or 0x0b                               |
| `<unk7>`       | Usually 0x08 or 0x0c                               |


### VERTICES

Mad Tracks coordinate system:
-X right  / +X left
-Y bottom / +Y up
-Z front  / +Z back

```
    0       1       2       3       4       5       6       7    bytes
+-------------------------------+-------------------------------+
| position-x                    | position-y                    |
+-------------------------------+-------------------------------+
| position-z                    | normal-x                      |
+-------------------------------+-------------------------------+
| normal-y                      | normal-z                      |
+-------------------------------+-------------------------------+
| uv-x                          | uv-y                          |
+-------------------------------+-------------------------------+
| <unknown1>                    | <unknown2a>                   |
+-------------------------------+-------------------------------+
| <unknown2b>                   | <unknown3>                    |
+-------------------------------+-------------------------------+
```

| Field          | Description                                        |
|----------------|----------------------------------------------------|
| `position-x`   |                                                    |
| `position-y`   |                                                    |
| `position-z`   | Position                                           |
|                |                                                    |
| `normal-x`     |                                                    |
| `normal-y`     |                                                    |
| `normal-z`     | Normal                                             |
|                |                                                    |
| `uv-x`         | Texture UV                                         |
| `uv-y`         | (0;0) = top left corner                            |
|                | Texture repeats probably above 1                   |
|                |                                                    |
| `<unknown1>`   | Appears when `<unk6>` in MESH HEADER is 0x0b       |
|                |                                                    |
| `<unknown2a>`  |                                                    |
| `<unknown2b>`  | Repeated value, testing doesn't reveal anything    |
|                |                                                    |
| `<unknown3>`   | Appears when `<unk7>` in MESH HEADER is 0x0c       |


### TRIS HEADER

```
    0       1       2       3    bytes
+-------------------------------+
| tri-seq-cnt                  |
+-------------------------------+
```

| Field          | Description                                        |
|----------------|----------------------------------------------------|
| `tri-seq-cnt`  | Number of tri sequences                            |


### TRI SEQUENCE

```
    0       1       2       3       4       5       6       7    bytes
+-------------------------------+-------------------------------+
| material-id                   | sequence-len                  |
+---------------+---------------+---------------+---------------+
| vertex-id1    | vertex-id2    | vertex-id3    |
...
```

| Field          | Description                                        |
|----------------|----------------------------------------------------|
| `material-id`  | ID of the assigned material                        |
|                |                                                    |
| `sequence-len` | Number of tris in the sequence                     |
|                |                                                    |
| `vertex-id1`   |                                                    |
| `vertex-id2`   |                                                    |
| `vertex-id3`   | ID of the vertices making a tri.                   |
|                | The order determines which side the tri is facing  |
|                | (clockwise = in, counter-clockwise = out)          |


### DUMMY HEADER

Atomic dummies are too obscure at the moment.
`madtracks-addon` has just enough knowledge to skip them and reach EOF.
See madstructs.py for more info.
