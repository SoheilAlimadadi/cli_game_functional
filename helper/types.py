from typing import (
    List,
    NewType
)

GameMap = NewType('GameMap', List[List[str]])
Coordinate = NewType("Coordinate", tuple[int, int])