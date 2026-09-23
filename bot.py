import json
import os
import threading
from flask import Flask
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# --- سيرفر الويب الأساسي لضمان بقاء البورت مفتوحاً على رندر ---
app = Flask("")


@app.route("/")
def home():
  return "Uni Helper Bot is alive and running!"


ADMIN_PASSWORD = "15309"
DATA_FILE = "znu_dental_data.json"


def load_data():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "sections" not in data or "custom_buttons" not in data:
          return {
              "sections": {
                  "محاضرات": {"title": "المحاضرات", "lectures": {}},
                  "كتب": {"title": "الكتب", "items": []},
              },
              "custom_buttons": {},
          }
        return data
    except:
      pass

  return {
      "sections": {
          "محاضرات": {"title": "المحاضرات", "lectures": {}},
          "كتب": {"title": "الكتب", "items": []},
      },
      "custom_buttons": {},
  }


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# لوحة التحكم الرئيسية
def get_main_reply_keyboard():
  data = load_data()
  custom_buttons = data.get("custom_buttons", {})

  keyboard = [
      [KeyboardButton("📚 المحاضرات"), KeyboardButton("📚 كتب طب الأسنان")],
      [KeyboardButton("➕ ضيف محاضرة"), KeyboardButton("➕ ضيف كتاب")],
      [KeyboardButton("🗑️ امسح محاضرة"), KeyboardButton("🗑️ امسح كتاب")],
      [KeyboardButton("❌ خروج")],
  ]

  for btn_name in custom_buttons.keys():
    keyboard.insert(0, [KeyboardButton(btn_name)])

  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# لوحة الأسابيع للمحاضرات
