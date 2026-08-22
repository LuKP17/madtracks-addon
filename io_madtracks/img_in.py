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

def import_file(filepath):
    filepath_real = filepath_insensitive(filepath)
    if os.path.exists(filepath_real):
        image = bpy.data.images.load(filepath_real)
        # Set a fake user because it doesn't get automatically set
        image.use_fake_user = True
        image.name = filepath_real.rsplit(os.sep, 1)[1]
        return image
    else:
        set_error('importing image', "Couldn't find image %s with sensitive case checking" % filepath)
        return None
