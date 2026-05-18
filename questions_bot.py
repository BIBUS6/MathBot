import re
import random
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Импорт для работы с PDF (используем pdfplumber вместо PyPDF2)
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("❌ Ошибка: pdfplumber не установлен.")
    print("Установите командой: pip3 install pdfplumber")
    exit(1)

# ============ НАСТРОЙКИ ============
TOKEN = "8599574987:AAFIZrNJYkqSCUNyzk_2f4XtDUmysbJwA9k"
PDF_FILE = "Математический_Анализ_2_семестр.pdf"

# ============ ФУНКЦИИ ДЛЯ ЧТЕНИЯ PDF ============

def extract_text_from_pdf(pdf_path: str) -> str:
    """Извлекает текст из PDF-файла с помощью pdfplumber (лучше для формул)"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 Найдено страниц: {len(pdf.pages)}")
            for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                print(f"   Страница {i}: {len(page_text) if page_text else 0} символов")
        return text
    except FileNotFoundError:
        print(f"❌ Файл не найден: {pdf_path}")
        return ""
    except Exception as e:
        print(f"❌ Ошибка при чтении PDF: {e}")
        return ""

def load_text() -> str:
    """Загружает текст из PDF-файла"""
    if not os.path.exists(PDF_FILE):
        print(f"❌ Файл {PDF_FILE} не найден!")
        print(f"📁 Текущая папка: {os.getcwd()}")
        print("Поместите PDF-файл в ту же папку, что и бот")
        return ""
    
    print(f"📄 Читаем PDF: {PDF_FILE}")
    text = extract_text_from_pdf(PDF_FILE)
    
    if text:
        print(f"✅ Загружено {len(text)} символов из PDF")
    else:
        print("❌ Не удалось извлечь текст из PDF")
    
    return text

# ============ ОЧИСТКА ТЕКСТА ============

def clean_text(text: str) -> str:
    """Очищает текст от битых символов и нормализует спецсимволы"""
    # Удаляем битые символы (оставляем только печатные)
    cleaned = re.sub(r'[^\x20-\x7E\x0A\x0D\u0400-\u04FF\u2000-\u206F\u2200-\u22FF\u25A0-\u25FF]', ' ', text)
    
    # Заменяем множественные пробелы на один
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Восстанавливаем часто встречающиеся математические символы
    replacements = {
        '∫': '∫',
        '∬': '∬',
        '∭': '∭',
        '∮': '∮',
        '∑': '∑',
        '∏': '∏',
        '∂': '∂',
        'Δ': 'Δ',
        '∇': '∇',
        '√': '√',
        '∛': '∛',
        '∜': '∜',
        '∞': '∞',
        '≠': '≠',
        '≤': '≤',
        '≥': '≥',
        '≈': '≈',
        'π': 'π',
        'α': 'α',
        'β': 'β',
        'γ': 'γ',
        'θ': 'θ',
        'λ': 'λ',
        'μ': 'μ',
        'ρ': 'ρ',
        'σ': 'σ',
        'τ': 'τ',
        'φ': 'φ',
        'ψ': 'ψ',
        'ω': 'ω',
        '→': '→',
        '⇒': '⇒',
        '⇔': '⇔',
        '·': '·',
        '×': '×',
        '÷': '÷',
        '±': '±',
        '∓': '∓',
    }
    
    # Также можно добавить замену для LaTeX-подобных команд
    # (оставляем как есть, они будут читабельны)
    
    return cleaned

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

def classify_item(item: dict) -> str:
    """Классифицирует элемент на основе номера и текста"""
    number = item['number']
    text = item['text'].lower()
    
    # Определения (1.x)
    if re.match(r'^1\.\d+', number):
        return 'definition'
    
    # Задачи (3.x, 4.x, 5.x)
    if re.match(r'^[3-5]\.', number):
        return 'problem'
    
    # Для 2.x — смотрим на ключевые слова
    if re.match(r'^2\.\d+', number):
        # Ключевые слова для теорем
        theorem_keywords = ['теорем', 'докажите', 'сформулируйте и докажите', 'доказательство']
        for keyword in theorem_keywords:
            if keyword in text:
                return 'theorem'
        # Остальное — задачи
        return 'problem'
    
    return 'other'

def get_type_emoji(item_type: str) -> str:
    """Возвращает эмодзи для типа"""
    emojis = {
        'definition': '📖',
        'theorem': '📐',
        'problem': '❓',
        'other': '📌'
    }
    return emojis.get(item_type, '📌')

def get_type_name(item_type: str) -> str:
    """Возвращает русское название типа"""
    names = {
        'definition': 'Определение',
        'theorem': 'Теорема (с доказательством)',
        'problem': 'Вопрос/Задача',
        'other': 'Материал'
    }
    return names.get(item_type, 'Материал')

# ============ ЗАГРУЗКА ДАННЫХ ============

print("=" * 50)
print("🤖 Бот по математическому анализу")
print("=" * 50)

# Загружаем текст из PDF
raw_text = load_text()

if not raw_text:
    print("❌ Не удалось загрузить материалы. Бот не запустится.")
    print("Альтернатива: создайте файл questions.txt с текстом вопросов")
    exit(1)

# Очищаем текст от битых символов
raw_text = clean_text(raw_text)

# Парсим все элементы
all_items = parse_all_items(raw_text)

if not all_items:
    print("❌ Не удалось распарсить материалы из PDF.")
    print("Возможно, PDF имеет нестандартную структуру.")
    print("Попробуйте сохранить PDF как текстовый файл и использовать его.")
    exit(1)

# Классифицируем элементы
definitions = []
theorems = []
problems = []

for item in all_items:
    item_type = classify_item(item)
    if item_type == 'definition':
        definitions.append(item)
    elif item_type == 'theorem':
        theorems.append(item)
    else:
        problems.append(item)

print("-" * 50)
print(f"📖 Определений (1.x): {len(definitions)}")
print(f"📐 Теорем (2.x с 'докажите'): {len(theorems)}")
print(f"❓ Вопросов/задач (3.x,4.x,5.x и остальные 2.x): {len(problems)}")
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
        "🎲 `/rand` — совершенно случайный материал любого типа\n"
        "📊 `/stats` — статистику\n"
        "🆘 `/help` — эту справку\n\n"
        "➕ **Короткие команды:** `/d`, `/t`, `/qq`, `/r`\n\n"
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

async def random_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not problems:
        await update.message.reply_text("❌ Вопросы/задачи не найдены")
        return
    item = random.choice(problems)
    await update.message.reply_text(
        f"❓ **Вопрос/Задача** (п. {item['number']}):\n\n{item['text']}",
        parse_mode="Markdown"
    )

async def random_any(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not all_items:
        await update.message.reply_text("❌ Материалы не найдены")
        return
    item = random.choice(all_items)
    item_type = classify_item(item)
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
        f"❓ Вопросов/задач: {len(problems)}\n"
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
        "🎲 `/rand` или `/r` — случайный материал любого типа\n"
        "📊 `/stats` — статистика\n"
        "🆘 `/help` — эта справка\n\n"
        f"📚 **Всего в базе:** {len(all_items)} материалов",
        parse_mode="Markdown"
    )

async def reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перезагружает материалы из PDF"""
    global all_items, definitions, theorems, problems
    
    await update.message.reply_text("🔄 Перезагрузка материалов из PDF...")
    
    raw_text = load_text()
    if not raw_text:
        await update.message.reply_text("❌ Не удалось загрузить PDF-файл")
        return
    
    raw_text = clean_text(raw_text)
    new_items = parse_all_items(raw_text)
    
    if not new_items:
        await update.message.reply_text("❌ Не удалось распарсить материалы из PDF")
        return
    
    all_items = new_items
    definitions = []
    theorems = []
    problems = []
    
    for item in all_items:
        item_type = classify_item(item)
        if item_type == 'definition':
            definitions.append(item)
        elif item_type == 'theorem':
            theorems.append(item)
        else:
            problems.append(item)
    
    await update.message.reply_text(
        f"✅ Материалы перезагружены из PDF!\n\n"
        f"📖 Определений: {len(definitions)}\n"
        f"📐 Теорем: {len(theorems)}\n"
        f"❓ Вопросов/задач: {len(problems)}\n"
        f"📚 Всего: {len(all_items)}"
    )

# ============ ЗАПУСК ============

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("def", random_definition))
    app.add_handler(CommandHandler("th", random_theorem))
    app.add_handler(CommandHandler("q", random_problem))
    app.add_handler(CommandHandler("rand", random_any))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reload", reload))
    
    app.add_handler(CommandHandler("d", random_definition))
    app.add_handler(CommandHandler("t", random_theorem))
    app.add_handler(CommandHandler("qq", random_problem))
    app.add_handler(CommandHandler("r", random_any))
    
    print("\n🚀 Бот запущен и работает!")
    print("📱 Найдите бота в Telegram и отправьте /start")
    print("⏹️ Для остановки нажмите Ctrl+C\n")
    
    app.run_polling()

if __name__ == "__main__":
    main()
