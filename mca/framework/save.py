import json
import logging

from mca.framework import parameters, io_registry, PlotBlock


def save_block_structure(file_path):
    """Saves the current block structure to the given file_path as
    a .json.

    Args:
        file_path (str): Path of the .json file.
    """
    logging.info(f"Saving block structure to {file_path}")
    block_structure = blocks_to_json(io_registry.Registry.get_all_blocks())
    with open(file_path, "w") as save_file:
        save_file.write(block_structure)


def blocks_to_json(blocks):
    """Extracts status data of the given blocks (parameter values, connections,
     gui_data) and dumps them into a json format.

    Args:
        blocks(list): List of blocks to extract data from.
    Returns:
        json (str): json-formatted string of the extracted data.
     """

    data = {"blocks": []}
    for block in blocks:
        parameter_dict = {}
        plot_parameter_dict = {}
        for parameter_name, parameter in block.parameters.items():
            if isinstance(parameter, parameters.ParameterBlock):
                sub_parameter_dict = {}
                for sub_parameter_name, sub_parameter in parameter.parameters.items():
                    sub_parameter_dict[
                        sub_parameter_name] = sub_parameter.value
                parameter_dict[parameter_name] = sub_parameter_dict
            else:
                parameter_dict[parameter_name] = parameter.value
        if isinstance(block, PlotBlock):
            for parameter_name, parameter in block.plot_parameters.items():
                plot_parameter_dict[parameter_name] = parameter.value
        save_block = {"class": str(type(block)),
                      "parameters": parameter_dict,
                      "plot_parameters": plot_parameter_dict,
                      "inputs": [],
                      "outputs": [{
                          "id": output.id.int,
                          "metadata": {"signal_name": output.metadata.name,
                                       "quantity_a": output.metadata.quantity_a,
                                       "symbol_a": output.metadata.symbol_a,
                                       "unit_a": repr(
                                           output.metadata.unit_a),
                                       "quantity_o": output.metadata.quantity_o,
                                       "symbol_o": output.metadata.symbol_o,
                                       "unit_o": repr(
                                           output.metadata.unit_o)},
                          "abscissa_metadata": output.abscissa_metadata,
                          "ordinate_metadata": output.ordinate_metadata
                      }
                          for output in block.outputs],
                      "gui_data": block.gui_data["save_data"]}
        for input_ in block.inputs:
            input_save = {}
            if input_.connected_output:
                input_save[
                    "connected_output"] = input_.connected_output.id.int
            save_block["inputs"].append(input_save)
        data["blocks"].append(save_block)
    return json.dumps(data)
