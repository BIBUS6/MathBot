import re
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ============ ВАШ ТОКЕН ============
TOKEN = "8599574987:AAFIZrNJYkqSCUNyzk_2f4XtDUmysbJwA9k"

# ============ ТЕКСТ С ВАШЕГО PDF ============
FULL_TEXT = """
1.1. точки локального экстремума функции нескольких переменных;
1.2. функции y = f(x), заданной неявно уравнением F(x, y) = 0;
1.3. функции z = f(x, y), заданной неявно уравнением F(x, y, z) = 0;
1.4. зависимости функций f1(x1,...,xn),..., fk(x1,...,xn);
1.5. квадрариуемой плоской фигуры;
1.6. площади плоской фигуры;
1.7. интегральной суммы для двойного интеграла;
1.8. диаметра ограниченного множества G;
1.9. предела интегральных сумм при стремлении диаметра разбиения к нулю;
1.10. экстремума функции u(x,y) с условием связи f(x,y)=0;
1.11. экстремума функции u(x,y,z) с условием связи f(x,y,z)=0;
1.12. экстремума функции u(x,y,z) с двумя условиями связи f(x,y,z)=0, g(x,y,z)=0;

2.1. Сформулируйте и докажите теорему о необходимых условиях локального экстремума функции двух переменных.
2.2. Сформулируйте и докажите теорему о достаточных условиях локального экстремума функции двух переменных.
2.3. Сформулируйте и докажите теорему о существовании и непрерывности функции y = f(x), заданной неявно уравнением F(x, y) = 0.
2.4. Сформулируйте и докажите теорему о дифференцируемости функции y=f(x), заданной неявно уравнением F(x,y)=0.
2.5. Сформулируйте и докажите теорему о существовании и непрерывности функции z=f(x,y), заданной неявно уравнением F(x,y,z)=0.
2.6. Сформулируйте и докажите теорему о существовании и дифференцируемости функций y=f(x), z=g(x), заданных неявно системой уравнений F(x,y,z)=0, G(x,y,z)=0.
2.7. Сформулируйте и докажите теорему о существовании и дифференцируемости функций x=f(u,v), y=g(u,v), заданных неявно системой уравнений F(x,y)=u, G(x,y)=v.
2.8. Сформулируйте и докажите теорему о достаточных условиях независимости функций.
2.9. Сформулируйте и докажите теорему о необходимых условиях экстремума функции u(x,y) с условием связи f(x,y)=0 в форме Лагранжа.
2.10. Сформулируйте и докажите теорему о необходимых условиях экстремума функции u(x,y,z) с условием связи f(x,y,z)=0 в форме Лагранжа.
2.11. Сформулируйте и докажите теорему о необходимых условиях экстремума функции u(x,y,z) с двумя условиями связи f(x,y,z)=0, g(x,y,z)=0 в форме Лагранжа.
2.12. Сформулируйте и докажите теорему о достаточных условиях экстремума функции u(x,y) с условием связи f(x,y)=0 в форме Лагранжа.
2.13. Сформулируйте и докажите теорему о достаточных условиях экстремума функции u(x,y,z) с условием связи f(x,y,z)=0 в форме Лагранжа.
2.14. Сформулируйте и докажите теорему о достаточных условиях экстремума функции u(x,y,z) с двумя условиями связи f(x,y,z)=0, g(x,y,z)=0 в форме Лагранжа.
2.15. Теорема о формуле замены переменных для двойного интеграла.
2.16. Теорема о формуле замены переменных для тройного интеграла.
2.17. Теорема о среднем значении для двойного интеграла.
2.18. Теорема о необходимом и достаточном условии квадрируемости плоской фигуры.
2.19. Теорема о площади криволинейной трапеции.
2.20. Теорема о сведении двойного интеграла к повторному.
2.21. Теорема об интегрируемости непрерывной функции двух переменных.
2.22. Теорема о замене переменных в двойном интеграле для случая линейной замены.

3.1. Пусть функции u(x,y) и v(x,y) имеют локальный минимум в точке M0(x0,y0). Докажите, что функция u(x,y)+v(x,y) также имеет локальный минимум в указанной точке.
3.2. Приведите пример функций u(x,y) и v(x,y), которые имеют локальный минимум в точке M0(x0,y0), а функция u(x,y)·v(x,y) имеет локальный максимум в указанной точке.
3.3. Приведите пример функций u(x,y) и v(x,y), которые имеют локальный минимум в точке M0(x0,y0), а функция u(x,y)·v(x,y) не имеет локального экстремума в указанной точке.
3.4. Приведите пример функции u(x,y), имеющей в точке M0(1;1) локальный экстремум, у которой не существует ∂u/∂y (M0).
3.5. Приведите пример функции u(x,y), удовлетворяющей условию du(0;0)=0, но не имеющей в точке M0(0;0) локального экстремума.
3.6. Пусть кривая С на плоскости задана уравнением F(x,y)=0. Напишите уравнение нормали к кривой С в некоторой точке.
3.7. Пусть кривая С на плоскости задана уравнением F(x,y)=0. Напишите уравнение касательной к кривой С в некоторой точке.
3.8. Пусть функция y=f(x) задана неявно уравнением x–g(y)=0. Сформулируйте достаточные условия дифференцируемости функции f(x) и запишите формулу для вычисления её производной.
3.9. Пусть функции y=y(x), z=z(x) заданы неявно системой уравнений f(x,y,z)=0, g(x,y,z)=0. Найдите первый дифференциал функции y(x) и dz/dx.
3.10. Пусть функции x=f(u,v), y=g(u,v) заданы неявно системой уравнений F(x,y)=u, G(x,y)=v. Найдите du и dv.
3.11. Сформулируйте достаточные условия существования и дифференцируемости функций u=u(x,y), v=v(x,y), заданных неявно системой уравнений x=F(u,v), y=G(u,v). Найдите du и dv.
3.12. Докажите, что отличный от нуля градиент дифференцируемой функции z=u(x,y) в точке M0(x0,y0) направлен перпендикулярно касательной к линии уровня функции u(x,y) в точке M0.
3.13. Пусть в точке N0(x0,y0) выполнены необходимые (в форме Лагранжа) условия экстремума функции u(x,y) с условием связи f(x,y)=0 и к тому же grad u(x0,y0)≠0, grad f(x0,y0)≠0. Докажите, что в точке M0(x0,y0) градиенты функций u(x,y) и f(x,y) коллинеарны.
3.14. Пусть в точке N0(x0,y0) выполнены необходимые (в форме Лагранжа) условия экстремума функции u(x,y) с условием связи ax+by=c и d²u|M0>0, M0(x0,y0). Докажите, что в точке M0(x0,y0) имеет место экстремум указанной функции с указанным условием связи.
3.15. Пусть в точке N0(x0,y0) выполнены необходимые (в форме Лагранжа) условия экстремума функции u(x,y)=ax+by с условием связи f(x,y)=0 и d²f|M0>0, M0(x0,y0). Докажите, что в точке M0(x0,y0) имеет место экстремум указанной функции с указанным условием связи.

4.1.1. D = {(x,y): 1 ≤ x ≤ 2, 0 ≤ y ≤ x+1}
4.1.2. D = {(x,y): -2 ≤ x ≤ -1, x+1 ≤ y ≤ 0}
4.1.3. D - область на плоскости (x,y), ограниченная прямыми x=-3, y=0, y=1, y=-1-x
4.1.4. D - область, ограниченная прямыми x=0, y=1, y=-2x
4.1.5. D - область, ограниченная прямыми y=0, x=1, x=2y
4.1.6. D - область, ограниченная линиями y=0, y=1-x, x²+y²=1 (x²+y² ≤ 1)
4.1.7. D - область, ограниченная прямыми x=-1, x=0, y=2x и частью верхней полуокружности x²+y²=1
4.1.8. D = {(x,y): |x|+|y| ≤ 1}
4.1.9. D = {(x,y): y² ≤ x+2, y ≥ x}

4.2. Выражение для площади плоской фигуры в декартовой системе координат через двойной интеграл.
4.3. Выражение для площади плоской фигуры в полярной системе координат через двойной интеграл.
4.4. Формулы для массы и координат центра тяжести плоской фигуры (материальной пластины) с поверхностной плотностью ρ(x,y) через двойной интеграл.
4.5. Формулы для моментов инерции плоской фигуры (материальной пластины) с поверхностной плотностью ρ(x,y) через двойной интеграл.
"""

