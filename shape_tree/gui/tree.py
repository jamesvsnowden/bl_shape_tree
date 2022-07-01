
from typing import TYPE_CHECKING, Iterable
from bpy.types import UILayout, UIList
if TYPE_CHECKING:
    from bpy.types import Context
    from ..api.node import ShapeTreeNode
    from ..api.tree import ShapeTree

# TODO error operator rather than icon

class SHAPETREE_UL_tree(UIList):
    bl_idname = 'SHAPETREE_UL_tree'

    def draw_item(self, _0, layout: 'UILayout', _1, node: 'ShapeTreeNode', _2, _3, _4, _5, _6) -> None:
        key = node.id_data

        split = layout.split(factor=0.5)
        row = split.row(align=True)

        for _ in range(node.depth):
            # TODO switch for custom separator icon
            row.label(icon='BLANK1')

        if len(node) > 0 or node.type == 'GROUP':
            row.prop(node, "show_expanded",
                     text="",
                     icon=f'DISCLOSURE_TRI_{"DOWN" if node.show_expanded else "RIGHT"}',
                     emboss=False)
        else:
            row.label(icon='BLANK1')

        # TODO switch for custom node icon
        row.prop(node, "name", text="", icon='SHAPEKEY_DATA', emboss=False)

        row = split.row(align=True)
        # row.enabled = context.object.mode not in ('EDIT', 'SCULPT')
        row.alignment = 'RIGHT'
        row.emboss = 'NONE_OR_STATUS'

        sub = row.row(align=True)
        sub.ui_units_x = 4.6
        
        data = node.data
        if data is not None:
            sub.prop(key, data.influence_property_path, text="", slider=True)
        else:
            sub.label(icon='ERROR')

        sub = row.row(align=True)
        sub.ui_units_x = 2.2
        sub.alignment = 'CENTER'
        # sub.enabled = node.depth > 0
        if data is not None:
            sub.prop(key, data.weight_property_path, text="", slider=True)
        else:
            sub.label(icon='ERROR')

        sub = row.row(align=True)
        sub.ui_units_x = 2.2
        sub.alignment = 'CENTER'
        if node.type in {'SHAPEKEY', 'INBETWEEN', 'COMBINATION'}:
            shape = key.key_blocks.get(node.name)
            if shape is not None:
                sub.prop(shape, "value", text="")
            else:
                sub.label(icon='ERROR')
        else:
            sub.label(icon='BLANK1')

    def filter_items(self, _, tree: 'ShapeTree', prop: str):
        nodes = getattr(tree, prop)
        flags = [self.bitflag_filter_item] * len(nodes)
        order = list(range(len(nodes)))
        depth = -1

        node: ShapeTreeNode
        for index, node in enumerate(nodes):

            if depth > -1 and node.depth > depth:
                flags[index] &= ~self.bitflag_filter_item
                continue

            if node.get("length", 0) > 0 and not node.show_expanded:
                depth = node.depth
                continue

            depth = -1

        return flags, order