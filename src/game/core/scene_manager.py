from __future__ import annotations
from typing import List, Type

class SceneManager:
    def __init__(self, app, start_scene_cls: Type):
        self.app = app
        self.stack: List = []
        self.push(start_scene_cls(self))

    @property
    def current_scene(self):
        return self.stack[-1] if self.stack else None

    def push(self, scene):
        self.stack.append(scene)

    def pop(self):
        if self.stack:
            self.stack.pop()