# ============ ПАРСИНГ ВСЕХ ЭЛЕМЕНТОВ ============

def parse_all_items(text: str):
    """Парсит все нумерованные элементы и возвращает список с номерами и текстом"""
    lines = text.split('\n')
    items = []
    current_item = []
    current_number = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Ищем номера вида 1.1, 2.1, 3.1, 4.1.1 и т.д.
        match = re.match(r'^(\d+(?:\.\d+)+)\.?\s*(.*)', line)
        
        if match:
            # Сохраняем предыдущий
            if current_item and current_number:
                items.append({
                    'number': current_number,
                    'text': ' '.join(current_item)
                })
            # Начинаем новый
            current_number = match.group(1)
            current_item = [match.group(2)] if match.group(2) else []
        elif current_item:
            current_item.append(line)
    
    # Добавляем последний
    if current_item and current_number:
        items.append({
            'number': current_number,
            'text': ' '.join(current_item)
        })
    
    return items

def get_type_from_number(number: str) -> str:
    """Определяет тип элемента по номеру"""
    if re.match(r'^1\.\d+', number):
        return 'definition'
    elif re.match(r'^2\.\d+', number):
        return 'theorem'
    elif re.match(r'^3\.\d+', number):
        return 'question'
    elif re.match(r'^4\.', number):
        return 'integral_task'
    else:
        return 'other'

def get_type_emoji(item_type: str) -> str:
    """Возвращает эмодзи для типа"""
    emojis = {
        'definition': '📖',
        'theorem': '📐',
        'question': '❓',
        'integral_task': '🔢',
        'other': '📌'
    }
    return emojis.get(item_type, '📌')