def get_weeks_reply_keyboard():
  data = load_data()
  lectures_dict = data["sections"]["محاضرات"].get("lectures", {})

  keyboard = []
  for week_name in lectures_dict.keys():
    keyboard.append([KeyboardButton(f"📅 {week_name}")])

  keyboard.append([KeyboardButton("🔙 رجوع للقائمة الرئيسية")])
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# لوحة الأيام للمحاضرات
def get_days_reply_keyboard(week_name):
  data = load_data()
  days_dict = (
      data["sections"]["محاضرات"].get("lectures", {}).get(week_name, {})
  )

  keyboard = []
  for day_name in days_dict.keys():
    keyboard.append([KeyboardButton(f"🗓️ يوم {day_name} ({week_name})")])

  keyboard.append([KeyboardButton("🔙 رجوع للأسابيع")])
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# لوحة قائمة الكتب في الأزرار السفلية
def get_books_reply_keyboard():
  data = load_data()
  books_list = data["sections"]["كتب"].get("items", [])

  keyboard = []
  for book in books_list:
    book_name = book.get("name", "كتاب بدون اسم")
    keyboard.append([KeyboardButton(f"📖 {book_name}")])

  keyboard.append([KeyboardButton("🔙 رجوع للقائمة الرئيسية")])
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data.clear()
  text_msg = (
      "منور يا دكتور في بوت **Uni Helper** لطب أسنان جامعة الزقازيق الأهلية"
      " (ZNU) 🦷🎓\n\nاختر من الأزرار بالأسفل:"
  )
  await update.message.reply_text(
      text_msg, reply_markup=get_main_reply_keyboard(), parse_mode="Markdown"
  )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_data = context.user_data
  text = update.message.text.strip() if update.message.text else ""
  data = load_data()

  if text in ["❌ خروج", "🔙 رجوع للقائمة الرئيسية"]:
    user_data.clear()
    await update.message.reply_text(
        "تم يا باشا، دي القائمة الرئيسية:",
        reply_markup=get_main_reply_keyboard(),
    )
    return

  if text == "🔙 رجوع للأسابيع":
    await update.message.reply_text(
        "📂 دي قائمة الأسابيع تاني:", reply_markup=get_weeks_reply_keyboard()
    )
    return

  # 1. قسم المحاضرات
  if text == "📚 المحاضرات":
    user_data.clear()
    lectures_dict = data["sections"]["محاضرات"].get("lectures", {})
    if not lectures_dict:
      await update.message.reply_text(
          "لسه مفيش أي أسابيع مسجلة يا دكتور.",
          reply_markup=get_main_reply_keyboard(),
      )
      return
    await update.message.reply_text(
        "📂 اتفضل يا دكتور، دي قائمة الأسابيع 👇",
        reply_markup=get_weeks_reply_keyboard(),
    )
    return

  if text.startswith("📅 "):
    week_name = text.replace("📅 ", "").strip()
    days_dict = (
        data["sections"]["محاضرات"]
        .get("lectures", {})
        .get(week_name, {})
    )
    if not days_dict:
      await update.message.reply_text(
          f"مفيش أيام محطوطة في ({week_name}) لسه.",
          reply_markup=get_weeks_reply_keyboard(),
      )
      return
    await update.message.reply_text(
        f"📂 **{week_name}**\nاختر اليوم 👇",
        reply_markup=get_days_reply_keyboard(week_name),
        parse_mode="Markdown",
    )
    return

  if text.startswith("🗓️ يوم "):
    try:
      parts = text.replace("🗓️ يوم ", "").split(" (")
      day_name = parts[0].strip()
      week_name = parts[1].replace(")", "").strip()
    except:
      return

    lectures_in_day = (
        data["sections"]["محاضرات"]
        .get("lectures", {})
        .get(week_name, {})
        .get(day_name, [])
    )
    if not lectures_in_day:
      await update.message.reply_text(
          f"مفيش محاضرات مسجلة في يوم ({day_name}).",
          reply_markup=get_days_reply_keyboard(week_name),
      )
      return

    await update.message.reply_text(
        f"📂 {week_name} ⬅️ 🗓️ يوم {day_name}\n------------------",
    )
    for item in lectures_in_day:
      name = item.get("name")
      files = item.get("files", [])
      await update.message.reply_text(f"🎧 محاضرة: {name}")
      for f in files:
        f_id = f.get("file_id")
        f_type = f.get("file_type")
        if f_type == "audio":
          await context.bot.send_audio(chat_id=update.message.chat_id, audio=f_id)
        elif f_type == "voice":
          await context.bot.send_voice(chat_id=update.message.chat_id, voice=f_id)
        elif f_type == "document":
          await context.bot.send_document(
              chat_id=update.message.chat_id, document=f_id
          )
    return

  # 2. قسم الكتب التفاعلي
  if text == "📚 كتب طب الأسنان":
    user_data.clear()
    books_list = data["sections"]["كتب"].get("items", [])
    if not books_list:
      await update.message.reply_text(
          "لسه مفيش كتب مضافة يا دكتور.", reply_markup=get_main_reply_keyboard()
      )
      return
    await update.message.reply_text(
        "📚 اتفضل يا دكتور، دي قائمة الكتب المتاحة ظهرت في الأزرار بالأسفل 👇",
        reply_markup=get_books_reply_keyboard(),
    )
    return

  if text.startswith("📖 "):
    book_title = text.replace("📖 ", "").strip()
    books_list = data["sections"]["كتب"].get("items", [])
    target_book = None
    for b in books_list:
      if b.get("name") == book_title:
        target_book = b
        break

    if target_book:
      await update.message.reply_text(f"📖 كتاب: **{book_title}**")
      f_id = target_book.get("file_id")
      f_type = target_book.get("file_type", "document")
      if f_type == "audio":
        await context.bot.send_audio(chat_id=update.message.chat_id, audio=f_id)
      elif f_type == "voice":
        await context.bot.send_voice(chat_id=update.message.chat_id, voice=f_id)
      else:
        await context.bot.send_document(
            chat_id=update.message.chat_id, document=f_id
        )
    else:
      await update.message.reply_text("⚠️ عذراً، لم يتم العثور على هذا الكتاب.")
    return

  # 3. الأوامر والإدارة
  if text in ["➕ ضيف محاضرة", "اضافه محاضرة"] or text == "/addlecture":
    user_data.clear()
    user_data["state"] = "AUTH_PASSWORD"
    await update.message.reply_text(
        "🔒 [إضافة محاضرة]\nهات باسورد المسؤول الأول:"
    )
    return

  if text == "➕ ضيف كتاب":
    user_data.clear()
    user_data["state"] = "AUTH_BOOK_PASSWORD"
    await update.message.reply_text("🔒 [إضافة كتاب جديد]\nهات باسورد المسؤول الأول:")
    return

  if text in ["🗑️ امسح محاضرة", "/delete"]:
    user_data.clear()
    user_data["state"] = "AUTH_DELETE"
    await update.message.reply_text("🔒 [حذف محاضرة]\nهات باسورد المسؤول الأول:")
    return

  if text == "🗑️ امسح كتاب":
    user_data.clear()
    user_data["state"] = "AUTH_DELETE_BOOK"
    await update.message.reply_text("🔒 [حذف كتاب]\nهات باسورد المسؤول الأول:")
    return

  current_state = user_data.get("state")

  if current_state in [
      "AUTH_PASSWORD",
      "AUTH_BOOK_PASSWORD",
      "AUTH_DELETE",
      "AUTH_DELETE_BOOK",
  ]:
    if text == ADMIN_PASSWORD:
      if current_state == "AUTH_PASSWORD":
        user_data["state"] = "WAITING_WEEK_NAME"
        await update.message.reply_text(
            "تمام ✅. اكتب اسم الأسبوع (مثال: الاسبوع الاول):"
        )
      elif current_state == "AUTH_BOOK_PASSWORD":
        user_data["state"] = "WAITING_BOOK_NAME"
        await update.message.reply_text(
            "تمام ✅. اكتب اسم الكتاب الجديد الذي تريد إضافته:"
        )
      elif current_state == "AUTH_DELETE":
        user_data["state"] = "WAITING_DELETE_WEEK"
        weeks = list(data["sections"]["محاضرات"].get("lectures", {}).keys())
        msg = "تمام ✅. اكتب اسم الأسبوع الذي تريد حذف يوم منه:"
        if weeks:
          msg += f"\nالأسابيع المتاحة: {', '.join(weeks)}"
        await update.message.reply_text(msg)
      elif current_state == "AUTH_DELETE_BOOK":
        user_data["state"] = "WAITING_DELETE_BOOK_NAME"
        books_list = data["sections"]["كتب"].get("items", [])
        book_names = [b.get("name") for b in books_list]
        msg = "تمام ✅. اكتب اسم الكتاب الذي تريد مسحه:"
        if book_names:
          msg += f"\nالكتب المتاحة: {', '.join(book_names)}"
        await update.message.reply_text(msg)
    else:
      user_data.clear()
      await update.message.reply_text(
          "❌ الباسورد غلط.", reply_markup=get_main_reply_keyboard()
      )
    return

  # دورة إضافة كتاب جديد
  if current_state == "WAITING_BOOK_NAME":
    if not text:
      await update.message.reply_text("من فضلك اكتب اسم الكتاب بشكل صحيح.")
      return
    user_data["temp_book_name"] = text
    user_data["state"] = "WAITING_BOOK_FILE"
    await update.message.reply_text(
        f"سجلنا اسم الكتاب: ({text}) 📖\nالآن ابعت **ملف الكتاب** (بي دي إف أو"
        " مستند أو صوتي):",
        reply_markup=get_main_reply_keyboard(),
    )
    return

  if current_state == "WAITING_BOOK_FILE":
    file_id = None
    file_type = None

    if update.message.audio:
      file_id = update.message.audio.file_id
      file_type = "audio"
    elif update.message.voice:
      file_id = update.message.voice.file_id
      file_type = "voice"
    elif update.message.document:
      file_id = update.message.document.file_id
      file_type = "document"

    if file_id:
      book_name = user_data.get("temp_book_name")
      if "items" not in data["sections"]["كتب"]:
        data["sections"]["كتب"]["items"] = []

      data["sections"]["كتب"]["items"].append(
          {"name": book_name, "file_id": file_id, "file_type": file_type}
      )
      save_data(data)
      user_data.clear()

      await update.message.reply_text(
          f"📚 تم حفظ الكتاب ({book_name}) بنجاح!\nاضغط الآن على زر **📚 كتب طب"
          " الأسنان** لتجد كتابك ظهر في القائمة بالأسفل 🚀",
          reply_markup=get_main_reply_keyboard(),
      )
      return
    else:
      await update.message.reply_text(
          "⚠️ من فضلك ابعت ملف الكتاب (مستند أو ملف صوتي) لكي نتمكن من حفظه."
      )
      return

  # دورة مسح كتاب
  if current_state == "WAITING_DELETE_BOOK_NAME":
    target_book_name = text
    books_list = data["sections"]["كتب"].get("items", [])
    updated_books = [b for b in books_list if b.get("name") != target_book_name]

    if len(updated_books) < len(books_list):
      data["sections"]["كتب"]["items"] = updated_books
      save_data(data)
      user_data.clear()
      await update.message.reply_text(
          f"🗑️ تم حذف الكتاب ({target_book_name}) بنجاح!",
          reply_markup=get_main_reply_keyboard(),
      )
    else:
      user_data.clear()
      await update.message.reply_text(
          f"⚠️ لم يتم العثور على كتاب بهذا الاسم ({target_book_name}).",
          reply_markup=get_main_reply_keyboard(),
      )
    return

  if current_state == "WAITING_DELETE_WEEK":
    target_week = text
    lectures_sec = data["sections"]["محاضرات"].get("lectures", {})
    if target_week in lectures_sec:
      user_data["delete_week_target"] = target_week
      user_data["state"] = "WAITING_DELETE_DAY"
      days = list(lectures_sec[target_week].keys())
      await update.message.reply_text(
          f"الأيام المتاحة في ({target_week}):"
          f" [{', '.join(days) if days else 'لا توجد'}]. اكتب اسم اليوم المراد"
          " حذفه:"
      )
    else:
      user_data.clear()
      await update.message.reply_text(
          "⚠️ الأسبوع غير موجود.", reply_markup=get_main_reply_keyboard()
      )
    return

  if current_state == "WAITING_DELETE_DAY":
    target_day = text
    target_week = user_data.get("delete_week_target")
    lectures_sec = data["sections"]["محاضرات"].get("lectures", {})
    if target_week in lectures_sec and target_day in lectures_sec[target_week]:
      del lectures_sec[target_week][target_day]
      save_data(data)
      user_data.clear()
      await update.message.reply_text(
          f"🗑️ تم حذف يوم ({target_day}) بنجاح!",
          reply_markup=get_main_reply_keyboard(),
      )
    else:
      user_data.clear()
      await update.message.reply_text(
          "⚠️ اليوم غير موجود.", reply_markup=get_main_reply_keyboard()
      )
    return

  if current_state == "WAITING_WEEK_NAME":
    if not text:
      await update.message.reply_text("من فضلك اكتب اسم الأسبوع بشكل صحيح.")
      return
    user_data["temp_week_name"] = text
    user_data["state"] = "WAITING_DAY_CHOICE"
    keyboard = [
        [
            KeyboardButton("الثلاثاء"),
            KeyboardButton("الأربعاء"),
            KeyboardButton("الخميس"),
        ],
        [KeyboardButton("🔙 إلغاء")],
    ]
    await update.message.reply_text(
        f"سجلنا الأسبوع: ({text}). اختر اليوم من الأزرار بالأسفل:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return

  if current_state == "WAITING_DAY_CHOICE":
    if text == "🔙 إلغاء":
      user_data.clear()
      await update.message.reply_text(
          "تم الإلغاء.", reply_markup=get_main_reply_keyboard()
      )
      return
    if text not in ["الثلاثاء", "الأربعاء", "الخميس"]:
      await update.message.reply_text(
          "⚠️ من فضلك اختر اليوم من الأزرار الموجودة بالأسفل."
      )
      return
    user_data["temp_day_name"] = text
    user_data["temp_files"] = []
    user_data["temp_caption"] = None
    user_data["state"] = "WAITING_FILES"
    await update.message.reply_text(
        f"اخترت يوم: {text} 🗓️\nابعت الملفات أو الفويس (تقدر تبعت أكتر من ملف"
        " مع بعض دفعة واحدة، وبعد ما تخلص ابعت اسم المحاضرة في رسالة):",
        reply_markup=get_main_reply_keyboard(),
    )
    return

  if current_state == "WAITING_FILES":
    file_id = None
    file_type = None

    if update.message.audio:
      file_id = update.message.audio.file_id
      file_type = "audio"
    elif update.message.voice:
      file_id = update.message.voice.file_id
      file_type = "voice"
    elif update.message.document:
      file_id = update.message.document.file_id
      file_type = "document"

    if file_id:
      user_data["temp_files"].append(
          {"file_id": file_id, "file_type": file_type}
      )
      if update.message.caption:
        user_data["temp_caption"] = update.message.caption.strip()

      await update.message.reply_text(
          f"📥 تم استلام الملف (إجمالي الملفات: {len(user_data['temp_files'])})."
          " ابعت تاني لو حابب، ولو خلصت ابعت اسم المحاضرة في رسالة:"
      )
      return
    else:
      lecture_name = text if text else user_data.get("temp_caption")
      if not lecture_name:
        if user_data.get("temp_files"):
          lecture_name = "محاضرة بدون اسم"
        else:
          await update.message.reply_text(
              "⚠️ أنت لم ترسل أي ملفات! ابعت الملفات الصوتية أولاً."
          )
          return

      week_name = user_data.get("temp_week_name")
      day_name = user_data.get("temp_day_name")
      files_list = user_data.get("temp_files")
      lectures_dict = data["sections"]["محاضرات"]["lectures"]

      if week_name not in lectures_dict:
        lectures_dict[week_name] = {}
      if day_name not in lectures_dict[week_name]:
        lectures_dict[week_name][day_name] = []

      lectures_dict[week_name][day_name].append(
          {"name": lecture_name, "files": files_list}
      )
      save_data(data)
      user_data.clear()

      await update.message.reply_text(
          f"🚀 تم حفظ المحاضرة ({lecture_name}) بعدد ({len(files_list)}) ملف"
          " بنجاح تام!",
          reply_markup=get_main_reply_keyboard(),
      )
      return


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 8080))
  web_thread = threading.Thread(
      target=lambda: app.run(host="0.0.0.0", port=port)
  )
  web_thread.daemon = True
  web_thread.start()

  TOKEN = "8964990492:AAFy3kskRFG46huYcmCcUthpPdF4Tx_tvJw"
  app_bot = ApplicationBuilder().token(TOKEN).build()
  app_bot.add_handler(CommandHandler("start", start))
  app_bot.add_handler(
      MessageHandler(filters.ALL & ~filters.COMMAND, handle_message)
  )

  app_bot.run_polling()
