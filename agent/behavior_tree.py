# agent/behavior_tree.py
from abc import ABC, abstractmethod

class BTStatus:
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3

class Node(ABC):
    @abstractmethod
    def tick(self, blackboard):
        pass

class Sequence(Node):
    def __init__(self, children):
        self.children = children

    def tick(self, bb):
        for c in self.children:
            res = c.tick(bb)
            if res != BTStatus.SUCCESS:
                return res
        return BTStatus.SUCCESS

class Selector(Node):
    def __init__(self, children):
        self.children = children

    def tick(self, bb):
        for c in self.children:
            res = c.tick(bb)
            if res == BTStatus.SUCCESS:
                return BTStatus.SUCCESS
        return BTStatus.FAILURE

class Condition(Node):
    def __init__(self, func):
        self.func = func

    def tick(self, bb):
        return BTStatus.SUCCESS if self.func(bb) else BTStatus.FAILURE

class Action(Node):
    def __init__(self, func):
        self.func = func

    def tick(self, bb):
        return self.func(bb)
