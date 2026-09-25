import json
import os
import threading
from flask import Flask
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from supabase import create_client, Client

# --- إعدادات Supabase السحابية (مع القيم الافتراضية لضمان عدم حدوث كراش) ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://avpfzachffhwlsssihlg.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_8dlyeVdXJzariNrA_oOOoQ_KY1pVx3D")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- سيرفر الويب الأساسي لضمان بقاء البورت مفتوحاً ---
app = Flask("")


@app.route("/")
def home():
  return "Uni Helper Bot is alive and running!"


ADMIN_PASSWORD = "15309"

# سجل لتخزين آخر الرسائل المعالجة لمنع التكرار المزدوج نهائياً
processed_updates = set()

# --- 30 سؤالاً تفصيلياً لـ anatomy (عملي) لصفحه 6 ---
ANATOMY_P6_QUIZ = [
    {
        "question": "The skull protects the brain and the organs of special sense, and its bones are united by:",
        "options": ["A) Cartilage exclusively", "B) Sutures", "C) Direct muscular fusion", "D) Fibrocartilage joints"],
        "correct": 1
    },
    {
        "question": "In the anatomical position, which two margins are in the same horizontal plane?",
        "options": [
            "A) Lower orbital margin and upper margin of external acoustic meatus",
            "B) Upper orbital margin and lower margin of external acoustic meatus",
            "C) Glabella and Inion",
            "D) Nasion and Bregma"
        ],
        "correct": 0
    },
    {
        "question": "The view of the skull seen from above is called:",
        "options": ["A) Norma frontalis", "B) Norma verticalis", "C) Norma occipitalis", "D) Norma basalis"],
        "correct": 1
    },
    {
        "question": "Which bones share in forming the Norma verticalis?",
        "options": [
            "A) Frontal, Parietal, and Occipital bones",
            "B) Temporal and Sphenoid only",
            "C) Maxilla and Zygomatic",
            "D) Mandible and Temporal"
        ],
        "correct": 0
    },
    {
        "question": "The sagittal suture extends anteroposteriorly between which bones?",
        "options": [
            "A) Frontal and parietal bones",
            "B) Two parietal bones",
            "C) Parietal and occipital bones",
            "D) Temporal and parietal bones"
        ],
        "correct": 1
    },
    {
        "question": "The coronal suture lies transversely between which bones?",
        "options": [
            "A) Frontal and parietal bones",
            "B) Parietal and occipital bones",
            "C) Two parietal bones",
            "D) Temporal and sphenoid"
        ],
        "correct": 0
    },
    {
        "question": "The upper part of the lambdoid suture lies between:",
        "options": [
            "A) Frontal and parietal bones",
            "B) Occipital and parietal bones",
            "C) Temporal and zygomatic bones",
            "D) Maxilla and nasal bones"
        ],
        "correct": 1
    },
    {
        "question": "The point of meeting of the sagittal and coronal sutures is called:",
        "options": ["A) Lambda", "B) Bregma", "C) Nasion", "D) Pterion"],
        "correct": 1
    },
    {
        "question": "The point of meeting of the sagittal and lambdoid sutures is called:",
        "options": ["A) Bregma", "B) Lambda", "C) Glabella", "D) Inion"],
        "correct": 1
    },
    {
        "question": "Bregma and lambda indicate the positions of which structures in the fetus?",
        "options": [
            "A) Ossified tubercles",
            "B) Anterior and posterior fontanels respectively",
            "C) Emissary veins",
            "D) Parietal eminences"
        ],
        "correct": 1
    },
    {
        "question": "The parietal foramen transmits which of the following structures?",
        "options": [
            "A) Facial nerve",
            "B) Emissary vein between scalp veins and superior sagittal sinus",
            "C) Middle meningeal artery",
            "D) Internal carotid artery"
        ],
        "correct": 1
    },
    {
        "question": "The bones of the vault of the skull develop from:",
        "options": ["A) Cartilage models", "B) Membranes that ossify to form bones", "C) Direct muscular ossification", "D) Endochondral ossification exclusively"],
        "correct": 1
    },
    {
        "question": "An area of the membrane that is still not ossified at birth where two or more sutures meet is called:",
        "options": ["A) Foramen", "B) Fontanelle", "C) Fossa", "D) Sulcus"],
        "correct": 1
    },
    {
        "question": "The anterior fontanelle is present at the junction of:",
        "options": [
            "A) Sagittal and lambdoid sutures",
            "B) Coronal and sagittal sutures",
            "C) Metopic and coronal sutures",
            "D) Squamous and lambdoid sutures"
        ],
        "correct": 1
    },
    {
        "question": "Normally, the anterior fontanelle closes at what time after birth?",
        "options": ["A) 1 to 2 months", "B) 6 months", "C) 18 to 24 months", "D) 3 to 4 years"],
        "correct": 2
    },
    {
        "question": "The posterior fontanelle is present at the junction of:",
        "options": [
            "A) Coronal and sagittal sutures",
            "B) Sagittal and lambdoid sutures",
            "C) Frontal and nasal sutures",
            "D) Temporal and parietal sutures"
        ],
        "correct": 1
    },
    {
        "question": "Normally, the posterior fontanelle closes at what time after birth?",
        "options": ["A) 6 months", "B) 12 months", "C) 18 to 24 months", "D) At birth"],
        "correct": 0
    },
    {
        "question": "Clinically, the anterior fontanelle is known to exhibit which of the following signs?",
        "options": [
            "A) It bulges in case of increased intracranial tension",
            "B) It sinks in cases of hypertension",
            "C) It enlarges permanently after 5 years",
            "D) It ossifies completely within the first week"
        ],
        "correct": 0
    },
    {
        "question": "In case of dehydration, the anterior fontanelle appears:",
        "options": ["A) Bulging", "B) Shrunken", "C) Hyperemic", "D) Pulsating excessively"],
        "correct": 1
    },
    {
        "question": "Which of the following is a clinical use of the anterior fontanelle?",
        "options": [
            "A) Estimating the newborn's age",
            "B) Measuring direct blood pressure",
            "C) Administering oral vaccines",
            "D) Extracting cerebrospinal fluid safely"
        ],
        "correct": 0
    },
    {
        "question": "The parietal eminence is located as a prominence on either side of:",
        "options": ["A) The sagittal suture", "B) The coronal suture", "C) The lambdoid suture", "D) The squamous suture"],
        "correct": 0
    },
    {
        "question": "The skull bones are united by irregular lines called:",
        "options": ["A) Fissures", "B) Sutures", "C) Canals", "D) Grooves"],
        "correct": 1
    },
    {
        "question": "Which fontanelle is diamond-shaped in the skull at birth?",
        "options": ["A) Posterior fontanelle", "B) Anterior fontanelle", "C) Sphenoidal fontanelle", "D) Mastoid fontanelle"],
        "correct": 1
    },
    {
        "question": "Which fontanelle is triangular-shaped in the skull at birth?",
        "options": ["A) Anterior fontanelle", "B) Posterior fontanelle", "C) Metopic fontanelle", "D) Sagittal fontanelle"],
        "correct": 1
    },
    {
        "question": "The interior of the skull is commonly referred to as:",
        "options": ["A) The cranial cavity", "B) The temporal fossa", "C) The infratemporal fossa", "D) The orbital cavity"],
        "correct": 0
    },
    {
        "question": "The sagittal suture separates which two anatomical structures?",
        "options": ["A) Frontal bones", "B) Two parietal bones", "C) Occipital and temporal bones", "D) Nasal bones"],
        "correct": 1
    },
    {
        "question": "The coronal suture separates the frontal bone from which other bone?",
        "options": ["A) Occipital bone", "B) Parietal bone", "C) Temporal bone", "D) Sphenoid bone"],
        "correct": 1
    },
    {
        "question": "The lambdoid suture separates the parietal bones from:",
        "options": ["A) The frontal bone", "B) The occipital bone", "C) The zygomatic bone", "D) The maxilla"],
        "correct": 1
    },
    {
        "question": "What is the primary function of the cranium regarding neural structures?",
        "options": [
            "A) To circulate cerebrospinal fluid",
            "B) To protect the brain and special sense organs",
            "C) To anchor facial expression muscles directly",
            "D) To produce red blood cells"
        ],
        "correct": 1
    },
    {
        "question": "Which suture runs in a transverse direction across the skull vault?",
        "options": ["A) Sagittal suture", "B) Coronal suture", "C) Metopic suture", "D) Internasal suture"],
        "correct": 1
    }
]


