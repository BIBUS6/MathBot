import re
import random
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Попытка импортировать PyPDF2 (если установлен)
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PyPDF2 не установлен. Установите: pip3 install PyPDF2")
    print("⚠️ Будет использован текстовый режим (файл .txt)")

# ============ НАСТРОЙКИ ============
TOKEN = "8599574987:AAFIZrNJYkqSCUNyzk_2f4XtDUmysbJwA9k"
PDF_FILE = "Математический_Анализ_2_семестр.pdf"  # Имя вашего PDF-файла
TXT_FILE = "questions.txt"  # Резервный текстовый файл

# ============ ФУНКЦИИ ДЛЯ ЧТЕНИЯ ФАЙЛА ============

def extract_text_from_pdf(pdf_path: str) -> str:
    """Извлекает текст из PDF-файла"""
    if not PDF_AVAILABLE:
        return ""
    
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"❌ Ошибка при чтении PDF: {e}")
        return ""

def extract_text_from_txt(txt_path: str) -> str:
    """Извлекает текст из TXT-файла"""
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        print(f"❌ Ошибка при чтении TXT: {e}")
        return ""

def load_text() -> str:
    """Загружает текст из доступного источника (PDF -> TXT)"""
    # Пробуем загрузить из PDF
    if PDF_AVAILABLE and os.path.exists(PDF_FILE):
        print(f"📄 Читаем PDF: {PDF_FILE}")
        text = extract_text_from_pdf(PDF_FILE)
        if text:
            print(f"✅ Загружено {len(text)} символов из PDF")
            return text
    
    # Если PDF нет или не удалось прочитать, пробуем TXT
    if os.path.exists(TXT_FILE):
        print(f"📄 Читаем TXT: {TXT_FILE}")
        text = extract_text_from_txt(TXT_FILE)
        if text:
            print(f"✅ Загружено {len(text)} символов из TXT")
            return text
    
    # Если ничего не загрузилось
    print("❌ Не удалось загрузить файл с вопросами!")
    return ""

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
        # Также ищем русские номера с точкой (1.1., 2.1., 3.1.)
        match = re.match(r'^(\d+(?:\.\d+)+)\.?\s*(.*)', line)
        
        # Если не нашли, пробуем найти номера с точкой на конце (1.1. текст)
        if not match:
            match = re.match(r'^(\d+(?:\.\d+)+)\.\s+(.*)', line)
        
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
        'theorem': 'Теорема (с доказательством)',
        'question': 'Вопрос/Задача',
        'integral_task': 'Задача (кратные интегралы)',
        'other': 'Материал'
    }
    return names.get(item_type, 'Материал')

# ============ ЗАГРУЗКА ДАННЫХ ============

print("=" * 50)
print("🤖 Бот по математическому анализу")
print("=" * 50)

# Загружаем текст из файла
raw_text = load_text()

if not raw_text:
    print("❌ Не удалось загрузить материалы. Бот не запустится.")
    exit(1)

# Парсим все элементы
all_items = parse_all_items(raw_text)

# Создаём отдельные списки по типам
definitions = [item for item in all_items if get_type_from_number(item['number']) == 'definition']
theorems = [item for item in all_items if get_type_from_number(item['number']) == 'theorem']
questions = [item for item in all_items if get_type_from_number(item['number']) == 'question']
integral_tasks = [item for item in all_items if get_type_from_number(item['number']) == 'integral_task']

print(f"📖 Определений: {len(definitions)}")
print(f"📐 Теорем: {len(theorems)}")
print(f"❓ Вопросов/задач: {len(questions)}")
print(f"🔢 Задач по интегралам: {len(integral_tasks)}")
print(f"📚 Всего материалов: {len(all_items)}")
print("=" * 50)
print("✅ Бот готов к работе!")
print("=" * 50)

# ============ КОМАНДЫ БОТА ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 **Привет! Я бот для подготовки по математическому анализу**\n\n"
        "Я умею выдавать случайные материалы разных типов:\n\n"
        "📖 `/def` — случайное определение\n"
        "📐 `/th` — случайную теорему (с доказательством)\n"
        "❓ `/q` — случайный вопрос/задачу\n"
        "🔢 `/int` — случайную задачу по кратным интегралам\n"
        "🎲 `/rand` — совершенно случайный материал любого типа\n"
        "📊 `/stats` — статистику\n"
        "🆘 `/help` — эту справку\n\n"
        "➕ **Короткие команды:** `/d`, `/t`, `/qq`, `/i`, `/r`\n\n"
        "Удачи в подготовке! 🍀",
        parse_mode="Markdown"
    )