def get_type_name(item_type: str) -> str:
    """Возвращает русское название типа"""
    names = {
        'definition': 'Определение',
        'theorem': 'Теорема',
        'question': 'Вопрос/Задача',
        'integral_task': 'Задача (кратные интегралы)',
        'other': 'Материал'
    }
    return names.get(item_type, 'Материал')

# Парсим и группируем по типам
all_items = parse_all_items(FULL_TEXT)

# Создаём отдельные списки по типам
definitions = [item for item in all_items if get_type_from_number(item['number']) == 'definition']
theorems = [item for item in all_items if get_type_from_number(item['number']) == 'theorem']
questions = [item for item in all_items if get_type_from_number(item['number']) == 'question']
integral_tasks = [item for item in all_items if get_type_from_number(item['number']) == 'integral_task']

print(f"📊 Загружено: определений - {len(definitions)}, теорем - {len(theorems)}, вопросов - {len(questions)}, задач по интегралам - {len(integral_tasks)}")

# ============ КОМАНДЫ БОТА ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 **Привет! Я бот для подготовки по матанализу**\n\n"
        "Я умею выдавать случайные материалы разных типов:\n\n"
        "📖 `/def` — случайное определение\n"
        "📐 `/th` — случайную теорему (с доказательством)\n"
        "❓ `/q` — случайный вопрос/задачу\n"
        "🔢 `/int` — случайную задачу по кратным интегралам\n"
        "🎲 `/rand` — совершенно случайный материал любого типа\n"
        "📊 `/stats` — статистику\n"
        "🆘 `/help` — эту справку\n\n"
        "Удачи в подготовке! 🍀",
        parse_mode="Markdown"
    )

async def random_definition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not definitions:
        await update.message.reply_text("❌ Определения не найдены")
        return
    item = random.choice(definitions)
    await update.message.reply_text(
        f"📖 **Определение** (п.{item['number']}):\n\n{item['text']}",
        parse_mode="Markdown"
    )

async def random_theorem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not theorems:
        await update.message.reply_text("❌ Теоремы не найдены")
        return
    item = random.choice(theorems)
    await update.message.reply_text(
        f"📐 **Теорема** (п.{item['number']}):\n\n{item['text']}",
        parse_mode="Markdown"
    )

async def random_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not questions:
        await update.message.reply_text("❌ Вопросы не найдены")
        return
    item = random.choice(questions)
    await update.message.reply_text(
        f"❓ **Вопрос/Задача** (п.{item['number']}):\n\n{item['text']}",
        parse_mode="Markdown"
    )

async def random_integral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not integral_tasks:
        await update.message.reply_text("❌ Задачи по интегралам не найдены")
        return
    item = random.choice(integral_tasks)
    await update.message.reply_text(
        f"🔢 **Задача (кратные интегралы)** (п.{item['number']}):\n\n{item['text']}",
        parse_mode="Markdown"
    )

async def random_any(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not all_items:
        await update.message.reply_text("❌ Материалы не найдены")
        return
    item = random.choice(all_items)
    item_type = get_type_from_number(item['number'])
    emoji = get_type_emoji(item_type)
    type_name = get_type_name(item_type)
    
    await update.message.reply_text(
        f"{emoji} **{type_name}** (п.{item['number']}):\n\n{item['text']}",
        parse_mode="Markdown"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 **Статистика базы материалов:**\n\n"
        f"📖 Определений: {len(definitions)}\n"
        f"📐 Теорем: {len(theorems)}\n"
        f"❓ Вопросов/задач: {len(questions)}\n"
        f"🔢 Задач по интегралам: {len(integral_tasks)}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📚 **Всего:** {len(all_items)}",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **Доступные команды:**\n\n"
        "📖 `/def` — случайное определение\n"
        "📐 `/th` — случайная теорема\n"
        "❓ `/q` — случайный вопрос/задача\n"
        "🔢 `/int` — случайная задача по интегралам\n"
        "🎲 `/rand` — случайный материал любого типа\n"
        "📊 `/stats` — статистика\n"
        "🆘 `/help` — эта справка\n\n"
        "➕ **Короткие команды:** `/d`, `/t`, `/qq`, `/i`, `/r`",
        parse_mode="Markdown"
    )

# ============ ЗАПУСК ============

def main():
    app = Application.builder().token(TOKEN).build()
    
    # Основные команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("def", random_definition))
    app.add_handler(CommandHandler("th", random_theorem))
    app.add_handler(CommandHandler("q", random_question))
    app.add_handler(CommandHandler("int", random_integral))
    app.add_handler(CommandHandler("rand", random_any))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    
    # Короткие синонимы
    app.add_handler(CommandHandler("d", random_definition))
    app.add_handler(CommandHandler("t", random_theorem))
    app.add_handler(CommandHandler("qq", random_question))
    app.add_handler(CommandHandler("i", random_integral))
    app.add_handler(CommandHandler("r", random_any))
    
    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
