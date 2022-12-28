from lapyx.components import TableData, Table, TabularType
from lapyx.parsing import EnumEx, _enum_options

bullet = "\u2022"
value = {}
print(TabularType._default)
raise TypeError(
                f"Tabular type must be a string, integer, or TabularType, not {type(value)}. Valid options are:" + 
                "".join([f"\n\t{bullet} {n}" for n in _enum_options(TabularType)])
            )