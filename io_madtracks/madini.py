# Copyright (C) 2024  Lucas Pottier
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
Files used for Mad Tracks levels and object descriptors.
The game uses its own .ini dialect. For instance, level .ini files
are made up of duplicate sections and their order matters for trackpart placement.
This dedicated .ini parser supports this dialect.

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
        for line in file:
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
                parameter.name, values = line[:-1].split("=", 1)
                if values[0] == '"':
                    # string value
                    parameter.values = values[1:-1]
                elif "," in values:
                    # multiple numbers
                    values = values.split(",")
                    for value in values:
                        parameter.values.append(float(value))
                else:
                    # one number
                    if "f" in values:
                        values = values.replace('f', '0')
                    parameter.values = float(values)
                # add parameter to the last section added
                self.sections[-1].params.append(parameter)
                
    def as_dict(self):
        dic = {}
        for s in self.sections:
            dic[s.name] = {}
            for p in s.params:
                dic[s.name][p.name] = p.values
        return dic


class Section:
    def __init__(self):
        self.name = ""      # section name without brackets
        self.params = []    # sequence of Parameters objects
    
    def as_dict(self):
        dic = {}
        for p in self.params:
            dic[p.name] = p.values
        return dic


class Parameter:
    def __init__(self):
        self.name = ""      # parameter name
        self.values = []    # sequence of values
