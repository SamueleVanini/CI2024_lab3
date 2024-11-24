from dataclasses import dataclass, field
from queue import PriorityQueue
from typing import Self

import numpy as np


class State:

    def __init__(self, value: np.ndarray | Self) -> None:
        self.value = value.copy()

    def __eq__(self, other: Self) -> bool:
        return other._hash == self._hash

    def __hash__(self) -> int:
        return self._hash

    def lock_data(self):
        self.value.setflags(write=False)
        self._hash = hash(self.value.tobytes())

    def copy(self):
        return self.value.copy()


@dataclass(order=True)
class Item:
    priority: int
    data: State = field(compare=False)

    def __eq__(self, other: Self) -> bool:
        return self.data == other.data


class SvanniPriorityQueue(PriorityQueue):

    def __init__(self, maxsize: int = 0) -> None:
        super().__init__(maxsize)
        self._item_set = set()

    def replace(self, old_item: Item, new_item: Item):
        self.queue.remove(old_item)
        self._item_set.discard(old_item.data)
        self.put(new_item)

    # NOTE: even if the word item is used, we refer to the data contained in the class Item(priority, data)
    # the name "item" is used to be similar with PriorityQueue interface.
    def __contains__(self, item: State):
        return item in self._item_set

    def _put(self, item: Item):
        assert item.data not in self, f"Trying to add a duplicated item in the priority queue"
        self._item_set.add(item.data)
        super()._put(item)

    def _get(self):
        item = super()._get()
        self._item_set.remove(item.data)
        return item
