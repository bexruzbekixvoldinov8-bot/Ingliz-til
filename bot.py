import os
import telebot
from telebot import types
import json
from flask import Flask
import logging
import threading
from datetime import date

# ==================== RENDER SERVER ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host="0.0.0.0", port=port)

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "7963263075:AAFy0uOwjihtt2YOSy0bZmjXu5CpdVTtfRQ"
ADMIN_IDS = [7384088509, 533170952]
ADMIN_PASSWORD = "2026"
DAILY_PRICE = 25000  # so'm

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
telebot.logger.setLevel("ERROR")

DB_FILE = "database.json"
LEVELS = ["Starter", "Beginner", "Elementary", "Pre-Intermediate", "Intermediate", "Upper-Intermediate", "Advanced"]

# ==================== ESSENTIAL SO'ZLARI ====================
VOCABULARY = {
    "Essential 1": {
        "Unit 1": [
            ("hello", "salom"), ("goodbye", "xayr"), ("yes", "ha"), ("no", "yo'q"),
            ("please", "iltimos"), ("thank you", "rahmat"), ("sorry", "kechirasiz"),
            ("good", "yaxshi"), ("bad", "yomon"), ("ok", "mayli"),
        ],
        "Unit 2": [
            ("cat", "mushuk"), ("dog", "it"), ("bird", "qush"), ("fish", "baliq"),
            ("horse", "ot"), ("cow", "sigir"), ("sheep", "qo'y"), ("pig", "cho'chqa"),
            ("rabbit", "quyon"), ("mouse", "sichqon"),
        ],
        "Unit 3": [
            ("apple", "olma"), ("banana", "banan"), ("orange", "apelsin"), ("grape", "uzum"),
            ("watermelon", "tarvuz"), ("melon", "qovun"), ("strawberry", "qulupnay"),
            ("lemon", "limon"), ("pear", "nok"), ("peach", "shaftoli"),
        ],
        "Unit 4": [
            ("mother", "ona"), ("father", "ota"), ("brother", "aka/uka"), ("sister", "opa/singil"),
            ("grandfather", "bobo"), ("grandmother", "buvi"), ("son", "o'g'il"),
            ("daughter", "qiz"), ("husband", "er"), ("wife", "xotin"),
        ],
        "Unit 5": [
            ("red", "qizil"), ("blue", "ko'k"), ("green", "yashil"), ("yellow", "sariq"),
            ("white", "oq"), ("black", "qora"), ("orange", "to'q sariq"), ("pink", "pushti"),
            ("purple", "binafsha"), ("brown", "jigarrang"),
        ],
    },
    "Essential 2": {
        "Unit 1": [
            ("morning", "ertalab"), ("afternoon", "tushdan keyin"), ("evening", "kechqurun"),
            ("night", "kecha"), ("today", "bugun"), ("tomorrow", "ertaga"),
            ("yesterday", "kecha"), ("week", "hafta"), ("month", "oy"), ("year", "yil"),
        ],
        "Unit 2": [
            ("school", "maktab"), ("teacher", "o'qituvchi"), ("student", "o'quvchi"),
            ("book", "kitob"), ("pen", "qalam"), ("pencil", "qo'rg'oshin qalam"),
            ("notebook", "daftar"), ("desk", "parta"), ("board", "doska"), ("class", "sinf"),
        ],
        "Unit 3": [
            ("house", "uy"), ("room", "xona"), ("kitchen", "oshxona"), ("bedroom", "yotoqxona"),
            ("bathroom", "hammom"), ("door", "eshik"), ("window", "deraza"),
            ("floor", "pol"), ("ceiling", "shift"), ("wall", "devor"),
        ],
        "Unit 4": [
            ("eat", "yemoq"), ("drink", "ichmoq"), ("sleep", "uxlamoq"), ("walk", "yurmoq"),
            ("run", "yugurmoq"), ("sit", "o'tirmoq"), ("stand", "turmoq"),
            ("read", "o'qimoq"), ("write", "yozmoq"), ("speak", "gapirmoq"),
        ],
        "Unit 5": [
            ("big", "katta"), ("small", "kichik"), ("tall", "baland"), ("short", "past"),
            ("long", "uzun"), ("wide", "keng"), ("narrow", "tor"), ("heavy", "og'ir"),
            ("light", "engil"), ("fast", "tez"),
        ],
    },
    "Essential 3": {
        "Unit 1": [
            ("airport", "aeroport"), ("station", "vokzal"), ("hospital", "kasalxona"),
            ("pharmacy", "dorixona"), ("bank", "bank"), ("market", "bozor"),
            ("restaurant", "restoran"), ("hotel", "mehmonxona"), ("park", "bog'"),
            ("library", "kutubxona"),
        ],
        "Unit 2": [
            ("doctor", "shifokor"), ("nurse", "hamshira"), ("engineer", "muhandis"),
            ("lawyer", "advokat"), ("driver", "haydovchi"), ("cook", "oshpaz"),
            ("farmer", "dehqon"), ("soldier", "askar"), ("police", "politsiyachi"),
            ("pilot", "uchuvchi"),
        ],
        "Unit 3": [
            ("weather", "ob-havo"), ("sunny", "quyoshli"), ("cloudy", "bulutli"),
            ("rainy", "yomg'irli"), ("windy", "shamolли"), ("snowy", "qorli"),
            ("hot", "issiq"), ("cold", "sovuq"), ("warm", "iliq"), ("foggy", "tumanli"),
        ],
        "Unit 4": [
            ("money", "pul"), ("price", "narx"), ("cheap", "arzon"), ("expensive", "qimmat"),
            ("buy", "sotib olmoq"), ("sell", "sotmoq"), ("pay", "to'lamoq"),
            ("free", "bepul"), ("discount", "chegirma"), ("receipt", "chek"),
        ],
        "Unit 5": [
            ("happy", "xursand"), ("sad", "xafa"), ("angry", "g'azablangan"),
            ("tired", "charchagan"), ("hungry", "och"), ("thirsty", "chanqagan"),
            ("scared", "qo'rqqan"), ("excited", "hayajonlangan"), ("bored", "zerikkan"),
            ("surprised", "hayron"),
        ],
    },
}