def load_data():
  default_data = {
      "sections": {
          "محاضرات": {"title": "المحاضرات", "lectures": {}},
          "كتب": {"title": "الكتب", "items": []},
          "groups": {},
          "youtube_doctors": {},
          "ai_summaries": {},
      },
      "custom_buttons": {},
      "users": [],
  }

  try:
    response = supabase.table("bot_storage").select("value").eq("key", "main_data").execute()
    if response.data and len(response.data) > 0:
      data = response.data[0]["value"]
      if "sections" not in data:
        data["sections"] = default_data["sections"]
      else:
        for key in default_data["sections"]:
          if key not in data["sections"]:
            data["sections"][key] = default_data["sections"][key]

      if "users" not in data:
        data["users"] = []
      if "custom_buttons" not in data:
        data["custom_buttons"] = {}

      return data
    else:
      save_data(default_data)
      return default_data
  except Exception as e:
    print(f"Error loading data from supabase: {e}")
    return default_data


def save_data(data):
  try:
    supabase.table("bot_storage").upsert({
        "key": "main_data",
        "value": data
    }).execute()
  except Exception as e:
    print(f"Error saving data to supabase: {e}")


def register_user(user_id):
  data = load_data()
  if "users" not in data:
    data["users"] = []
  if user_id not in data["users"]:
    data["users"].append(user_id)
    save_data(data)