async def random_definition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not definitions:
        await update.message.reply_text("❌ Определения не найдены")
        return
    item = random.choice(definitions)
    await update.message.reply_text(
        f"📖 **Определение** (п. {item['number']}):\n\n{item['text']}",
        parse_mode="Markdown"
    )

async def random_theorem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not theorems:
        await update.message.reply_text("❌ Теоремы не найдены")
        return
    item = random.choice(theorems)
    await update.message.reply_text(
        f"📐 **Теорема** (п. {item['number']}):\n\n{item['text']}",
        parse_mode="Markdown"
    )

async def random_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not questions:
        await update.message.reply_text("❌ Вопросы не найдены")
        return
    item = random.choice(questions)
    await update.message.reply_text(
        f"❓ **Вопрос/Задача** (п. {item['number']}):\n\n{item['text']}",
        parse_mode="Markdown"
    )

async def random_integral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not integral_tasks:
        await update.message.reply_text("❌ Задачи по интегралам не найдены")
        return
    item = random.choice(integral_tasks)
    await update.message.reply_text(
        f"🔢 **Задача (кратные интегралы)** (п. {item['number']}):\n\n{item['text']}",
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
        f"{emoji} **{type_name}** (п. {item['number']}):\n\n{item['text']}",
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
        f"📚 **Всего материалов:** {len(all_items)}",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **Доступные команды:**\n\n"
        "📖 `/def` или `/d` — случайное определение\n"
        "📐 `/th` или `/t` — случайная теорема (с доказательством)\n"
        "❓ `/q` или `/qq` — случайный вопрос/задача\n"
        "🔢 `/int` или `/i` — случайная задача по интегралам\n"
        "🎲 `/rand` или `/r` — случайный материал любого типа\n"
        "📊 `/stats` — статистика\n"
        "🆘 `/help` — эта справка\n\n"
        f"📚 **Всего в базе:** {len(all_items)} материалов\n\n"
        "💡 **Совет:** Используйте короткие команды для быстрого доступа!",
        parse_mode="Markdown"
    )

# Команда для перезагрузки вопросов из файла (только для админа)
async def reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перезагружает вопросы из файла (только для админа)"""
    global all_items, definitions, theorems, questions, integral_tasks
    
    # ID администратора (замените на свой Telegram ID)
    ADMIN_ID = @egoryyaan  # ← ВСТАВЬТЕ ВАШ TELEGRAM ID
    
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для этой команды")
        return
    
    await update.message.reply_text("🔄 Перезагрузка материалов из файла...")
    
    raw_text = load_text()
    if not raw_text:
        await update.message.reply_text("❌ Не удалось загрузить файл")
        return
    
    new_items = parse_all_items(raw_text)
    
    if not new_items:
        await update.message.reply_text("❌ Не удалось распарсить материалы")
        return
    
    # Обновляем глобальные переменные
    all_items = new_items
    definitions = [item for item in all_items if get_type_from_number(item['number']) == 'definition']
    theorems = [item for item in all_items if get_type_from_number(item['number']) == 'theorem']
    questions = [item for item in all_items if get_type_from_number(item['number']) == 'question']
    integral_tasks = [item for item in all_items if get_type_from_number(item['number']) == 'integral_task']
    
    await update.message.reply_text(
        f"✅ Материалы перезагружены!\n\n"
        f"📖 Определений: {len(definitions)}\n"
        f"📐 Теорем: {len(theorems)}\n"
        f"❓ Вопросов/задач: {len(questions)}\n"
        f"🔢 Задач по интегралам: {len(integral_tasks)}\n"
        f"📚 Всего: {len(all_items)}"
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
    app.add_handler(CommandHandler("reload", reload))  # Команда для перезагрузки
    
    # Короткие синонимы
    app.add_handler(CommandHandler("d", random_definition))
    app.add_handler(CommandHandler("t", random_theorem))
    app.add_handler(CommandHandler("qq", random_question))
    app.add_handler(CommandHandler("i", random_integral))
    app.add_handler(CommandHandler("r", random_any))
    
    print("\n🚀 Бот запущен и работает!")
    print("📱 Найдите бота в Telegram и отправьте /start")
    print("⏹️ Для остановки нажмите Ctrl+C\n")
    
    app.run_polling()

if __name__ == "__main__":
    main()