# ==================== DATABASE ====================
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                pass
    return {"users": {}, "tests": [], "results": {}, "attendance": {}, "homeworks": {}, "vocab_progress": {}, "payments": {}}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_states = {}
user_data = {}
test_states = {}
vocab_states = {}

# ==================== YORDAMCHI ====================
def is_admin(user_id):
    if user_id in ADMIN_IDS:
        return True
    db = load_db()
    uid = str(user_id)
    return uid in db["users"] and db["users"][uid].get("role") == "admin"

def get_name(user_id):
    db = load_db()
    uid = str(user_id)
    if uid in db["users"]:
        return db["users"][uid]["name"]
    return "Foydalanuvchi"

# ==================== MENYU ====================
def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if is_admin(user_id):
        markup.add("👨‍🏫 O'qituvchilar", "👨‍🎓 O'quvchilar ro'yxati")
        markup.add("📊 Statistika", "📝 Yangi Test qo'shish")
        markup.add("📥 Kelgan Uy vazifalari", "💰 To'lovlar")
        markup.add("📣 Hammaga xabar yuborish")
    else:
        markup.add("📝 Test yechish", "📊 Natijalarim")
        markup.add("✅ Keldim", "📚 Uy vazifa topshirish")
        markup.add("📖 So'z o'rganish", "💳 To'lov qildim")
        markup.add("ℹ️ Profil")
    return markup

# ==================== START ====================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Foydalanuvchi"
    db = load_db()
    uid = str(user_id)
    if uid in db["users"]:
        name = db["users"][uid]["name"]
        role = "Admin" if db["users"][uid].get("role") == "admin" else "O'quvchi"
        bot.send_message(
            message.chat.id,
            f"👋 Salom, *{name}*!\n\nXush kelibsiz, *{role}*!",
            parse_mode="Markdown",
            reply_markup=main_menu(user_id)
        )
    else:
        user_states[user_id] = "waiting_name"
        bot.send_message(
            message.chat.id,
            f"👋 Salom, *{first_name}*!\n\n"
            f"🇺🇸 English Learning Botga xush kelibsiz!\n\n"
            f"Ro'yxatdan o'tish uchun ism va familiyangizni kiriting:",
            parse_mode="Markdown"
        )