def get_main_reply_keyboard():
  keyboard = [
      [KeyboardButton("📚 المحاضرات"), KeyboardButton("📚 كتب طب الأسنان")],
      [KeyboardButton("🔗 أهم الجروبات"), KeyboardButton("🎥 أفضل دكاترة يوتيوب")],
      [KeyboardButton("🤖 تلخيصات AI"), KeyboardButton("✍️ امتحن نفسك (AI)")],
      [KeyboardButton("➕ ضيف محاضرة"), KeyboardButton("➕ ضيف كتاب")],
      [KeyboardButton("🗑️ امسح محاضرة"), KeyboardButton("🗑️ امسح كتاب")],
      [KeyboardButton("⚙️ لوحة الأدمن والإحصائيات"), KeyboardButton("❌ خروج")],
  ]
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# لوحة قائمة الامتحانات التي تظهر بالأسفل
def get_quiz_reply_keyboard():
  keyboard = [
      [KeyboardButton("📝 امتحان: anatomy (عملي) لصفحه 6")],
      [KeyboardButton("🔙 رجوع للقائمة الرئيسية")],
  ]
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_weeks_reply_keyboard():
  data = load_data()
  lectures_dict = data["sections"]["محاضرات"].get("lectures", {})

  keyboard = []
  for week_name in lectures_dict.keys():
    keyboard.append([KeyboardButton(f"📅 {week_name}")])

  keyboard.append([KeyboardButton("🔙 رجوع للقائمة الرئيسية")])
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


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


