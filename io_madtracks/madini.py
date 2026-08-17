# Copyright (C) 2024-2026  Lucas Pottier
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Mad Tracks Blender Add-on, based on Re-Volt Blender Add-on.
#-----------------------------------------------------------------------------

"""
Name:    madini
Purpose: Reading and writing Mad Tracks .ini files

Description:
.ini files are used for Mad Tracks levels and object descriptors.
The game uses its own .ini dialect. For instance, level .ini files
are made up of duplicate sections and their order matters for trackpart placement.
This dedicated .ini parser was written to support this dialect.

"""

class INI:
    """
    Reads and writes a Mad Tracks .ini file
    If an opened file is supplied, it immediately starts reading from it.
    """
    def __init__(self, file=None):
        self.sections = []  # sequence of Section objects

        if file:
            self.read(file)

    def read(self, file):
        commented = False
        for line in file:
            # check for block comment markers
            if "*/" in line:
                commented = False
                # all stock files have block comment markers in their own line
                continue
            if commented == True:
                # line is part of a block comment
                continue
            if "/*" in line:
                commented = True
                # all stock files have block comment markers in their own line
                continue
            # remove comments, but keep the newline
            if "//" in line:
                line = line.rsplit("//", 1)[0]
                line = line + "\n"
            # remove all whitespaces and tabs
            line = line.replace(" ", "")
            line = line.replace("\t", "")
            # handle last line
            if "\n" not in line:
                if len(line) > 1:
                    # last line needs to be read
                    line = line + "\n"
                else:
                    # last line is blank as it should be
                    continue
            # check line type
            if line[0] == '[' and line[-2] == ']':
                # add new section with name contained between the brackets
                section = Section()
                section.name = line[1:-2].lower()
                self.sections.append(section)
            elif line[0] == '\n':
                # blank line, ignore it
                continue
            else:
                # read parameter
                parameter = Parameter()
                parameter.name, value = line[:-1].split("=", 1)
                parameter.name = parameter.name.lower()
                if value[0] == '"' or value[-4:] == ".ldo":  # thanks Load Inc
                    # string value
                    parameter.value = value.replace("\"", "")
                    parameter.value = parameter.value.lower()
                elif "," in value:
                    # multiple numbers
                    value = value.split(",")
                    for v in value:
                        parameter.value.append(float(v))
                else:
                    # one number
                    if "f" in value:
                        value = value.replace('f', '0')
                    parameter.value = float(value)
                # add parameter to the last section added
                self.sections[-1].params.append(parameter)
                
    def as_dict(self):
        dic = {}
        for s in self.sections:
            dic[s.name] = {}
            for p in s.params:
                dic[s.name][p.name] = p.value
        return dic


class Section:
    def __init__(self):
        self.name = ""      # section name without brackets
        self.params = []    # sequence of Parameters objects
    
    def as_dict(self):
        dic = {}
        for p in self.params:
            dic[p.name] = p.value
        return dic


class Parameter:
    def __init__(self):
        self.name = ""
        self.value = []
