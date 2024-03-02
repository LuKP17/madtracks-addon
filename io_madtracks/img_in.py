# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original file name: img_in.py
# Original author: Marvin Thiel
#
# File first modified on 02/29/24
# Author: Lucas Pottier
#-----------------------------------------------------------------------------

"""
Name:    img_in
Purpose: Imports image files.

Description:


"""

import bpy
import os

def load_image(filepath):
    path, fname = filepath.rsplit(os.sep, 1)
    if os.path.exists(filepath):
        image = bpy.data.images.load(filepath)
        # Sets a fake user because it doesn't get automatically set
        image.use_fake_user = True
        image.name = fname
    else:
        # Finds existing dummy texture
        for img in bpy.data.images:
            if img.name == fname:
                return img
        # Creates a dummy texture
        print("Texture not found: ", filepath)
        bpy.ops.image.new(name=fname, width=512, height=512,
                          generated_type="UV_GRID")
        image = bpy.data.images.get(fname)

    return image

def import_file(filepath):
    return load_image(filepath)
