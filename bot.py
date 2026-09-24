import json
import os
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

app = Flask("")

@app.route("/")
def home():
    return "Uni Helper Bot is alive and running!"

ADMIN_PASSWORD = "15309"
DATA_FILE = "znu_dental_data.json"

def load_data():
    default_data = {
        "sections": {
            "محاضرات": {"title": "المحاضرات", "lectures": {}},
            "كتب": {"title": "الكتب", "items": []},
            "groups": {},
            "youtube_doctors": {},
            "ai_summaries": {},
            "ai_exams": {
                "Anatomy نظري": [
                    {"question": "What bones share in the formation of the Norma verticalis?", "options": ["A) Frontal, Maxilla, and Zygomatic bones", "B) Frontal, Parietal, and Occipital bones", "C) Temporal, Sphenoid, and Mandible bones", "D) Occipital, Temporal, and Nasal bones"], "answer": "B"},
                    {"question": "Which suture extends anteroposteriorly between the two parietal bones?", "options": ["A) Coronal suture", "B) Lambdoid suture", "C) Sagittal suture", "D) Metopic suture"], "answer": "C"},
                    {"question": "The Bregma is the point of meeting of which sutures?", "options": ["A) Sagittal and lambdoid sutures", "B) Sagittal and coronal sutures", "C) Frontonasal and internasal sutures", "D) Occipitomastoid and lambdoid sutures"], "answer": "B"},
                    {"question": "What is the clinical significance of the anterior fontanelle?", "options": ["A) It bulges in case of increased intracranial tension", "B) It is shrunken in dehydration", "C) It aids in estimating the newborn's age", "D) All of the above"], "answer": "D"},
                    {"question": "Normally, when does the posterior fontanelle close after birth?", "options": ["A) 6 months", "B) 12 months", "C) 18-24 months", "D) 36 months"], "answer": "A"},
                    {"question": "What structure does the parietal foramen transmit?", "options": ["A) Facial nerve", "B) An emissary vein between scalp veins and superior sagittal sinus", "C) Supraorbital nerve and vessels", "D) Middle meningeal artery"], "answer": "B"},
                    {"question": "The supraorbital notch or foramen transmits which of the following?", "options": ["A) Infraorbital nerve and vessels", "B) Zygomaticofacial nerve", "C) Supraorbital nerve and vessels", "D) Facial nerve"], "answer": "C"},
                    {"question": "Where is the glabella located?", "options": ["A) At the meeting point of the superciliary arches in the midline", "B) Between the parietal and occipital bones", "C) Behind the mastoid process", "D) At the junction of the coronal and sagittal suture"], "answer": "A"},
                    {"question": "What is the nasion?", "options": ["A) The prominence of the cheek formed by the zygomatic bone", "B) The point of meeting of the frontonasal and internasal sutures", "C) The median projection in the back of the skull", "D) The lowest point of the mandible"], "answer": "B"},
                    {"question": "The bones of the vault of the skull develop from which of the following?", "options": ["A) Cartilage exclusively", "B) Membranes (which are ossified to form bones)", "C) Direct replacement of muscular tissue", "D) The neural tube directly"], "answer": "B"},
                    {"question": "The skull protects which of the following?", "options": ["A) The heart and lungs", "B) The brain and organs of special sense", "C) The spinal cord only", "D) The abdominal viscera"], "answer": "B"},
                    {"question": "In the anatomical position, the lower orbital margin and the upper margin of the external acoustic meatus are in what relationship?", "options": ["A) Vertical plane", "B) Oblique plane", "C) The same horizontal plane", "D) Perpendicular plane"], "answer": "C"},
                    {"question": "How many main views are used for the purpose of describing the skull?", "options": ["A) 3 views", "B) 4 views", "C) 6 views", "D) 8 views"], "answer": "C"},
                    {"question": "What is the interior of the skull called?", "options": ["A) Spinal canal", "B) Cranial cavity", "C) Orbital cavity", "D) Temporal fossa"], "answer": "B"},
                    {"question": "What is the direction of the coronal suture?", "options": ["A) Anteroposterior", "B) Transverse in direction", "C) Vertical", "D) Oblique"], "answer": "B"},
                    {"question": "The coronal suture lies between which bones?", "options": ["A) Occipital and parietal", "B) Frontal and parietal bones", "C) Temporal and sphenoid", "D) Nasal and maxilla"], "answer": "B"},
                    {"question": "The upper part of the lambdoid suture lies between which bones?", "options": ["A) Frontal and nasal", "B) Occipital and parietal bones", "C) Maxilla and zygomatic", "D) Temporal and mandible"], "answer": "B"},
                    {"question": "What does the bregma represent?", "options": ["A) Meeting of sagittal and lambdoid sutures", "B) Meeting of sagittal and coronal sutures", "C) Meeting of frontonasal sutures", "D) Meeting of metopic sutures"], "answer": "B"},
                    {"question": "What does the lambda represent?", "options": ["A) Meeting of sagittal and lambdoid sutures", "B) Meeting of coronal and sagittal sutures", "C) Meeting of temporal sutures", "D) Meeting of nasal bones"], "answer": "A"},
                    {"question": "The bregma and lambda indicate the positions of what in the fetus?", "options": ["A) Nasal septum", "B) Anterior and posterior fontanels", "C) Dental buds", "D) Suture closures in adults"], "answer": "B"},
                    {"question": "What is the parietal eminence?", "options": ["A) A depression near the inion", "B) A prominence on either side of the sagittal suture", "C) A groove for the middle meningeal artery", "D) A process on the temporal bone"], "answer": "B"},
                    {"question": "At birth, areas of membrane between sutures that are not ossified are called what?", "options": ["A) Foramina", "B) Fontanelles", "C) Sinuses", "D) Fosseae"], "answer": "B"},
                    {"question": "Where is the anterior fontanelle present?", "options": ["A) Junction of coronal and sagittal suture", "B) Junction of sagittal and lambdoid suture", "C) Junction of temporal and sphenoid", "D) At the mastoid process"], "answer": "A"},
                    {"question": "Normally, when does the anterior fontanelle close after birth?", "options": ["A) 1 to 3 months", "B) 6 months", "C) 18-24 months", "D) 36 months"], "answer": "C"},
                    {"question": "When does the posterior fontanelle normally close after birth?", "options": ["A) 6 months", "B) 12 months", "C) 18 months", "D) 24 months"], "answer": "A"},
                    {"question": "Which of the following is a clinical sign associated with the anterior fontanelle?", "options": ["A) It is shrunken in dehydration", "B) It bulges in increased intracranial tension", "C) It aids in estimating newborn age", "D) All of the above"], "answer": "D"},
                    {"question": "What is the anterior view of the skull called?", "options": ["A) Norma verticalis", "B) Norma frontalis", "C) Norma occipitalis", "D) Norma basalis"], "answer": "B"},
                    {"question": "Which bones share in the Norma frontalis?", "options": ["A) Frontal, zygomatic, maxillary, nasal, and lacrimal bones", "B) Occipital and temporal only", "C) Parietal and sphenoid only", "D) Mandible and vertebrae"], "answer": "A"},
                    {"question": "Where are the frontal eminences located?", "options": ["A) Two elevations one on each side of the frontal bone", "B) At the base of the occiput", "C) Inside the cranial cavity", "D) Along the sagittal suture"], "answer": "A"},
                    {"question": "Where is the supraorbital margin located?", "options": ["A) Below the mandible", "B) Above the orbital cavity", "C) Behind the external acoustic meatus", "D) Inside the nasal cavity"], "answer": "B"},
                    {"question": "Where are the superciliary arches located?", "options": ["A) Below frontal eminences and above orbital cavities", "B) On the medial side of the mandible", "C) Inside the orbit", "D) At the posterior skull"], "answer": "A"},
                    {"question": "The superciliary arches join in the middle line at what point?", "options": ["A) Nasion", "B) Glabella", "C) Bregma", "D) Lambda"], "answer": "B"},
                    {"question": "What is found in the medial third of the supraorbital margin?", "options": ["A) Supra-orbital notch or foramen", "B) Mental foramen", "C) Foramen ovale", "D) Carotid canal"], "answer": "A"},
                    {"question": "What lies in the midline of the Norma frontalis below the nasal bones?", "options": ["A) Anterior nasal opening", "B) Foramen magnum", "C) External occipital protuberance", "D) Pterion"], "answer": "A"},
                    {"question": "The two nasal bones unite in the midline by what suture?", "options": ["A) Internasal suture", "B) Coronal suture", "C) Lambdoid suture", "D) Sagittal suture"], "answer": "A"},
                    {"question": "What is the nasion defined as?", "options": ["A) Meeting of frontonasal and internasal sutures", "B) Meeting of sagittal and coronal sutures", "C) Tip of the mastoid process", "D) Center of the hard palate"], "answer": "A"},
                    {"question": "The maxilla carries what structures on its alveolar margin?", "options": ["A) Lower teeth", "B) Upper teeth", "C) Tongue papillae", "D) Salivary glands"], "answer": "B"},
                    {"question": "Which bone forms the prominence of the cheek?", "options": ["A) Zygomatic bone", "B) Frontal bone", "C) Mandible", "D) Temporal bone"], "answer": "A"},
                    {"question": "What does the zygomaticofacial foramen perforate?", "options": ["A) The zygomatic bone", "B) The frontal bone", "C) The parietal bone", "D) The occipital bone"], "answer": "A"},
                    {"question": "What does the infraorbital foramen transmit?", "options": ["A) Infraorbital nerve and vessels", "B) Facial nerve", "C) Mandibular nerve", "D) Lingual nerve"], "answer": "A"},
                    {"question": "What is the skull seen from behind called?", "options": ["A) Norma occipitalis", "B) Norma frontalis", "C) Norma lateralis", "D) Norma verticalis"], "answer": "A"},
                    {"question": "Which bones share in the Norma occipitalis?", "options": ["A) Occipital bone, parietal bone, and mastoid part of temporal bone", "B) Frontal and maxilla only", "C) Sphenoid and ethmoid only", "D) Zygomatic and nasal only"], "answer": "A"},
                    {"question": "What is the median projection in the back of the skull that is palpable in the living?", "options": ["A) External occipital protuberance", "B) Infratemporal crest", "C) Zygomatic arch", "D) Styloid process"], "answer": "A"},
                    {"question": "What is the external occipital crest?", "options": ["A) A median ridge extending down to the foramen magnum", "B) A lateral line on the forehead", "C) A suture on the vault", "D) A ridge inside the orbit"], "answer": "A"},
                    {"question": "How many nuchal lines are described in the Norma occipitalis section?", "options": ["A) One line", "B) Two lines", "C) Three lines (highest, superior, and inferior)", "D) Five lines"], "answer": "C"},
                    {"question": "What does the mastoid foramen transmit?", "options": ["A) An emissary vein between scalp veins and sigmoid sinus", "B) The optic nerve", "C) The facial nerve", "D) The lingual artery"], "answer": "A"},
                    {"question": "What forms the temporal lines?", "options": ["A) Superior and inferior temporal lines", "B) Anterior and posterior lines", "C) Internal and external plates", "D) Vertical and horizontal lines"], "answer": "A"},
                    {"question": "Which suture connects the parietal bone with the occipital bone?", "options": ["A) Coronal suture", "B) Lambdoid suture", "C) Sagittal suture", "D) Squamous suture"], "answer": "B"},
                    {"question": "What is the point of intersection between the sagittal and lambdoid sutures?", "options": ["A) Bregma", "B) Lambda", "C) Nasion", "D) Pterion"], "answer": "B"},
                    {"question": "Which bone forms the forehead and the upper part of the orbits?", "options": ["A) Frontal bone", "B) Parietal bone", "C) Occipital bone", "D) Temporal bone"], "answer": "A"}
                ]
            }
        },
        "custom_buttons": {},
        "users": []
    }
    
    if not os.path.exists(DATA_FILE):
        return default_data
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "sections" not in data:
                data["sections"] = default_data["sections"]
            else:
                for key in default_data["sections"]:
                    if key not in data["sections"]:
                        data["sections"][key] = default_data["sections"][key]
                if "ai_exams" not in data["sections"] or not data["sections"]["ai_exams"]:
                    data["sections"]["ai_exams"] = default_data["sections"]["ai_exams"]
                    
            if "users" not in data:
                data["users"] = []
            if "custom_buttons" not in data:
                data["custom_buttons"] = {}
                
            return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return default_data

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")

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
        [KeyboardButton("⚙️ لوحة الأدمن والإحصائيات"), KeyboardButton("❌ خروج")]
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
    days_dict = data["sections"]["محاضرات"].get("lectures", {}).get(week_name, {})
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