# ==================== RO'YXATDAN O'TISH ====================
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "waiting_name")
def reg_get_name(message):
    name = message.text.strip()
    if len(name) < 3:
        bot.send_message(message.chat.id, "⚠️ Iltimos, to'liq ism familiyangizni kiriting.")
        return
    user_data[message.from_user.id] = {"name": name}
    user_states[message.from_user.id] = "waiting_level"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for lvl in LEVELS:
        markup.add(lvl)
    bot.send_message(
        message.chat.id,
        f"✅ Rahmat, *{name}*!\n\n📊 Ingliz tili darajangizni tanlang:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "waiting_level")
def reg_get_level(message):
    if message.text not in LEVELS:
        bot.send_message(message.chat.id, "⚠️ Iltimos, darajani ro'yxatdan tanlang!")
        return
    user_data[message.from_user.id]["level"] = message.text
    user_states[message.from_user.id] = "waiting_phone"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📱 Raqamni yuborish", request_contact=True))
    name = user_data[message.from_user.id]["name"]
    bot.send_message(
        message.chat.id,
        f"👍 *{message.text}* darajasi tanlandi!\n\n"
        f"📞 *{name}*, endi telefon raqamingizni yuboring:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(content_types=["contact"])
def reg_get_contact(message):
    user_id = message.from_user.id
    if user_states.get(user_id) != "waiting_phone":
        return
    db = load_db()
    data = user_data.get(user_id, {})
    role = "admin" if user_id in ADMIN_IDS else "student"
    db["users"][str(user_id)] = {
        "name": data["name"],
        "level": data["level"],
        "phone": message.contact.phone_number,
        "telegram_id": user_id,
        "role": role
    }
    save_db(db)
    user_states.pop(user_id, None)
    user_data.pop(user_id, None)
    if role == "admin":
        user_states[user_id] = "waiting_admin_password"
        bot.send_message(
            message.chat.id,
            f"🔐 *{data['name']}*, siz admin sifatida aniqlandingiz!\n\nParolni kiriting:",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            message.chat.id,
            f"🎉 *{data['name']}*, muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
            f"📊 Darajangiz: *{data['level']}*\n\nQuyidagi menyudan foydalaning:",
            parse_mode="Markdown",
            reply_markup=main_menu(user_id)
        )

# ==================== ADMIN PAROL ====================
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "waiting_admin_password")
def check_admin_pass(message):
    user_id = message.from_user.id
    name = get_name(user_id)
    if message.text == ADMIN_PASSWORD:
        user_states.pop(user_id, None)
        bot.send_message(
            message.chat.id,
            f"✅ *{name}*, admin panel muvaffaqiyatli ochildi!",
            parse_mode="Markdown",
            reply_markup=main_menu(user_id)
        )
    else:
        bot.send_message(message.chat.id, "❌ Parol noto'g'ri! Qayta kiriting:")

# ==================== ADMIN: O'QITUVCHILAR ====================
@bot.message_handler(func=lambda m: m.text == "👨‍🏫 O'qituvchilar")
def admin_teachers(message):
    if not is_admin(message.from_user.id):
        return
    name = get_name(message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"👨‍🏫 *{name}*, o'qituvchilar bo'limi:\n\n"
        f"Hozircha faqat siz — Admin sifatida dars berasiz.\n"
        f"Kelajakda bu yerga yangi o'qituvchilar qo'shiladi.",
        parse_mode="Markdown",
        reply_markup=main_menu(message.from_user.id)
    )

# ==================== ADMIN: O'QUVCHILAR RO'YXATI ====================
@bot.message_handler(func=lambda m: m.text == "👨‍🎓 O'quvchilar ro'yxati")
def admin_students_list(message):
    if not is_admin(message.from_user.id):
        return
    db = load_db()
    students = [(uid, u) for uid, u in db["users"].items() if u.get("role") == "student"]
    if not students:
        bot.send_message(message.chat.id, "Hali o'quvchilar ro'yxatdan o'tmagan.", reply_markup=main_menu(message.from_user.id))
        return
    text = f"👨‍🎓 *O'quvchilar ro'yxati* ({len(students)} kishi):\n\n"
    for i, (uid, u) in enumerate(students, 1):
        text += (
            f"{i}. *{u['name']}*\n"
            f"   📊 Level: {u['level']}\n"
            f"   📞 Tel: {u['phone']}\n\n"
        )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(message.from_user.id))

# ==================== ADMIN: STATISTIKA ====================
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def admin_stats(message):
    if not is_admin(message.from_user.id):
        show_my_results(message)
        return
    db = load_db()
    students = [u for u in db["users"].values() if u.get("role") == "student"]
    total_tests = len(db["tests"])
    total_results = sum(len(v) for v in db["results"].values())
    total_homeworks = sum(len(v) for v in db["homeworks"].values()) if db.get("homeworks") else 0
    today = str(date.today())
    today_attendance = sum(
        1 for att in db.get("attendance", {}).values() if today in att
    )
    text = (
        f"📊 *Umumiy Statistika:*\n\n"
        f"👨‍🎓 O'quvchilar: *{len(students)}* kishi\n"
        f"📝 Testlar soni: *{total_tests}* ta\n"
        f"✅ Topshirilgan testlar: *{total_results}* ta\n"
        f"📚 Uy vazifalari: *{total_homeworks}* ta\n"
        f"📅 Bugun kelganlar: *{today_attendance}* kishi"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(message.from_user.id))

# ==================== ADMIN: UY VAZIFALARI ====================
@bot.message_handler(func=lambda m: m.text == "📥 Kelgan Uy vazifalari")
def admin_homeworks(message):
    if not is_admin(message.from_user.id):
        return
    db = load_db()
    homeworks = db.get("homeworks", {})
    all_hw = []
    for uid, hw_list in homeworks.items():
        user_name = db["users"].get(uid, {}).get("name", "Noma'lum")
        for hw in hw_list:
            all_hw.append((user_name, hw))
    if not all_hw:
        bot.send_message(message.chat.id, "📭 Hali uy vazifasi topshirilmagan.", reply_markup=main_menu(message.from_user.id))
        return
    text = f"📥 *Kelgan Uy Vazifalari* ({len(all_hw)} ta):\n\n"
    for i, (name, hw) in enumerate(all_hw, 1):
        text += f"{i}. *{name}*:\n{hw['text']}\n📅 {hw.get('date', '')}\n\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(message.from_user.id))

