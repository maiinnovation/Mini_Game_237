from abc import ABC, abstractmethod
from core import Character, CritMixin
from skills import FireballSkill, PoisonEffect, ShieldEffect
from typing import List


class BossStrategy(ABC):

    @abstractmethod
    def execute(self, boss: 'Boss', targets: List[Character]) -> str:
        pass


class AggressiveStrategy(BossStrategy):

    def execute(self, boss: 'Boss', targets: List[Character]) -> str:
        alive_targets = [t for t in targets if t.is_alive]
        if not alive_targets:
            return "Нет целей для атаки"

        weakest_target = min(alive_targets, key=lambda x: x.hp)
        damage = boss.strength * 1.2
        weakest_target.take_damage(damage)
        return f"Босс яростно атакует {weakest_target.name} и наносит {damage:.1f} урона!"


class AoeStrategy(BossStrategy):

    def execute(self, boss: 'Boss', targets: List[Character]) -> str:
        alive_targets = [t for t in targets if t.is_alive]
        if not alive_targets:
            return "Нет целей для атаки"

        result = "Босс использует атаку по площади! "
        damage = boss.strength * 0.8
        for target in alive_targets:
            target.take_damage(damage)
            result += f"{target.name} получает {damage:.1f} урона. "

        return result


class DebuffStrategy(BossStrategy):

    def execute(self, boss: 'Boss', targets: List[Character]) -> str:
        alive_targets = [t for t in targets if t.is_alive]
        if not alive_targets:
            return "Нет целей для атаки"

        import random
        target = random.choice(alive_targets)
        target.add_effect(PoisonEffect(10))
        boss.add_effect(ShieldEffect(30))

        return f"Босс накладывает яд на {target.name} и создает щит!"


class Boss(Character, CritMixin):

    def __init__(self, name: str, level: int = 5):
        super().__init__(name, level, fraction="boss")
        self.strength = 15 + level * 3
        self.agility = 20 + level * 2
        self.intellect = 15 + level * 2
        self.max_hp = 200 + level * 50
        self.hp = self.max_hp
        self.max_mp = 100 + level * 20
        self.mp = self.max_mp

        self._strategies = {
            'phase1': AggressiveStrategy(),
            'phase2': AoeStrategy(),
            'phase3': DebuffStrategy()
        }
        self._current_strategy = self._strategies['phase1']

    def basic_attack(self, target: Character) -> str:
        damage = self.strength * 1.0
        damage = self.calculate_crit(damage, crit_chance=0.2, crit_multiplier=2.0)
        target.take_damage(damage)
        return f"Босс {self.name} атакует {target.name} и наносит {damage:.1f} урона!"

    def use_skill(self, target: Character, skill_index: int = 0) -> str:
        hp_percent = self.hp / self.max_hp

        if hp_percent > 0.6:
            self._current_strategy = self._strategies['phase1']
        elif hp_percent > 0.3:
            self._current_strategy = self._strategies['phase2']
        else:
            self._current_strategy = self._strategies['phase3']

        return f"Фаза босса изменена! " + self._current_strategy.execute(self, target if isinstance(target, list) else [
            target])

    def change_phase(self, phase_name: str):
        if phase_name in self._strategies:
            self._current_strategy = self._strategies[phase_name]
            return f"Босс переходит в фазу '{phase_name}'!"
        return "Неизвестная фаза"