def get_ai_exams_reply_keyboard():
    data = load_data()
    ai_exams = data["sections"].get("ai_exams", {})
    keyboard = []
    for subject_name in ai_exams.keys():
        keyboard.append([KeyboardButton(f"✍️ امتحان: {subject_name}")])
    keyboard.append([KeyboardButton("🔙 رجوع للقائمة الرئيسية")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    register_user(user_id)
    context.user_data.clear()
    text_msg = "منور يا دكتور في بوت Uni Helper لطب أسنان جامعة الزقازيق الأهلية ZNU\n\nاختر من الأزرار بالأسفل:"
    await update.message.reply_text(text_msg, reply_markup=get_main_reply_keyboard())

async def send_or_edit_question(query, context, subject_name, feedback_text=""):
    user_data = context.user_data
    data = load_data()
    all_questions = data["sections"]["ai_exams"].get(subject_name, [])
    limit = user_data.get("exam_limit", len(all_questions))
    questions = all_questions[:limit]
    
    q_index = user_data.get("q_index", 0)
    
    if q_index >= len(questions):
        score = user_data.get("score", 0)
        total = len(questions)
        msg = f"انتهى امتحان مادة {subject_name} بنجاح\n\nدرجاتك: {score} من {total}\nعاش يا دكتور"
        user_data.clear()
        await query.message.edit_text(msg, reply_markup=None)
        await query.message.reply_text("اختر امتحان آخر لو تحب:", reply_markup=get_ai_exams_reply_keyboard())
        return

    q_data = questions[q_index]
    q_text = q_data.get("question")
    options = q_data.get("options", [])
    
    keyboard = []
    for opt in options:
        opt_letter = opt.split(")")[0].strip()
        keyboard.append([InlineKeyboardButton(opt, callback_data=f"ans_{subject_name}_{opt_letter}")])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    question_msg = f"{feedback_text}\n\nالسؤال رقم {q_index + 1} من {len(questions)}:\n{q_text}"
    
    await query.message.edit_text(question_msg, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data_callback = query.data
    
    if data_callback.startswith("count_"):
        parts = data_callback.split("_")
        subject_name = parts[1]
        count = int(parts[2])
        
        user_data = context.user_data
        user_data["q_index"] = 0
        user_data["score"] = 0
        user_data["exam_limit"] = count
        user_data["current_exam"] = subject_name
        
        await query.message.edit_text(f"تم اختيار {count} سؤال لمادة {subject_name}\nيبدأ الامتحان الآن...")
        await send_or_edit_question(query, context, subject_name)
        return

    if data_callback.startswith("ans_"):
        parts = data_callback.split("_")
        subject_name = parts[1]
        selected_option = parts[2]
        
        data = load_data()
        all_questions = data["sections"]["ai_exams"].get(subject_name, [])
        user_data = context.user_data
        limit = user_data.get("exam_limit", len(all_questions))
        questions = all_questions[:limit]
        
        q_index = user_data.get("q_index", 0)
        
        if q_index < len(questions):
            correct_answer = questions[q_index].get("answer").strip().upper()
            feedback = ""
            
            if selected_option == correct_answer:
                user_data["score"] = user_data.get("score", 0) + 1
                feedback = "إجابة صحيحة بطل"
            else:
                feedback = f"إجابة خاطئة الإجابة الصحيحة هي {correct_answer}"
                
            user_data["q_index"] = q_index + 1
            await send_or_edit_question(query, context, subject_name, feedback)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    register_user(user_id)
    
    user_data = context.user_data
    text = update.message.text.strip() if update.message.text else ""
    data = load_data()
    
    if text in ["❌ خروج", "🔙 رجوع للقائمة الرئيسية"]:
        user_data.clear()
        await update.message.reply_text("تم يا باشا، دي القائمة الرئيسية:", reply_markup=get_main_reply_keyboard())
        return

    if text == "🔙 رجوع للأسابيع":
        await update.message.reply_text("دي قائمة الأسابيع تاني:", reply_markup=get_weeks_reply_keyboard())
        return

    if text == "📚 المحاضرات":
        user_data.clear()
        lectures_dict = data["sections"]["محاضرات"].get("lectures", {})
        if not lectures_dict:
            await update.message.reply_text("لسه مفيش أي أسابيع مسجلة يا دكتور.", reply_markup=get_main_reply_keyboard())
            return
        await update.message.reply_text("اتفضل يا دكتور، دي قائمة الأسابيع", reply_markup=get_weeks_reply_keyboard())
        return

    if text.startswith("📅 "):
        week_name = text.replace("📅 ", "").strip()
        days_dict = data["sections"]["محاضرات"].get("lectures", {}).get(week_name, {})
        if not days_dict:
            await update.message.reply_text(f"مفيش أيام محطوطة في {week_name} لسه.", reply_markup=get_weeks_reply_keyboard())
            return
        await update.message.reply_text(f"قائمة {week_name}\nاختر اليوم:", reply_markup=get_days_reply_keyboard(week_name))
        return

    if text.startswith("🗓️ يوم "):
        try:
            parts = text.replace("🗓️ يوم ", "").split(" (")
            day_name = parts[0].strip()
            week_name = parts[1].replace(")", "").strip()
        except:
            return
            
        lectures_in_day = data["sections"]["محاضرات"].get("lectures", {}).get(week_name, {}).get(day_name, [])
        if not lectures_in_day:
            await update.message.reply_text(f"مفيش محاضرات مسجلة في يوم {day_name}.", reply_markup=get_days_reply_keyboard(week_name))
            return
            
        await update.message.reply_text(f"محاضرات يوم {day_name}")
        for item in lectures_in_day:
            name = item.get("name")
            files = item.get("files", [])
            await update.message.reply_text(f"محاضرة: {name}")
            for f in files:
                f_id = f.get("file_id")
                f_type = f.get("file_type")
                if f_type == "audio":
                    await context.bot.send_audio(chat_id=update.message.chat_id, audio=f_id)
                elif f_type == "voice":
                    await context.bot.send_voice(chat_id=update.message.chat_id, audio=f_id)
                elif f_type == "document":
                    await context.bot.send_document(chat_id=update.message.chat_id, document=f_id)
        return

    if text == "📚 كتب طب الأسنان":
        user_data.clear()
        books_list = data["sections"]["كتب"].get("items", [])
        if not books_list:
            await update.message.reply_text("لسه مفيش كتب مضافة يا دكتور.", reply_markup=get_main_reply_keyboard())
            return
        await update.message.reply_text("دي قائمة الكتب المتاحة:", reply_markup=get_books_reply_keyboard())
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
            await update.message.reply_text(f"كتاب: {book_title}")
            f_id = target_book.get("file_id")
            f_type = target_book.get("file_type", "document")
            if f_type == "audio":
                await context.bot.send_audio(chat_id=update.message.chat_id, audio=f_id)
            elif f_type == "voice":
                await context.bot.send_voice(chat_id=update.message.chat_id, audio=f_id)
            else:
                await context.bot.send_document(chat_id=update.message.chat_id, document=f_id)
        else:
            await update.message.reply_text("عذراً لم يتم العثور على هذا الكتاب.")
        return

    if text == "🔗 أهم الجروبات":
        user_data.clear()
        groups = data["sections"].get("groups", {})
        if not groups:
            await update.message.reply_text("مفيش جروبات مضافة حالياً يا دكتور.", reply_markup=get_main_reply_keyboard())
            return
            
        msg = "أهم الجروبات والروابط الرسمية للدفعة:\n\n"
        for g_name, g_link in groups.items():
            msg += f"- {g_name}: {g_link}\n"
        await update.message.reply_text(msg, reply_markup=get_main_reply_keyboard())
        return

    if text == "🎥 أفضل دكاترة يوتيوب":
        user_data.clear()
        yt_doctors = data["sections"].get("youtube_doctors", {})
        if not yt_doctors:
            await update.message.reply_text("لسه مفيش مواد أو شروحات مضافة حالياً يا دكتور.", reply_markup=get_main_reply_keyboard())
            return
        await update.message.reply_text("اختر المادة أو الشرح:", reply_markup=get_yt_reply_keyboard())
        return

    if text.startswith("🎓 دكتور: "):
        subject_name = text.replace("🎓 دكتور: ", "").strip()
        yt_doctors = data["sections"].get("youtube_doctors", {})
        yt_link = yt_doctors.get(subject_name)
        
        if yt_link:
            await update.message.reply_text(f"شرح مادة {subject_name}\nرابط الشرح: {yt_link}", reply_markup=get_yt_reply_keyboard())
        else:
            await update.message.reply_text("عذراً لم يتم العثور على هذا الشرح.")
        return

    if text == "🤖 تلخيصات AI":
        user_data.clear()
        ai_summaries = data["sections"].get("ai_summaries", {})
        if not ai_summaries:
            await update.message.reply_text("لسه مفيش تلخيصات مضافة من الإدارة حالياً يا دكتور.", reply_markup=get_main_reply_keyboard())
            return
            
        await update.message.reply_text("اختر التلخيص أو المادة:", reply_markup=get_ai_reply_keyboard())
        return

    if text.startswith("🤖 تلخيص: "):
        subject_name = text.replace("🤖 تلخيص: ", "").strip()
        ai_summaries = data["sections"].get("ai_summaries", {})
        target_summary = ai_summaries.get(subject_name)
        
        if target_summary:
            await update.message.reply_text(f"تلخيص مادة {subject_name}")
            f_id = target_summary.get("file_id")
            f_type = target_summary.get("file_type")
            if f_type == "audio":
                await context.bot.send_audio(chat_id=update.message.chat_id, audio=f_id, reply_markup=get_ai_reply_keyboard())
            elif f_type == "voice":
                await context.bot.send_voice(chat_id=update.message.chat_id, audio=f_id, reply_markup=get_ai_reply_keyboard())
            else:
                await context.bot.send_document(chat_id=update.message.chat_id, document=f_id, reply_markup=get_ai_reply_keyboard())
        else:
            await update.message.reply_text("عذراً لم يتم العثور على هذا التلخيص.")
        return

    if text == "✍️ امتحن نفسك (AI)":
        user_data.clear()
        ai_exams = data["sections"].get("ai_exams", {})
        if not ai_exams:
            await update.message.reply_text("لم يتم إضافة أي امتحانات حتى الآن يا دكتور.", reply_markup=get_main_reply_keyboard())
            return
            
        await update.message.reply_text("اختر مادة الامتحان لبدء التحدي:", reply_markup=get_ai_exams_reply_keyboard())
        return

    if text.startswith("✍️ امتحان: "):
        subject_name = text.replace("✍️ امتحان: ", "").strip()
        ai_exams = data["sections"].get("ai_exams", {})
        if subject_name not in ai_exams:
            await update.message.reply_text("عذراً لا توجد أسئلة لهذه المادة.")
            return
            
        keyboard = [
            [
                InlineKeyboardButton("10 أسئلة", callback_data=f"count_{subject_name}_10"),
                InlineKeyboardButton("30 سؤال", callback_data=f"count_{subject_name}_30"),
                InlineKeyboardButton("50 سؤال", callback_data=f"count_{subject_name}_50")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"اختر عدد الأسئلة التي تريدها لمادة {subject_name}:", reply_markup=reply_markup)
        return

    if text == "⚙️ لوحة الأدمن والإحصائيات":
        user_data.clear()
        user_data["state"] = "AUTH_ADMIN_PANEL"
        await update.message.reply_text("لوحة تحكم المسؤول\nأدخل كلمة مرور المسؤول:")
        return

    if text in ["➕ ضيف محاضرة", "اضافه محاضرة"] or text == "/addlecture":
        user_data.clear()
        user_data["state"] = "AUTH_PASSWORD"
        await update.message.reply_text("إضافة محاضرة\nأدخل كلمة مرور المسؤول:")
        return

    if text == "➕ ضيف كتاب":
        user_data.clear()
        user_data["state"] = "AUTH_BOOK_PASSWORD"
        await update.message.reply_text("إضافة كتاب جديد\nأدخل كلمة مرور المسؤول:")
        return

    if text in ["🗑️ امسح محاضرة", "/delete"]:
        user_data.clear()
        user_data["state"] = "AUTH_DELETE"
        await update.message.reply_text("حذف محاضرة\nأدخل كلمة مرور المسؤول:")
        return

    if text == "🗑️ امسح كتاب":
        user_data.clear()
        user_data["state"] = "AUTH_DELETE_BOOK"
        await update.message.reply_text("حذف كتاب\nأدخل كلمة مرور المسؤول:")
        return

    current_state = user_data.get("state")

    if current_state in ["AUTH_PASSWORD", "AUTH_BOOK_PASSWORD", "AUTH_DELETE", "AUTH_DELETE_BOOK", "AUTH_ADMIN_PANEL", "AUTH_BROADCAST", "AUTH_ADD_GROUP", "AUTH_ADD_YT", "AUTH_ADD_AI", "AUTH_ADD_EXAM"]:
        if text == ADMIN_PASSWORD:
            if current_state == "AUTH_PASSWORD":
                user_data["state"] = "WAITING_WEEK_NAME"
                await update.message.reply_text("تم. اكتب اسم الأسبوع (مثال: الاسبوع الاول):")
            elif current_state == "AUTH_BOOK_PASSWORD":
                user_data["state"] = "WAITING_BOOK_NAME"
                await update.message.reply_text("تم. اكتب اسم الكتاب الجديد الذي تريد إضافته:")
            elif current_state == "AUTH_DELETE":
                user_data["state"] = "WAITING_DELETE_WEEK"
                weeks = list(data["sections"]["محاضرات"].get("lectures", {}).keys())
                msg = "تم. اكتب اسم الأسبوع الذي تريد حذف يوم منه:"
                if weeks:
                    msg += f"\nالأسابيع المتاحة: {', '.join(weeks)}"
                await update.message.reply_text(msg)
            elif current_state == "AUTH_DELETE_BOOK":
                user_data["state"] = "WAITING_DELETE_BOOK_NAME"
                books_list = data["sections"]["كتب"].get("items", [])
                book_names = [b.get("name") for b in books_list]
                msg = "تم. اكتب اسم الكتاب الذي تريد مسحه:"
                if book_names:
                    msg += f"\nالكتب المتاحة: {', '.join(book_names)}"
                await update.message.reply_text(msg)
            elif current_state == "AUTH_ADMIN_PANEL":
                users_count = len(data.get("users", []))
                user_data.clear()
                keyboard = [
                    [KeyboardButton("📢 إرسال إعلان عام (Broadcast)")],
                    [KeyboardButton("➕ إضافة جروب مهم"), KeyboardButton("🎥 إضافة شرح يوتيوب")],
                    [KeyboardButton("🤖 إضافة تلخيص AI"), KeyboardButton("✍️ إضافة امتحان AI")],
                    [KeyboardButton("🔙 رجوع للقائمة الرئيسية")]
                ]
                await update.message.reply_text(f"لوحة التحكم والإحصائيات:\n\nإجمالي عدد المستخدمين للبوت: {users_count} طالب.\n\nاختر العملية المطلوبة من الأزرار بالأسفل:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            elif current_state == "AUTH_BROADCAST":
                user_data["state"] = "WAITING_BROADCAST_MESSAGE"
                await update.message.reply_text("أرسل الآن نص أو ملف الإعلان المراد إرساله للطلاب مباشرة:")
            elif current_state == "AUTH_ADD_GROUP":
                user_data["state"] = "WAITING_GROUP_LINK"
                await update.message.reply_text("أرسل الآن رابط الجروب:")
            elif current_state == "AUTH_ADD_YT":
                user_data["state"] = "WAITING_YT_LINK"
                await update.message.reply_text("أرسل الآن رابط مقطع أو نص يوتيوب الشرح:")
            elif current_state == "AUTH_ADD_AI":
                user_data["state"] = "WAITING_AI_FILE"
                await update.message.reply_text("أرسل الآن ملف التلخيص أو المقطع الصوتي الخاص بـ AI:")
            elif current_state == "AUTH_ADD_EXAM":
                user_data["state"] = "WAITING_EXAM_SUBJECT"
                await update.message.reply_text("أرسل الآن اسم المادة الخاصة بالامتحان (مثال: Anatomy نظري):")
        else:
            user_data.clear()
            await update.message.reply_text("كلمة المرور غير صحيحة", reply_markup=get_main_reply_keyboard())
        return

    if text == "📢 إرسال إعلان عام (Broadcast)":
        user_data.clear()
        user_data["state"] = "AUTH_BROADCAST"
        await update.message.reply_text("إرسال إعلان عام\nأدخل كلمة مرور المسؤول:")
        return

    if text == "➕ إضافة جروب مهم":
        user_data.clear()
        user_data["state"] = "AUTH_ADD_GROUP"
        await update.message.reply_text("إضافة جروب\nأدخل كلمة مرور المسؤول:")
        return

    if text == "🎥 إضافة شرح يوتيوب":
        user_data.clear()
        user_data["state"] = "AUTH_ADD_YT"
        await update.message.reply_text("إضافة شرح يوتيوب\nأدخل كلمة مرور المسؤول:")
        return

    if text == "🤖 إضافة تلخيص AI":
        user_data.clear()
        user_data["state"] = "AUTH_ADD_AI"
        await update.message.reply_text("إضافة تلخيص AI\nأدخل كلمة مرور المسؤول:")
        return

    if text == "✍️ إضافة امتحان AI":
        user_data.clear()
        user_data["state"] = "AUTH_ADD_EXAM"
        await update.message.reply_text("إضافة امتحان AI جديد\nأدخل كلمة مرور المسؤول:")
        return

    if current_state == "WAITING_EXAM_SUBJECT":
        user_data["temp_exam_subject"] = text
        user_data["state"] = "WAITING_EXAM_DATA"
        await update.message.reply_text("تم اعتماد الامتحان بنجاح للمادة الجديدة")
        return

    if current_state == "WAITING_EXAM_DATA":
        subject = user_data.get("temp_exam_subject", "Anatomy نظري")
        user_data.clear()
        await update.message.reply_text(f"تم حفظ الامتحان بنجاح تحت اسم {subject}", reply_markup=get_main_reply_keyboard())
        return

    if current_state == "WAITING_BROADCAST_MESSAGE":
        users = data.get("users", [])
        success_count = 0
        await update.message.reply_text("جاري إرسال الرسالة لجميع المستخدمين...")
        for uid in users:
            try:
                await context.bot.send_message(chat_id=uid, text=text)
                success_count += 1
            except Exception:
                pass
        user_data.clear()
        await update.message.reply_text(f"تم إرسال الرسالة بنجاح إلى {success_count} مستخدماً من إجمالي {len(users)}.", reply_markup=get_main_reply_keyboard())
        return

    if current_state == "WAITING_GROUP_LINK":
        user_data["temp_group_link"] = text
        user_data["state"] = "WAITING_GROUP_NAME"
        await update.message.reply_text("الآن أرسل اسم الجروب:")
        return

    if current_state == "WAITING_GROUP_NAME":
        g_link = user_data.get("temp_group_link")
        g_name = text
        if "groups" not in data["sections"]:
            data["sections"]["groups"] = {}
        data["sections"]["groups"][g_name] = g_link
        save_data(data)
        user_data.clear()
        await update.message.reply_text(f"تم إضافة الجروب {g_name} بنجاح", reply_markup=get_main_reply_keyboard())
        return

    if current_state == "WAITING_YT_LINK":
        user_data["temp_yt_link"] = text
        user_data["state"] = "WAITING_YT_SUBJECT_NAME"
        await update.message.reply_text("الآن أرسل اسم المادة الخاصة بالشرح:")
        return

    if current_state == "WAITING_YT_SUBJECT_NAME":
        yt_link = user_data.get("temp_yt_link")
        subject_name = text
        if "youtube_doctors" not in data["sections"]:
            data["sections"]["youtube_doctors"] = {}
        data["sections"]["youtube_doctors"][subject_name] = yt_link
        save_data(data)
        user_data.clear()
        await update.message.reply_text(f"تم حفظ شرح مادة {subject_name} بنجاح", reply_markup=get_main_reply_keyboard())
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
            await update.message.reply_text("ممتاز. الآن أرسل اسم المادة أو عنوان التلخيص:")
            return
        else:
            await update.message.reply_text("من فضلك أرسل ملف التلخيص أو المقطع أولاً.")
            return

    if current_state == "WAITING_AI_SUBJECT_NAME":
        subject_name = text
        f_id = user_data.get("temp_ai_file_id")
        f_type = user_data.get("temp_ai_file_type")
        
        if "ai_summaries" not in data["sections"]:
            data["sections"]["ai_summaries"] = {}
            
        data["sections"]["ai_summaries"][subject_name] = {"file_id": f_id, "file_type": f_type}
        save_data(data)
        user_data.clear()
        
        await update.message.reply_text(f"تم حفظ تلخيص مادة {subject_name} بنجاح", reply_markup=get_main_reply_keyboard())
        return

    if current_state == "WAITING_BOOK_NAME":
        if not text:
            await update.message.reply_text("من فضلك اكتب اسم الكتاب بشكل صحيح.")
            return
        user_data["temp_book_name"] = text
        user_data["state"] = "WAITING_BOOK_FILE"
        await update.message.reply_text(f"سجلنا اسم الكتاب {text}\nالآن أرسل ملف الكتاب:", reply_markup=get_main_reply_keyboard())
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
                
            data["sections"]["كتب"]["items"].append({"name": book_name, "file_id": file_id, "file_type": file_type} )
            save_data(data)
            user_data.clear()
            
            await update.message.reply_text(f"تم حفظ الكتاب {book_name} بنجاح", reply_markup=get_main_reply_keyboard())
            return
        else:
            await update.message.reply_text("من فضلك أرسل ملف الكتاب لكي نتمكن من حفظه.")
            return

    if current_state == "WAITING_DELETE_BOOK_NAME":
        target_book_name = text
        books_list = data["sections"]["كتب"].get("items", [])
        updated_books = [b for b in books_list if b.get("name") != target_book_name]
        
        if len(updated_books) < len(books_list):
            data["sections"]["كتب"]["items"] = updated_books
            save_data(data)
            user_data.clear()
            await update.message.reply_text(f"تم حذف الكتاب {target_book_name} بنجاح", reply_markup=get_main_reply_keyboard())
        else:
            user_data.clear()
            await update.message.reply_text(f"لم يتم العثور على كتاب بهذا الاسم {target_book_name}.", reply_markup=get_main_reply_keyboard())
        return

    if current_state == "WAITING_DELETE_WEEK":
        target_week = text
        lectures_sec = data["sections"]["محاضرات"].get("lectures", {})
        if target_week in lectures_sec:
            user_data["delete_week_target"] = target_week
            user_data["state"] = "WAITING_DELETE_DAY"
            days = list(lectures_sec[target_week].keys())
            await update.message.reply_text(f"الأيام المتاحة في {target_week}: [{', '.join(days) if days else 'لا توجد'}]. اكتب اسم اليوم المراد حذفه:")
        else:
            user_data.clear()
            await update.message.reply_text("الأسبوع غير موجود.", reply_markup=get_main_reply_keyboard())
        return

    if current_state == "WAITING_DELETE_DAY":
        target_day = text
        target_week = user_data.get("delete_week_target")
        lectures_sec = data["sections"]["محاضرات"].get("lectures", {})
        if target_week in lectures_sec and target_day in lectures_sec[target_week]:
            del lectures_sec[target_week][target_day]
            save_data(data)
            user_data.clear()
            await update.message.reply_text(f"تم حذف يوم {target_day} بنجاح", reply_markup=get_main_reply_keyboard())
        else:
            user_data.clear()
            await update.message.reply_text("اليوم غير موجود.", reply_markup=get_main_reply_keyboard())
        return

    if current_state == "WAITING_WEEK_NAME":
        if not text:
            await update.message.reply_text("من فضلك اكتب اسم الأسبوع بشكل صحيح.")
            return
        user_data["temp_week_name"] = text
        user_data["state"] = "WAITING_DAY_CHOICE"
        keyboard = [
            [KeyboardButton("الثلاثاء"), KeyboardButton("الأربعاء"), KeyboardButton("الخميس")],
            [KeyboardButton("إلغاء")]
        ]
        await update.message.reply_text(f"سجلنا الأسبوع {text}. اختر اليوم من الأزرار بالأسفل:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    if current_state == "WAITING_DAY_CHOICE":
        if text == "إلغاء":
            user_data.clear()
            await update.message.reply_text("تم الإلغاء.", reply_markup=get_main_reply_keyboard())
            return
        if text not in ["الثلاثاء", "الأربعاء", "الخميس"]:
            await update.message.reply_text("من فضلك اختر اليوم من الأزرار الموجودة بالأسفل.")
            return
        user_data["temp_day_name"] = text
        user_data["temp_files"] = []
        user_data["temp_caption"] = None
        user_data["state"] = "WAITING_FILES"
        await update.message.reply_text(f"اخترت يوم {text}\nأرسل الملفات أو الفويس وبعد ما تخلص أرسل اسم المحاضرة في رسالة:", reply_markup=get_main_reply_keyboard())
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
            user_data["temp_files"].append({"file_id": file_id, "file_type": file_type})
            if update.message.caption:
                user_data["temp_caption"] = update.message.caption.strip()
                
            await update.message.reply_text(f"تم استلام الملف وإجمالي الملفات {len(user_data['temp_files'])}. أرسل تاني أو اكتب اسم المحاضرة في رسالة:")
            return
        else:
            lecture_name = text if text else user_data.get("temp_caption")
            if not lecture_name:
                if user_data.get("temp_files"):
                    lecture_name = "محاضرة بدون اسم"
                else:
                    await update.message.reply_text("أنت لم ترسل أي ملفات أرسل الملفات أولاً.")
                    return
                    
            week_name = user_data.get("temp_week_name")
            day_name = user_data.get("temp_day_name")
            files_list = user_data.get("temp_files")
            lectures_dict = data["sections"]["محاضرات"]["lectures"]
            
            if week_name not in lectures_dict:
                lectures_dict[week_name] = {}
            if day_name not in lectures_dict[week_name]:
                lectures_dict[week_name][day_name] = []
                
            lectures_dict[week_name][day_name].append({"name": lecture_name, "files": files_list})
            save_data(data)
            user_data.clear()
            
            await update.message.reply_text(f"تم حفظ المحاضرة {lecture_name} بنجاح", reply_markup=get_main_reply_keyboard())
            return

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port))
    web_thread.daemon = True
    web_thread.start()

    TOKEN = "8964990492:AAFy3kskRFG46huYcmCcUthpPdF4Tx_tvJw"
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(button_callback))
    app_bot.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    app_bot.run_polling()
