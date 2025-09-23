from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from core import Character


class Item:

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    def use(self, target: 'Character') -> str:
        raise NotImplementedError("Метод use должен быть реализован в дочернем классе")

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"


class HealthPotion(Item):

    def __init__(self, heal_amount: int = 30):
        super().__init__("Зелье здоровья", f"Восстанавливает {heal_amount} HP")
        self.heal_amount = heal_amount

    def use(self, target: 'Character') -> str:
        if not target.is_alive:
            return f"{target.name} мертв, зелье не действует!"

        old_hp = target.hp
        target.heal(self.heal_amount)
        actual_heal = target.hp - old_hp
        return f"{target.name} использует {self.name} и восстанавливает {actual_heal} HP!"


class ManaPotion(Item):

    def __init__(self, mana_amount: int = 30):
        super().__init__("Зелье маны", f"Восстанавливает {mana_amount} MP")
        self.mana_amount = mana_amount

    def use(self, target: 'Character') -> str:
        old_mp = target.mp
        target.mp = min(target.max_mp, target.mp + self.mana_amount)
        actual_mana = target.mp - old_mp
        return f"{target.name} использует {self.name} и восстанавливает {actual_mana} MP!"


class Elixir(Item):

    def __init__(self):
        super().__init__("Эликсир", "Полностью восстанавливает HP и MP")

    def use(self, target: 'Character') -> str:
        if not target.is_alive:
            return f"{target.name} мертв, эликсир не действует!"

        hp_healed = target.max_hp - target.hp
        mp_restored = target.max_mp - target.mp

        target.hp = target.max_hp
        target.mp = target.max_mp

        return f"{target.name} использует {self.name}! Восстановлено: {hp_healed} HP, {mp_restored} MP"


class Inventory:

    def __init__(self):
        self._items: List[Item] = []

    def add_item(self, item: Item):
        self._items.append(item)

    def use_item(self, item_index: int, target: 'Character') -> str:
        if item_index < 0 or item_index >= len(self._items):
            return "Неверный индекс предмета!"

        item = self._items[item_index]
        result = item.use(target)
        self._items.pop(item_index)
        return result

    def get_items_list(self) -> List[str]:
        return [f"{i}: {item}" for i, item in enumerate(self._items)]

    @property
    def items_count(self) -> int:
        return len(self._items)

    def __str__(self) -> str:
        if not self._items:
            return "Инвентарь пуст"
        return "\n".join(self.get_items_list())