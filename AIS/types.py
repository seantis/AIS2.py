from typing import Protocol
from typing import Union


class SupportsBinaryRead(Protocol):
    def read(self, __size: int = -1) -> bytes: ...


FileLike = Union[str, SupportsBinaryRead]
