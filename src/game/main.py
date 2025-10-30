from __future__ import annotations
from .core.app import GameApp
from .scenes.menu import MenuScene

def main():
    app = GameApp(start_scene_cls=MenuScene)
    app.run()

if __name__ == "__main__":
    main()
