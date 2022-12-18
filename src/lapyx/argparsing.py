# contains functions for parsing latex style arguments, especially key-value pairs.

from __future__ import annotations

from typing import List
from .main import EnumEx
from .exceptions import LatexParsingError




def split_at_char_outside_bracket(string: str, split_char: str) -> List[str]:
    # find the first instance of split_char that is not inside a bracket
    # return a list of the string split at that point
    # if there is no such instance, return the whole string
    # if the string is None, return an empty list
    if string is None:
        return []
    
    stack = []
    in_string = False
    for i, char in enumerate(string):
        if char in ["[", "{", "("]:
            if i > 0 and not string[i-1] == "\\":
                stack.append(char)
        elif char in ["]", "}", ")"]:
            if i > 0 and not string[i-1] == "\\":
                stack.pop()
        elif char == '"' or char == "'":
            if i > 0 and not string[i-1] == "\\":
                in_string = not in_string
        elif char == split_char:
            if len(stack) == 0 and not in_string:
                break
    else:
        i = len(string)
    
    if i < len(string):
        return [string[:i].strip(), string[i+1:].strip()]
    else:
        return [string.strip(), ""]


class KeyVal:

    # self._key is always a string
    # self._value should always be None or an Arg instance internally.

    def __init__(self, key: str, value: str | Arg | KeyVal = None):
        self._key = key
        if value is None:
            self._value = None
        elif isinstance(value, str):
            self._value = self.parse_value(value)
        elif isinstance(value, Arg):
            self._value = value
        elif isinstance(value, KeyVal):
            self._value = Arg(value)
        else:
            raise LatexParsingError(f"Value must be a string or Arg, not {type(value)}")
    
        if isinstance(self._value, Arg) and len(self._value) == 0:
            self._value = None
    
    @staticmethod
    def parse_value(value: str) -> str | Length | Arg:
        if value is None or value == "":
            return None
        
        value = value.strip()
        if value[0] == "{" and value[-1] == "}":
            value = value[1:-1].strip()
        
        return Arg(value)

    def __str__(self):
        if self._value is None:
            return self._key
        else:
            if len(self.value) == 1 and not self.value[0]._has_value():
                # we just have {key} = {value} for some string value
                return f"{self.key} = {self._value}"
            return f"{self._key} = {{{self._value}}}"
    
    def __repr__(self):
        if self._value is None:
            return f"KeyVal({self._key})"
        else:
            return f"KeyVal({self._key}, {repr(self._value)})"

    @property
    def key(self) -> str:
        return self._key
    
    @key.setter
    def key(self, key: str):
        self._key = key
    
    @property
    def value(self) -> str:
        return self._value
    
    @value.setter
    def value(self, value: str):
        if value is None:
            self._value = None
        else:
            self._value = self.parse_value(value)

    def _has_value(self):
        # perform a thorough check to see if the value contains any data.
        # should return False if the value is:
        # - None
        # - an empty string  <-- Should not be able to happen. Check anyway.
        # - an empty Arg
        # - an empty list    <-- Should not be able to happen. Check anyway.

        if self._value is None:
            return False
        
        if isinstance(self._value, str):
            return len(self._value) > 0
        
        if isinstance(self._value, Arg):
            return not self._value._is_empty()
        
        if isinstance(self._value, list):
            return len(self._value) > 0

    def __iter__(self):
        yield self.key
        yield self.value

    def update_value(self, new_value: str | Arg):
        
        if new_value is None or len(new_value) == 0:
            self._value = None
            return

        # if it's not already an Arg, make it one
        if not isinstance(new_value, Arg):
            new_value = Arg(new_value)
        
        # if the current value is None, just set it
        if self._value is None:
            self._value = new_value
            return
        
        if not isinstance(new_value, Arg):
            raise LatexParsingError(f"Value must be an Arg, not {type(new_value)}")
        # current value *must* be an Arg, so just update it
        self._value.update(new_value)


