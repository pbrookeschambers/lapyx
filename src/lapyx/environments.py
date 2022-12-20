
from __future__ import annotations

from typing import List, Tuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .components import Table, Figure, Subfigures

from abc import ABC, abstractmethod

from .parsing import EnumEx, Arg, KeyVal
from .exceptions import LatexParsingError

class Unit(EnumEx):
    # LaTeX length units
    PT = 0
    MM = 1
    CM = 2
    IN = 3
    BP = 4
    PC = 5
    DD = 6
    EX = 7
    EM = 8

class Length:

    def __init__(self, value: str | float, unit: str | Unit = None):
        if isinstance(value, int) or isinstance(value, float):
            self.value = value
            if unit is None:
                self.unit = Unit.CM # default unit
            else:
                if isinstance(unit, str):
                    self.unit = Unit(unit.upper())
                else:
                    self.unit = unit
        if isinstance(value, str):
            # if it ends with a unit symbol, use that
            for unit in Unit:
                if value.lower().endswith(unit.name.lower()):
                    self.value = float(value[:-len(unit.name.lower())])
                    self.unit = unit
                    return

            # otherwise, assume cm
            try: 
                self.value = float(value)
                self.unit = Unit.CM
            except ValueError:
                raise LatexParsingError(f"Could not parse length {value}")
    
    def __str__(self):
        return f"{self.value}{self.unit.name.lower()}"

    def __repr__(self):
        return f"Length({self.value}, {self.unit.name.lower()})"

    def _value_as_pt(self):
        # values taken from https://tex.stackexchange.com/a/113513
        # convert to pt
        if self.unit == Unit.PT:
            return self.value
        elif self.unit == Unit.MM:
            return self.value * 7227 / 2540
        elif self.unit == Unit.CM:
            return self.value * 7227 / 254
        elif self.unit == Unit.IN:
            return self.value * 7227 / 100
        elif self.unit == Unit.BP:
            return self.value * 803 / 800
        elif self.unit == Unit.PC:
            return self.value * 12
        elif self.unit == Unit.DD:
            return self.value * 1238 / 1157
        elif self.unit == Unit.EX:
            # use standard font size of 12
            return self.value * 35271 / 8192
        elif self.unit == Unit.EM:
            # use standard font size of 12
            return self.value * 655361 / 65536
        else:
            raise ValueError(f"Unknown unit {self.unit.name}")

    @staticmethod
    def _pt_to_unit(value: float, unit: Unit | str):
        if isinstance(unit, str):
            unit = Unit(unit.upper())
        # convert to pt
        if unit == Unit.PT:
            return value
        elif unit == Unit.MM:
            return value * 2540 / 7227
        elif unit == Unit.CM:
            return value * 254 / 7227
        elif unit == Unit.IN:
            return value * 100 / 7227
        elif unit == Unit.BP:
            return value * 800 / 803
        elif unit == Unit.PC:
            return value / 12
        elif unit == Unit.DD:
            return value * 1157 / 1238
        elif unit == Unit.EX:
            # use standard font size of 12
            return value * 8192 / 35271
        elif unit == Unit.EM:
            # use standard font size of 12
            return value * 65536 / 655361
        else:
            raise ValueError(f"Unknown unit {unit.name}")


    def convert_to(self, unit: Unit | str):
        if isinstance(unit, str):
            unit = Unit(unit.upper())
        if self.unit == unit:
            return self
        
        return Length(self._pt_to_unit(self._value_as_pt(), unit), unit)


# -----------------------------------------------------------------------------------------------------
# These need updating to use the new Arg class
# -----------------------------------------------------------------------------------------------------

