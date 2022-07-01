
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from bpy.props import StringProperty
from shape_tree.lib.driver_utils import driver_find
from ..lib.asks import COMPAT_ENGINES, COMPAT_OBJECTS, idprop_create
from ..api.node import NODE_TYPE_TABLE, node_name_unique
from ..app.drivers import is_asks_driver, node_value_driver_create, node_weight_driver_create
if TYPE_CHECKING:
    from bpy.types import Context

class SHAPETREE_OT_group_add(Operator):

    bl_idname = "shape_tree.group_add"
    bl_label = "Group"
    bl_description="Add a new group node"
    bl_options = {'REGISTER', 'UNDO'}

    parent: StringProperty(
        name="Parent",
        description="Name of the parent node to add group to",
        default="",
        options=set()
        )

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                return object.data.shape_keys is not None
        return False

    def execute(self, context: 'Context') -> Set[str]:
        key = context.object.data.shape_keys
        tree = key.shape_tree

        parent = self.parent
        if not parent:
            parent = None
        else:
            parent = tree.get(parent)

            if parent is None:
                self.report({'ERROR'}, f'{self.bl_idname} parent "{self.parent}" not found')
                return {'CANCELLED'}

            if parent.type != 'GROUP':
                self.report({'ERROR'}, f'{self.bl_idname} parent must be a group node')
                return {'CANCELLED'}

        nodes = tree.collection__internal__
        node = nodes.add()
        node["type"] = NODE_TYPE_TABLE['GROUP']
        node["name"] = node_name_unique(node, "Group")

        idprop_create(key, node.influence_property_name)
        idprop_create(key, node.weight_property_name)
        node_weight_driver_create(node, parent)

        if parent is not None:
            index = parent.subtree[-1].index + 1
            node["index"] = index
            node["depth"] = parent.depth + 1
            nodes.move(len(nodes)-1, index)
        else:
            index = len(nodes)-1
            node["index"] = index
            node["depth"] = 0

        tree["active_index"] = index
        return {'FINISHED'}


class SHAPETREE_OT_shapekey_add(Operator):

    bl_idname = "shape_tree.shapekey_add"
    bl_label = "Shape Key"
    bl_description="Add a new shape key node"
    bl_options = {'REGISTER', 'UNDO'}

    parent: StringProperty(
        name="Parent",
        description="Name of the parent node to add shape to",
        default="",
        options=set()
        )

    shape_key: StringProperty(
        name="Shape Key",
        description="Name of existing shape key to use (optional)",
        default="",
        options=set()
        )

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                return object.data.shape_keys is not None
        return False

    def execute(self, context: 'Context') -> Set[str]:
        object = context.object
        key = object.data.shape_keys
        tree = key.shape_tree

        parent = self.parent
        if not parent:
            parent = None
        else:
            parent = tree.get(parent)

            if parent is None:
                self.report({'ERROR'}, f'{self.bl_idname} parent "{self.parent}" not found')
                return {'CANCELLED'}

            if parent.type != 'GROUP':
                self.report({'ERROR'}, f'{self.bl_idname} parent must be a group node')
                return {'CANCELLED'}

        shape = self.shape_key
        if shape:
            shape = key.key_blocks.get(shape)

            if shape is None:
                self.report({'ERROR'}, f'{self.bl_idname} shape_key "{self.shape_key}" not found')
                return {'CANCELLED'}

        else:
            shape = object.shape_key_add()

        nodes = tree.collection__internal__
        node = nodes.add()
        node["type"] = NODE_TYPE_TABLE['SHAPEKEY']
        node["name"] = shape.name

        idprop_create(key, node.influence_property_name)
        idprop_create(key, node.weight_property_name)
        node_weight_driver_create(node, parent)

        fcurve = driver_find(key, f'key_blocks["{shape.name}"].value')
        if fcurve is None:
            node_value_driver_create(node)
        elif not is_asks_driver(fcurve):
            fcurve.data_path = node.influence_property_path

        if parent is not None:
            index = parent.subtree[-1].index + 1
            node["index"] = index
            node["depth"] = parent.depth + 1
            nodes.move(len(nodes)-1, index)
        else:
            index = len(nodes)-1
            node["index"] = index
            node["depth"] = 0

        object.active_shape_key_index = key.key_blocks.find(shape.name)
        tree["active_index"] = index
        return {'FINISHED'}


class SHAPETREE_OT_node_add(Operator):

    bl_idname = "shape_tree.node_add"
    bl_label = "Add"
    bl_description="Add a new node"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                return object.data.shape_keys is not None
        return False

    @staticmethod
    def draw_func(self, context: 'Context') -> None:
        key = context.object.data.shape_keys
        tree = key.shape_tree
        layout = self.layout
        # TODO icons
        layout.operator(SHAPETREE_OT_group_add.bl_idname, text="Add Group", icon='ADD')
        layout.operator(SHAPETREE_OT_shapekey_add.bl_idname, text="Add Shape", icon='ADD')
        active = tree.active
        if active is not None:
            if active.type == 'GROUP':
                name = active.name
                # TODO icons
                layout.operator(SHAPETREE_OT_group_add.bl_idname, text="Append Group", icon='ADD').parent = name
                layout.operator(SHAPETREE_OT_shapekey_add.bl_idname, text="Append Shape", icon='ADD').parent = name

    def execute(self, context: 'Context') -> None:
        context.window_manager.popup_menu(self.draw_func)
        return {'FINISHED'}
