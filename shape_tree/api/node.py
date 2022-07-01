
from typing import List, Optional, TYPE_CHECKING, Union
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty, IntProperty, StringProperty
from ..lib.asks import ASKSComponent
from ..lib.events import dataclass, dispatch_event, Event
if TYPE_CHECKING:
    from bpy.types import Key, ShapeKey

NODE_TYPE_ITEMS = [
    ('GROUP', "Group", ""),
    ('XYZ', "XYZ Group", ""),
    ('SHAPEKEY', "Shape Key", ""),
    ('COMBINATION', "Combination", ""),
    ('INBETWEEN', "In-Between", ""),
    ]
NODE_TYPE_INDEX = [_x[0] for _x in NODE_TYPE_ITEMS]
NODE_TYPE_TABLE = {_x[0]: _i for _i, _x in enumerate(NODE_TYPE_ITEMS)}
NODE_TYPE_CHILD = {
    'GROUP': {'GROUP', 'XYZ', 'SHAPEKEY', 'COMBINATION'},
    'XYZ': set(),
    'SHAPEKEY': {'INBETWEEN'},
    'COMBINATION': {'INBETWEEN'},
    'INBETWEEN': {'INBETWEEN'},
    }


def can_use_group(key: 'Key') -> bool:
    return True


def can_use_xyz(key: 'Key') -> bool:
    return hasattr(key, "split_xyz")


def can_use_combination(key: 'Key') -> bool:
    return hasattr(key, "combination_shape_keys")


def can_use_inbetween(key: 'Key') -> bool:
    return hasattr(key, "in_betweens")


def can_use_shapekey(key: 'Key') -> bool:
    return True


NODE_TYPE_VALID = {
    'GROUP': can_use_group,
    'XYZ': can_use_xyz,
    'COMBINATION': can_use_combination,
    'INBETWEEN': can_use_inbetween,
    'SHAPEKEY': can_use_shapekey
    }


@dataclass(frozen=True)
class ShapeTreeNodeNameUpdateEvent(Event):
    node: 'ShapeTreeNode'
    value: str
    previous_value: str


def node_data_path(node: 'ShapeTreeNode') -> str:
    return node.get("data_path", "") if node.type != 'GROUP' else node.path_from_id()


def node_depth(node: 'ShapeTreeNode') -> int:
    return node.get("depth", 0)


def node_index(node: 'ShapeTreeNode') -> int:
    return node.get("index", 0)


def node_name(node: 'ShapeTreeNode') -> str:
    return node.get("name", "")


def node_name_set(node: 'ShapeTreeNode', value: str) -> None:
    cache = node_name(node)
    node["name"] = node_name_unique(node, value)
    dispatch_event(ShapeTreeNodeNameUpdateEvent(node, value, cache))


def node_name_unique(node: 'ShapeTreeNode', name: str) -> str:
    index = 0
    value = name
    names = list(node.id_data.key_blocks.keys())
    names.extend(node.id_data.shape_tree.collection__internal__.keys())
    while value in names:
        index += 1
        value = f'{name}.{str(index).zfill(3)}'
    return value


def node_type(node: 'ShapeTreeNode') -> int:
    return node.get("type", 0)