class CommandBase(ABC):
    def __init__(
        self,
        name: str,
        arguments: Arg | str | List[str | Arg] = None
    ):
        self.name = name
        self.arguments = []
        self._arguments_optional = []
        if arguments is None:
            arguments = []
        elif not isinstance(arguments, list):
            if isinstance(arguments, tuple):
                arguments = list(arguments)
            else:
                arguments = [arguments]
        for a in arguments:
            self.add_argument(a)

    def add_optional_argument(self, argument: str | Arg | dict):
        """Add an optional argument to the macro or environment.

        Parameters
        ----------
        argument : str | Arg | OptArg | dict | List[str | Arg | OptArg]
            Argument to add
        """        
        if not isinstance(argument, Arg):
            argument = Arg(argument)
        self.arguments.append(argument)
        self._arguments_optional.append(True)
    

    def add_argument(self, argument: str | Arg | dict , optional: bool = False):
        """Add an argument to the macro or environment.

        Parameters
        ----------
        argument : Arg | OptArg | str
            Argument to add
        optional : bool, optional, default ``False``
            If ``True`` and the ``argument`` is a string, it will be converted to an ``OptArg``. If
            ``False`` and the ``argument`` is a string, it will be converted to an ``Arg``.
        """        
        if optional:
            self.add_optional_argument(argument)
            return
        if not isinstance(argument, Arg):
            argument = Arg(argument)
        self.arguments.append(argument)
        self._arguments_optional.append(optional)
    
    def set_argument(self, argument: str | Arg | dict, index: int, optional: bool = False):
        """Set an argument at a given index.

        Parameters
        ----------
        argument : Arg | OptArg | str
            The new argument to be stored.
        index : int
            The index of the argument to be replaced.
        optional : bool, optional, default ``False``
            If ``True`` and the ``argument`` is a string, it will be converted to an ``OptArg``. If
            ``False`` and the ``argument`` is a string, it will be converted to an ``Arg``.

        Raises
        ------
        IndexError
            If the index is out of range for the number of arguments in the macro or environment.
        """         
        # Set an option at a specific index. If the index is out of range, raise an error
        if index >= len(self.arguments):
            raise IndexError(f"Cannot set option: index {index} is out of range for options list of length {len(self.arguments)}")
        if not isinstance(argument, Arg):
            argument = Arg(argument)
        self.arguments[index] = argument
        self._arguments_optional[index] = optional

    def insert_argument(self, argument: str | Arg | dict, index: int, optional: bool = False):
        """Insert an argument at a given index, without replacing any existing arguments.

        Parameters
        ----------
        argument : Arg | OptArg | str
            The new argument to be stored.
        index : int
            The index at which the argument should be inserted.
        optional : bool, optional, default ``False``
            If ``True`` and the ``argument`` is a string, it will be converted to an ``OptArg``. If
            ``False`` and the ``argument`` is a string, it will be converted to an ``Arg``.

        Raises
        ------
        IndexError
            If the index is out of range for the number of arguments in the macro or environment.
        """        
        # Insert an option at a specific index. If the index is out of range, raise an error
        if index > len(self.arguments):
            raise IndexError(f"Cannot insert option: index {index} is out of range for options list of length {len(self.arguments)}")
        if not isinstance(argument, Arg):
            argument = Arg(argument)
        self.arguments.insert(index, argument)
        self._arguments_optional.insert(index, optional)
    
    def remove_argument(self, index: int):
        """Remove the argument at a given index.

        Parameters
        ----------
        index : int
            The index of the argument to be removed.

        Raises
        ------
        IndexError
            If the index is out of range for the number of arguments in the macro or environment.
        """        
        # Remove an option at a specific index. If the index is out of range, raise an error
        if index >= len(self.arguments):
            raise IndexError(f"Cannot remove option: index {index} is out of range for options list of length {len(self.arguments)}")
        if index == 0:
            self.arguments = self.arguments[1:]
            self._arguments_optional = self._arguments_optional[1:]
        elif index == len(self.arguments) - 1:
            self.arguments = self.arguments[:-1]
            self._arguments_optional = self._arguments_optional[:-1]
        else:
            self.arguments = self.arguments[:index] + self.arguments[index+1:]
            self._arguments_optional = self._arguments_optional[:index] + self._arguments_optional[index+1:]
    
    @abstractmethod
    def __str__(self):
        pass

