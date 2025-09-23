import unittest
from characters import Warrior, Mage, Healer
from boss import Boss
from items import HealthPotion, Inventory
from skills import PoisonEffect, ShieldEffect


class TestGame(unittest.TestCase):

    def setUp(self):
        self.warrior = Warrior("Тестовый воин", 1)
        self.mage = Mage("Тестовый маг", 1)
        self.healer = Healer("Тестовый лекарь", 1)
        self.boss = Boss("Тестовый босс", 1)

    def test_character_creation(self):
        self.assertTrue(self.warrior.is_alive)
        self.assertEqual(self.warrior.name, "Тестовый воин")
        self.assertGreater(self.warrior.strength, 0)

    def test_faction_mechanics(self):
        result = self.healer.use_skill(self.boss, 0)
        self.assertIn("не может лечить врага", result)

        result = self.warrior.basic_attack(self.healer)
        self.assertIn("не может атаковать союзника", result)

        result = self.warrior.basic_attack(self.boss)
        self.assertIn("атакует", result)

    def test_basic_attack(self):
        initial_hp = self.boss.hp
        self.warrior.basic_attack(self.boss)
        self.assertLess(self.boss.hp, initial_hp)

    def test_healing(self):
        self.warrior.take_damage(30)
        damaged_hp = self.warrior.hp

        self.healer.use_skill(self.warrior, 0)
        self.assertGreater(self.warrior.hp, damaged_hp)

    def test_poison_effect(self):
        poison = PoisonEffect(10)
        initial_hp = self.warrior.hp

        poison.on_apply(self.warrior)
        poison.on_turn(self.warrior)

        self.assertLess(self.warrior.hp, initial_hp)

    def test_shield_effect(self):
        shield = ShieldEffect(20)
        shield.on_apply(self.warrior)

        absorbed_damage = shield.absorb_damage(15)
        self.assertEqual(absorbed_damage, 0)
        self.assertEqual(shield.remaining_shield, 5)

    def test_inventory(self):
        inventory = Inventory()
        potion = HealthPotion()

        inventory.add_item(potion)
        self.assertEqual(inventory.items_count, 1)

        self.warrior.take_damage(30)
        damaged_hp = self.warrior.hp

        inventory.use_item(0, self.warrior)
        self.assertGreater(self.warrior.hp, damaged_hp)
        self.assertEqual(inventory.items_count, 0)

    def test_boss_phases(self):
        self.boss.hp = self.boss.max_hp * 0.8
        self.boss.use_skill(self.warrior, 0)

        self.boss.hp = self.boss.max_hp * 0.4
        self.boss.use_skill(self.warrior, 0)

        self.boss.hp = self.boss.max_hp * 0.2
        self.boss.use_skill(self.warrior, 0)

    def test_death_mechanics(self):
        self.warrior.take_damage(self.warrior.max_hp + 100)
        self.assertFalse(self.warrior.is_alive)

        result = self.warrior.basic_attack(self.boss)
        self.assertIn("мертв", result.lower())


if __name__ == "__main__":
    unittest.main()