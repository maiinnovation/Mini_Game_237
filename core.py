from abc import ABC, abstractmethod
import random
from typing import List, Optional


class BoundedStat:

    def __init__(self, min_value: int = 0, max_value: int = 1000):
        self.min_value = min_value
        self.max_value = max_value
        self.name = None

    def __set_name__(self, owner, name):
        self.name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, 0)

    def __set__(self, obj, value):
        if not (self.min_value <= value <= self.max_value):
            raise ValueError(f"Значение {value} должно быть между {self.min_value} и {self.max_value}")
        setattr(obj, self.name, value)


class LoggerMixin:

    def log(self, message: str):
        print(f"[LOG] {message}")


class CritMixin:

    def calculate_crit(self, base_damage: float, crit_chance: float = 0.1, crit_multiplier: float = 1.5) -> float:
        if random.random() < crit_chance:
            print("КРИТИЧЕСКИЙ УДАР!")
            return base_damage * crit_multiplier
        return base_damage


class Human:

    hp = BoundedStat(0, 1000)
    max_hp = BoundedStat(1, 1000)
    mp = BoundedStat(0, 500)
    max_mp = BoundedStat(0, 500)
    strength = BoundedStat(1, 100)
    agility = BoundedStat(1, 100)
    intellect = BoundedStat(1, 100)

    def __init__(self, name: str, level: int = 1):
        self._name = name
        self._level = level

        self.max_hp = 50 + level * 10
        self.hp = self.max_hp
        self.max_mp = 20 + level * 5
        self.mp = self.max_mp
        self.strength = 10
        self.agility = 10
        self.intellect = 10

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> int:
        return self._level

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, damage: int):
        self.hp = max(0, self.hp - damage)

    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)

    def __str__(self) -> str:
        return f"{self.name} (Ур. {self.level}) HP: {self.hp}/{self.max_hp} MP: {self.mp}/{self.max_mp}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}', {self.level})"


class Character(Human, ABC):

    def __init__(self, name: str, level: int = 1, fraction: str = "party"):
        super().__init__(name, level)
        self._active_effects = []
        self._cooldowns = {}
        self.fraction = fraction

    def is_ally(self, target: 'Character') -> bool:
        return self.fraction == target.fraction

    def is_enemy(self, target: 'Character') -> bool:
        return self.fraction != target.fraction

    def basic_attack(self, target: 'Character') -> str:
        if not self.is_alive:
            return f"{self.name} мертв и не может атаковать!"
        if not target.is_alive:
            return f"{target.name} уже мертв!"
        if not self.is_enemy(target):
            return f"{self.name} не может атаковать союзника {target.name}!"

        raise NotImplementedError("Метод должен быть реализован в дочернем классе")

    @abstractmethod
    def use_skill(self, target: 'Character', skill_index: int = 0) -> str:
        pass

    def add_effect(self, effect: 'Effect'):
        self._active_effects.append(effect)
        effect.on_apply(self)

    def process_effects(self) -> List[str]:
        results = []
        expired_effects = []

        for effect in self._active_effects:
            result = effect.on_turn(self)
            if result:
                results.append(result)
            if effect.is_expired():
                expired_effects.append(effect)

        for effect in expired_effects:
            self._active_effects.remove(effect)
            results.append(f"Эффект {effect.name} закончился")

        return results

    @property
    def active_effects(self) -> List[str]:
        return [effect.name for effect in self._active_effects]