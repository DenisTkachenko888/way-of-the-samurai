import pygame
import pytest

from game.core.animation import Animation


@pytest.fixture(scope="module", autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


def make_dummy_frames(n=3):
    return [pygame.Surface((16, 16)) for _ in range(n)]


def test_non_loop_animation_finishes_and_stays_on_last_frame():
    frames = make_dummy_frames(3)
    anim = Animation(frames, ms_per_frame=100, loop=False)

    # Дадим анимации "очень много времени", чтобы точно докрутиться до конца
    for _ in range(10):
        anim.update(1000)  # значение dt достаточно большое для любого варианта реализации

    assert anim.finished() is True
    assert anim.index == len(frames) - 1
    # current_frame должен быть последним кадром
    assert anim.current_frame() is frames[-1]


def test_loop_animation_does_not_finish():
    frames = make_dummy_frames(3)
    anim = Animation(frames, ms_per_frame=100, loop=True)

    for _ in range(10):
        anim.update(1000)

    # Зацикленная анимация не должна считаться "finished"
    assert anim.finished() is False
    # Индекс должен быть в допустимом диапазоне
    assert 0 <= anim.index < len(frames)