# ==================== ADMIN: TEST QO'SHISH ====================
@bot.message_handler(func=lambda m: m.text == "📝 Yangi Test qo'shish")
def admin_add_test_start(message):
    if not is_admin(message.from_user.id):
        return
    user_states[message.from_user.id] = "admin_test_title"
    bot.send_message(message.chat.id, "📝 Test nomini kiriting:", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "admin_test_title")
def admin_test_title(message):
    user_id = message.from_user.id
    user_data[user_id] = {"test_title": message.text.strip(), "questions": []}
    user_states[user_id] = "admin_test_question"
    q_num = len(user_data[user_id]["questions"]) + 1
    bot.send_message(message.chat.id, f"✏️ {q_num}-savolni kiriting:")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "admin_test_question")
def admin_test_question(message):
    user_id = message.from_user.id
    user_data[user_id]["questions"].append({"question": message.text.strip(), "options": [], "correct": 0})
    user_states[user_id] = "admin_test_opt1"
    bot.send_message(message.chat.id, "1️⃣ 1-variantni kiriting:")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) in ["admin_test_opt1", "admin_test_opt2", "admin_test_opt3", "admin_test_opt4"])
def admin_test_option(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    opt_num = int(state.replace("admin_test_opt", ""))
    user_data[user_id]["questions"][-1]["options"].append(message.text.strip())
    if opt_num < 4:
        user_states[user_id] = f"admin_test_opt{opt_num + 1}"
        bot.send_message(message.chat.id, f"{opt_num + 1}️⃣ {opt_num + 1}-variantni kiriting:")
    else:
        user_states[user_id] = "admin_test_correct"
        bot.send_message(message.chat.id, "✅ To'g'ri javob raqamini kiriting (1-4):")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "admin_test_correct")
def admin_test_correct(message):
    user_id = message.from_user.id
    try:
        correct = int(message.text)
        if 1 <= correct <= 4:
            user_data[user_id]["questions"][-1]["correct"] = correct - 1
            user_states[user_id] = "admin_test_next"
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("➕ Savol qo'shish", "💾 Testni saqlash")
            bot.send_message(message.chat.id, "Yana savol qo'shasizmi?", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "⚠️ 1 dan 4 gacha raqam kiriting!")
    except:
        bot.send_message(message.chat.id, "⚠️ Faqat raqam kiriting!")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "admin_test_next")
def admin_test_next(message):
    user_id = message.from_user.id
    if message.text == "➕ Savol qo'shish":
        q_num = len(user_data[user_id]["questions"]) + 1
        user_states[user_id] = "admin_test_question"
        bot.send_message(message.chat.id, f"✏️ {q_num}-savolni kiriting:", reply_markup=types.ReplyKeyboardRemove())
    else:
        db = load_db()
        new_test = {
            "title": user_data[user_id]["test_title"],
            "questions": user_data[user_id]["questions"]
        }
        db["tests"].append(new_test)
        save_db(db)
        user_states.pop(user_id, None)
        user_data.pop(user_id, None)
        q_count = len(new_test["questions"])
        bot.send_message(
            message.chat.id,
            f"✅ *{new_test['title']}* testi saqlandi!\n📝 Savollar soni: *{q_count}* ta",
            parse_mode="Markdown",
            reply_markup=main_menu(user_id)
        )

