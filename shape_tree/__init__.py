# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Shape Tree",
    "description": "Shape Tree",
    "author": "James Snowden",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D",
    "warning": "",
    "doc_url": "https://jamesvsnowden.xyz/asks/shape_tree/docs",
    "tracker_url": "https://github.com/jamesvsnowden/bl_shape_tree/issues",
    "category": "Animation",
}

UPDATE_URL = ""

from .api.node import ShapeTreeNode
from .api.tree import ShapeTree
from .ops.add import (SHAPETREE_OT_group_add,
                      SHAPETREE_OT_shapekey_add,
                      SHAPETREE_OT_node_add)
from .gui.tree import SHAPETREE_UL_tree
from .gui.main import SHAPETREE_PT_main


def classes():
    return [
        ShapeTreeNode,
        ShapeTree,
        SHAPETREE_OT_group_add,
        SHAPETREE_OT_shapekey_add,
        SHAPETREE_OT_node_add,
        SHAPETREE_UL_tree,
        SHAPETREE_PT_main,
    ]


def register():
    from bpy.types import Key
    from bpy.props import PointerProperty
    from bpy.utils import register_class
    from .lib import asks

    asks.register("shape_tree")

    for cls in classes():
        register_class(cls)

    Key.shape_tree = PointerProperty(
        name="Shape Tree",
        type=ShapeTree,
        options=set()
        )


def unregister():
    import sys
    from operator import itemgetter
    from bpy.types import Key
    from bpy.utils import unregister_class
    from .lib import asks

    asks.unregister()

    try:
        del Key.shape_tree
    except: pass

    for cls in reversed(classes()):
        unregister_class(cls)

    modules_ = sys.modules 
    modules_ = dict(sorted(modules_.items(), key=itemgetter(0)))
   
    for name in modules_.keys():
        if name.startswith(__name__):
            del sys.modules[name]
