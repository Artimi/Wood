# -*- coding: utf-8 -*-

import queue
from .base_priority_queue import BasePriorityQueue


class MemoryPriorityQueue(BasePriorityQueue):
    def __init__(self):
        super().__init__()
        self._queue = queue.PriorityQueue()

    def put(self, item):
        self._queue.put(item)

    def peek(self, index):
        return self._queue.queue[index]

    def get(self):
        return self._queue.get()

    def remove(self, item):
        self._queue.queue.remove(item)

    def remove_by_id(self, order_id):
        for elem in self._queue.queue:
            if elem.order_id == order_id:
                self.remove(elem)

    def __getattr__(self, item):
        return getattr(self._queue, item)

    def __len__(self):
        return self._queue.qsize()
