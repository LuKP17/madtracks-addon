# Copyright (C) 2024-2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
# Original author: Marvin Thiel
#-----------------------------------------------------------------------------

"""
Name:    img_in
Purpose: Imports image files.

"""

import bpy
import os

from .common import *

def import_file(filepath, reuse=True):
    """
    Load and return an image, optionally reuse it if already loaded, return None if not found
    """
    # check for known extension
    ext = None
    if filepath.rsplit(".", 1)[-1].lower() in ["dds", "png"]:
        ext = filepath.rsplit(".", 1)[-1].lower()
    if ext:
        # reuse or load filepath as is
        ret = image_load(filepath_insensitive(filepath, reuse))
    else:
        # consider that only one extension of a given texture can be loaded,
        # which greatly speeds up level import with Texture mode
        if reuse:
            for image in bpy.data.images:
                if filepath + "." in image.filepath:
                    return image
        # try known extensions, if an image exists in multiple extensions, favor PNG
        ret = image_load(filepath_insensitive(filepath + ".png"), reuse)
        if ret == None:
            ret = image_load(filepath_insensitive(filepath + ".dds"), reuse)

    if ret == None:
        set_error('loading image', "Image %s not found" % filepath)
    return ret


def image_load(filepath, reuse):
    if os.path.exists(filepath):
        idx = bpy.data.images.find(filepath.rsplit(os.sep, 1)[1])
        if reuse and idx >= 0:
            return bpy.data.images[idx]
        else:
            image = bpy.data.images.load(filepath)
            # Set a fake user because it doesn't get automatically set
            image.use_fake_user = True
            image.name = filepath.rsplit(os.sep, 1)[1]
            return image
    else:
        return None
