
from typing import TYPE_CHECKING
from bpy.types import Panel
from ..lib.asks import COMPAT_ENGINES, COMPAT_OBJECTS, split_layout
from ..ops.add import SHAPETREE_OT_node_add
from .tree import SHAPETREE_UL_tree
if TYPE_CHECKING:
    from bpy.types import Context


class SHAPETREE_PT_main(Panel):

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_label = "Shape Tree"
    bl_description = "Shape Tree"

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            return object is not None and object.type in COMPAT_OBJECTS
        return False

    def draw(self, context: 'Context') -> None:
        object = context.object
        key = object.data.shape_keys
        tree = key.shape_tree
        layout = self.layout

        row = layout.row()

        col = row.column()
        col.template_list(SHAPETREE_UL_tree.bl_idname, "",
                          tree, "collection__internal__",
                          tree, "active_index")

        col = row.column(align=True)
        col.operator(SHAPETREE_OT_node_add.bl_idname, text="", icon='ADD')

        node = tree.active
        if node is not None:
            data = node.data

            if data is None:
                # TODO
                return

            col = split_layout(layout, "Influence", padding=True)
            col.prop(key, data.influence_property_path, text="", slider=True)

            col = split_layout(layout, "Weight", padding=True)
            col.prop(key, data.weight_property_path, text="", slider=True)

            if node.is_shape:
                shape = node.shape
                if shape is None:
                    # TODO
                    return

                col = split_layout(layout, "Value", padding=True)
                col.prop(shape, "value", text="")

                col = split_layout(layout, "Vertex Group", padding=True)
                col.prop_search(shape, "vertex_group", object, "vertex_groups", text="")

                col = split_layout(layout, "Relative To", padding=True)
                col.prop_search(shape, "relative_key", key, "key_blocks", text="")
