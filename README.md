# Blender BAM Exporter
Addon for Blender (3.x+) for exporting Panda3D "BAM" files. Uses the [blend2bam](https://github.com/Moguri/blend2bam) tool as the backend. Not related to the [older addon](https://github.com/tobspr/Panda3D-Bam-Exporter) for Blender 2.7x.

<img width="271" height="226" alt="bam_exporter0" src="https://github.com/user-attachments/assets/4a5a03a3-a325-46bb-91ec-6bb13ed835b5" />

## Installation
To install the addon into Blender, press the green "Code" button above and choose Download ZIP. The resulting ZIP file can be installed via the Install button in the Blender addon preferences.

## Setup
1. Before making your first export, you must first open the Blender addon preferences and add the full absolute path to the Panda3D Python executable. See the screenshot below.
    - <img width="494" height="321" alt="bam_exporter1" src="https://github.com/user-attachments/assets/afca2fd0-d19a-402d-8c16-f9f5445b88a6" />
    - If you installed Python via the Panda3D SDK, the path will likely be somewhere in C:\Panda3D-x.xx.xx-x64\python (at least on Windows)
    - If using the Anaconda distribution of Python, look in your C:\ProgramData\anaconda folder (on Windows)
    - Just using `python` or `python3` can also work depending on your operating system.
    - You can also specify the directory where blender is located, if blend2bam is unable to find it.
2. This addon requires the "[blend2bam](https://github.com/Moguri/blend2bam)" CLI tool to be installed. If you already have blend2bam installed, then you're set. If you don't have blend2bam installed, the Blender addon will attempt to install blend2bam for you automatically when you first try to export a scene, as long as you've set the correct Python path first.
