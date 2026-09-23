import json
import os
import threading
from flask import Flask
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# --- سيرفر الويب الأساسي عشان رندر يفتح البورت وما يديش خطأ Time Out ---
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


# لوحة التحكم الرئيسية بالعامية المصرية
def get_main_reply_keyboard():
  data = load_data()
  custom_buttons = data.get("custom_buttons", {})

  keyboard = [
      [KeyboardButton("📚 المحاضرات"), KeyboardButton("📚 كتب طب الأسنان")],
      [KeyboardButton("➕ ضيف محاضرة"), KeyboardButton("➕ ضيف قسم جديد")],
      [KeyboardButton("🗑️ امسح محاضرة"), KeyboardButton("❌ خروج")],
  ]

  for btn_name in custom_buttons.keys():
    keyboard.insert(0, [KeyboardButton(btn_name)])

  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# لوحة الأسابيع في الأزرار السفلية
def get_weeks_reply_keyboard():
  data = load_data()
  lectures_dict = data["sections"]["محاضرات"].get("lectures", {})

  keyboard = []
  for week_name in lectures_dict.keys():
    keyboard.append([KeyboardButton(f"📅 {week_name}")])

  keyboard.append([KeyboardButton("🔙 رجوع للقائمة الرئيسية")])
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# لوحة الأيام الخاصة بأسبوع معين في الأزرار السفلية
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data.clear()

  text_msg = (
      "منور يا دكتور في بوت **Uni Helper** لطب أسنان جامعة الزقازيق الأهلية"
      " (ZNU) 🦷🎓\n\nاضغط على **📚 المحاضرات** من الأزرار تحت عشان تختار الأسبوع"
      " واليوم براحتك:"
  )
  await update.message.reply_text(
      text_msg, reply_markup=get_main_reply_keyboard(), parse_mode="Markdown"
  )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_data = context.user_data
  text = update.message.text.strip() if update.message.text else ""
  data = load_data()

  if text == "❌ خروج" or text == "🔙 رجوع للقائمة الرئيسية":
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

  # 1. قائمة المحاضرات (تظهر الأسابيع في الأزرار السفلية)
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
        "📂 اتفضل يا دكتور، دي قائمة الأسابيع ظهرت عندك في الأزرار اللي تحت 👇",
        reply_markup=get_weeks_reply_keyboard(),
    )
    return

  # 2. عند الضغط على أسبوع معين من تحت، نظهر الأيام في الأزرار السفلية
  if text.startswith("📅 "):
    week_name = text.replace("📅 ", "").strip()
    days_dict = (
        data["sections"]["محاضرات"]
        .get("lectures", {})
        .get(week_name, {})
    )

    if not days_dict:
      await update.message.reply_text(
          f"مفيش أيام أو محاضرات محطوطة في ({week_name}) لسه.",
          reply_markup=get_weeks_reply_keyboard(),
      )
      return

    await update.message.reply_text(
        f"📂 **{week_name}**\nاختر اليوم من الأزرار اللي تحت عشان تشوف"
        " محاضراته 👇",
        reply_markup=get_days_reply_keyboard(week_name),
        parse_mode="Markdown",
    )
    return

  # 3. عند الضغط على اليوم من الأزرار السفلية
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
          f"مفيش محاضرات مسجلة في يوم ({day_name}) لأسبوع ({week_name}).",
          reply_markup=get_days_reply_keyboard(week_name),
      )
      return

    await update.message.reply_text(
        f"📂 **{week_name}** ⬅️ 🗓️ **يوم {day_name}**\n------------------",
        parse_mode="Markdown",
    )

    for item in lectures_in_day:
      name = item.get("name")
      files = item.get("files", [])

      await update.message.reply_text(
          f"🎧 محاضرة: **{name}** ({week_name} - {day_name})",
          parse_mode="Markdown",
      )

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

  # 4. إضافة محاضرة
  if text == "➕ ضيف محاضرة" or "اضافه محاضرة" in text or text == "/addlecture":
    user_data.clear()
    user_data["state"] = "AUTH_PASSWORD"
    await update.message.reply_text(
        "🔒 [إضافة محاضرة]\nيلا هات الباسورد الأول عشان نتأكد إنك أنت:"
    )
    return

  # 5. عرض الكتب
  if text == "📚 كتب طب الأسنان":
    user_data.clear()
    books = data["sections"]["كتب"].get("items", [])
    if not books:
      await update.message.reply_text(
          "لسه مفيش كتب مضافة يا دكتور.", reply_markup=get_main_reply_keyboard()
      )
    else:
      msg = "📚 **كتب طب الأسنان المرجعية:**\n\n"
      for i, b in enumerate(books, 1):
        msg += f"{i}. {b}\n"
      await update.message.reply_text(
          msg, parse_mode="Markdown", reply_markup=get_main_reply_keyboard()
      )
    return

  # 6. إضافة قسم جديد
  if text == "➕ ضيف قسم جديد" or "اضف خيار" in text:
    user_data.clear()
    user_data["state"] = "AUTH_OPTION"
    await update.message.reply_text(
        "🔒 [إضافة قسم جديد]\nهات الباسورد يا باشا عشان نكمل:"
    )
    return

  # 7. حذف محاضرة
  if text == "🗑️ امسح محاضرة" or text == "/delete":
    user_data.clear()
    user_data["state"] = "AUTH_DELETE"
    await update.message.reply_text(
        "🔒 [حذف محتوى]\nدخل الباسورد عشان نسمح لك بالحذف:"
    )
    return

  current_state = user_data.get("state")

  if current_state in ["AUTH_PASSWORD", "AUTH_OPTION", "AUTH_DELETE"]:
    if text == ADMIN_PASSWORD:
      if current_state == "AUTH_PASSWORD":
        user_data["state"] = "WAITING_WEEK_NAME"
        await update.message.reply_text(
            "تمام، الباسورد صح ✅.\n📅 اكتب اسم الأسبوع الأول (زي مثلاً:"
            " `الاسبوع الاول`):"
        )
      elif current_state == "AUTH_OPTION":
        user_data["state"] = "WAITING_OPTION_NAME"
        await update.message.reply_text(
            "الباسورد مظبوط ✅.\nاكتب اسم القسم الجديد اللي عايزه (زي: سكشن"
            " أناتومي):"
        )
      elif current_state == "AUTH_DELETE":
        user_data["state"] = "WAITING_DELETE_TARGET"
        weeks = list(data["sections"]["محاضرات"].get("lectures", {}).keys())
        msg = (
            "الباسورد صح ✅.\nابعث اسم الأسبوع اللي عايز تمسحه بكل محاضراته:"
        )
        if weeks:
          msg += f"\nالأسابيع الموجودة حالياً: {', '.join(weeks)}"
        await update.message.reply_text(msg)
    else:
      user_data.clear()
      await update.message.reply_text(
          "❌ الباسورد غلط يا صاحبي، اللعبة اتلغت.",
          reply_markup=get_main_reply_keyboard(),
      )
    return

  if current_state == "WAITING_OPTION_NAME":
    user_data["temp_option_name"] = text
    user_data["state"] = "WAITING_OPTION_CMD"
    await update.message.reply_text(
        "تسلم! اكتب بقى اسم الزرار اللي هيظهر تحت عشان يفتح القسم ده:"
    )
    return

  if current_state == "WAITING_OPTION_CMD":
    btn_text = text
    opt_name = user_data.get("temp_option_name")
    sec_key = "custom_" + str(len(data["sections"]) + 1)

    data["sections"][sec_key] = {"title": opt_name, "lectures": {}}
    if "custom_buttons" not in data:
      data["custom_buttons"] = {}
    data["custom_buttons"][btn_text] = sec_key

    save_data(data)
    user_data.clear()

    await update.message.reply_text(
        f"🎉 قشطة! عملنا القسم ({opt_name}) والزرار ({btn_text}) اتضاف تحت زي"
        " الفل 🚀",
        reply_markup=get_main_reply_keyboard(),
    )
    return

  if current_state == "WAITING_DELETE_TARGET":
    target_week = text
    lectures_sec = data["sections"]["محاضرات"].get("lectures", {})

    if target_week in lectures_sec:
      days_in_week = list(lectures_sec[target_week].keys())
      del lectures_sec[target_week]
      save_data(data)
      user_data.clear()
      days_str = ", ".join(days_in_week) if days_in_week else "لا توجد أيام"
      await update.message.reply_text(
          f"🗑️ تم مسح الأسبوع ({target_week}) بالكامل!\n🗓️ الأيام التي كانت"
          f" موجودة وتم حذفها: [{days_str}] بنجاح.",
          reply_markup=get_main_reply_keyboard(),
      )
    else:
      await update.message.reply_text(
          f"⚠️ مش ملقيين أسبوع بالاسم ده ({target_week})، اتأكد من الكتابة.",
          reply_markup=get_main_reply_keyboard(),
      )
    return

  # ----------------- دورة الإضافة بالترتيب -----------------
  if current_state == "WAITING_WEEK_NAME":
    if not text:
      await update.message.reply_text("يا ريت تكتب اسم الأسبوع صح لو سمحت.")
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
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"تمام، سجلنا الأسبوع: ({text}) 📅\nاختر **اليوم** من الأزرار اللي تحت"
        " دي:",
        reply_markup=reply_markup,
        parse_mode="Markdown",
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
    user_data["state"] = "WAITING_FILES"

    await update.message.reply_text(
        f"عاش يا دكتور، اخترت يوم: **{text}** 🗓️\n📁 ابعت بقى ملف أو كذا ملف صوتي"
        " مع بعض (دفعة واحدة)، وبعد ما تخلص ابعت أي كلمة أو حرف عشان تكتب"
        " اسم المحاضرة:",
        reply_markup=get_main_reply_keyboard(),
        parse_mode="Markdown",
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

    # لو المستخدم أرسل ملف ومعاه نص في نفس الرسالة (Caption)
    if file_id and update.message.caption:
      user_data["temp_files"].append({"file_id": file_id, "file_type": file_type})
      lecture_name = update.message.caption.strip()
      
      # حفظ المحاضرة مباشرة لأن الاسم مدمج مع الملف
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
          f"فل يا دكتور! اتضافت تمام مع الاسم بالملف:\n📂 الأسبوع: **{week_name}**\n🗓️ اليوم: **{day_name}**\n🎧 المحاضرة: **{lecture_name}** (عدد الملفات: {len(files_list)})\n\nاضغط على **📚 المحاضرات** من تحت عشان تشوف الشغل التمام!",
          reply_markup=get_main_reply_keyboard(),
          parse_mode="Markdown",
      )
      return

    if file_id:
      user_data["temp_files"].append({"file_id": file_id, "file_type": file_type})
      await update.message.reply_text(
          f"📥 استلمنا ملف (عدد الملفات لحد دلوقتي:"
          f" {len(user_data['temp_files'])}).\nلو معاك تاني ابعته، لو خلصت ابعت"
          " اسم المحاضرة علطول:"
      )
      return
    else:
      if not user_data.get("temp_files"):
        await update.message.reply_text(
            "⚠️ انت مابعتش أي ملفات يا دكتور! ابعت الملفات الأول."
        )
        return

      if not text:
        await update.message.reply_text(
            "⚠️ من فضلك اكتب اسم المحاضرة بشكل صحيح."
        )
        return

      lecture_name = text
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
          f"فل يا دكتور! اتضافت تمام:\n📂 الأسبوع: **{week_name}**\n🗓️ اليوم:"
          f" **{day_name}**\n🎧 المحاضرة: **{lecture_name}** (عدد الملفات:"
          f" {len(files_list)})\n\nاضغط على **📚 المحاضرات** من تحت عشان تشوف"
          " الشغل التمام!",
          reply_markup=get_main_reply_keyboard(),
          parse_mode="Markdown",
      )
      return


if __name__ == "__main__":
  # 1. تشغيل سيرفر الويب في خيط فرعي (Background Thread) ليبقى البورت مفتوحاً لرندر
  port = int(os.environ.get("PORT", 8080))
  web_thread = threading.Thread(
      target=lambda: app.run(host="0.0.0.0", port=port)
  )
  web_thread.daemon = True
  web_thread.start()
  print(f"سيرفر الويب شغال على البورت {port}...")

  # 2. تشغيل بوت تيليجرام في الخيط الأساسي (Main Thread) لتجنب أخطاء النظام
  TOKEN = "8964990492:AAFy3kskRFG46huYcmCcUthpPdF4Tx_tvJw"
  app_bot = ApplicationBuilder().token(TOKEN).build()

  app_bot.add_handler(CommandHandler("start", start))
  app_bot.add_handler(
      MessageHandler(filters.ALL & ~filters.COMMAND, handle_message)
  )

  print("Uni Helper Bot يعمل الآن في الخيط الأساسي...")
  app_bot.run_polling()
