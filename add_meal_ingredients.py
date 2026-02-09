#!/usr/bin/env python3
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from app import app, db
from models import Meal, Inventory, MealIngredient


def create_meal_ingredients():
    print("=" * 60)
    print("СОЗДАНИЕ СВЯЗЕЙ МЕЖДУ БЛЮДАМИ И ИНГРЕДИЕНТАМИ")
    print("=" * 60)

    with app.app_context():
        MealIngredient.query.delete()

        ingredients = Inventory.query.all()
        ingredient_dict = {}
        for ing in ingredients:
            name_lower = ing.ingredient.lower()
            ingredient_dict[name_lower] = ing

        meal_ingredients_data = {
            'Каша манная': {
                'ингредиенты': [
                    {'name': 'Манка', 'quantity': 0.1, 'unit': 'кг', 'min_quantity': 0.05},
                    {'name': 'Молоко', 'quantity': 0.2, 'unit': 'л', 'min_quantity': 0.1},
                    {'name': 'Сахар', 'quantity': 0.02, 'unit': 'кг', 'min_quantity': 0.01},
                    {'name': 'Масло сливочное', 'quantity': 0.01, 'unit': 'кг', 'min_quantity': 0.005}
                ]
            },
            'Омлет с сыром': {
                'ингредиенты': [
                    {'name': 'Яйца', 'quantity': 2, 'unit': 'шт', 'min_quantity': 1},
                    {'name': 'Молоко', 'quantity': 0.05, 'unit': 'л', 'min_quantity': 0.025},
                    {'name': 'Сыр', 'quantity': 0.03, 'unit': 'кг', 'min_quantity': 0.015},
                    {'name': 'Масло сливочное', 'quantity': 0.01, 'unit': 'кг', 'min_quantity': 0.005}
                ]
            },
            'Бутерброды с колбасой': {
                'ингредиенты': [
                    {'name': 'Хлеб', 'quantity': 0.1, 'unit': 'кг', 'min_quantity': 0.05},
                    {'name': 'Колбаса', 'quantity': 0.05, 'unit': 'кг', 'min_quantity': 0.025},
                    {'name': 'Масло сливочное', 'quantity': 0.01, 'unit': 'кг', 'min_quantity': 0.005}
                ]
            },
            'Суп куриный с лапшой': {
                'ингредиенты': [
                    {'name': 'Курица', 'quantity': 0.15, 'unit': 'кг', 'min_quantity': 0.075},
                    {'name': 'Лапша', 'quantity': 0.08, 'unit': 'кг', 'min_quantity': 0.04},
                    {'name': 'Морковь', 'quantity': 0.05, 'unit': 'кг', 'min_quantity': 0.025},
                    {'name': 'Лук', 'quantity': 0.03, 'unit': 'кг', 'min_quantity': 0.015},
                    {'name': 'Картофель', 'quantity': 0.1, 'unit': 'кг', 'min_quantity': 0.05}
                ]
            },
            'Котлета с картофельным пюре': {
                'ингредиенты': [
                    {'name': 'Курица', 'quantity': 0.15, 'unit': 'кг', 'min_quantity': 0.075},
                    {'name': 'Картофель', 'quantity': 0.2, 'unit': 'кг', 'min_quantity': 0.1},
                    {'name': 'Молоко', 'quantity': 0.05, 'unit': 'л', 'min_quantity': 0.025},
                    {'name': 'Масло сливочное', 'quantity': 0.02, 'unit': 'кг', 'min_quantity': 0.01},
                    {'name': 'Лук', 'quantity': 0.02, 'unit': 'кг', 'min_quantity': 0.01}
                ]
            },
            'Макароны по-флотски': {
                'ингредиенты': [
                    {'name': 'Макароны', 'quantity': 0.15, 'unit': 'кг', 'min_quantity': 0.075},
                    {'name': 'Говядина', 'quantity': 0.1, 'unit': 'кг', 'min_quantity': 0.05},
                    {'name': 'Лук', 'quantity': 0.03, 'unit': 'кг', 'min_quantity': 0.015},
                    {'name': 'Морковь', 'quantity': 0.03, 'unit': 'кг', 'min_quantity': 0.015},
                    {'name': 'Масло растительное', 'quantity': 0.02, 'unit': 'л', 'min_quantity': 0.01}
                ]
            },
            'Компот из сухофруктов': {
                'ингредиенты': [
                    {'name': 'Сухофрукты', 'quantity': 0.05, 'unit': 'кг', 'min_quantity': 0.025},
                    {'name': 'Сахар', 'quantity': 0.03, 'unit': 'кг', 'min_quantity': 0.015}
                ]
            },
            'Чай с сахаром': {
                'ингредиенты': [
                    {'name': 'Чай', 'quantity': 0.005, 'unit': 'кг', 'min_quantity': 0.0025},
                    {'name': 'Сахар', 'quantity': 0.02, 'unit': 'кг', 'min_quantity': 0.01}
                ]
            }
        }

        total_ingredients_added = 0
        total_connections_created = 0

        for meal_name, data in meal_ingredients_data.items():
            meal = Meal.query.filter_by(name=meal_name).first()
            if not meal:
                print(f"⚠️  Блюдо '{meal_name}' не найдено")
                continue

            print(f"\n🍽️  Добавляем ингредиенты для блюда: {meal_name}")

            for ing_data in data['ингредиенты']:
                ing_name = ing_data['name'].lower()

                ingredient = None
                for key, ing in ingredient_dict.items():
                    if ing_name in key or key in ing_name:
                        ingredient = ing
                        break

                if not ingredient:
                    print(f"  ➕ Создаем новый ингредиент: {ing_data['name']}")
                    ingredient = Inventory(
                        ingredient=ing_data['name'],
                        quantity=50.0,
                        unit=ing_data['unit'],
                        min_quantity=ing_data.get('min_quantity', ing_data['quantity'] * 2)
                    )
                    db.session.add(ingredient)
                    db.session.flush()

                    ingredient_dict[ing_name] = ingredient
                    total_ingredients_added += 1

                meal_ingredient = MealIngredient(
                    meal_id=meal.id,
                    ingredient_id=ingredient.id,
                    quantity_required=ing_data['quantity'],
                    unit=ing_data['unit']
                )
                db.session.add(meal_ingredient)
                total_connections_created += 1
                print(f"  ✅ {ingredient.ingredient}: {ing_data['quantity']} {ing_data['unit']}")

        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print("✅ СВЯЗИ МЕЖДУ БЛЮДАМИ И ИНГРЕДИЕНТАМИ СОЗДАНЫ!")
            print("=" * 60)
            print(f"✅ Добавлено новых ингредиентов: {total_ingredients_added}")
            print(f"✅ Всего связей создано: {total_connections_created}")
            print(f"✅ Всего ингредиентов в базе: {Inventory.query.count()}")
            print(f"✅ Всего связей в базе: {MealIngredient.query.count()}")

            if total_ingredients_added > 0:
                print("\n📊 Новые ингредиенты в базе:")
                new_ingredients = db.session.query(Inventory).order_by(Inventory.id.desc()).limit(
                    total_ingredients_added).all()
                for ing in reversed(new_ingredients):
                    print(f"  • {ing.ingredient} ({ing.quantity} {ing.unit}) - мин: {ing.min_quantity} {ing.unit}")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка при сохранении: {e}")
            import traceback
            traceback.print_exc()


