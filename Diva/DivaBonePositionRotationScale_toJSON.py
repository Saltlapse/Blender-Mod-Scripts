import bpy
import mathutils
import json
from bpy_extras.io_utils import ExportHelper

def format_vector(value):
    """Format the vector component to remove trailing zeros."""
    return f"{value:.6f}".rstrip('0').rstrip('.')  # Remove trailing zeros and possible decimal point

def get_bone_data(armature):
    """Get formatted bone data for JSON export."""
    bones_data = []

    # Iterate through all bones in the armature
    for bone in armature.data.bones:
        # Get the bone's local transformation matrix
        bone_matrix_local = bone.matrix_local

        # Get the parent bone (if it exists)
        parent_bone = bone.parent
        parent_name = parent_bone.name if parent_bone else "None"

        # If there is a parent, get its local transformation matrix and combine
        if parent_bone:
            parent_matrix_local = parent_bone.matrix_local
            bone_matrix_in_parent_space = parent_matrix_local.inverted() @ bone_matrix_local
        else:
            bone_matrix_in_parent_space = bone_matrix_local
            
        # Create permutation for converting X,Y,Z
        permutation_matrix = mathutils.Matrix((
            (0, 1, 0, 0),  
            (1, 0, 0, 0),   
            (0, 0, -1, 0),   
            (0, 0, 0, 1)    
        ))

        # Apply the permutation to convert X,Y,Z to Diva orientation
        converted_matrix = permutation_matrix @ bone_matrix_in_parent_space @ permutation_matrix.transposed()

        # Decompose the transformation into translation, rotation, and scale
        translation, rotation, scale = converted_matrix.decompose()

        # Normalize quaternion
        rotation.normalize()
        
        # Convert the quaternion to Euler angles (XYZ)
        rotation_euler = rotation.to_euler('XYZ')

        # Append the formatted data for each bone to a list
        bones_data.append({
            "Signature": "OSG",
            "ParentName": parent_name,
            "Position": f"<{format_vector(translation.x)}, {format_vector(translation.y)}, {format_vector(translation.z)}>",
            "Rotation": f"<{format_vector(rotation_euler.x)}, {format_vector(rotation_euler.y)}, {format_vector(rotation_euler.z)}>",
            "Scale": f"<{format_vector(scale.x)}, {format_vector(scale.y)}, {format_vector(scale.z)}>",
            "Name": bone.name 
        })

    return bones_data

class ExportBoneDataJSON(bpy.types.Operator, ExportHelper):
    """Export Bone Data to JSON"""
    bl_idname = "export_bone.json"
    bl_label = "Export Bone Data to JSON"
    filename_ext = ".json"

    def execute(self, context):
        armature = context.active_object
        if armature and armature.type == 'ARMATURE':
            bone_data = get_bone_data(armature)
            with open(self.filepath, 'w') as f:
                json.dump(bone_data, f, indent=4)
            self.report({'INFO'}, "Bone data exported successfully.")
        else:
            self.report({'WARNING'}, "No armature selected.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(ExportBoneDataJSON)

def unregister():
    bpy.utils.unregister_class(ExportBoneDataJSON)

if __name__ == "__main__":
    register()
    bpy.ops.export_bone.json('INVOKE_DEFAULT')
