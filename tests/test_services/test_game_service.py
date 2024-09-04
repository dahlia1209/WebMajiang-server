import pytest
from app.services.game_service import GameService

def test_game_service_init():
    game_service=GameService()
    game_service.qipai()
    assert len(game_service.game.shan.pais)==70
    