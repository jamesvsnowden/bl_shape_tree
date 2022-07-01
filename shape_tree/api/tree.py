
from typing import Optional
from bpy.types import PropertyGroup
from bpy.props import CollectionProperty, IntProperty
from ..lib.asks import ASKSNamespace
from .node import NODE_TYPE_CHILD, NODE_TYPE_VALID, ShapeTreeNode, NODE_TYPE_TABLE


class ShapeTree(ASKSNamespace[ShapeTreeNode], PropertyGroup):

    active_index: IntProperty(
        name="Shape Tree Node",
        min=0,
        default=0,
        options=set()
        )

    @property
    def active(self) -> Optional[ShapeTreeNode]:
        index = self.active_index
        return self[index] if index < len(self) else None

    collection__internal__: CollectionProperty(
        type=ShapeTreeNode,
        options={'HIDDEN'}
        )
