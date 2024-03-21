# Copyright (C) 2024  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    trackparts
Purpose: Trackpart position and rotation offsets.

Description:
TODO Explain why its needed. Used for level import and export

"""

trackparts = {
    "M_gris_amorce_30_in.ini" : {
        "pos_offset" : [0, 0, 30], # the 2 offset on the Y axis shouldn't be taken into account
        "rot_offset" : [0, 0, 0]
    },
    "M_gris_rail_50.ini" : {
        "pos_offset" : [0, 0, 50],
        "rot_offset" : [0, 0, 0]
    },
    "M_gris_virage_45_left.ini" : {
        "pos_offset" : [17.54, 0, 42.43],
        "rot_offset" : [45, 0, 0]
    },
    "M_gris_virage_45_right.ini" : {
        "pos_offset" : [-17.54, 0, 42.43],
        "rot_offset" : [-45, 0, 0]
    },
}
