from typing import Tuple, Union

# A pypi version ala (1, 1), (1, 1, 0) or (1, 1, 'a1').
VersionType = Union[Tuple[int, int], Tuple[int, int, Union[int, str]]]

# Django choices where they key can either be a string or integer.
DjangoChoicesType = Tuple[Tuple[Union[int, str], str], ...]