class Macro(CommandBase):
    def __init__(
        self,
        name: str,
        arguments: Arg | str | List[Arg | str] = None
    ):
        """``Macro`` is a helper class for storing and outputting LaTeX macros with (ordered) 
        optional and required arguments.

        Parameters
        ----------
        name : str
            Name fo the macro as a string, without the leading ``\\``.
        arguments : Arg | OptArg | str | List[str  |  Arg  |  OptArg], optional, default ``None``
            A list of arguments to be passed to the macro. Each element should be a string, 
            ``Arg``, or ``OptArg`` instance. ``KWArgs`` instances must be wrapped in an ``Arg``
            or ``OptArg`` instance. If a single argument is passed, it will be wrapped in a list.
        """    
        super().__init__(name, arguments)

    def __str__(self):
        return f"\\{self.name}" + "".join([f"[{a}]" if o else f"{{{a}}}" for a, o in zip(self.arguments, self._arguments_optional)])

    def __repr__(self):
        return f"Macro({self.name}, {self.arguments})"

class Environment(CommandBase):

    def __init__(
        self, 
        name: str, 
        arguments: Arg | str | List[str | Arg] = None,
        content: str | Table | Figure | Subfigures | Environment | Macro | List[str | Table | Figure | Subfigures | Environment | Macro]  = None 
        # can also be Environment or list of Environments, but for type hints only in python >= 3.11   
    ):
        """A helper class for storing LaTeX environments and their arguments, possibly in a nested 
        structure.

        Parameters
        ----------
        name : str
            The name of the environment, which will be rendered as ``\\begin{name}`` and
            ``\\end{name}``.
        arguments : Arg | OptArg | str | List[str  |  Arg  |  OptArg], optional, default ``None``
            Argument or list of arguments for the environment. Each element should be a string,
            ``Arg``, or ``OptArg`` instance. ``KWArgs`` instances must be wrapped in an ``Arg``
            or ``OptArg`` instance. If a single argument is passed, it will be wrapped in a list.
        content : str | Table | Figure | Macro | Environment | List[ str  |  Table  |  Figure Macro | Environment], optional, default ``None``
            The content to be stored in and rendered in the environment. Any ``lapyx.components`` 
            class is acceptable, except those derived from ``Arg`` or ``KWArgs``, including 
            other Environments. A list of the same is also acceptable. These will be rendered in 
            the order in which they are added.

            .. warning::
                Be careful not to add an ``Environment`` to its own content or that of its
                children. Recursion is not checked, and will result in an infinite loop.  
        """        
        super().__init__(name, arguments)
        
        if content is None:
            self.content = []
        elif not isinstance(content, list):
            self.content = [content]
        else:
            self.content = content
    
    def add_content(self, content: str | Table | Figure | Subfigures | Environment | Macro):
        """Add content to the end of the environment.

        Parameters
        ----------
        content : str | Table | Figure | Macro | Environment
            The new content to be added. Any ``lapyx.components`` class is acceptable, except
            those derived from ``Arg`` or ``KWArgs``, including other Environments. A list of 
            the same is also acceptable and will be added in order. This will be appended as the 
            last item within the environment.
        """        
        # content can also be Environment or list of Environments, but for type hints only in python >= 3.11   
        if isinstance(content, list) or isinstance(content, tuple):
            self.content.extend(content)
        else:
            self.content.append(content)

    def set_content(self, content: str | Table | Figure | Subfigures | Environment | Macro, index: int):
        """Set the content at a given index.

        Parameters
        ----------
        content : str | Table | Figure | Macro | Environment
            The new content to be stored. Any ``lapyx.components`` class is acceptable, except
            those derived from ``Arg`` or ``KWArgs``, including other Environments.
        index : int
            The index of the content to be replaced.

        Raises
        ------
        IndexError
            If the index is out of range for the number of content items in the environment.
        """        
        # content can also be Environment or list of Environments, but for type hints only in python >= 3.11   
        # Set an option at a specific index. If the index is out of range, raise an error
        if index >= len(self.content):
            raise IndexError(f"Cannot set content: index {index} is out of range for content list of length {len(self.content)}")
        self.content[index] = content
    
    def insert_content(self, content: str | Table | Figure | Subfigures | Environment | Macro, index: int):
        """Insert content at a given index, without replacing any existing content.

        Parameters
        ----------
        content : str | Table | Figure | Macro | Environment
            The new content to be stored. Any ``lapyx.components`` class is acceptable, except
            those derived from ``Arg`` or ``KWArgs``, including other Environments.
        index : int
            The index at which the content should be inserted.

        Raises
        ------
        IndexError
            If the index is out of range for the number of content items in the environment.
        """        
        # content can also be Environment or list of Environments, but for type hints only in python >= 3.11   
        # Insert an option at a specific index. If the index is out of range, raise an error, unless the index is the length of the array in which case just append
        if index > len(self.content):
            raise IndexError(f"Cannot insert content: index {index} is out of range for content list of length {len(self.content)}")
        self.content.insert(index, content)
    
    def remove_content(self, index: int):
        """Remove the content at a given index.

        Parameters
        ----------
        index : int
            The index of the content to be removed.

        Raises
        ------
        IndexError
            If the index is out of range for the number of content items in the environment.
        """        
        # Remove an option at a specific index. If the index is out of range, raise an error
        if index >= len(self.content):
            raise IndexError(f"Cannot remove content: index {index} is out of range for content list of length {len(self.content)}")
        del self.content[index]

    def set_parent(self, other):
        """Adds this environment to the content of another environment.

        Parameters
        ----------
        other : Environment
            The environment to which this environment should be appended as content.

        Raises
        ------
        TypeError
            If the other object is not an ``Environment`` instance.
        """        
        if not isinstance(other, Environment):
            raise TypeError(f"Cannot set parent: {other} is not an Environment")
        other.add_content(self)

    def __str__(self):
        # start_line = f"\\begin{{{self.name}}}{''.join([str(o) for o in self.arguments])}"
        start_line = rf"\begin{{{self.name}}}{''.join([f'[{a}]' if o else f'{{{a}}}' for a, o in zip(self.arguments, self._arguments_optional)])}"
        # end_line = f"\\end{{{self.name}}}"
        end_line = str(Macro("end", [self.name]))
        mid_lines = "\n".join([str(item) for item in self.content])
        # indent each of mid_lines by one tab
        mid_lines = "\n".join(["\t" + line for line in mid_lines.split("\n")])
        return start_line + "\n" + mid_lines + "\n" + end_line
    
class Container(Environment):
    """``EmptyEnvironment`` is a convenience class for creating an ``Environment`` object which 
    will not be rendered in the final output, but **will** render its content. This is useful 
    for consistency within Python, but has exactly the same effect as passing each element of
    ``content`` to ``export()`` directly.

    Parameters
    ----------
    content : str | Table | Figure | Macro | Environment | List[ str  |  Table  |  Figure Macro | Environment], optional, default ``None``
        The content to be stored in and rendered in the environment. Any ``lapyx.components`` 
        class is acceptable, except those derived from ``Arg`` or ``KWArgs``, including 
        other Environments. A list of the same is also acceptable. These will be rendered in 
        the order in which they are added.
    """        
    def __init__(self, content: str | Table | Figure | Subfigures | Environment | Macro | List[str | Table | Figure | Subfigures | Environment | Macro] = None):
        super().__init__(name = None, content = content)

    def __str__(self):
        return "\n".join([str(item) for item in self.content])