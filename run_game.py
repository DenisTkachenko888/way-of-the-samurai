# run_game.py
import runpy

if __name__ == "__main__":
    # эквивалент: python -m game.main
    runpy.run_module("game.main", run_name="__main__")
