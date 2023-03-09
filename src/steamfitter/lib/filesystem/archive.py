from typing import NamedTuple


class __Policies(NamedTuple):
    invalid: str
    unknown: str
    do_nothing: str
    archive: str
    delete: str


ARCHIVE_POLICIES = __Policies(*__Policies._fields)
