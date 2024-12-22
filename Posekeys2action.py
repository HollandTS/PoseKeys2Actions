bl_info = {
    "name": "PoseKeys2Action",
    "author": "HollandTS",
    "version": (1, 1, 0),
    "blender": (4, 3, 2),
    "location": "3D View > Sidebar > Pose Keys to Action",
    "description": "Create a new action from selected keyframes in Pose Mode",
    "doc_url": "",
    "category": "Animation",
}

import bpy


class PoseKeys2ActionProperties(bpy.types.PropertyGroup):
    action_name: bpy.props.StringProperty(
        name="Name of Action",
        description="Enter a name for the new action",
        default="NewAction",
    )


class PoseKeys2ActionPanel(bpy.types.Panel):
    """Creates a panel in Pose Mode for the PoseKeys2Action addon."""
    bl_label = "Pose Keys to Action"
    bl_idname = "POSE_PT_pose_keys_to_action"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pose Keys"
    bl_context = "posemode"

    def draw(self, context):
        layout = self.layout
        props = context.scene.pose_keys_to_action_props

        layout.label(text="Create Action from Selected Keyframes")
        layout.prop(props, "action_name", text="Action Name")
        layout.operator("pose.create_new_action", text="Create Action!")


class CreateNewActionOperator(bpy.types.Operator):
    """Operator to create a new action from selected keyframes."""
    bl_idname = "pose.create_new_action"
    bl_label = "Create New Action"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        props = context.scene.pose_keys_to_action_props

        # Validation: Ensure in Pose Mode and armature selected
        if not obj or obj.type != 'ARMATURE' or context.mode != 'POSE':
            self.report({'ERROR'}, "Please select an armature and switch to Pose Mode.")
            return {'CANCELLED'}

        anim_data = obj.animation_data
        if not anim_data or not anim_data.action:
            self.report({'ERROR'}, "No action found on the selected object.")
            return {'CANCELLED'}

        current_action = anim_data.action

        # Create a new action
        new_action_name = props.action_name.strip()
        if not new_action_name:
            self.report({'ERROR'}, "Action name cannot be empty.")
            return {'CANCELLED'}

        new_action = bpy.data.actions.new(name=new_action_name)
        obj.animation_data.action = new_action

        # Copy selected keyframes
        selected_keyframes = self.get_selected_keyframes(current_action)
        if not selected_keyframes:
            self.report({'ERROR'}, "No keyframes selected.")
            return {'CANCELLED'}

        for fcurve in current_action.fcurves:
            # Create equivalent FCurve in new action
            new_fcurve = new_action.fcurves.new(data_path=fcurve.data_path, index=fcurve.array_index)
            for frame in selected_keyframes:
                for keyframe_point in fcurve.keyframe_points:
                    if frame == keyframe_point.co[0]:
                        new_fcurve.keyframe_points.insert(frame, keyframe_point.co[1])
                        break

        self.report({'INFO'}, f"New action '{new_action_name}' created.")
        return {'FINISHED'}

    @staticmethod
    def get_selected_keyframes(action):
        """Retrieve selected keyframes from the active action."""
        selected_frames = set()
        for fcurve in action.fcurves:
            for keyframe_point in fcurve.keyframe_points:
                if keyframe_point.select_control_point:
                    selected_frames.add(keyframe_point.co[0])  # Add frame to set
        return sorted(selected_frames)


# Registration
def register():
    bpy.utils.register_class(PoseKeys2ActionProperties)
    bpy.utils.register_class(PoseKeys2ActionPanel)
    bpy.utils.register_class(CreateNewActionOperator)
    bpy.types.Scene.pose_keys_to_action_props = bpy.props.PointerProperty(
        type=PoseKeys2ActionProperties
    )


def unregister():
    bpy.utils.unregister_class(PoseKeys2ActionProperties)
    bpy.utils.unregister_class(PoseKeys2ActionPanel)
    bpy.utils.unregister_class(CreateNewActionOperator)
    del bpy.types.Scene.pose_keys_to_action_props


if __name__ == "__main__":
    register()
