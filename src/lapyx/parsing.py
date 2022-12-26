# contains functions for parsing latex style arguments, especially key-value pairs.

from __future__ import annotations
from functools import singledispatch

from typing import List

import random
import string
from enum import Enum

from .exceptions import LatexParsingError


class EnumEx(Enum):
    # Extended enum class that allows for comparison with integers and other enums more consistently
    def __eq__(self, other):
        from enum import Enum
        # return self is other or (type(other) == Enum and self.value == other.value) or (type(other) == int and self.value == other)
        if isinstance(other, EnumEx) or isinstance(other, Enum):
            return self is other or self.value == other.value
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, str):
            return self.name.lower() == other.lower()
        return False

    def __int__(self):
        return self.value

    def __add__(self, other):
        if type(other) == type(self):
            return self.value + other.value
        return self.value + other

    def __sub__(self, other):
        if type(other) == type(self):
            return self.value - other.value
        return self.value - other

    def __mul__(self, other):
        if type(other) == type(self):
            return self.value * other.value
        return self.value * other

    def __truediv__(self, other):
        if type(other) == type(self):
            return self.value / other.value
        return self.value / other

    def __str__(self):
        return f"{self.name}: \t{self.value}"

    def __gt__(self, other):
        if type(other) == type(self):
            return self.value > other.value
        return self.value > other

    def __lt__(self, other):
        if type(other) == type(self):
            return self.value < other.value
        return self.value < other

    def __ge__(self, other):
        if type(other) == type(self):
            return self.value >= other.value
        return self.value >= other

    def __le__(self, other):
        if type(other) == type(self):
            return self.value <= other.value
        return self.value <= other

    def __ne__(self, other):
        if type(other) == type(self):
            return self.value != other.value
        return self.value != other

def _generate_ID() -> str:  
    return ''.join(
        random.choice(
            string.ascii_uppercase
            + string.ascii_lowercase
            + string.digits
        ) for _ in range(10))

def _find_matching_bracket(string: str) -> int:
    bracketPairs = {
        "{": "}",
        "[": "]",
        "(": ")"
    }
    endBracket = bracketPairs[string[0]]
    bracketCount = 1
    for i in range(1, len(string)):
        if string[i] == string[0]:
            bracketCount += 1
        elif string[i] == endBracket:
            bracketCount -= 1
        if bracketCount == 0:
            return i
    return None

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
    def parse_value(value: str) -> str | Arg:
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


    