from typing import List, Iterator
import json
from datetime import datetime

from core import Character, LoggerMixin
from items import Inventory, HealthPotion, ManaPotion

class TurnOrder(Iterator):

    def __init__(self, participants: List[Character]):
        self._participants = sorted(
            [p for p in participants if p.is_alive],
            key=lambda x: x.agility,
            reverse=True
        )
        self._current_index = 0

    def __iter__(self) -> Iterator:
        return self

    def __next__(self) -> Character:
        if not self._participants:
            raise StopIteration("Нет живых участников")

        self._participants = [p for p in self._participants if p.is_alive]

        if not self._participants:
            raise StopIteration("Все участники мертвы")

        if self._current_index >= len(self._participants):
            self._current_index = 0

        participant = self._participants[self._current_index]
        self._current_index += 1

        return participant

    def get_current_order(self) -> List[str]:
        return [f"{p.name} (ловкость: {p.agility})" for p in self._participants]


class Battle(LoggerMixin):

    def __init__(self, party: List[Character], boss: Character):
        self.party = party
        self.boss = boss
        self.turn_order = TurnOrder(party + [boss])
        self.round_number = 0
        self._battle_log = []

        for character in party:
            if not hasattr(character, 'inventory'):
                character.inventory = Inventory()
            character.inventory.add_item(HealthPotion())
            character.inventory.add_item(ManaPotion())

    def start(self) -> bool:
        self.log("НАЧАЛО БОЯ")
        self._log_event("Бой начинается!")

        while self._battle_continues():
            self.round_number += 1
            self._log_event(f"\n Раунд {self.round_number} ")

            self._process_round_effects()

            self._execute_turns()

            if not self.boss.is_alive:
                self._log_event("ПОБЕДА! Босс повержен!")
                return True

            if not any(char.is_alive for char in self.party):
                self._log_event("ПОРАЖЕНИЕ! Все члены пати мертвы!")
                return False

        return False

    def _battle_continues(self) -> bool:
        return (self.boss.is_alive and
                any(char.is_alive for char in self.party) and
                self.round_number < 50)

    def _process_round_effects(self):
        all_participants = self.party + [self.boss]

        for participant in all_participants:
            if participant.is_alive:
                effect_results = participant.process_effects()
                for result in effect_results:
                    self._log_event(result)

    def _execute_turns(self):
        participants_copy = list(self.party) + [self.boss]

        for participant in participants_copy:
            if not participant.is_alive:
                continue

            try:
                current_turn = next(self.turn_order)
                self._execute_single_turn(current_turn)
            except StopIteration:
                break

    def _execute_single_turn(self, character: Character):
        if not character.is_alive:
            return

        self._log_event(f"\nХод {character.name}:")

        if character == self.boss:
            self._boss_turn(character)
        else:
            self._player_character_turn(character)

    def _boss_turn(self, boss: Character):
        alive_party = [p for p in self.party if p.is_alive]
        if not alive_party:
            return

        import random
        if random.random() < 0.5 and boss.mp > 20:
            target = random.choice(alive_party)
            result = boss.use_skill(target, 0)
        else:
            target = random.choice(alive_party)
            result = boss.basic_attack(target)

        self._log_event(result)

    def _player_character_turn(self, character: Character):
        import random

        action = random.random()

        if action < 0.6:
            if self.boss.is_alive:
                result = character.basic_attack(self.boss)
            else:
                result = "Нет цели для атаки"

        elif action < 0.9 and character.mp > 10:
            if self.boss.is_alive:
                result = character.use_skill(self.boss, 0)
            else:
                result = "Нет цели для навыка"

        else:
            if hasattr(character, 'inventory') and character.inventory.items_count > 0:
                result = character.inventory.use_item(0, character)
            else:
                result = "Нет предметов для использования"

        self._log_event(result)

    def _log_event(self, message: str):
        self._battle_log.append(f"[Раунд {self.round_number}] {message}")
        self.log(message)

    def get_battle_log(self) -> List[str]:
        return self._battle_log

    def get_battle_status(self) -> str:
        alive_party = [p for p in self.party if p.is_alive]
        status = f"Раунд {self.round_number}\n"
        status += f"Босс: {self.boss.hp:.1f}/{self.boss.max_hp} HP\n"
        status += f"Живых в пати: {len(alive_party)}/{len(self.party)}\n"

        for char in self.party:
            status += f"{char.name}: {char.hp:.1f}/{char.max_hp} HP"
            if not char.is_alive:
                status += " 💀"
            status += "\n"

        return status

    def save_state(self, filename: str):
        state = {
            'round_number': self.round_number,
            'boss': {
                'name': self.boss.name,
                'hp': self.boss.hp,
                'max_hp': self.boss.max_hp,
                'mp': self.boss.mp,
                'max_mp': self.boss.max_mp
            },
            'party': [],
            'timestamp': datetime.now().isoformat()
        }

        for char in self.party:
            state['party'].append({
                'name': char.name,
                'class': char.__class__.__name__,
                'hp': char.hp,
                'max_hp': char.max_hp,
                'mp': char.mp,
                'max_mp': char.max_mp,
                'level': char.level
            })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        self._log_event(f"Состояние сохранено в {filename}")