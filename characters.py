from core import Character, CritMixin
from skills import FireballSkill, HealSkill, PowerStrikeSkill, PoisonEffect


class Warrior(Character, CritMixin):

    def __init__(self, name: str, level: int = 1):
        super().__init__(name, level, fraction="party")
        self.strength = 20 + level * 2
        self.agility = 15 + level
        self.intellect = 5 + level
        self.max_hp = 100 + level * 15
        self.hp = self.max_hp
        self.max_mp = 30 + level * 2
        self.mp = self.max_mp

        self.skills = [PowerStrikeSkill()]

    def basic_attack(self, target: Character) -> str:
        if not self.is_alive:
            return f"{self.name} мертв и не может атаковать!"
        if not target.is_alive:
            return f"{target.name} уже мертв!"
        if not self.is_enemy(target):
            return f"{self.name} не может атаковать союзника {target.name}!"
        damage = self.strength * 0.8
        damage = self.calculate_crit(damage, crit_chance=0.15)
        target.take_damage(damage)
        return f"{self.name} атакует {target.name} и наносит {damage:.1f} урона!"

    def use_skill(self, target: Character, skill_index: int = 0) -> str:
        if not self.is_enemy(target):
            return f"{self.name} не может использовать боевой навык на союзника {target.name}!"
        if skill_index < len(self.skills):
            skill = self.skills[skill_index]
            return skill.use(self, target)
        return "Неверный индекс навыка!"


class Mage(Character, CritMixin):

    def __init__(self, name: str, level: int = 1):
        super().__init__(name, level, fraction="party")
        self.strength = 5 + level
        self.agility = 10 + level
        self.intellect = 25 + level * 3
        self.max_hp = 60 + level * 8
        self.hp = self.max_hp
        self.max_mp = 80 + level * 10
        self.mp = self.max_mp

        self.skills = [FireballSkill()]

    def basic_attack(self, target: Character) -> str:
        if not self.is_alive:
            return f"{self.name} мертв и не может атаковать!"
        if not target.is_alive:
            return f"{target.name} уже мертв!"
        if not self.is_enemy(target):
            return f"{self.name} не может атаковать союзника {target.name}!"
        damage = self.intellect * 0.6
        target.take_damage(damage)
        return f"{self.name} атакует {target.name} магией и наносит {damage:.1f} урона!"

    def use_skill(self, target: Character, skill_index: int = 0) -> str:
        if not self.is_enemy(target):
            return f"{self.name} не может использовать боевой навык на союзника {target.name}!"
        if skill_index < len(self.skills):
            skill = self.skills[skill_index]
            result = skill.use(self, target)
            if skill_index == 0 and self.mp > 20:
                target.add_effect(PoisonEffect(5))
                result += " Цель отравлена!"
            return result
        return "Неверный индекс навыка!"


class Healer(Character):

    def __init__(self, name: str, level: int = 1):
        super().__init__(name, level, fraction="party")
        self.strength = 8 + level
        self.agility = 12 + level
        self.intellect = 20 + level * 2
        self.max_hp = 80 + level * 10
        self.hp = self.max_hp
        self.max_mp = 60 + level * 8
        self.mp = self.max_mp

        self.skills = [HealSkill()]

    def basic_attack(self, target: Character) -> str:
        if not self.is_alive:
            return f"{self.name} мертв и не может атаковать!"
        if not target.is_alive:
            return f"{target.name} уже мертв!"
        if not self.is_enemy(target):
            return f"{self.name} не может атаковать союзника {target.name}!"
        damage = self.strength * 0.7
        target.take_damage(damage)
        return f"{self.name} атакует {target.name} и наносит {damage:.1f} урона!"

    def use_skill(self, target: Character, skill_index: int = 0) -> str:
        if skill_index == 0:
            if not self.is_ally(target):
                return f"{self.name} не может лечить врага {target.name}!"
        if skill_index < len(self.skills):
            skill = self.skills[skill_index]
            return skill.use(self, target)
        return "Неверный индекс навыка!"