def get_books_reply_keyboard():
  data = load_data()
  books_list = data["sections"]["كتب"].get("items", [])

  keyboard = []
  for book in books_list:
    book_name = book.get("name", "كتاب بدون اسم")
    keyboard.append([KeyboardButton(f"📖 {book_name}")])

  keyboard.append([KeyboardButton("🔙 رجوع للقائمة الرئيسية")])
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_yt_reply_keyboard():
  data = load_data()
  yt_doctors = data["sections"].get("youtube_doctors", {})

  keyboard = []
  for subject_name in yt_doctors.keys():
    keyboard.append([KeyboardButton(f"🎓 دكتور: {subject_name}")])

  keyboard.append([KeyboardButton("🔙 رجوع للقائمة الرئيسية")])
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_ai_reply_keyboard():
  data = load_data()
  ai_summaries = data["sections"].get("ai_summaries", {})

  keyboard = []
  for subject_name in ai_summaries.keys():
    keyboard.append([KeyboardButton(f"🤖 تلخيص: {subject_name}")])

  keyboard.append([KeyboardButton("🔙 رجوع للقائمة الرئيسية")])
  return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  update_id = update.update_id
  if update_id in processed_updates:
    return
  processed_updates.add(update_id)
  if len(processed_updates) > 100:
    processed_updates.pop()

  user_id = update.effective_user.id
  register_user(user_id)
  context.user_data.clear()
  text_msg = (
      "منور يا دكتور في بوت **Uni Helper** لطب أسنان جامعة الزقازيق الأهلية"
      " (ZNU) 🦷🎓\n\nاختر من الأزرار بالأسفل:"
  )
  await update.message.reply_text(
      text_msg, reply_markup=get_main_reply_keyboard(), parse_mode="Markdown"
  )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  update_id = update.update_id
  if update_id in processed_updates:
    return
  processed_updates.add(update_id)
  if len(processed_updates) > 200:
    processed_updates.pop()

  user_id = update.effective_user.id
  register_user(user_id)

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

  # قسم امتحن نفسك (AI)
  if text == "✍️ امتحن نفسك (AI)":
    user_data.clear()
    await update.message.reply_text(
        "✍️ **اختر الامتحان المطلوب من الأزرار بالأسفل 👇**",
        reply_markup=get_quiz_reply_keyboard(),
        parse_mode="Markdown"
    )
    return

  # بدء امتحان anatomy (عملي) لصفحه 6 مباشرة من الأزرار السفلية
  if text == "📝 امتحان: anatomy (عملي) لصفحه 6":
    user_data["quiz_index"] = 0
    user_data["quiz_score"] = 0
    await send_quiz_question_reply(update.message, context)
    return

  current_state = user_data.get("state")

  if current_state:
    if current_state in [
        "AUTH_PASSWORD",
        "AUTH_BOOK_PASSWORD",
        "AUTH_DELETE",
        "AUTH_DELETE_BOOK",
        "AUTH_ADMIN_PANEL",
        "AUTH_BROADCAST",
        "AUTH_ADD_GROUP",
        "AUTH_ADD_YT",
        "AUTH_ADD_AI",
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
        elif current_state == "AUTH_ADMIN_PANEL":
          users_count = len(data.get("users", []))
          user_data.clear()
          keyboard = [
              [KeyboardButton("📢 إرسال إعلان عام (Broadcast)")],
              [
                  KeyboardButton("➕ إضافة جروب مهم"),
                  KeyboardButton("🎥 إضافة شرح يوتيوب"),
              ],
              [KeyboardButton("🤖 إضافة تلخيص AI")],
              [KeyboardButton("🔙 رجوع للقائمة الرئيسية")],
          ]
          await update.message.reply_text(
              f"⚙️ **لوحة التحكم والإحصائيات:**\n\n👥 إجمالي عدد المستخدمين للبوت:"
              f" `{users_count}` طالب.\n\nاختر العملية المطلوبة من الأزرار بالأسفل:",
              reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
              parse_mode="Markdown",
          )
        elif current_state == "AUTH_BROADCAST":
          user_data["state"] = "WAITING_BROADCAST_MESSAGE"
          await update.message.reply_text(
              "📢 أرسل الآن نص أو ملف الإعلان المراد إرساله للطلاب مباشرة:"
          )
        elif current_state == "AUTH_ADD_GROUP":
          user_data["state"] = "WAITING_GROUP_LINK"
          await update.message.reply_text("🔗 أرسل الآن **رابط الجروب**:")
        elif current_state == "AUTH_ADD_YT":
          user_data["state"] = "WAITING_YT_LINK"
          await update.message.reply_text(
              "🔗 أرسل الآن **رابط مقطع أو نص يوتيوب الشرح**:"
          )
        elif current_state == "AUTH_ADD_AI":
          user_data["state"] = "WAITING_AI_FILE"
          await update.message.reply_text(
              "🤖 أرسل الآن **ملف التلخيص أو المقطع الصوتي** الخاص بـ AI:"
          )
      else:
        user_data.clear()
        await update.message.reply_text(
            "❌ الباسورد غلط.", reply_markup=get_main_reply_keyboard()
        )
      return

    if current_state == "WAITING_BROADCAST_MESSAGE":
      users = data.get("users", [])
      success_count = 0
      await update.message.reply_text("⏳ جاري إرسال الرسالة لجميع المستخدمين...")
      for uid in users:
        try:
          await context.bot.send_message(
              chat_id=uid, text=text, parse_mode="Markdown"
          )
          success_count += 1
        except Exception:
          pass
      user_data.clear()
      await update.message.reply_text(
          f"✅ تم إرسال الرسالة بنجاح إلى `{success_count}` مستخدماً من إجمالي"
          f" `{len(users)}`.",
          reply_markup=get_main_reply_keyboard(),
      )
      return

    if current_state == "WAITING_GROUP_LINK":
      user_data["temp_group_link"] = text
      user_data["state"] = "WAITING_GROUP_NAME"
      await update.message.reply_text(
          "📝 ممتاز، الآن أرسل **اسم الجروب** (مثال: جروب الدفعة الرسمي):"
      )
      return

    if current_state == "WAITING_GROUP_NAME":
      g_link = user_data.get("temp_group_link")
      g_name = text
      if "groups" not in data["sections"]:
        data["sections"]["groups"] = {}
      data["sections"]["groups"][g_name] = g_link
      save_data(data)
      user_data.clear()
      await update.message.reply_text(
          f"✅ تم إضافة الجروب **{g_name}** بنجاح وتخزينه في القاعدة!",
          reply_markup=get_main_reply_keyboard(),
      )
      return

    if current_state == "WAITING_YT_LINK":
      user_data["temp_yt_link"] = text
      user_data["state"] = "WAITING_YT_SUBJECT_NAME"
      await update.message.reply_text(
          "📝 ممتاز، الآن أرسل **اسم المادة** الخاصة بالشرح (مثال: Anatomy - محاضرة"
          " 1):"
      )
      return

    if current_state == "WAITING_YT_SUBJECT_NAME":
      yt_link = user_data.get("temp_yt_link")
      subject_name = text
      if "youtube_doctors" not in data["sections"]:
        data["sections"]["youtube_doctors"] = {}
      data["sections"]["youtube_doctors"][subject_name] = yt_link
      save_data(data)
      user_data.clear()
      await update.message.reply_text(
          f"✅ تم حفظ شرح مادة **{subject_name}** بنجاح، وظهرت في قائمة أفضل دكاترة"
          " اليوتيوب بالأزرار! 🎥🚀",
          reply_markup=get_main_reply_keyboard(),
      )
      return

    if current_state == "WAITING_AI_FILE":
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
        user_data["temp_ai_file_id"] = file_id
        user_data["temp_ai_file_type"] = file_type
        user_data["state"] = "WAITING_AI_SUBJECT_NAME"
        await update.message.reply_text(
            "📝 ممتاز، استلمنا الملف. الآن أرسل **اسم المادة** أو عنوان التلخيص"
            " (مثال: Histology - Summary 1):"
        )
        return
      else:
        await update.message.reply_text(
            "⚠️ من فضلك أرسل ملف التلخيص أو المقطع الصوتي أولاً."
        )
        return

    if current_state == "WAITING_AI_SUBJECT_NAME":
      subject_name = text
      f_id = user_data.get("temp_ai_file_id")
      f_type = user_data.get("temp_ai_file_type")

      if "ai_summaries" not in data["sections"]:
        data["sections"]["ai_summaries"] = {}

      data["sections"]["ai_summaries"][subject_name] = {
          "file_id": f_id,
          "file_type": f_type,
      }
      save_data(data)
      user_data.clear()

      await update.message.reply_text(
          f"✅ تم حفظ تلخيص مادة **{subject_name}** بنجاح، وظهرت مباشرة في قسم"
          " تلخيصات AI بالأزرار! 🤖🚀",
          reply_markup=get_main_reply_keyboard(),
      )
      return

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
          [KeyboardButton("🔄 إلغاء")],
      ]
      await update.message.reply_text(
          f"سجلنا الأسبوع: ({text}). اختر اليوم من الأزرار بالأسفل:",
          reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
      )
      return

    if current_state == "WAITING_DAY_CHOICE":
      if text == "🔄 إلغاء":
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
          f"اخترت يوم: {text} 🗓️\nابعث الملفات أو الفويس (تقدر تبعت أكتر من ملف مع"
          " بعض دفعة واحدة، وبعد ما تخلص ابعت اسم المحاضرة في رسالة):",
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
            " بنجاح تام وسحابياً!",
            reply_markup=get_main_reply_keyboard(),
        )
        return

  # 3. الأقسام الرئيسية والأوامر العادية
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
        await context.bot.send_voice(chat_id=update.message.chat_id, audio=f_id)
      else:
        await context.bot.send_document(
            chat_id=update.message.chat_id, document=f_id
        )
    else:
      await update.message.reply_text("⚠️ عذراً، لم يتم العثور على هذا الكتاب.")
    return

  if text == "🔗 أهم الجروبات":
    user_data.clear()
    groups = data["sections"].get("groups", {})
    if not groups:
      await update.message.reply_text(
          "🔗 مفيش جروبات مضافة حالياً يا دكتور.\n(يمكن للأدمن إضافتها من لوحة"
          " التحكم).",
          reply_markup=get_main_reply_keyboard(),
      )
      return

    msg = "🔗 **أهم الجروبات والروابط الرسمية للدفعة:**\n\n"
    for g_name, g_link in groups.items():
      msg += f"• [{g_name}]({g_link})\n"
    await update.message.reply_text(
        msg, reply_markup=get_main_reply_keyboard(), parse_mode="Markdown"
    )
    return

  if text == "🎥 أفضل دكاترة يوتيوب":
    user_data.clear()
    yt_doctors = data["sections"].get("youtube_doctors", {})
    if not yt_doctors:
      await update.message.reply_text(
          "🎥 **أفضل قنوات وشروحات دكاترة الأسنان على اليوتيوب:**\n\nلسه مفيش"
          " مواد أو شروحات مضافة حالياً يا دكتور.",
          reply_markup=get_main_reply_keyboard(),
      )
      return
    await update.message.reply_text(
        "🎥 **اختر المادة أو الشرح من الأزرار بالأسفل لتظهر لك الروابط 👇**",
        reply_markup=get_yt_reply_keyboard(),
    )
    return

  if text.startswith("🎓 دكتور: "):
    subject_name = text.replace("🎓 دكتور: ", "").strip()
    yt_doctors = data["sections"].get("youtube_doctors", {})
    yt_link = yt_doctors.get(subject_name)

    if yt_link:
      await update.message.reply_text(
          f"🎥 **شرح مادة: {subject_name}**\n\n🔗 [اضغط هنا لمشاهدة المقطع]"
          f"({yt_link})",
          parse_mode="Markdown",
          reply_markup=get_yt_reply_keyboard(),
      )
    else:
      await update.message.reply_text("⚠️ عذراً، لم يتم العثور على هذا الشرح.")
    return

  if text == "🤖 تلخيصات AI":
    user_data.clear()
    ai_summaries = data["sections"].get("ai_summaries", {})
    if not ai_summaries:
      await update.message.reply_text(
          "🤖 **قسم تلخيصات الذكاء الاصطناعي:**\n\nلسه مفيش تلخيصات مضافة من"
          " الإدارة حالياً يا دكتور.",
          reply_markup=get_main_reply_keyboard(),
      )
      return

    await update.message.reply_text(
        "🤖 **اختر التلخيص أو المادة من الأزرار بالأسفل ليتم إرسال الملف فوراً"
        " 👇**",
        reply_markup=get_ai_reply_keyboard(),
    )
    return

  if text.startswith("🤖 تلخيص: "):
    subject_name = text.replace("🤖 تلخيص: ", "").strip()
    ai_summaries = data["sections"].get("ai_summaries", {})
    target_summary = ai_summaries.get(subject_name)

    if target_summary:
      await update.message.reply_text(
          f"📄 **تلخيص مادة/موضوع: {subject_name}**"
      )
      f_id = target_summary.get("file_id")
      f_type = target_summary.get("file_type")
      if f_type == "audio":
        await context.bot.send_audio(
            chat_id=update.message.chat_id,
            audio=f_id,
            reply_markup=get_ai_reply_keyboard(),
        )
      elif f_type == "voice":
        await context.bot.send_voice(
            chat_id=update.message.chat_id,
            voice=f_id,
            reply_markup=get_ai_reply_keyboard(),
        )
      else:
        await context.bot.send_document(
            chat_id=update.message.chat_id,
            document=f_id,
            reply_markup=get_ai_reply_keyboard(),
        )
    else:
      await update.message.reply_text("⚠️ عذراً، لم يتم العثور على هذا التلخيص.")
    return

  # طلوع حالات الأدمن وبداية الدورات الجديدة
  if text == "⚙️ لوحة الأدمن والإحصائيات":
    user_data.clear()
    user_data["state"] = "AUTH_ADMIN_PANEL"
    await update.message.reply_text(
        "🔒 [لوحة تحكم المسؤول]\nهات باسورد المسؤول الأول:"
    )
    return

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

  if text == "📢 إرسال إعلان عام (Broadcast)":
    user_data.clear()
    user_data["state"] = "AUTH_BROADCAST"
    await update.message.reply_text(
        "🔒 [إرسال إعلان عام]\nهات باسورد المسؤول الأول:"
    )
    return

  if text == "➕ إضافة جروب مهم":
    user_data.clear()
    user_data["state"] = "AUTH_ADD_GROUP"
    await update.message.reply_text("🔗 أرسل الآن **رابط الجروب**:")
    return

  if text == "🎥 إضافة شرح يوتيوب":
    user_data.clear()
    user_data["state"] = "AUTH_ADD_YT"
    await update.message.reply_text(
        "🎥 أرسل الآن **رابط الشرح**:"
    )
    return

  if text == "🤖 إضافة تلخيص AI":
    user_data.clear()
    user_data["state"] = "AUTH_ADD_AI"
    await update.message.reply_text(
        "🤖 أرسل الآن **ملف التلخيص**:"
    )
    return


