from . import block_base
from .. import exceptions
from . import block_registry


class DynamicBlock(block_base.Block):
    """Basic dynamic block class is the subclass of the 
    :class:`.Block` class with the extension of adding and 
    removing :class:`.Output` s and :class:`.Input` s. Further Blocks with 
    dynamic amount of inputs or dynamic amount of outputs need to inherit from 
    this class. Furthermore it can be chosen between only the amount of inputs 
    being dynamic, only the amount of outputs being dynamic or both. It is 
    advised to overwrite the following methods in subclasses, if only specific 
    classes of inputs or outputs should be added to the block or if further 
    validation is needed.
    
    Attributes:
        dynamic_output: (lower limit, upper limit) The upper limit and 
            lower limit of the amount of outputs. The lower limit is an 
            integer and for it applies: lower limit >= 0.
            The upper limit is an integer and
            for it applies: upper limit > lower limit. The upper limit can also
            be set to None meaning there is no finite upper limit. 
            By default dynamic_output is set to None meaning the amount of 
            outputs are not dynamic and no outputs can be added or removed 
            after the initialization.
            
        dynamic_input: (lower limit, upper limit) The upper limit and 
            lower limit of the amount of inputs. The lower limit is an 
            interger and for it applies: lower limit >= 0. The upper limit 
            is an integer and for it applies: upper limit > lower limit. 
            The upper limit can also be set to None meaning there is no 
            finite upper limit. By default dynamic_input is set to None 
            meaning the amount of inputs are not dynamic and no inputs can 
            be added or removed after the initialization.
            
            Examples:          
                >>> self.dynamic_output = None
                No outputs can be added or removed               
                >>> self.dynamic_input = (0, 5)
                The amount of inputs can vary between 0 and 5
                >>> self.dynamic_output = (3, None)
                There are at least 3 outputs and any amount of outputs 
                can be added
            
    """

    def __init__(self):
        """Initialize DynamicBlock class."""
        super().__init__()
        self.dynamic_output = None
        self.dynamic_input = None

    def add_input(self, input_):
        """Adds an input to the Block.
        
        Args:
            input_: Input instance added to the block.
        Raises:
            :class:`.InputOutputError`: If adding the Input was not successful
        """
        if input_ in block_registry.Registry._graph.nodes:
            raise exceptions.InputOutputError("Input already added")
        if not self.dynamic_input:
            raise exceptions.InputOutputError("No permission to create input")

        if self.dynamic_input[1]:
            if self.dynamic_input[1] <= len(self.inputs):
                raise exceptions.InputOutputError("Maximum inputs reached")
            self.inputs.append(block_registry.Registry.add_node(input_))
        else:
            self.inputs.append(block_registry.Registry.add_node(input_))

    def add_output(self, output):
        """Adds an output to the Block.
        
        Args:
            output: Output instance added to the block.
        Raises:
            :class:`.InputOutputError`: If adding the Output was not successful
        """
        if output in block_registry.Registry._graph.nodes:
            raise exceptions.InputOutputError("Output already added")
        if not self.dynamic_output:
            raise exceptions.InputOutputError("No permission to create output")
        if self.dynamic_output[1]:
            if self.dynamic_output[1] <= len(self.outputs):
                raise exceptions.InputOutputError("Maximum outputs reached")
            self.outputs.append(block_registry.Registry.add_node(output))
        else:
            self.outputs.append(block_registry.Registry.add_node(output))
        self._process()

    def delete_input(self, input_index):
        """Removes an input from the Block.
        
        Args:
            input_index: Index of the input in the list called inputs.
        Raises:
            :class:`.InputOutputError`: If the lower limit of the inputs is 
                reached or dynamic_input is set to None.
        """
        if not self.dynamic_input:
            raise exceptions.InputOutputError("No permission to delete input")
        if self.dynamic_input[0] >= len(self.inputs):
            raise exceptions.InputOutputError("Minimum inputs reached")
        block_registry.Registry.remove_input(self.inputs.pop(input_index))

    def delete_output(self, output_index):
        """Removes an output from the Block.
        
        Args:
            output_index: Index of the output in the list called outputs.
        Raises:
            :class:`.InputOutputError`: If the lower limit of the outputs is 
                reached or dynamic_output is set to None.
        """
        if not self.dynamic_output:
            raise exceptions.InputOutputError("No permission to delete output")
        if self.dynamic_output[0] >= len(self.outputs):
            raise exceptions.InputOutputError("Minimum outputs reached")
        block_registry.Registry.remove_output(self.outputs.pop(output_index))