def check_meal_ingredients():
    with app.app_context():
        print("=" * 60)
        print("ПРОВЕРКА СВЯЗЕЙ МЕЖДУ БЛЮДАМИ И ИНГРЕДИЕНТАМИ")
        print("=" * 60)

        meals = Meal.query.all()

        for meal in meals:
            print(f"\n🍽️  Блюдо: {meal.name}")

            if meal.meal_ingredients:
                print(f"  ✅ Связи через MealIngredient: {len(meal.meal_ingredients)}")
                for mi in meal.meal_ingredients:
                    if mi.ingredient:
                        print(
                            f"    • {mi.ingredient.ingredient}: {mi.quantity_required} {mi.unit or mi.ingredient.unit}")
                    else:
                        print(f"    ⚠️  Связь #{mi.id}: ингредиент не найден")
            else:
                print(f"  ⚠️  Нет связей через MealIngredient")

            if meal.ingredients:
                print(f"  📝 Текстовое описание: {meal.ingredients[:50]}...")
            else:
                print(f"  ⚠️  Нет текстового описания ингредиентов")

        print("\n" + "=" * 60)
        print(f"📊 ИТОГИ:")
        print(f"  • Всего блюд: {Meal.query.count()}")
        print(f"  • Всего ингредиентов: {Inventory.query.count()}")
        print(f"  • Всего связей MealIngredient: {MealIngredient.query.count()}")
        print("=" * 60)


if __name__ == '__main__':
    create_meal_ingredients()