class ShapeTreeNode(ASKSComponent, PropertyGroup):

    @property
    def ancestors(self) -> List['ShapeTreeNode']:
        data = []
        node = self.parent
        while node is not None:
            data.append(node)
            node = node.parent
        return data

    @property
    def children(self) -> List['ShapeTreeNode']:
        result = []
        nodes = self.id_data.shape_tree.collection__internal__
        depth = self.depth + 1
        index = self.index + 1
        count = len(nodes)
        while index < count:
            node = nodes[index]
            node_depth = node.depth
            if node_depth < depth: break
            if node_depth == depth: result.append(node)
            index += 1
        return result

    data_path: StringProperty(
        name="Data Path",
        get=node_data_path,
        options=set()
        )

    @property
    def data(self) -> Optional[ASKSComponent]:
        if self.type in {'GROUP', 'SHAPEKEY'}:
            return self
        try:
            return self.id_data.path_resolve(self.data_path)
        except ValueError: pass
        return None

    depth: IntProperty(
        name="Depth",
        description="The depth of the node in the tree (read-only)",
        get=node_depth,
        options=set()
        )

    @property
    def first_child(self) -> Optional['ShapeTreeNode']:
        return self.children[0] if len(self) > 0 else None

    index: IntProperty(
        name="Index",
        description="The index of the node in the tree (read-only)",
        get=node_index,
        options=set()
        )

    @property
    def is_shape(self) -> bool:
        return self.type in {'SHAPEKEY', 'COMBINATION', 'XYZ', 'INBETWEEN'}

    @property
    def is_valid(self) -> bool:
        return not self.is_shape or self.name in self.id_data.key_blocks

    @property
    def last_child(self) -> Optional['ShapeTreeNode']:
        if len(self):
            return self.children[-1]

    @property
    def last_descendant(self) -> Optional['ShapeTreeNode']:
        node = self.subtree[-1]
        if node != self:
            return node

    name: StringProperty(
        name="Name",
        description="Unique shape tree node name",
        get=node_name,
        set=node_name_set,
        options=set()
        )

    @property
    def next_sibling(self) -> Optional['ShapeTreeNode']:
        nodes = self.id_data.shape_tree.collection__internal__
        depth = self.depth
        index = nodes.find(self.name)+1
        count = len(nodes)
        while index < count:
            node = nodes[index]
            node_depth = node.depth
            if node_depth < depth: break
            if node_depth == depth: return node
            index += 1

    @property
    def parent(self) -> Optional['ShapeTreeNode']:
        depth = self.depth - 1
        if depth >= 0:
            nodes = self.id_data.shape_tree.collection__internal__
            index = nodes.find(self.name) - 1
            while index >= 0:
                node = nodes[index]
                if node.depth == depth: return node
                index -= 1

    @property
    def previous_sibling(self) -> Optional['ShapeTreeNode']:
        nodes = self.id_data.shape_tree.collection__internal__
        depth = self.depth
        index = nodes.find(self.name)-1
        while index >= 0:
            node = nodes[index]
            node_depth = node.depth
            if node_depth < depth: break
            if node_depth == depth: return node
            index -= 1

    @property
    def shape(self) -> Optional['ShapeKey']:
        if self.is_shape:
            return self.id_data.key_blocks.get(self.name)

    show_expanded: BoolProperty(
        name="Expand",
        description="Expand the node to show subnodes in the UI",
        default=True,
        options=set()
        )

    @property
    def subtree(self) -> List['ShapeTreeNode']:
        stree = [self]
        nodes = self.id_data.shape_tree.collection__internal__
        depth = self.depth + 1
        count = len(nodes)
        index = self.index + 1
        while index < count:
            node = nodes[index]
            if node.depth < depth: break
            stree.append(node)
            index += 1
        return stree

    type: EnumProperty(
        name="Type",
        description="The type of tree node",
        items=NODE_TYPE_ITEMS,
        get=node_type,
        options=set()
        )

    @property
    def influence_property_name(self) -> Optional[str]:
        if self.type in {'GROUP', 'SHAPEKEY'}:
            return super().influence_property_name
        else:
            data = self.data
            if data is not None:
                return data.influence_property_name

    @property
    def weight_property_name(self) -> Optional[str]:
        if self.type in {'GROUP', 'SHAPEKEY'}:
            return super().weight_property_name
        else:
            data = self.data
            if data is not None:
                return data.weight_property_name

    def __len__(self) -> int:
        return self.get("length", 0)

    def is_child_of(self, node) -> bool:
        return node.is_parent_of(self)

    def is_descendant_of(self, node) -> bool:
        return node.is_ancestor_of(self)

    def is_parent_of(self, node) -> bool:
        return node.parent == self

    def is_sibling_of(self, node) -> bool:
        return self.parent == node.parent