# --- نظام إرسال الأسئلة عبر الأزرار التفاعلية (Inline) داخل الشات السفلي ---
async def quiz_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()
  data = query.data
  user_data = context.user_data

  if data.startswith("ans_"):
    parts = data.split("_")
    q_index = int(parts[1])
    selected_option = int(parts[2])

    current_q = ANATOMY_P6_QUIZ[q_index]
    correct_option = current_q["correct"]

    if selected_option == correct_option:
      user_data["quiz_score"] = user_data.get("quiz_score", 0) + 1
      res_text = "✅ إجابة صحيحة بطل!"
    else:
      correct_text = current_q["options"][correct_option]
      res_text = f"❌ إجابة خاطئة!\nالإجابة الصحيحة هي: {correct_text}"

    user_data["quiz_index"] = q_index + 1

    if user_data["quiz_index"] < len(ANATOMY_P6_QUIZ):
      await query.message.edit_text(f"{res_text}\n\nجاري الانتقال للسؤال التالي...")
      import asyncio
      await asyncio.sleep(1)
      await send_quiz_question_inline(query.message, context, edit=True)
    else:
      score = user_data.get("quiz_score", 0)
      total = len(ANATOMY_P6_QUIZ)
      await query.message.edit_text(
          f"🏁 **انتهى امتحان anatomy (عملي) لصفحه 6 بنجاح!**\n\n"
          f"📊 درجاتك: `{score}` من `{total}`\n"
          f"عاش يا دكتور ! 🦷🎓",
          parse_mode="Markdown"
      )
      user_data.clear()


