
# `KeyVal`

- Properties:
    - `_key` (`str`)
    - `_value` (`None` or `Arg`)

- Methods:
    - `init`
    - `update_value`
        - takes a new_value as a string or `Arg`
        - If current `value` is `None`, sets it to the new value
        - If `self._value is not None`, `self._value.update(new_value)` 



# `Arg`

- Properties:
    - `_args` (`list` of `KeyVal`)

- Methods:
    - `init`
    - `update`
        - takes a new_value as a string or `Arg`
        - If `new_value` is a `str`, parse into an `Arg` object
        - If `new_value` is an `Arg`:
            - for key, val in new_value.args:
                - if key is in self, self[key].update_value(val)
                - else, self[key] = val


`Arg` should be responsible for all parsing of strings. KeyVal should just check if value is None or len(value) == 0 and update accordingly.

Don't bother converting to int, float, or Length. Just store as a string.