# ==================== O'QUVCHI: TEST YECHISH ====================
@bot.message_handler(func=lambda m: m.text == "📝 Test yechish")
def student_test_start(message):
    db = load_db()
    if not db["tests"]:
        bot.send_message(message.chat.id, "😔 Hozircha testlar mavjud emas.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for t in db["tests"]:
        markup.add(t["title"])
    user_states[message.from_user.id] = "waiting_test_select"
    name = get_name(message.from_user.id)
    bot.send_message(message.chat.id, f"📋 *{name}*, qaysi testni yechmoqchisiz?", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "waiting_test_select")
def student_select_test(message):
    user_id = message.from_user.id
    db = load_db()
    test = next((t for t in db["tests"] if t["title"] == message.text), None)
    if not test:
        bot.send_message(message.chat.id, "⚠️ Test topilmadi, qaytadan tanlang.")
        return
    user_states[user_id] = "taking_test"
    test_states[user_id] = {"test": test, "current_q": 0, "score": 0}
    show_test_question(user_id)

def show_test_question(user_id):
    state = test_states[user_id]
    q_idx = state["current_q"]
    questions = state["test"]["questions"]
    if q_idx >= len(questions):
        finish_test(user_id)
        return
    q = questions[q_idx]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i, opt in enumerate(q["options"]):
        markup.add(f"{i+1}. {opt}")
    bot.send_message(user_id, f"*{q_idx+1}-savol:* {q['question']}", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "taking_test")
def student_answer(message):
    user_id = message.from_user.id
    state = test_states[user_id]
    q_idx = state["current_q"]
    try:
        ans_idx = int(message.text.split(".")[0]) - 1
        correct_idx = state["test"]["questions"][q_idx]["correct"]
        if ans_idx == correct_idx:
            state["score"] += 1
        state["current_q"] += 1
        show_test_question(user_id)
    except:
        bot.send_message(message.chat.id, "⚠️ Variant raqamini bosing (1-4).")

def finish_test(user_id):
    state = test_states.pop(user_id, {})
    user_states.pop(user_id, None)
    score = state.get("score", 0)
    total = len(state["test"]["questions"])
    title = state["test"]["title"]
    db = load_db()
    uid = str(user_id)
    if uid not in db["results"]:
        db["results"][uid] = []
    db["results"][uid].append({"test_title": title, "score": score, "total": total, "date": str(date.today())})
    save_db(db)
    name = get_name(user_id)
    percent = int(score / total * 100) if total > 0 else 0
    emoji = "🏆" if percent >= 80 else "👍" if percent >= 60 else "📚"
    bot.send_message(
        user_id,
        f"{emoji} *{name}*, test yakunlandi!\n\n"
        f"📝 Test: *{title}*\n"
        f"✅ To'g'ri javoblar: *{score} / {total}*\n"
        f"📊 Natija: *{percent}%*",
        parse_mode="Markdown",
        reply_markup=main_menu(user_id)
    )

# ==================== O'QUVCHI: NATIJALAR ====================
@bot.message_handler(func=lambda m: m.text == "📊 Natijalarim")
def show_my_results(message):
    db = load_db()
    uid = str(message.from_user.id)
    name = get_name(message.from_user.id)
    results = db["results"].get(uid, [])
    if not results:
        bot.send_message(message.chat.id, f"*{name}*, siz hali test topshirmagansiz.", parse_mode="Markdown")
        return
    text = f"📊 *{name}*, sizning natijalaringiz:\n\n"
    for i, r in enumerate(results, 1):
        percent = int(r["score"] / r["total"] * 100) if r["total"] > 0 else 0
        text += f"{i}. 📝 {r['test_title']}: *{r['score']}/{r['total']}* ({percent}%)\n"
        if r.get("date"):
            text += f"   📅 {r['date']}\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ==================== O'QUVCHI: DAVOMAT ====================
@bot.message_handler(func=lambda m: m.text == "✅ Keldim")
def student_attendance(message):
    user_id = message.from_user.id
    db = load_db()
    uid = str(user_id)
    today = str(date.today())
    name = get_name(user_id)
    if uid not in db["attendance"]:
        db["attendance"][uid] = []
    if today in db["attendance"][uid]:
        bot.send_message(
            message.chat.id,
            f"⚠️ *{name}*, siz bugun allaqachon davomat qilgansiz!",
            parse_mode="Markdown"
        )
    else:
        db["attendance"][uid].append(today)
        save_db(db)
        bot.send_message(
            message.chat.id,
            f"✅ *{name}*, bugungi davomatingiz qabul qilindi!\n📅 Sana: {today}",
            parse_mode="Markdown"
        )

# ==================== O'QUVCHI: UY VAZIFA ====================
@bot.message_handler(func=lambda m: m.text == "📚 Uy vazifa topshirish")
def student_homework_start(message):
    user_id = message.from_user.id
    name = get_name(user_id)
    user_states[user_id] = "waiting_homework"
    bot.send_message(
        message.chat.id,
        f"📚 *{name}*, uy vazifangizni yozing:",
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "waiting_homework")
def student_homework_submit(message):
    user_id = message.from_user.id
    db = load_db()
    uid = str(user_id)
    name = get_name(user_id)
    today = str(date.today())
    if uid not in db["homeworks"]:
        db["homeworks"][uid] = []
    db["homeworks"][uid].append({"text": message.text, "date": today})
    save_db(db)
    user_states.pop(user_id, None)
    bot.send_message(
        message.chat.id,
        f"✅ *{name}*, uy vazifangiz muvaffaqiyatli topshirildi!\n📅 Sana: {today}",
        parse_mode="Markdown",
        reply_markup=main_menu(user_id)
    )

# ==================== SO'Z O'RGANISH: BOSHLASH ====================
@bot.message_handler(func=lambda m: m.text == "📖 So'z o'rganish")
def vocab_start(message):
    user_id = message.from_user.id
    name = get_name(user_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for book in VOCABULARY.keys():
        markup.add(book)
    markup.add("🏠 Asosiy menyu")
    user_states[user_id] = "vocab_choose_book"
    bot.send_message(
        message.chat.id,
        f"📚 *{name}*, qaysi kitobdan o'rganmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== SO'Z O'RGANISH: KITOB TANLASH ====================
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "vocab_choose_book")
def vocab_choose_book(message):
    user_id = message.from_user.id
    if message.text == "🏠 Asosiy menyu":
        user_states.pop(user_id, None)
        bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu(user_id))
        return
    if message.text not in VOCABULARY:
        bot.send_message(message.chat.id, "⚠️ Iltimos, kitobni tanlang!")
        return
    vocab_states[user_id] = {"book": message.text}
    user_states[user_id] = "vocab_choose_unit"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for unit in VOCABULARY[message.text].keys():
        markup.add(unit)
    markup.add("⬅️ Orqaga")
    bot.send_message(
        message.chat.id,
        f"📖 *{message.text}* — qaysi unitni o'rganmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== SO'Z O'RGANISH: UNIT TANLASH ====================
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "vocab_choose_unit")
def vocab_choose_unit(message):
    user_id = message.from_user.id
    if message.text == "⬅️ Orqaga":
        user_states[user_id] = "vocab_choose_book"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for book in VOCABULARY.keys():
            markup.add(book)
        markup.add("🏠 Asosiy menyu")
        bot.send_message(message.chat.id, "📚 Kitobni tanlang:", reply_markup=markup)
        return
    book = vocab_states[user_id]["book"]
    if message.text not in VOCABULARY[book]:
        bot.send_message(message.chat.id, "⚠️ Iltimos, unitni tanlang!")
        return
    words = VOCABULARY[book][message.text]
    vocab_states[user_id].update({
        "unit": message.text,
        "words": words,
        "index": 0
    })
    user_states[user_id] = "vocab_learning"
    show_vocab_word(user_id, message.chat.id)

# ==================== SO'Z O'RGANISH: SO'Z KO'RSATISH ====================
def show_vocab_word(user_id, chat_id):
    state = vocab_states[user_id]
    words = state["words"]
    idx = state["index"]
    total = len(words)

    if idx >= total:
        # Barcha so'zlar tugadi
        book = state["book"]
        unit = state["unit"]
        db = load_db()
        uid = str(user_id)
        if "vocab_progress" not in db:
            db["vocab_progress"] = {}
        if uid not in db["vocab_progress"]:
            db["vocab_progress"][uid] = {}
        key = f"{book}|{unit}"
        db["vocab_progress"][uid][key] = True
        save_db(db)
        name = get_name(user_id)
        user_states.pop(user_id, None)
        vocab_states.pop(user_id, None)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📖 So'z o'rganish", "🏠 Asosiy menyu")
        bot.send_message(
            chat_id,
            f"🎉 *{name}*, *{unit}* unitidagi barcha so'zlarni tugatdingiz!\n\n"
            f"✅ Jami: *{total}* ta so'z o'rgandingiz!\n\n"
            f"Boshqa unit tanlaysizmi?",
            parse_mode="Markdown",
            reply_markup=markup
        )
        return

    eng, uzb = words[idx]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ Yodladim", "🔄 Qayta ko'raman")
    markup.add("⏭ O'tkazib yuborish", "❌ Chiqish")

    bot.send_message(
        chat_id,
        f"📖 *{state['book']}* — *{state['unit']}*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📝 So'z: *{eng}*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📊 {idx + 1} / {total}",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== SO'Z O'RGANISH: JAVOB QAYTA ISHLASH ====================
@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "vocab_learning")
def vocab_answer(message):
    user_id = message.from_user.id
    state = vocab_states.get(user_id)
    if not state:
        return

    if message.text == "❌ Chiqish":
        user_states.pop(user_id, None)
        vocab_states.pop(user_id, None)
        bot.send_message(message.chat.id, "Asosiy menyu:", reply_markup=main_menu(user_id))
        return

    words = state["words"]
    idx = state["index"]
    eng, uzb = words[idx]

    if message.text == "✅ Yodladim":
        bot.send_message(
            message.chat.id,
            f"✅ *{eng}* = *{uzb}*\n\nBravo! Keyingi so'z 👇",
            parse_mode="Markdown"
        )
        state["index"] += 1
        show_vocab_word(user_id, message.chat.id)

    elif message.text == "🔄 Qayta ko'raman":
        bot.send_message(
            message.chat.id,
            f"🔄 *{eng}* = *{uzb}*\n\nEslab qoling! Keyingi so'z keladi 👇",
            parse_mode="Markdown"
        )
        # So'zni oxiriga surish
        state["words"].append(state["words"].pop(idx))
        show_vocab_word(user_id, message.chat.id)

    elif message.text == "⏭ O'tkazib yuborish":
        state["index"] += 1
        show_vocab_word(user_id, message.chat.id)

# ==================== 🏠 ASOSIY MENYU TUGMASI ====================
@bot.message_handler(func=lambda m: m.text == "🏠 Asosiy menyu")
def go_main_menu(message):
    user_id = message.from_user.id
    user_states.pop(user_id, None)
    vocab_states.pop(user_id, None)
    bot.send_message(message.chat.id, "🏠 Asosiy menyu:", reply_markup=main_menu(user_id))

# ==================== PROFIL ====================
@bot.message_handler(func=lambda m: m.text == "ℹ️ Profil")
def show_profile(message):
    db = load_db()
    uid = str(message.from_user.id)
    if uid not in db["users"]:
        bot.send_message(message.chat.id, "⚠️ Avval /start orqali ro'yxatdan o'ting.")
        return
    u = db["users"][uid]
    role_text = "Admin" if u.get("role") == "admin" else "O'quvchi"
    attendance_count = len(db.get("attendance", {}).get(uid, []))
    results_count = len(db.get("results", {}).get(uid, []))

    # O'rganilgan unitlar soni
    vocab_done = len(db.get("vocab_progress", {}).get(uid, {}))

    bot.send_message(
        message.chat.id,
        f"👤 *Profilingiz:*\n\n"
        f"📝 Ism: {u['name']}\n"
        f"📊 Level: {u['level']}\n"
        f"📞 Tel: {u['phone']}\n"
        f"🎖 Role: {role_text}\n\n"
        f"✅ Davomat: {attendance_count} kun\n"
        f"📝 Topshirilgan testlar: {results_count} ta\n"
        f"📖 Tugatilgan unitlar: {vocab_done} ta",
        parse_mode="Markdown"
    )

# ==================== O'QUVCHI: TO'LOV QILDIM ====================
@bot.message_handler(func=lambda m: m.text == "💳 To'lov qildim")
def student_payment(message):
    user_id = message.from_user.id
    name = get_name(user_id)
    db = load_db()
    uid = str(user_id)

    # Kelgan kunlar sonini hisoblash
    attendance_days = len(db.get("attendance", {}).get(uid, []))
    total_debt = attendance_days * DAILY_PRICE

    # To'langan summa
    paid_total = sum(
        p["amount"] for p in db.get("payments", {}).get(uid, [])
        if p.get("status") == "confirmed"
    )
    remaining = max(0, total_debt - paid_total)

    user_states[user_id] = "waiting_payment_amount"
    bot.send_message(
        message.chat.id,
        f"💳 *{name}*, to'lov ma'lumotlari:\n\n"
        f"📅 Kelgan kunlar: *{attendance_days}* kun\n"
        f"💰 Kunlik narx: *{DAILY_PRICE:,}* so'm\n"
        f"📊 Jami to'lov: *{total_debt:,}* so'm\n"
        f"✅ To'langan: *{paid_total:,}* so'm\n"
        f"❗ Qoldiq: *{remaining:,}* so'm\n\n"
        f"Qancha pul to'laganingizni kiriting (so'mda):",
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "waiting_payment_amount")
def payment_amount_received(message):
    user_id = message.from_user.id
    name = get_name(user_id)
    try:
        amount = int(message.text.replace(" ", "").replace(",", ""))
        if amount <= 0:
            raise ValueError
    except:
        bot.send_message(message.chat.id, "⚠️ Iltimos, faqat raqam kiriting (masalan: 75000)")
        return

    db = load_db()
    uid = str(user_id)
    today = str(date.today())

    if "payments" not in db:
        db["payments"] = {}
    if uid not in db["payments"]:
        db["payments"][uid] = []

    payment_id = f"{uid}_{today}_{len(db['payments'][uid])}"
    db["payments"][uid].append({
        "id": payment_id,
        "amount": amount,
        "date": today,
        "status": "pending"
    })
    save_db(db)

    user_states.pop(user_id, None)

    # Adminlarga xabar yuborish
    for admin_id in ADMIN_IDS:
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"pay_confirm_{uid}_{payment_id}"),
                types.InlineKeyboardButton("❌ Rad etish", callback_data=f"pay_reject_{uid}_{payment_id}")
            )
            bot.send_message(
                admin_id,
                f"💳 *Yangi to'lov so'rovi!*\n\n"
                f"👤 O'quvchi: *{name}*\n"
                f"💰 Summa: *{amount:,}* so'm\n"
                f"📅 Sana: {today}\n\n"
                f"Tasdiqlaysizmi?",
                parse_mode="Markdown",
                reply_markup=markup
            )
        except:
            pass

    bot.send_message(
        message.chat.id,
        f"✅ *{name}*, to'lov so'rovingiz adminga yuborildi!\n\n"
        f"💰 Summa: *{amount:,}* so'm\n"
        f"⏳ Admin tasdiqlashini kuting...",
        parse_mode="Markdown",
        reply_markup=main_menu(user_id)
    )