class Arg:
    # Contains a list of KeyVal objects, some of which may have a value of None
    def __init__(self, args: str | List[KeyVal] = None):
        if args is None or args == "":
            self._args = []
        elif isinstance(args, str):
            args = self.parse_args(args)
            self._args = args
        elif isinstance(args, KeyVal):
            self._args = [args]
        elif isinstance(args, list) or isinstance(args, tuple):
            self._args = []
            for arg in args:
                if isinstance(arg, str):
                    arg = self.parse_args(arg)
                    self._args.append(arg)
                elif isinstance(arg, KeyVal):
                    self._args.append(arg)
                else:
                    raise LatexParsingError(f"Arg must be a string, KeyVal, or list of the same (or None), not {type(arg)}")
        else:
            raise LatexParsingError(f"Arg must be a string, KeyVal, or list of the same (or None), not {type(args)}")
    
    @staticmethod
    def parse_args(args: str):
        # args will be a string of the form
        # "key1, key2=value2, key3={value3}, key4={value4, subkey1: subvalue1, subkey2: subvalue2}"
        # This should be parsed into a list of KeyVal objects, recursively. 

        if args is None or args == "":
            return []
        
        parsed_args = []

        while len(args) > 0:

            args = args.lstrip()
            arg, args = split_at_char_outside_bracket(args, ",")
            key, value = split_at_char_outside_bracket(arg, "=")
            if value is None or value == "":
                parsed_args.append(KeyVal(key))
            else:
                parsed_args.append(KeyVal(key, value))
        
        return parsed_args
    

    def update(self, new_args: str | Arg | List[KeyVal], key : str = None):

        """
            1. Check if key is provided. If it is: 
                - If the key is already in the args, update the Value
                - If the key is not in the args, add it with the new value.
                - Return
            2. If new_args is a string, list, or tuple, convert it to an Arg (if possible)
            3. If new_args is not an Arg by now, raise an error
            4. If len(self) == len(new_args) == 1, and self[0].__has_value() == False and new_args[0].__has_value() == False, update the key and return
            5. for keyval in new_args:
                - If keyval.key in self:
                    - self.get_keyval(keyval.key).update_value(keyval.value)
                - else:
                    - self.append(keyval)
                - return
            
        """

        if key is not None and key != "":
            if key in self:
                self.get_keyval(key).update_value(new_args)
            else:
                self.append(KeyVal(key, new_args))
            return
        
        # If it's not already an Arg, make it one
        if isinstance(new_args, str):
            new_args = Arg(new_args)
        elif isinstance(new_args, list) or isinstance(new_args, tuple):
            if any(not isinstance(arg, KeyVal) for arg in new_args):
                raise LatexParsingError(f"Arg must be a string or Arg, not {type(new_args)}")
            new_args = Arg(new_args)
        
        # Anything else can't be converted to an Arg
        if not isinstance(new_args, Arg):
            raise LatexParsingError(f"Arg must be a string or Arg, not {type(new_args)}")
        
        # if (
        #     len(self) == 1 and 
        #     len(new_args) == 1 and 
        #     not self._args[0]._has_value() and 
        #     not new_args._args[0]._has_value()
        # ):
        #     self[0].update_value(new_args[0].value)
        #     return
        
        for keyval in new_args:
            if keyval.key in self:
                self.get_keyval(keyval.key).update_value(keyval.value)
            else:
                self.append(keyval)
        return



    def get_keyval(self, key: str) -> KeyVal:
        if key not in self:
            raise LatexParsingError(f"Key {key} not found in Arg {self}")
        for keyval in self:
            if keyval.key == key:
                return keyval

    def append(self, new_keyval: KeyVal):
        self._args.append(new_keyval)

    def _is_empty(self):
        if self._args is None:
            return True

        if isinstance(self._args, list) or isinstance(self._args, tuple):
            if len(self._args) == 0:
                return True
            
            for arg in self._args:
                if isinstance(arg, KeyVal):
                    return False
            
            for arg in self._args:
                if not isinstance(arg, KeyVal):
                    raise LatexParsingError(f"Arg must be a list of KeyVal objects, not {type(arg)}: " + repr(arg))
        
        return False

    def _clean(self):
        for i in range(len(self._args)-1, -1, -1):
            if not isinstance(self._args[i], KeyVal):
                raise LatexParsingError(f"Arg must be a list of KeyVal objects, not {type(self._args[i])}: " + repr(self._args[i]))
            elif self._args[i].value is not None:
                self._args[i].value._clean()
                


    def __str__(self):
        if len(self) == 1 and self[0].value is None:
            return self[0].key
        return ", ".join([str(arg) for arg in self._args])

    def __repr__(self):
        out_string = "Arg(" + ", ".join([repr(arg) for arg in self._args]) + ")"
        return out_string

    def __iter__(self):
        for arg in self._args:
            yield arg
    
    def __getitem__(self, key: str | int) -> KeyVal:
        if isinstance(key, int):
            return self._args[key]
        
        for arg in self._args:
            if arg.key == key:
                return arg.value

        return None

    def __contains__(self, key: str | KeyVal) -> bool:
        if isinstance(key, KeyVal):
            return key in self
        
        for arg in self._args:
            if arg.key == key:
                return True
        
        return False

    def __len__(self):
        return len(self._args)

    def __delitem__(self, key: str | int):
        if isinstance(key, int):
            self._args = self._args[:key] + self._args[key+1:]  
        else:
            for i, arg in enumerate(self._args):
                if arg.key == key:
                    self._args = self._args[:i] + self._args[i+1:]
                    return
        
        raise KeyError(f"Key {key} not found")
    
    def remove(self, key: str | int):
        if isinstance(key, int):
            self._args = self._args[:key] + self._args[key+1:]
        else:
            for i, arg in enumerate(self._args):
                if arg.key == key:
                    self._args = self._args[:i] + self._args[i+1:]
                    return


    


