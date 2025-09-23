from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core import Character


class Effect(ABC):

    def __init__(self, name: str, duration: int = 3):
        self.name = name
        self.duration = duration
        self.current_duration = duration

    @abstractmethod
    def on_apply(self, target: 'Character'):
        pass

    @abstractmethod
    def on_turn(self, target: 'Character') -> str:
        pass

    def is_expired(self) -> bool:
        self.current_duration -= 1
        return self.current_duration <= 0


class PoisonEffect(Effect):

    def __init__(self, damage_per_turn: int = 5):
        super().__init__("Отравление", 3)
        self.damage_per_turn = damage_per_turn

    def on_apply(self, target: 'Character'):
        return f"{target.name} отравлен!"

    def on_turn(self, target: 'Character') -> str:
        target.take_damage(self.damage_per_turn)
        return f"{target.name} получает {self.damage_per_turn} урона от яда"


class ShieldEffect(Effect):

    def __init__(self, shield_strength: float = 20):
        super().__init__("Щит", 2)
        self.shield_strength = shield_strength
        self.remaining_shield = shield_strength

    def on_apply(self, target: 'Character'):
        return f"{target.name} получает щит!"

    def on_turn(self, target: 'Character') -> str:
        return f"Щит защищает {target.name} ({self.remaining_shield} прочности)"

    def absorb_damage(self, damage: float) -> float:
        if self.remaining_shield >= damage:
            self.remaining_shield -= damage
            return 0
        else:
            remaining_damage = damage - self.remaining_shield
            self.remaining_shield = 0
            return remaining_damage


class RegenerationEffect(Effect):

    def __init__(self, heal_per_turn: int = 10):
        super().__init__("Регенерация", 3)
        self.heal_per_turn = heal_per_turn

    def on_apply(self, target: 'Character'):
        return f"{target.name} начинает regenerировать!"

    def on_turn(self, target: 'Character') -> str:
        target.heal(self.heal_per_turn)
        return f"{target.name} восстанавливает {self.heal_per_turn} HP"


class Skill:

    def __init__(self, name: str, mp_cost: float = 0, cooldown: int = 0, target_type: str = "ally"):
        self.name = name
        self.mp_cost = mp_cost
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.target_type = target_type

    def can_use(self, caster: 'Character', target: 'Character') -> bool:
        if caster.mp < self.mp_cost:
            return False
        if self.current_cooldown > 0:
            return False
        if self.target_type == "ally" and not caster.is_ally(target):
            return False
        if self.target_type == "enemy" and not caster.is_enemy(target):
            return False
        return True

    def use(self, caster: 'Character', target: 'Character') -> str:
        if not self.can_use(caster, target):
            return f"Навык {self.name} недоступен!"

        caster.mp -= self.mp_cost
        self.current_cooldown = self.cooldown
        return self._apply_effect(caster, target)

    @abstractmethod
    def _apply_effect(self, caster: 'Character', target: 'Character') -> str:
        pass

    def reduce_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


class FireballSkill(Skill):

    def __init__(self):
        super().__init__("Огненный шар", mp_cost=15, cooldown=2, target_type="enemy")

    def _apply_effect(self, caster: 'Character', target: 'Character') -> str:
        damage = caster.intellect * 1.5
        target.take_damage(damage)
        return f"{caster.name} использует Огненный шар! {target.name} получает {damage} урона"


class HealSkill(Skill):

    def __init__(self):
        super().__init__("Лечение", mp_cost=20, cooldown=3, target_type='ally')

    def _apply_effect(self, caster: 'Character', target: 'Character') -> str:
        heal_amount = caster.intellect * 2
        target.heal(heal_amount)
        return f"{caster.name} использует Лечение! {target.name} восстанавливает {heal_amount} HP"


class PowerStrikeSkill(Skill):

    def __init__(self):
        super().__init__("Мощный удар", mp_cost=10, cooldown=1, target_type='enemy')

    def _apply_effect(self, caster: 'Character', target: 'Character') -> str:
        damage = caster.strength * 2
        target.take_damage(damage)
        return f"{caster.name} использует Мощный удар! {target.name} получает {damage} урона"