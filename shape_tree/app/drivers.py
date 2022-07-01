
from typing import TYPE_CHECKING, Optional
from ..lib.driver_utils import driver_ensure, driver_variables_clear
if TYPE_CHECKING:
    from bpy.types import FCurve
    from ..api.node import ShapeTreeNode


def is_asks_driver(fcurve: 'FCurve') -> bool:
    variables = fcurve.driver.variables
    if len(variables) > 0:
        variable = variables[0]
        if variable.name.startswith(("pose_driven_", "cone_based")):
            target = variable.targets[0]
            return (target.id_type == 'KEY'
                    and target.id == fcurve.id_data
                    and target.data_path == "reference_key.value")
    return False


def node_weight_driver_create(node: 'ShapeTreeNode',
                              parent: Optional['ShapeTreeNode']=None) -> None:

    fcurve = driver_ensure(node.id_data, node.weight_property_path)
    driver = fcurve.driver

    variables = driver.variables
    driver_variables_clear(variables)

    variable = variables.new()
    variable.type = 'SINGLE_PROP'
    variable.name = "i"

    target = variable.targets[0]
    target.id_type = 'KEY'
    target.id = node.id_data
    target.data_path = node.influence_property_path

    expression = variable.name

    if parent is not None:
        variable = variables.new()
        variable.type = 'SINGLE_PROP'
        variable.name = "w"

        target = variable.targets[0]
        target.id_type = 'KEY'
        target.id = parent.id_data
        target.data_path = parent.weight_property_path

        expression = f'{variable.name}*{expression}'

    driver.type = 'SCRIPTED'
    driver.expression = expression


def node_value_driver_create(node: 'ShapeTreeNode') -> None:
    fcurve = driver_ensure(node.id_data, f'key_blocks["{node.name}"].value')
    driver = fcurve.driver

    variables = driver.variables
    driver_variables_clear(variables)

    variable = variables.new()
    variable.type = 'SINGLE_PROP'
    variable.name = "w"

    target = variable.targets[0]
    target.id_type = 'KEY'
    target.id = node.id_data
    target.data_path = node.weight_property_path

    driver.type = 'SCRIPTED'
    driver.expression = variable.name
