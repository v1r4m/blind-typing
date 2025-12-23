from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import time

from .sentences import get_random_sentence


class GameState(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"


class Role(Enum):
    PLAYER = "player"
    SPECTATOR = "spectator"
    ADMIN = "admin"


@dataclass
class Player:
    sid: str
    nickname: str
    role: Role
    current_input: str = ""
    is_finished: bool = False
    finish_time: Optional[float] = None
    errors: list = field(default_factory=list)

    def to_dict(self):
        return {
            "sid": self.sid,
            "nickname": self.nickname,
            "role": self.role.value,
            "current_input": self.current_input,
            "is_finished": self.is_finished,
            "finish_time": self.finish_time,
            "errors": self.errors,
        }


class GameRoom:
    MAX_PLAYERS = 4

    def __init__(self):
        self.players: dict[str, Player] = {}
        self.spectators: dict[str, Player] = {}
        self.admins: dict[str, Player] = {}
        self.state: GameState = GameState.WAITING
        self.current_sentence: str = ""
        self.language: str = "korean"
        self.winner: Optional[Player] = None
        self.game_start_time: Optional[float] = None

    def add_player(self, sid: str, nickname: str, role: Role) -> tuple[bool, str]:
        if role == Role.PLAYER:
            if len(self.players) >= self.MAX_PLAYERS:
                return False, "최대 플레이어 수(4명)에 도달했습니다."
            if self.state == GameState.PLAYING:
                return False, "게임이 진행 중입니다. 다음 라운드를 기다려주세요."
            self.players[sid] = Player(sid=sid, nickname=nickname, role=role)
        elif role == Role.SPECTATOR:
            self.spectators[sid] = Player(sid=sid, nickname=nickname, role=role)
        elif role == Role.ADMIN:
            self.admins[sid] = Player(sid=sid, nickname=nickname, role=role)
        return True, "성공"

    def remove_player(self, sid: str):
        if sid in self.players:
            del self.players[sid]
        elif sid in self.spectators:
            del self.spectators[sid]
        elif sid in self.admins:
            del self.admins[sid]

    def start_game(self, language: str = "korean") -> tuple[bool, str]:
        if self.state == GameState.PLAYING:
            return False, "게임이 이미 진행 중입니다."
        if len(self.players) == 0:
            return False, "플레이어가 없습니다."

        self.language = language
        self.current_sentence = get_random_sentence(language)
        self.state = GameState.PLAYING
        self.winner = None
        self.game_start_time = time.time()

        for player in self.players.values():
            player.current_input = ""
            player.is_finished = False
            player.finish_time = None
            player.errors = []

        return True, self.current_sentence

    def update_typing(self, sid: str, text: str) -> dict:
        if sid not in self.players:
            return {}

        player = self.players[sid]
        player.current_input = text

        errors = self._calculate_errors(text)
        player.errors = errors

        if text == self.current_sentence and not player.is_finished:
            player.is_finished = True
            player.finish_time = time.time() - self.game_start_time
            if self.winner is None:
                self.winner = player
                self.state = GameState.FINISHED

        return {
            "nickname": player.nickname,
            "current_input": text,
            "errors": errors,
            "is_finished": player.is_finished,
            "progress": len(text) / len(self.current_sentence) * 100 if self.current_sentence else 0,
        }

    def _calculate_errors(self, text: str) -> list:
        errors = []
        for i, char in enumerate(text):
            if i < len(self.current_sentence):
                if char != self.current_sentence[i]:
                    errors.append({
                        "position": i,
                        "expected": self.current_sentence[i],
                        "actual": char,
                    })
        return errors

    def reset_game(self):
        self.state = GameState.WAITING
        self.current_sentence = ""
        self.winner = None
        self.game_start_time = None
        for player in self.players.values():
            player.current_input = ""
            player.is_finished = False
            player.finish_time = None
            player.errors = []

    def get_all_players_status(self) -> list:
        return [player.to_dict() for player in self.players.values()]

    def get_room_info(self) -> dict:
        return {
            "state": self.state.value,
            "player_count": len(self.players),
            "spectator_count": len(self.spectators),
            "admin_count": len(self.admins),
            "current_sentence": self.current_sentence if self.state != GameState.WAITING else "",
            "winner": self.winner.nickname if self.winner else None,
            "players": self.get_all_players_status(),
        }


game_room = GameRoom()