# ==================== ADMIN: TO'LOV TASDIQLASH (CALLBACK) ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def payment_callback(call):
    parts = call.data.split("_")
    action = parts[1]       # confirm yoki reject
    uid = parts[2]          # user id
    payment_id = "_".join(parts[3:])

    db = load_db()
    user_payments = db.get("payments", {}).get(uid, [])
    payment = next((p for p in user_payments if p["id"] == payment_id), None)

    if not payment:
        bot.answer_callback_query(call.id, "To'lov topilmadi!")
        return

    if payment["status"] != "pending":
        bot.answer_callback_query(call.id, "Bu to'lov allaqachon ko'rib chiqilgan!")
        return

    name = db["users"].get(uid, {}).get("name", "Noma'lum")
    amount = payment["amount"]

    if action == "confirm":
        payment["status"] = "confirmed"
        save_db(db)

        # To'langan va qoldiq hisoblash
        attendance_days = len(db.get("attendance", {}).get(uid, []))
        total_debt = attendance_days * DAILY_PRICE
        paid_total = sum(p["amount"] for p in db["payments"].get(uid, []) if p.get("status") == "confirmed")
        remaining = max(0, total_debt - paid_total)

        bot.edit_message_text(
            f"✅ *To'lov tasdiqlandi!*\n\n"
            f"👤 O'quvchi: *{name}*\n"
            f"💰 Summa: *{amount:,}* so'm\n"
            f"📅 Sana: {payment['date']}",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        try:
            bot.send_message(
                int(uid),
                f"✅ *To'lovingiz tasdiqlandi!*\n\n"
                f"💰 Tasdiqlangan summa: *{amount:,}* so'm\n"
                f"📊 Umumiy to'lov: *{paid_total:,}* so'm\n"
                f"❗ Qoldiq qarz: *{remaining:,}* so'm",
                parse_mode="Markdown"
            )
        except:
            pass

    elif action == "reject":
        payment["status"] = "rejected"
        save_db(db)
        bot.edit_message_text(
            f"❌ *To'lov rad etildi!*\n\n"
            f"👤 O'quvchi: *{name}*\n"
            f"💰 Summa: *{amount:,}* so'm",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
        try:
            bot.send_message(
                int(uid),
                f"❌ *To'lovingiz rad etildi!*\n\n"
                f"💰 Summa: *{amount:,}* so'm\n\n"
                f"Iltimos, admin bilan bog'laning.",
                parse_mode="Markdown"
            )
        except:
            pass

    bot.answer_callback_query(call.id)

# ==================== ADMIN: TO'LOVLAR RO'YXATI ====================
@bot.message_handler(func=lambda m: m.text == "💰 To'lovlar")
def admin_payments(message):
    if not is_admin(message.from_user.id):
        return
    db = load_db()
    payments = db.get("payments", {})

    text = "💰 *Barcha to'lovlar:*\n\n"
    total_confirmed = 0
    total_pending = 0
    has_any = False

    for uid, pay_list in payments.items():
        user_name = db["users"].get(uid, {}).get("name", "Noma'lum")
        attendance_days = len(db.get("attendance", {}).get(uid, []))
        total_debt = attendance_days * DAILY_PRICE
        paid = sum(p["amount"] for p in pay_list if p.get("status") == "confirmed")
        pending = sum(p["amount"] for p in pay_list if p.get("status") == "pending")
        remaining = max(0, total_debt - paid)

        if pay_list:
            has_any = True
            text += (
                f"👤 *{user_name}*\n"
                f"   📅 {attendance_days} kun | Jami: {total_debt:,} so'm\n"
                f"   ✅ To'langan: {paid:,} so'm\n"
                f"   ⏳ Kutilmoqda: {pending:,} so'm\n"
                f"   ❗ Qoldiq: {remaining:,} so'm\n\n"
            )
            total_confirmed += paid
            total_pending += pending

    if not has_any:
        bot.send_message(message.chat.id, "💭 Hali hech qanday to'lov yo'q.", reply_markup=main_menu(message.from_user.id))
        return

    text += f"━━━━━━━━━━━━━━━━\n"
    text += f"✅ Jami tasdiqlangan: *{total_confirmed:,}* so'm\n"
    text += f"⏳ Jami kutilmoqda: *{total_pending:,}* so'm"

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu(message.from_user.id))

# ==================== ADMIN: HAMMAGA XABAR ====================
@bot.message_handler(func=lambda m: m.text == "📣 Hammaga xabar yuborish")
def broadcast_start(message):
    if not is_admin(message.from_user.id):
        return
    user_states[message.from_user.id] = "waiting_broadcast"
    bot.send_message(
        message.chat.id,
        "📣 *Yubormoqchi bo'lgan xabaringizni kiriting:*\n\n"
        "(Barcha o'quvchilarga yuboriladi)",
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "waiting_broadcast")
def broadcast_send(message):
    admin_id = message.from_user.id
    if not is_admin(admin_id):
        return
    user_states.pop(admin_id, None)
    db = load_db()
    students = [(uid, u) for uid, u in db["users"].items() if u.get("role") == "student"]

    sent = 0
    failed = 0
    for uid, u in students:
        try:
            bot.send_message(
                int(uid),
                f"📣 *Admin xabari:*\n\n{message.text}",
                parse_mode="Markdown"
            )
            sent += 1
        except:
            failed += 1

    bot.send_message(
        message.chat.id,
        f"✅ Xabar yuborildi!\n\n"
        f"📨 Yuborildi: *{sent}* ta\n"
        f"❌ Yuborilmadi: *{failed}* ta",
        parse_mode="Markdown",
        reply_markup=main_menu(admin_id)
    )

# ==================== MAIN ====================
if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    bot.infinity_polling()