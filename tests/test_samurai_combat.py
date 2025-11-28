import pygame
import pytest

from game.entities.samurai import Samurai


@pytest.fixture(scope="module", autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


def make_samurai():
    enemies = pygame.sprite.Group()
    samurai = Samurai((100, 300), enemies_group=enemies)
    return samurai


def test_samurai_takes_full_damage_without_guard():
    s = make_samurai()
    start_hp = s.hp

    s.take_damage(10)

    assert s.hp == start_hp - 10
    assert s.is_dead is False


def test_samurai_block_reduces_damage():
    s = make_samurai()
    start_hp = s.hp

    s.is_guarding = True
    s.take_damage(40)  # при блоке должно быть ~25% от урона

    expected_loss = max(1, int(40 * 0.25))
    assert s.hp == start_hp - expected_loss
    assert s.is_dead is False