# def options_to_dict(options: str) -> dict:
#     # options will be a string of the form
#     # "key1, key2=value2, key3={value3}, key4={value4, subkey1: subvalue1, subkey2: subvalue2}"
#     # This should be parsed into a dictionary: {"key1": None, "key2": value2, "key3": value3, "key4": {subkey1: subvalue1, subkey2: subvalue2}}
#     if options is None or options == "":
#         return {}

#     parsed_options = {}

#     while len(options) > 0:
#         # First, we remove any leading whitespace
#         options = options.lstrip()

#         # Now we can split the string at the first comma
#         # We need to make sure that the comma is not inside a bracket or quotation mark
#         # We can use a stack to keep track of the brackets and quotation marks
#         stack = []
#         for i, char in enumerate(options):
#             if char in ["[", "{", "("]:
#                 stack.append(char)
#             elif char in ["]", "}", ")"]:
#                 stack.pop()
#             elif char == ",":
#                 if len(stack) == 0:
#                     # We have found the first comma that is not inside a bracket or quotation mark
#                     break
#         else:
#             # We have reached the end of the string without finding a comma
#             i = len(options)

#         # Now we can split the string at the comma
#         option = options[:i]
#         options = options[i+1:]

#         # Now we can split the option at the equals sign
#         # We need to make sure that the equals sign is not inside a bracket or quotation mark
#         # We can use a stack to keep track of the brackets and quotation marks
#         stack = []
#         for i, char in enumerate(option):
#             if char in ["[", "{", "("]:
#                 stack.append(char)
#             elif char in ["]", "}", ")"]:
#                 stack.pop()
#             elif char == "=":
#                 if len(stack) == 0:
#                     # We have found the equals sign that is not inside a bracket or quotation mark
#                     break
#         else:
#             # We have reached the end of the string without finding an equals sign
#             i = len(option)

#         # Now we can split the string at the equals sign
#         key = option[:i].strip()
#         # check if there is a value
#         if i < len(option):
#             value = option[i+1:].strip()
#         else:
#             value = None
        
#         # Now we can parse the value
#         if value is not None:
#             # check if the value is a dictionary
#             if value.startswith("{"):
#                 # we need to parse the value into a dictionary
#                 value = options_to_dict(value[1:-1])
#             elif value.startswith("["):
#                 # we need to parse the value into a list
#                 value = options_to_dict(value[1:-1])
#             elif value.startswith("("):
#                 # we need to parse the value into a tuple
#                 value = options_to_dict(value[1:-1])
#             elif value.startswith('"') and value.endswith('"'):
#                 # we need to remove the quotation marks
#                 value = value[1:-1]
#             elif value.startswith("'") and value.endswith("'"):
#                 # we need to remove the quotation marks
#                 value = value[1:-1]
#             else:
#                 # value could be string, int, float, or length. Try int, then float, then length
#                 try:
#                     value = int(value)
#                 except ValueError:
#                     try:
#                         value = float(value)
#                     except ValueError:
#                         try:
#                             value = Length(value)
#                         except ValueError:
#                             # value is a string
#                             pass
        
#         # Now we can add the key-value pair to the dictionary
#         parsed_options[key] = value

#     return parsed_options

# def dict_to_latex(dictionary: dict) -> str:
#     # Convert a dictionary to a string of LaTeX options, recursively. Keys with a value of None will be passed as just the key
#     # e.g. {"key1": "value1", "key2": {"subkey1": "subvalue1", "subkey2": None}} -> "key1 = value1, key2 = {subkey1 = subvalue1, subkey2}"
#     if dictionary is None or len(dictionary) == 0:
#         return ""
#     if isinstance(dictionary, str):
#         return dictionary
#     options_str = []
#     for key, value in dictionary.items():
#         if value is None:
#             options_str.append(key)
#         elif isinstance(value, dict):
#             if len(value) == 0:
#                 options_str.append(key)
#             else:
#                 options_str.append(f"{key} = {{{dict_to_latex(value)}}}")
#         else:
#             options_str.append(f"{key} = {value}")
#     return ", ".join(options_str)



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
        
