import bpy
from bpy.utils import (register_class, unregister_class)
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator
import subprocess
import os
import sys

bl_info = {
    "name": "Export Panda3D BAM",
    "description": "Exports to Panda3D BAM",
    "author": "Addon by Theanine3D. blend2bam by Moguri",
    "version": (0, 4, 1),
    "blender": (3, 0, 0),
    "category": "Import-Export",
    "location": "File > Export",
    "support": "COMMUNITY"
}

class BAMPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__

    python_path: StringProperty(
        name="Python Command",
        description="Command to use python. Maybe python3 in some cases.",
        default="python",
        subtype='FILE_PATH'
    )
    blender_dir: StringProperty(
        name="Blender Path",
        description="The directory where Blender is installed. ",
        default="",
        subtype='DIR_PATH'
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "python_path")
        layout.prop(self, "blender_dir")

def display_msg_box(message="", title="Info", icon='INFO'):
    ''' Open a pop-up message box to notify the user of something               '''
    ''' Example:                                                                '''
    ''' display_msg_box("This is a message", "This is a custom title", "ERROR") '''

    def draw(self, context):
        lines = str(message).split("\n")
        for line in lines:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def writeBAM(context, filepath, material_mode, physics_engine, no_srgb, texture_mode, anim_mode, invisible_coll):
    proc = None
    python_path = bpy.context.preferences.addons[__name__].preferences.python_path
    blender_dir = bpy.context.preferences.addons[__name__].preferences.blender_dir
    if blender_dir == "":
        blender_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    current_filepath = bpy.data.filepath
    if current_filepath == "":
        display_msg_box(message="You must first save your Blender file to your hard drive.", title="Info", icon='INFO')
        return {'FINISHED'}
    
    # Check for dependency first
    check_dependency = [python_path, "-m", "pip", "list"]
    pip_list = subprocess.check_output(check_dependency, shell=False, text=True)
    if "panda3d-blend2bam" not in pip_list:
        print("\nDependency 'panda3d-blend2bam' not found. Installing...\n")
        # If blend2bam is not installed, install it with pip
        install_dependency = [python_path, "-m", "pip", "install", "panda3d-blend2bam"]
        try:
            proc = subprocess.Popen(install_dependency, shell=False)
            display_msg_box(message="Python dependency 'blend2bam' was installed. Please try to export again.", title="Info", icon='INFO')
        except subprocess.CalledProcessError as e:
            print(e.returncode)
            print(e.output)
            display_msg_box(message=e.output, title="Error", icon='ERROR')
        try:
            outs, errs = proc.communicate(timeout=6)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            print(e.output)
            display_msg_box(message="Attempted to install Python dependency, but operation timed out.", title="Error", icon='ERROR')
        finally:
            return {'FINISHED'}

    current_dir = os.path.dirname(current_filepath)
    current_filename = os.path.basename(current_filepath)
    source_file = bpy.data.filepath

    # Normalize file paths
    filepath = str(filepath).replace("\\","/").replace("//","/")
    python_path = str(python_path).replace("\\","/").replace("//","/")
    source_file = str(source_file).replace("\\","/").replace("//","/")
    blender_dir = blender_dir.replace("\\","/").replace("//","/")

    command = [python_path, "-m", "blend2bam", source_file, filepath, "--material-mode", material_mode, "--physics-engine", physics_engine, "--textures", texture_mode, "--animations", anim_mode, "--invisible-collisions-collection", invisible_coll, "--blender-dir", blender_dir,]
    if no_srgb:
        command.append("--no-srgb")
    
    try:
        print("\nAttempting BAM export...\n")
        proc = subprocess.run(command, timeout=10, stdout=subprocess.PIPE, stderr=True, text=True)
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        print(e.output)
        display_msg_box(message=e.output, title="Error", icon='ERROR')
    except subprocess.TimeoutExpired as e:
        print(e.output)
        display_msg_box(message="Attempted to export, but reached a time out.", title="Error", icon='ERROR')
    except Exception as e:
        display_msg_box(message=e, title="Error", icon='ERROR')


    if not os.path.isfile(filepath):
        print("\nFailed to export BAM.\n")
        display_msg_box(message="Failed to export BAM. See console.", title="Info", icon='INFO')

    print("\nCleaning up...\n")

    return {'FINISHED'}

class ExportBAM(Operator, ExportHelper):
    """Exports to the Panda3D BAM format"""
    bl_idname = "export.bam"
    bl_label = "Panda3D (.bam)"

    filename_ext = ".bam"

    filter_glob: StringProperty(
        default="*.bam",
        options={'HIDDEN'},
        maxlen=255,
    )
    material_mode: EnumProperty(
        name="Material Mode",
        description="The mode for exporting materials - physically-based or legacy (default: pbr)",
        items=(
            ('legacy', "Legacy", "The older legacy (non-PBR) material mode in Panda3D"),
            ('pbr', "PBR", "The newer physically-based material mode in Panda3D"),
        ),
        default='pbr',
    )
    physics_engine: EnumProperty(
        name="Physics Engine",
        description="The physics engine to build collision solids for (default: builtin)",
        items=(
            ('builtin', "Built-In", "The built-in physics engine in Panda3D"),
            ('bullet', "Bullet", "Bullet is a third-party open source physics engine used in many games and simulations"),
        ),
        default='builtin',
    )
    no_srgb: BoolProperty(
        name="No sRGB",
        description="If checked, textures will not be loaded as sRGB textures (default: Disabled)",
        default=False,
    )
    texture_mode: EnumProperty(
        name="Texture Mode",
        description="How to handle external textures (default: Reference)",
        items=(
            ('ref', "Reference", "References textures via their original file path"),
            ('copy', "Copy", "Copies textures to the destination folder"),
            ('embed', "Embed", "Embeds textures into the resulting exported BAM"),
        ),
        default='ref',
    )
    anim_mode: EnumProperty(
        name="Animation Mode",
        description="How to handle animations (default: Embed)",
        items=(
            ('embed', "Embed", "Embeds textures into the resulting exported BAM"),
            ('separate', "Separate", "Separates animations into individual files"),
            ('skip', "Skip", "Skips animation export entirely"),
        ),
        default='embed',
    )
    invisible_coll: StringProperty(
        name="Invis. Collection",
        description="Name of a collection in Blender whose collision objects will be exported without a visible geom node (default: InvisibleCollisions)",
        default="InvisibleCollisions",
    )

    def execute(self, context):
        return writeBAM(context, self.filepath, self.material_mode, self.physics_engine, self.no_srgb, self.texture_mode, self.anim_mode, self.invisible_coll)

def menu_func_export(self, context):
    self.layout.operator(ExportBAM.bl_idname, text="Panda3D (.bam)")

def register():
    bpy.utils.register_class(ExportBAM)
    bpy.utils.register_class(BAMPrefs)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportBAM)
    bpy.utils.unregister_class(BAMPrefs)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    bpy.ops.export.writeBAM('INVOKE_DEFAULT')
