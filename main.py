#!/usr/bin/env python3
import random
from characters import Warrior, Mage, Healer
from boss import Boss
from battle import Battle


def choose_difficulty():
    print("Выберите сложность:")
    print("1. Легкая (босс ур. 3)")
    print("2. Средняя (босс ур. 5)")
    print("3. Сложная (босс ур. 8)")

    while True:
        choice = input("Ваш выбор (1-3): ").strip()
        if choice in ['1', '2', '3']:
            levels = {'1': 3, '2': 5, '3': 8}
            return levels[choice]
        print("Пожалуйста, введите 1, 2 или 3")


def create_party():
    print("\n СОЗДАНИЕ КОМАНДЫ")

    classes = {
        '1': ('Воин', Warrior),
        '2': ('Маг', Mage),
        '3': ('Лекарь', Healer)
    }

    party = []

    for i in range(3):
        print(f"\nСоздание персонажа {i + 1}:")
        print("Доступные классы:")
        for key, (name, _) in classes.items():
            print(f"{key}. {name}")

        while True:
            class_choice = input("Выберите класс (1-3): ").strip()
            if class_choice in classes:
                class_name, class_obj = classes[class_choice]
                break
            print("Пожалуйста, введите 1, 2 или 3")

        name = input("Введите имя персонажа: ").strip()
        if not name:
            name = f"{class_name}{i + 1}"

        character = class_obj(name, level=5)
        party.append(character)

        print(f"Создан: {character}")

    return party


def show_party_status(party):
    print("\nВАША КОМАНДА")
    for i, char in enumerate(party, 1):
        status = "МЕРТВ" if not char.is_alive else (""
                                                    ""
                                                    ""
                                                    "ЖИВ")
        print(f"{i}. {char.name} ({char.__class__.__name__}) - {status}")
        print(f"   HP: {char.hp:.1f}/{char.max_hp} | MP: {char.mp:.1f}/{char.max_mp}")
        if hasattr(char, 'active_effects') and char.active_effects:
            print(f"   Эффекты: {', '.join(char.active_effects)}")


def main():
    print("ДОБРО ПОЖАЛОВАТЬ В ПАТИ ПРОТИВ БОССА!")

    random_seed = input("Введите seed для случайной генерации (или Enter для случайного): ").strip()
    if random_seed:
        random.seed(random_seed)
        print(f"Используется seed: {random_seed}")

    difficulty = choose_difficulty()
    party = create_party()

    boss_names = ["Дракон Гиммелут", "Демон Капучин", "Сфинктерион"]
    boss_name = random.choice(boss_names)
    boss = Boss(boss_name, level=difficulty)

    print(f"\nВАШ ПРОТИВНИК: {boss}")

    battle = Battle(party, boss)

    input("\nНажмите Enter чтобы начать бой...")

    victory = battle.start()

    print("\n")
    if victory:
        print("ПОЗДРАВЛЯЕМ! ВЫ ПОБЕДИЛИ!")
    else:
        print("ВЫ ПРОИГРАЛИ... ")

    print("\nСТАТИСТИКА БОЯ")
    print(f"Продолжительность: {battle.round_number} раундов")
    print(f"Босс: {boss.hp:.1f}/{boss.max_hp} HP")

    alive_count = sum(1 for char in party if char.is_alive)
    print(f"Выживших в пати: {alive_count}/{len(party)}")

    log_filename = f"battle_log_{random_seed if random_seed else 'random'}.txt"
    with open(log_filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(battle.get_battle_log()))

    print(f"\nПолный лог боя сохранен в: {log_filename}")

    battle.save_state("battle_state.json")


if __name__ == "__main__":
    main()