# Mad Tracks Blender Add-on

Import Mad Tracks files in Blender.

## Description

This add-on is based on the Re-Volt Blender add-on.  
Huge thanks to the original author, Marvin Thiel, who's work made this project possible.

Since Mad Tracks has been released on Steam, the game data files are located in a .zip file and easy to access and modify.  
The goal of this project is to understand what is contained in these files and write a Blender add-on to visualize them.  
The ultimate goal would be to create fan-made assets for the game using Blender, but it is not in the current scope of this project.

## Getting Started

### Dependencies

* Mad Tracks Steam version
* Blender 2.79b

### Installing

* Extract Mad Tracks' data.zip file in a folder and don't touch it (the add-on will use relative paths to find textures in the 'Graph' folder when importing a LDO file from the 'Gfx' folder for instance)
* Paste the io_madtracks folder in Blender's add-ons folder (<blender_path>/scripts/addons)
* Open Blender, then go to: File > User Preferences > Add-ons, and check "Import-Export: Mad Tracks"
* A new tab in 3D view tools panel called "Mad Tracks" should appear, you're good to go!

## License

This project is licensed under the GNU GPLv3 License - see the LICENSE file for details

## Acknowledgments

Based on:
* [revolt-addon](https://gitlab.com/re-volt/re-volt-addon)