async def send_quiz_question_reply(message, context):
  user_data = context.user_data
  q_index = user_data.get("quiz_index", 0)
  current_q = ANATOMY_P6_QUIZ[q_index]

  keyboard = []
  for idx, option in enumerate(current_q["options"]):
    keyboard.append([InlineKeyboardButton(option, callback_data=f"ans_{q_index}_{idx}")])

  reply_markup = InlineKeyboardMarkup(keyboard)
  q_text = (
      f"⏱️ **ملاحظة: معك 15 ثانية للإجابة!**\n"
      f"السؤال رقم {q_index + 1} من {len(ANATOMY_P6_QUIZ)}:\n\n"
      f"*{current_q['question']}*"
  )

  sent_msg = await message.reply_text(
      q_text,
      reply_markup=reply_markup,
      parse_mode="Markdown"
  )

  context.job_queue.run_once(
      timeout_quiz_question,
      15.0,
      chat_id=message.chat_id,
      data={"message_id": sent_msg.message_id, "expected_index": q_index},
      name=str(message.chat_id)
  )


async def send_quiz_question_inline(message, context, edit=False):
  user_data = context.user_data
  q_index = user_data.get("quiz_index", 0)
  current_q = ANATOMY_P6_QUIZ[q_index]

  keyboard = []
  for idx, option in enumerate(current_q["options"]):
    keyboard.append([InlineKeyboardButton(option, callback_data=f"ans_{q_index}_{idx}")])

  reply_markup = InlineKeyboardMarkup(keyboard)
  q_text = (
      f"⏱️ **ملاحظة: معك 15 ثانية للإجابة!**\n"
      f"السؤال رقم {q_index + 1} من {len(ANATOMY_P6_QUIZ)}:\n\n"
      f"*{current_q['question']}*"
  )

  if edit:
    sent_msg = await message.edit_text(q_text, reply_markup=reply_markup, parse_mode="Markdown")
  else:
    sent_msg = await message.reply_text(q_text, reply_markup=reply_markup, parse_mode="Markdown")

  context.job_queue.run_once(
      timeout_quiz_question,
      15.0,
      chat_id=message.chat_id,
      data={"message_id": sent_msg.message_id, "expected_index": q_index},
      name=str(message.chat_id)
  )


async def timeout_quiz_question(context: ContextTypes.DEFAULT_TYPE):
  job = context.job
  data = job.data
  chat_id = job.chat_id
  message_id = data["message_id"]

  try:
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="⏰ انتهى الوقت (15 ثانية)! انقضى وقت السؤال."
    )
  except Exception:
    pass


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 8080))
  web_thread = threading.Thread(
      target=lambda: app.run(host="0.0.0.0", port=port)
  )
  web_thread.daemon = True
  web_thread.start()

  # توكن البوت الأساسي الخاص بك
  TOKEN = "8964990492:AAHbOJ_dOeAkO80O-fZSemaRenz4bG93kFM"
  app_bot = ApplicationBuilder().token(TOKEN).build()
  app_bot.add_handler(CommandHandler("start", start))
  app_bot.add_handler(CallbackQueryHandler(quiz_callback_handler))
  app_bot.add_handler(
      MessageHandler(filters.ALL & ~filters.COMMAND, handle_message)
  )

  # تشغيل البوت مع تجاوز التحديثات القديمة لمنع تداخل الاستجابة
  app_bot.run_polling(drop_pending_updates=True)
