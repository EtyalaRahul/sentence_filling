import streamlit as st
from groq import Groq
import time
import json
import re
import random
import hashlib

st.set_page_config(page_title="TCS NQT Verbal Prep", page_icon="⚡", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Mono', monospace; }
.big-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem; font-weight: 700;
    background: linear-gradient(90deg, #7C5CFF, #00E0B8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.subtitle { color: #8A8FA3; font-size: 0.9rem; margin-bottom: 1.2rem; }
.question-card {
    background: #1c1f2e; border: 1px solid #2e324a;
    border-radius: 16px; padding: 28px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.passage-card {
    background: #12162a; border: 2px solid #7C5CFF55;
    border-radius: 16px; padding: 28px;
    box-shadow: 0 4px 32px rgba(124,92,255,0.15);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem; color: #E8E8F8; line-height: 1.9;
}
.recall-card {
    background: #0f1a18; border: 2px solid #00E0B855;
    border-radius: 16px; padding: 22px;
    box-shadow: 0 4px 32px rgba(0,224,184,0.1);
}
.email-card {
    background: #0f1422; border: 2px solid #7C5CFF55;
    border-radius: 16px; padding: 22px;
    box-shadow: 0 4px 32px rgba(124,92,255,0.15);
}
.phase-badge {
    display: inline-block; border-radius: 999px;
    padding: 5px 18px; font-size: 0.78rem; font-weight: 700;
    letter-spacing: 0.08em; margin-bottom: 16px;
}
.phase-read  { background: #7C5CFF22; color: #B8A6FF; border: 1px solid #7C5CFF55; }
.phase-write { background: #00E0B822; color: #00E0B8;  border: 1px solid #00E0B855; }
.phase-done  { background: #FF6B3522; color: #FF9966;  border: 1px solid #FF6B3555; }
.phase-email { background: #FFD70022; color: #FFD700;  border: 1px solid #FFD70055; }
.q-tag {
    display: inline-block; background: #7C5CFF22; color: #B8A6FF;
    border: 1px solid #7C5CFF55; border-radius: 999px;
    padding: 4px 14px; font-size: 0.75rem; letter-spacing: 0.05em; margin-bottom: 14px;
}
.reinforce-tag {
    display: inline-block; background: #FF6B3522; color: #FF9966;
    border: 1px solid #FF6B3555; border-radius: 999px;
    padding: 4px 14px; font-size: 0.75rem; letter-spacing: 0.05em; margin-bottom: 14px; margin-left: 8px;
}
.llm-tag {
    display: inline-block; background: #00E0B822; color: #00E0B8;
    border: 1px solid #00E0B855; border-radius: 999px;
    padding: 4px 14px; font-size: 0.75rem; letter-spacing: 0.05em; margin-bottom: 14px; margin-left: 8px;
}
.q-text { font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; color: #F3F3F7; line-height: 1.6; }
.q-num  { font-size: 0.75rem; color: #8A8FA3; margin-bottom: 10px; }
.timer-box {
    text-align: center; font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem; font-weight: 700; color: #00E0B8;
    border: 2px solid #00E0B8; border-radius: 50%;
    width: 65px; height: 65px; display: flex; align-items: center; justify-content: center; margin: 0 auto;
}
.timer-warn  { color: #FF6B35 !important; border-color: #FF6B35 !important; }
.timer-read  { color: #7C5CFF !important; border-color: #7C5CFF !important; }
.timer-write { color: #00E0B8 !important; border-color: #00E0B8 !important; }
.timer-email { color: #FFD700 !important; border-color: #FFD700 !important; }
.correct-box { background: #0d2b1f; border: 1px solid #1f9d6b; border-radius: 12px; padding: 18px; color: #6EE7B7; }
.wrong-box   { background: #2b0d12; border: 1px solid #c5455a; border-radius: 12px; padding: 18px; color: #FCA5A5; }
.lesson-box  { background: #1a1f2e; border-left: 4px solid #7C5CFF; border-radius: 8px; padding: 18px 22px; margin-top: 14px; color: #E4E4F0; }
.levelup-box { background: #1a2e1f; border-left: 4px solid #00E0B8;  border-radius: 8px; padding: 18px 22px; margin-top: 14px; color: #E4E4F0; }
.recall-score-box { background: #12162a; border: 2px solid #7C5CFF55; border-radius: 14px; padding: 22px; margin-top: 14px; color: #E4E4F0; }
.score-pill  { background: #1c1f2e; border-radius: 999px; padding: 8px 20px; display: inline-block; font-size: 0.85rem; color: #00E0B8; border: 1px solid #2e324a; }
.missed-chip { display: inline-block; background: #2b0d12; color: #FCA5A5; border: 1px solid #c5455a55; border-radius: 8px; padding: 4px 12px; margin: 4px; font-size: 0.8rem; }
.info-bar { background: #1a1f2e; border-radius: 10px; padding: 12px 18px; color: #8A8FA3; font-size: 0.82rem; margin-bottom: 12px; border: 1px solid #2e324a; }
.email-score-box { background: #12162a; border: 2px solid #FFD70055; border-radius: 14px; padding: 22px; margin-top: 14px; color: #E4E4F0; }
.stButton > button { background: linear-gradient(90deg, #7C5CFF, #00E0B8); color: #0f1117; font-weight: 700; border: none; border-radius: 10px; padding: 0.6rem 1.4rem; transition: transform 0.15s ease; }
.stButton > button:hover { transform: scale(1.03); }
.stTextArea textarea { background: #12162a !important; color: #E8E8F8 !important; border: 1px solid #2e324a !important; border-radius: 10px !important; font-family: 'IBM Plex Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  CONSTANTS — TCS NQT EXACT SPECS
# ═══════════════════════════════════════════════════════════════════════════

READ_TIME   = 30    # seconds to read passage (TCS spec)
WRITE_TIME  = 90    # seconds to reconstruct passage (TCS spec)
TIME_LIMIT  = 25    # seconds for sentence completion (TCS spec)
EMAIL_TIME  = 540   # seconds for email writing = 9 minutes (TCS spec)
EMAIL_MIN_WORDS = 100  # minimum words for email (TCS spec)
MAX_REINFORCE = 2

CATEGORY_FILTER = {
    "All Categories": None,
    "Workplace & Professional": "Workplace & Professional",
    "Technology & Science": "Technology & Science",
    "Social & Current Affairs": "Social & Current Affairs",
    "Academic & Student Life": "Academic & Student Life",
    "Tone & Context Awareness": "Tone & Context Awareness",
}

CATEGORY_THEMES = {
    "Workplace & Professional": "office tasks, appraisals, team meetings, client communication, corporate decisions",
    "Technology & Science": "AI research, software engineering, space missions, cybersecurity, scientific discoveries",
    "Social & Current Affairs": "government policy, climate change, social justice, media, public health",
    "Academic & Student Life": "exams, internships, research papers, campus life, faculty, placements",
    "Tone & Context Awareness": "contrast sentences with positive/negative/neutral tone shifts, adjective and adverb blanks",
}

PASSAGE_CATEGORIES = list(CATEGORY_THEMES.keys())

# ── 100-200 seed words per category ────────────────────────────────────────
SEED_WORDS = {
    "Workplace & Professional": [
        "deadline","appraisal","promotion","resignation","delegation","collaboration","efficiency",
        "presentation","invoice","feedback","onboarding","negotiation","compliance","recruitment",
        "strategy","budget","milestone","stakeholder","performance","productivity","initiative",
        "leadership","mentorship","workflow","approval","supervision","restructuring","incentive",
        "accountability","agenda","alliance","amendment","arbitration","attrition","audit",
        "authorization","benchmark","boardroom","briefing","bureaucracy","candidate","capacity",
        "certification","chairperson","client","closure","commission","commitment","competency",
        "confidentiality","consensus","consultation","contract","coordination","corporation",
        "counseling","credibility","crisis","cross-functional","customer","cutback","dashboard",
        "debrief","decision","deliverable","department","deputy","designation","directive",
        "disbursement","disclosure","dismissal","dispute","disruption","diversity","downsizing",
        "draft","due-diligence","empowerment","endorsement","escalation","ethics","evaluation",
        "expansion","expense","facilitation","forecasting","formulation","framework","grievance",
        "growth","handover","headcount","hierarchy","hiring","implementation","increment",
        "induction","integration","inventory","KPI","liaison","logistics","mandate","mediation",
        "merger","minutes","morale","motivation","networking","objective","operations",
        "outsourcing","overtime","partnership","payroll","pipeline","planning","policy",
        "portfolio","probation","procurement","profit","project","proposal","protocol",
        "punctuality","quota","recognition","redundancy","reimbursement","reporting","retention",
        "revenue","review","risk","roadmap","schedule","shortlisting","skillset","staffing",
        "succession","survey","sustainability","target","teamwork","tenure","termination",
        "timeline","training","transfer","transparency","turnaround","upskilling","vendor",
        "vision","workload","workshop","SLA","roster","rotation",
    ],
    "Technology & Science": [
        "algorithm","bandwidth","debugging","encryption","firmware","deployment","prototype",
        "simulation","hypothesis","calibration","automation","integration","optimization",
        "cybersecurity","satellite","genome","telescope","semiconductor","neural","database",
        "latency","virtualization","repository","compiler","authentication","quantum","sensor",
        "abstraction","agile","analytics","anomaly","API","architecture","artificial-intelligence",
        "backup","benchmark","bioinformatics","blockchain","botnet","cache","checksum","circuit",
        "cloning","cloud","code-review","cognitive","compilation","concurrency","configuration",
        "connectivity","container","data-mining","decryption","deep-learning","dependency",
        "diagnosis","distributed","DNS","docker","ecosystem","electromagnetism","endpoint",
        "entropy","experiment","extrapolation","fiber-optic","forensics","frequency","GPU",
        "hashing","hosting","inference","innovation","interface","IoT","iteration","kernel",
        "library","load-balancing","logging","machine-learning","malware","middleware","migration",
        "modeling","module","monitoring","nanotechnology","network","neural-network","node",
        "open-source","parameter","patch","payload","physics","pipeline","platform","plugin",
        "prediction","protocol","proxy","radiation","regression","rendering","replication",
        "research","robotics","runtime","scalability","schema","scripting","security","server",
        "signal","software","spectrum","stack","storage","streaming","syntax","testing",
        "thread","topology","transaction","transmission","update","validation","variable",
        "version-control","vulnerability","wavelength","wireless","machine-learning","API",
    ],
    "Social & Current Affairs": [
        "legislation","advocacy","referendum","humanitarian","infrastructure","sanitation",
        "deforestation","migration","pandemic","unemployment","subsidy","transparency","reform",
        "inequality","censorship","vaccination","welfare","climate","diplomacy","sovereignty",
        "nutrition","corruption","education","poverty","governance","regulation","protest",
        "accountability","activism","addiction","affirmative-action","agriculture","aid",
        "alienation","allocation","amnesty","anarchy","asylum","austerity","authoritarianism",
        "bias","biodiversity","border","boycott","capitalism","carbon-footprint","caste",
        "citizenship","civil-rights","coalition","communalism","community","compensation",
        "conflict","conservation","constitution","consumption","controversy","coup","crime",
        "crisis","cultural","cybercrime","debt","decentralization","deficit","democracy",
        "demographic","deprivation","development","dignity","disability","discrimination",
        "disparity","displacement","drought","economic","election","embargo","emission",
        "empowerment","epidemic","equity","ethnicity","exploitation","extremism","famine",
        "federalism","feminism","flooding","food-security","freedom","gender","geopolitics",
        "globalization","health","homelessness","human-rights","identity","immigration",
        "impeachment","incarceration","inclusion","indigenous","inflation","injustice",
        "insurgency","judicial","justice","labour","land-rights","law","lobbying","manifesto",
        "media","minority","nationalism","natural-disaster","NGO","obesity","oppression",
        "parliament","peacekeeping","polarization","policy","pollution","population","privilege",
        "propaganda","public-health","racism","recession","reconciliation","rehabilitation",
        "religion","representation","resilience","rights","rural","secularism","segregation",
        "social-media","strike","suffrage","surveillance","sustainable","taxation","terrorism",
        "treaty","urbanization","violence","xenophobia",
    ],
    "Academic & Student Life": [
        "dissertation","plagiarism","scholarship","internship","assessment","curriculum",
        "semester","attendance","fellowship","thesis","examination","placement","faculty",
        "laboratory","assignment","enrollment","competition","elective","graduation","project",
        "research","seminar","workshop","presentation","deadline","revision","mentorship",
        "absenteeism","accreditation","achievement","activity","admission","advisement",
        "affiliation","alumni","annotation","aptitude","archive","aspiration","backlogs",
        "campus","career","certificate","chapter","citation","class","coaching","cohort",
        "collaboration","college","comprehension","conference","convocation","course","credit",
        "debate","degree","demonstration","department","detention","diploma","discipline",
        "discussion","distinction","dormitory","dropout","eligibility","essay","evaluation",
        "experiment","extracurricular","fees","fieldwork","final-exam","foundation","CGPA",
        "grade","group-study","guidance","hackathon","hall-ticket","honor","hostel","hypothesis",
        "institution","interview","journal","knowledge","lecture","library","literature","marks",
        "module","notes","objective","olympiad","orientation","outline","peer","performance",
        "portfolio","practical","professor","quiz","rank","reasoning","record","reference",
        "registration","report","result","review","schedule","session","skill","study",
        "subject","submission","syllabus","talent","task","teacher","team","test","textbook",
        "theory","timetable","topic","training","transcript","tutorial","university","viva",
        "vocabulary","writing","scholarship","internship",
    ],
    "Tone & Context Awareness": [
        "reluctantly","enthusiastically","cautiously","abruptly","sincerely","meticulously",
        "consistently","unexpectedly","gradually","firmly","politely","passionately",
        "desperately","efficiently","temporarily","remarkably","significantly","precisely",
        "calmly","boldly","deliberately","rapidly","quietly","graciously","diligently",
        "accurately","aggressively","ambiguously","anxiously","apologetically","assertively",
        "attentively","awkwardly","briefly","briskly","candidly","carefully","cheerfully",
        "cleverly","coldly","compassionately","competently","concisely","condescendingly",
        "confusingly","constructively","contentedly","critically","curiously","cynically",
        "decisively","defensively","defiantly","dependably","directly","discreetly",
        "dismissively","dutifully","eagerly","earnestly","elegantly","empathetically",
        "equally","evasively","explicitly","expressively","fairly","faithfully","fearlessly",
        "fluently","forcefully","formally","frankly","freely","generously","gently",
        "gratefully","harshly","helpfully","honestly","humbly","impatiently","impeccably",
        "impressively","indifferently","informally","insistently","intently","ironically",
        "justly","keenly","kindly","logically","loyally","meekly","mindfully","modestly",
        "naively","neutrally","obediently","objectively","openly","optimistically","patiently",
        "perceptively","persistently","pessimistically","pointedly","powerfully","proactively",
        "professionally","promptly","proudly","prudently","rationally","reassuringly",
        "recklessly","remorsefully","respectfully","responsibly","ruthlessly","sarcastically",
        "sensibly","sharply","skillfully","slowly","smoothly","softly","spontaneously",
        "sternly","stubbornly","subtly","suddenly","swiftly","tactfully","thoughtfully",
        "timidly","transparently","trustworthily","urgently","vaguely","vigorously",
        "warmly","wisely","zealously",
    ],
}

# ── Email scenario templates for variety ────────────────────────────────
EMAIL_SCENARIOS = [
    {
        "situation": "Your team's project deadline has been moved up by one week without prior notice. Your manager has sent an email saying all deliverables must be submitted by Friday. You are concerned this is not feasible as two team members are on approved leave and a key dependency is still pending from another department.",
        "task": "Write an email to your manager explaining the challenges with the new deadline, providing specific reasons why it may not be achievable, and proposing a realistic alternative timeline or solution.",
        "to": "Your Manager",
        "subject_hint": "Concern Regarding Revised Project Deadline",
    },
    {
        "situation": "You attended a job interview last week at a reputed IT company for a Software Engineer role. The interviewer mentioned that results would be communicated within five working days. It has now been eight days and you have not received any response. You remain very interested in the position.",
        "task": "Write a follow-up email to the HR department politely enquiring about the status of your application and reiterating your interest in the role.",
        "to": "HR Department",
        "subject_hint": "Follow-Up on Software Engineer Interview",
    },
    {
        "situation": "Your college's placement cell has scheduled a campus recruitment drive. However, the date clashes with your end-semester examinations. Many students in your batch are facing the same conflict and have approached you as their class representative to raise this issue.",
        "task": "Write an email to the Placement Coordinator requesting a change in the recruitment drive date, explaining the reason for the conflict and suggesting alternative dates.",
        "to": "Placement Coordinator",
        "subject_hint": "Request to Reschedule Campus Recruitment Drive",
    },
    {
        "situation": "You are an employee who recently completed an advanced certification in cloud computing at your own expense. Your company has a policy of reimbursing employees for job-relevant certifications upon submission of proof, but your reimbursement claim has been pending for over three months despite multiple verbal reminders.",
        "task": "Write a formal email to the HR and Finance department requesting urgent processing of your reimbursement, providing relevant details and a polite but firm tone.",
        "to": "HR and Finance Department",
        "subject_hint": "Pending Reimbursement for Cloud Certification",
    },
    {
        "situation": "Your team recently launched a new product feature that received overwhelmingly positive feedback from clients. Your team lead and two colleagues put in exceptional overtime hours to meet the release deadline. You wish to formally appreciate their contribution.",
        "task": "Write an email to your department head appreciating your team lead and colleagues for their contribution, highlighting the positive impact of their work and suggesting that their effort be formally recognised.",
        "to": "Department Head",
        "subject_hint": "Appreciation for Team's Exceptional Contribution",
    },
    {
        "situation": "A new company policy mandates that all employees must complete a cybersecurity awareness training module within two weeks. You are a team lead and several of your team members are currently occupied with a critical product release during this period. Completing the training on time may impact delivery quality.",
        "task": "Write an email to your HR Business Partner explaining the situation, requesting an extension for your team to complete the training after the product release, and assuring compliance within the extended timeframe.",
        "to": "HR Business Partner",
        "subject_hint": "Request for Extension on Cybersecurity Training Deadline",
    },
    {
        "situation": "You ordered a laptop from an online retailer for official use three weeks ago. Despite multiple delivery attempts, the package was marked as delivered but never received. You have already contacted the courier company, which has asked you to raise a complaint with the retailer.",
        "task": "Write a formal complaint email to the retailer's customer support team, describing the situation clearly, providing order details, and requesting an urgent resolution such as a replacement or refund.",
        "to": "Customer Support Team",
        "subject_hint": "Complaint Regarding Non-Delivery of Order",
    },
    {
        "situation": "Your organisation is organising its annual company picnic and has asked for volunteers to help with planning and coordination. You are enthusiastic about contributing but are uncertain about your weekend availability due to an ongoing personal project.",
        "task": "Write an email to the event organising committee expressing your interest in volunteering, explaining your availability constraints, and suggesting specific roles you could take on without conflicts.",
        "to": "Event Organising Committee",
        "subject_hint": "Expression of Interest in Volunteering for Annual Picnic",
    },
]

# ═══════════════════════════════════════════════════════════════════════════
#  DEDUP HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def _sentence_hash(sentence: str) -> str:
    return hashlib.md5(_normalize(sentence).encode()).hexdigest()

# ═══════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════

def reset_vocab_state():
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.current_q = None
    st.session_state.start_time = None
    st.session_state.answered = False
    st.session_state.user_answer = ""
    st.session_state.live_answer = ""
    st.session_state.feedback = None
    st.session_state.lesson = None
    st.session_state.suggestion = None
    st.session_state.history = []
    st.session_state.missed_bank = []
    st.session_state.is_reinforce = False
    st.session_state.asked_hashes = set()
    st.session_state.asked_sentences = []
    st.session_state.used_seeds = {cat: [] for cat in CATEGORY_THEMES}
    st.session_state.cat_rotation_idx = 0

def reset_recall_state():
    st.session_state.pr_phase = "read"
    st.session_state.pr_passage = None
    st.session_state.pr_topic = None
    st.session_state.pr_start_time = None
    st.session_state.pr_live_text = ""
    st.session_state.pr_submitted_text = ""
    st.session_state.pr_score_data = None
    st.session_state.pr_history = []
    st.session_state.pr_count = 0

def reset_email_state():
    st.session_state.em_phase = "task"      # "task" | "writing" | "scored"
    st.session_state.em_scenario = None
    st.session_state.em_start_time = None
    st.session_state.em_live_text = ""
    st.session_state.em_submitted_text = ""
    st.session_state.em_score_data = None
    st.session_state.em_history = []
    st.session_state.em_count = 0
    st.session_state.em_used_scenarios = []

# ── Initialise all keys ──────────────────────────────────────────────────
_defaults = {
    "page": "setup",
    "score": 0, "total": 0,
    "current_q": None, "start_time": None,
    "answered": False, "is_reinforce": False,
    "user_answer": "", "live_answer": "",
    "feedback": None, "lesson": None, "suggestion": None,
    "history": [], "missed_bank": [], "asked_sentences": [],
    "asked_hashes": set(),
    "used_seeds": {cat: [] for cat in CATEGORY_THEMES},
    "cat_rotation_idx": 0,
    # passage recall
    "pr_phase": "read",
    "pr_passage": None, "pr_topic": None,
    "pr_start_time": None,
    "pr_live_text": "", "pr_submitted_text": "",
    "pr_score_data": None,
    "pr_history": [], "pr_count": 0,
    # email writing
    "em_phase": "task",
    "em_scenario": None, "em_start_time": None,
    "em_live_text": "", "em_submitted_text": "",
    "em_score_data": None,
    "em_history": [], "em_count": 0,
    "em_used_scenarios": [],
    "mode": "vocab",
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════════════════
#  GROQ HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def get_client(api_key):
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Groq error: {e}")
        st.stop()

def _call(client, messages, max_tokens=600, temp=0.7):
    resp = client.chat.completions.create(
        messages=messages, model="llama-3.3-70b-versatile",
        temperature=temp, max_tokens=max_tokens,
    )
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)

# ── Vocab Sprint helpers ─────────────────────────────────────────────────

def check_answer(client, sentence, accepted_answers, user_answer):
    ua = user_answer.strip().lower()
    if not ua:
        return False
    for ans in accepted_answers:
        if ua == ans.lower() or ans.lower() in ua or ua in ans.lower():
            return True
    try:
        resp = client.chat.completions.create(
            messages=[
                {"role":"system","content":"Strict English evaluator. Reply YES or NO only."},
                {"role":"user","content":f'Sentence: "{sentence}"\nAccepted: {accepted_answers}\nStudent: "{user_answer}"\nIs it correct? YES or NO.'}
            ],
            model="llama-3.3-70b-versatile", temperature=0.1, max_tokens=5
        )
        return "YES" in resp.choices[0].message.content.upper()
    except Exception:
        return False

def generate_lesson(client, word, sentence):
    try:
        return _call(client, [
            {"role":"system","content":"English teacher. Return valid JSON only."},
            {"role":"user","content":f'Word missed: "{word}" in: "{sentence}"\nReturn JSON: {{"meaning":"1-line def","synonyms":["s1","s2","s3"],"examples":["ex1","ex2"],"memory_tip":"tip","related_words":[{{"word":"w","meaning":"m","example":"e"}}]}}'}
        ], max_tokens=600)
    except Exception:
        return {"meaning":f"{word}: key vocabulary word.","synonyms":[],"examples":[],"memory_tip":"Review this word.","related_words":[]}

def generate_suggestion(client, word, sentence):
    try:
        return _call(client, [
            {"role":"system","content":"English tutor. Return valid JSON only."},
            {"role":"user","content":f'Student got "{word}" correct in: "{sentence}"\nReturn JSON: {{"tip":"1-2 sentence tip","advanced_word":"word","advanced_meaning":"meaning"}}'}
        ], max_tokens=200, temp=0.7)
    except Exception:
        return {"tip":f"Great use of '{word}'!","advanced_word":"","advanced_meaning":""}

def _pick_seed(category: str) -> str:
    pool  = SEED_WORDS.get(category, [])
    used  = st.session_state.used_seeds.get(category, [])
    unused = [w for w in pool if w not in used]
    if not unused:
        st.session_state.used_seeds[category] = []
        unused = pool
    seed = random.choice(unused) if unused else random.choice(pool)
    st.session_state.used_seeds.setdefault(category, []).append(seed)
    return seed

def _pick_category(configured_cat) -> str:
    if configured_cat:
        return configured_cat
    cats = list(CATEGORY_THEMES.keys())
    idx  = st.session_state.cat_rotation_idx % len(cats)
    st.session_state.cat_rotation_idx += 1
    if idx == 0 and st.session_state.total > 0:
        random.shuffle(cats)
        st.session_state.cat_order = cats
    order = st.session_state.get("cat_order", cats)
    return order[idx % len(order)]

def generate_llm_question(client, category, asked_sentences, seed_word, attempt_num):
    themes = CATEGORY_THEMES.get(category, "general English vocabulary")
    temp   = min(0.75 + attempt_num * 0.08, 1.0)
    avoid_list = asked_sentences[-40:] if len(asked_sentences) > 40 else asked_sentences
    avoid = "\n".join(f"- {s}" for s in avoid_list) if avoid_list else "none"

    prompt = f"""Create ONE unique sentence-completion question for TCS NQT Verbal Ability exam.

Category: {category}
Theme: {themes}
Focus seed word/concept: "{seed_word}" — incorporate this into the sentence context.
Difficulty: EASY TO MEDIUM — use common words a college student would know.

STRICT TCS NQT FORMAT:
- ONE sentence with exactly ONE blank written as ________
- The student must type ONE word (or at most two words) that best fits
- Sentence should be 10–20 words
- Clear grammatical context; only one logical answer fits
- The blank answer must NOT be "{seed_word}" itself — use it as context
- Do NOT copy or closely resemble these sentences:
{avoid}

Return ONLY valid JSON:
{{
  "sentence": "The software engineer ________ the bug before the product launch.",
  "accepted_answers": ["fixed", "resolved", "identified"],
  "category": "{category}"
}}"""

    data = _call(client, [
        {"role":"system","content":"You write unique English vocabulary exam questions. Return valid JSON only."},
        {"role":"user","content":prompt}
    ], max_tokens=300, temp=temp)

    assert "sentence" in data and "accepted_answers" in data
    assert "________" in data["sentence"], "Blank marker missing"
    assert len(data["accepted_answers"]) >= 1
    data["id"] = _sentence_hash(data["sentence"])
    data.setdefault("category", category)
    return data

FALLBACK_POOL = [
    {"sentence":"The intern ________ all the required documents before the interview.","accepted_answers":["submitted","prepared","organised"],"category":"Workplace & Professional"},
    {"sentence":"The scientist ________ the experiment under controlled laboratory conditions.","accepted_answers":["conducted","performed","carried out"],"category":"Technology & Science"},
    {"sentence":"The government ________ a new policy to reduce air pollution in cities.","accepted_answers":["introduced","announced","implemented"],"category":"Social & Current Affairs"},
    {"sentence":"The professor ________ the students for their outstanding research presentation.","accepted_answers":["praised","commended","appreciated"],"category":"Academic & Student Life"},
    {"sentence":"She ________ accepted the criticism and promised to improve her work.","accepted_answers":["graciously","humbly","politely"],"category":"Tone & Context Awareness"},
    {"sentence":"The team ________ the project well ahead of the scheduled deadline.","accepted_answers":["completed","finished","delivered"],"category":"Workplace & Professional"},
    {"sentence":"The developer ________ a critical security vulnerability in the application.","accepted_answers":["discovered","identified","detected"],"category":"Technology & Science"},
    {"sentence":"The charity ________ food and clothing to thousands of flood victims.","accepted_answers":["distributed","provided","supplied"],"category":"Social & Current Affairs"},
    {"sentence":"The student ________ for the entrance exam by practising daily for months.","accepted_answers":["prepared","studied","revised"],"category":"Academic & Student Life"},
    {"sentence":"The manager spoke ________ to the client despite the project delays.","accepted_answers":["confidently","calmly","professionally"],"category":"Tone & Context Awareness"},
    {"sentence":"The company ________ its profits by cutting unnecessary operational costs.","accepted_answers":["increased","improved","boosted"],"category":"Workplace & Professional"},
    {"sentence":"The engineers ________ a new prototype for the electric vehicle battery.","accepted_answers":["designed","built","developed"],"category":"Technology & Science"},
    {"sentence":"The journalist ________ corruption in the local municipal corporation.","accepted_answers":["exposed","uncovered","revealed"],"category":"Social & Current Affairs"},
    {"sentence":"The college ________ fifty merit scholarships for underprivileged students.","accepted_answers":["awarded","offered","announced"],"category":"Academic & Student Life"},
    {"sentence":"He ________ agreed to take on the extra workload during the busy season.","accepted_answers":["willingly","readily","happily"],"category":"Tone & Context Awareness"},
]

def get_next_question(client):
    configured_cat = st.session_state.get("category_filter")
    asked_hashes   = st.session_state.asked_hashes
    asked_sentences = st.session_state.asked_sentences
    chosen_cat = _pick_category(configured_cat)
    seed = _pick_seed(chosen_cat)
    for attempt in range(8):
        try:
            q = generate_llm_question(client, chosen_cat, asked_sentences, seed, attempt)
            if q["id"] not in asked_hashes:
                return q
            seed = _pick_seed(chosen_cat)
        except Exception:
            time.sleep(0.3)
    unused_fallbacks = [
        f for f in FALLBACK_POOL
        if _sentence_hash(f["sentence"]) not in asked_hashes
        and (not configured_cat or f["category"] == configured_cat)
    ]
    if unused_fallbacks:
        q = dict(random.choice(unused_fallbacks))
        q["id"] = _sentence_hash(q["sentence"])
        return q
    q = dict(random.choice(FALLBACK_POOL))
    q["id"] = _sentence_hash(q["sentence"] + str(random.random()))
    return q

def process_submission(client, q, ans, timed_out=False):
    with st.spinner("Checking…"):
        is_correct = False if timed_out else check_answer(client, q["sentence"], q["accepted_answers"], ans)
    st.session_state.answered    = True
    st.session_state.user_answer = "(timed out)" if timed_out else ans
    st.session_state.feedback    = is_correct
    st.session_state.total      += 1
    primary     = q["accepted_answers"][0]
    is_reinforce = st.session_state.is_reinforce
    if is_correct:
        st.session_state.score += 1
        if is_reinforce and st.session_state.missed_bank:
            if st.session_state.missed_bank[0]["id"] == q["id"]:
                st.session_state.missed_bank.pop(0)
        with st.spinner("Preparing tip…"):
            st.session_state.suggestion = generate_suggestion(client, primary, q["sentence"])
    else:
        if is_reinforce and st.session_state.missed_bank:
            if st.session_state.missed_bank[0]["id"] == q["id"]:
                st.session_state.missed_bank[0]["retries_left"] -= 1
                if st.session_state.missed_bank[0]["retries_left"] <= 0:
                    st.session_state.missed_bank.pop(0)
        else:
            existing_ids = {e["id"] for e in st.session_state.missed_bank}
            if q["id"] not in existing_ids:
                st.session_state.missed_bank.append({
                    "id": q["id"], "word": primary,
                    "sentence": q["sentence"],
                    "accepted_answers": q["accepted_answers"],
                    "category": q["category"],
                    "retries_left": MAX_REINFORCE,
                })
        with st.spinner("Preparing lesson…"):
            st.session_state.lesson = generate_lesson(client, primary, q["sentence"])
    st.session_state.history.append({"word":primary,"correct":is_correct,"qid":q["id"],"reinforce":is_reinforce})
    st.session_state.live_answer = ""

# ── Passage Recall helpers ───────────────────────────────────────────────

def generate_passage(client, category):
    """
    Generate a SHORT passage (1 to 1.5 lines / 25-35 words) for TCS NQT.
    TCS passages are brief — the student must recall content, not volume.
    """
    cat_theme = CATEGORY_THEMES.get(category, "general knowledge")
    try:
        resp = client.chat.completions.create(
            messages=[
                {"role":"system","content":"You write short, factual English sentences for reading comprehension tests. Return valid JSON only. No markdown."},
                {"role":"user","content":f"""Write ONE short factual passage (exactly 25 to 35 words) on a topic from: {cat_theme}.

Rules:
- STRICT word count: 25 to 35 words only — this simulates TCS NQT which uses 1 to 1.5 line passages
- Self-contained: all key facts must be inside the passage itself
- Flowing prose — no bullet points, no headings
- Include at least 2-3 distinct, specific facts or details the student must recall
- Suitable for a college student
- Do NOT start with "This passage" or "The following"

Return ONLY JSON: {{"topic":"short topic title","passage":"full passage text"}}"""}
            ],
            model="llama-3.3-70b-versatile", temperature=0.8, max_tokens=200
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        data = json.loads(raw)
        assert "passage" in data
        words = len(data["passage"].split())
        assert 18 <= words <= 50, f"Passage word count {words} out of range"
        return data
    except Exception:
        return {
            "topic": "Remote Work",
            "passage": (
                "Remote work increased by 140% between 2019 and 2023, boosting employee "
                "satisfaction by 22% while reducing office costs significantly for most organisations."
            )
        }

def score_recall(client, original_passage, user_response):
    """
    Score the recall based on TCS NQT criteria:
    - Content accuracy (not verbatim matching)
    - Key facts recalled
    - Clarity and coherence
    Passage is short (25-35 words), so scoring is strict on details.
    """
    if not user_response.strip():
        return {
            "score": 0, "max_score": 10,
            "content_accuracy": "No response submitted.",
            "key_points_covered": [],
            "key_points_missed": ["No response — all key facts missed."],
            "feedback": "You did not write anything. Try to recall at least the main idea next time.",
            "grade": "F"
        }
    prompt = f"""You are evaluating a TCS NQT passage recall answer.

ORIGINAL PASSAGE (25-35 words):
\"\"\"{original_passage}\"\"\"

STUDENT'S RECONSTRUCTION:
\"\"\"{user_response}\"\"\"

TCS NQT Scoring Criteria (total = 10 points):
- Main idea captured accurately: (0–4 pts)
- Specific facts/numbers/details recalled correctly: (0–4 pts)
- Clarity and readability of student's writing: (0–2 pts)

Important: Since the passage is very short (1-1.5 lines), every specific detail matters.
Award high marks only if the student captured the core facts accurately, not just the topic.
The student must show they understood the passage, NOT copy it word for word.

Return ONLY valid JSON:
{{
  "score": 7,
  "max_score": 10,
  "content_accuracy": "One sentence summary of accuracy",
  "key_points_covered": ["specific fact 1 they got right", "fact 2"],
  "key_points_missed": ["specific fact they missed or got wrong"],
  "feedback": "2-3 sentence constructive feedback",
  "grade": "B"
}}
Grade: 9-10=A, 7-8=B, 5-6=C, 3-4=D, 0-2=F"""

    try:
        return _call(client, [
            {"role":"system","content":"You are a strict TCS NQT verbal ability examiner. Return valid JSON only."},
            {"role":"user","content":prompt}
        ], max_tokens=500, temp=0.3)
    except Exception:
        words_written = len(user_response.strip().split())
        rough_score = min(10, max(0, words_written // 3))
        return {
            "score": rough_score, "max_score": 10,
            "content_accuracy": "Could not evaluate automatically.",
            "key_points_covered": [],
            "key_points_missed": [],
            "feedback": f"You wrote {words_written} words. Review the original passage.",
            "grade": "—"
        }

# ── Email Writing helpers ─────────────────────────────────────────────────

def get_email_scenario():
    used = st.session_state.em_used_scenarios
    available = [i for i in range(len(EMAIL_SCENARIOS)) if i not in used]
    if not available:
        st.session_state.em_used_scenarios = []
        available = list(range(len(EMAIL_SCENARIOS)))
    idx = random.choice(available)
    st.session_state.em_used_scenarios.append(idx)
    return EMAIL_SCENARIOS[idx]

def score_email(client, scenario, user_email):
    """
    Score the email per TCS NQT criteria:
    - Must be at least 100 words
    - Complete sentences
    - Addresses the situation
    - Appropriate tone and format
    """
    word_count = len(user_email.strip().split()) if user_email.strip() else 0

    if not user_email.strip() or word_count < 10:
        return {
            "score": 0, "max_score": 10,
            "word_count": word_count,
            "meets_minimum": False,
            "task_completion": "No email written.",
            "strengths": [],
            "improvements": ["Write at least 100 words to meet TCS NQT requirements."],
            "tone_assessment": "N/A",
            "structure_assessment": "N/A",
            "feedback": "You did not write a sufficient response. TCS NQT requires at least 100 words written in complete sentences.",
            "grade": "F"
        }

    prompt = f"""You are evaluating a TCS NQT Email Writing task response.

SITUATION:
{scenario['situation']}

TASK:
{scenario['task']}

STUDENT'S EMAIL:
\"\"\"{user_email}\"\"\"

WORD COUNT: {word_count}
MINIMUM REQUIRED: {EMAIL_MIN_WORDS} words

TCS NQT Email Writing Scoring Criteria (total = 10 points):
1. Task completion — does the email address all aspects of the situation? (0–3 pts)
2. Language and vocabulary — appropriate word choice, no grammatical errors? (0–2 pts)
3. Tone and register — professional, polite, and appropriate for the context? (0–2 pts)
4. Structure and organisation — clear subject, greeting, body, closing? (0–2 pts)
5. Word count compliance — at least 100 words in complete sentences? (0–1 pt)

Note: If word count is below 100, cap total score at 5 regardless of quality.

Return ONLY valid JSON:
{{
  "score": 7,
  "max_score": 10,
  "word_count": {word_count},
  "meets_minimum": {"true" if word_count >= EMAIL_MIN_WORDS else "false"},
  "task_completion": "One sentence about how well the task was addressed",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement area 1", "improvement area 2"],
  "tone_assessment": "One sentence about tone",
  "structure_assessment": "One sentence about email structure",
  "feedback": "3-4 sentence overall constructive feedback",
  "grade": "B"
}}
Grade: 9-10=A, 7-8=B, 5-6=C, 3-4=D, 0-2=F"""

    try:
        return _call(client, [
            {"role":"system","content":"You are a strict TCS NQT email writing examiner. Return valid JSON only."},
            {"role":"user","content":prompt}
        ], max_tokens=600, temp=0.3)
    except Exception:
        rough = min(10, max(0, word_count // 20)) if word_count >= EMAIL_MIN_WORDS else min(5, word_count // 20)
        return {
            "score": rough, "max_score": 10, "word_count": word_count,
            "meets_minimum": word_count >= EMAIL_MIN_WORDS,
            "task_completion": "Could not evaluate automatically.",
            "strengths": [], "improvements": [],
            "tone_assessment": "—", "structure_assessment": "—",
            "feedback": f"You wrote {word_count} words. {'Meets minimum.' if word_count >= EMAIL_MIN_WORDS else 'Below 100-word minimum.'}",
            "grade": "—"
        }

# ═══════════════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="big-title">⚡ TCS NQT Verbal Prep</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Sentence Completion · Passage Recall · Email Writing — AI-powered feedback</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  SETUP PAGE
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.page == "setup":
    st.markdown("""
    <div class="question-card" style="margin-bottom:20px;">
        <b style="color:#B8A6FF;">📋 TCS NQT Verbal Ability Structure</b><br><br>
        <table style="width:100%;border-collapse:collapse;font-size:0.82rem;color:#E4E4F0;">
            <tr style="background:#2e324a;">
                <th style="padding:8px;text-align:left;">Section</th>
                <th style="padding:8px;text-align:center;">Items</th>
                <th style="padding:8px;text-align:center;">Time/Question</th>
            </tr>
            <tr><td style="padding:8px;">Sentence Completion</td><td style="padding:8px;text-align:center;">20</td><td style="padding:8px;text-align:center;">25 seconds each</td></tr>
            <tr style="background:#1a1f2e;"><td style="padding:8px;">Passage Recall</td><td style="padding:8px;text-align:center;">4+4</td><td style="padding:8px;text-align:center;">30s read + 90s write</td></tr>
            <tr><td style="padding:8px;">Email Writing</td><td style="padding:8px;text-align:center;">1</td><td style="padding:8px;text-align:center;">9 minutes (min 100 words)</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    with st.form("setup_form"):
        api_key  = st.text_input("Groq API Key", type="password", help="Free at console.groq.com")
        mode     = st.radio(
            "Select Mode",
            ["⚡ Sentence Completion", "📖 Passage Recall", "✉️ Email Writing"],
            horizontal=True
        )
        cat_choice = st.selectbox("Category (for Sentence Completion)", list(CATEGORY_FILTER.keys()))
        submitted = st.form_submit_button("🚀 Start")

    if submitted:
        if not api_key.strip():
            st.error("Please enter your Groq API key.")
        else:
            reset_vocab_state()
            reset_recall_state()
            reset_email_state()
            st.session_state.api_key        = api_key
            st.session_state.category_filter = CATEGORY_FILTER[cat_choice]
            if "Sentence" in mode:
                st.session_state.mode = "vocab"
                st.session_state.page = "quiz"
            elif "Passage" in mode:
                st.session_state.mode = "recall"
                st.session_state.page = "recall"
            else:
                st.session_state.mode = "email"
                st.session_state.page = "email"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
#  VOCAB SPRINT / SENTENCE COMPLETION PAGE
# ═══════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "quiz":
    client       = get_client(st.session_state.api_key)
    missed_count = len(st.session_state.missed_bank)
    total_gen    = len(st.session_state.asked_hashes)

    st.markdown(
        f'<div class="score-pill">✅ {st.session_state.score}/{st.session_state.total} &nbsp;|&nbsp; '
        f'Q{st.session_state.total+1}/20 &nbsp;|&nbsp; 🔁 {missed_count} pending</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    c_end, c_recall, c_email = st.columns(3)
    with c_end:
        if st.button("🛑 End Quiz"):
            st.session_state.page = "summary"
            st.rerun()
    with c_recall:
        if st.button("📖 Passage Recall"):
            reset_recall_state()
            st.session_state.page = "recall"
            st.rerun()
    with c_email:
        if st.button("✉️ Email Writing"):
            reset_email_state()
            st.session_state.page = "email"
            st.rerun()
    st.write("")

    # ── Pick question ────────────────────────────────────────────────────
    if st.session_state.current_q is None:
        pull_reinforce = (
            st.session_state.missed_bank and
            st.session_state.total > 0 and
            st.session_state.total % 4 == 0
        )
        if pull_reinforce:
            entry = st.session_state.missed_bank[0]
            q = {"id":entry["id"],"sentence":entry["sentence"],
                 "accepted_answers":entry["accepted_answers"],"category":entry["category"]}
            st.session_state.is_reinforce = True
        else:
            with st.spinner("✨ Generating question…"):
                q = get_next_question(client)
            st.session_state.is_reinforce = False

        st.session_state.asked_hashes.add(q["id"])
        st.session_state.asked_sentences.append(q["sentence"])
        st.session_state.current_q  = q
        st.session_state.start_time = time.time()
        st.session_state.answered   = False
        st.session_state.feedback   = None
        st.session_state.lesson     = None
        st.session_state.suggestion = None
        st.session_state.live_answer = ""
        st.rerun()

    q           = st.session_state.current_q
    elapsed     = time.time() - st.session_state.start_time
    remaining   = max(0.0, TIME_LIMIT - elapsed)
    is_reinforce = st.session_state.is_reinforce

    if not st.session_state.answered:
        if remaining <= 0:
            captured  = st.session_state.live_answer.strip()
            timed_out = captured == ""
            process_submission(client, q, captured, timed_out=timed_out)
            st.rerun()

        col1, col2 = st.columns([4, 1])
        with col1:
            tags = f'<span class="q-tag">{q["category"].upper()}</span>'
            if is_reinforce:
                tags += '<span class="reinforce-tag">🔁 REINFORCE</span>'
            else:
                tags += '<span class="llm-tag">✨ AI</span>'
            q_label = f'Question {st.session_state.total + 1} of 20'
            st.markdown(
                f'<div class="question-card">{tags}'
                f'<div class="q-num">{q_label}</div>'
                f'<div class="q-text">{q["sentence"]}</div>'
                f'<div style="color:#8A8FA3;font-size:0.78rem;margin-top:10px;">Type ONE word that best fits the blank.</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col2:
            warn = "timer-warn" if remaining <= 8 else ""
            st.markdown(f'<div class="timer-box {warn}">{int(remaining)}</div>', unsafe_allow_html=True)
            st.markdown('<p style="text-align:center;color:#8A8FA3;font-size:0.72rem;">sec</p>', unsafe_allow_html=True)

        st.write("")

        def _save_live():
            st.session_state.live_answer = st.session_state._answer_input

        st.text_input(
            "Type ONE word:",
            placeholder="Your answer…",
            key="_answer_input",
            on_change=_save_live,
            value=st.session_state.live_answer,
        )
        if st.button("✅ Submit / Next"):
            process_submission(client, q, st.session_state.live_answer.strip(), timed_out=False)
            st.rerun()

        time.sleep(1)
        st.rerun()

    else:
        tags = f'<span class="q-tag">{q["category"].upper()}</span>'
        if is_reinforce: tags += '<span class="reinforce-tag">🔁 REINFORCE</span>'
        else:            tags += '<span class="llm-tag">✨ AI</span>'
        st.markdown(
            f'<div class="question-card">{tags}'
            f'<div class="q-num">Question {st.session_state.total}</div>'
            f'<div class="q-text">{q["sentence"]}</div></div>',
            unsafe_allow_html=True,
        )
        primary    = q["accepted_answers"][0]
        all_accept = " / ".join(q["accepted_answers"])

        if st.session_state.feedback:
            st.markdown(f"""
            <div class="correct-box">
                ✅ <b>Correct!</b> "<i>{st.session_state.user_answer}</i>" — well done.<br>
                <span style="font-size:0.85rem;">Accepted: <b>{all_accept}</b></span>
            </div>""", unsafe_allow_html=True)
            if st.session_state.suggestion:
                sug = st.session_state.suggestion
                adv = f"<br><b>Try next:</b> <i>{sug['advanced_word']}</i> — {sug['advanced_meaning']}" if sug.get("advanced_word") else ""
                st.markdown(f'<div class="levelup-box"><b style="color:#00E0B8;">💡 Tip</b><br>{sug["tip"]}{adv}</div>', unsafe_allow_html=True)
        else:
            timeout_note   = '<br><span style="font-size:0.8rem;color:#FF6B35;">⏰ Time ran out.</span>' if st.session_state.user_answer == "(timed out)" else ""
            reinforce_note = "" if is_reinforce else '<br><span style="font-size:0.8rem;color:#FF9966;">🔁 Will revisit for reinforcement.</span>'
            st.markdown(f"""
            <div class="wrong-box">
                ❌ <b>Incorrect.</b> You wrote: "<i>{st.session_state.user_answer}</i>"<br>
                <span style="font-size:0.85rem;">Answer: <b>{all_accept}</b></span>{timeout_note}{reinforce_note}
            </div>""", unsafe_allow_html=True)
            if st.session_state.lesson:
                L = st.session_state.lesson
                ex_html  = "".join(f"<li>{e}</li>" for e in L.get("examples", []))
                syn_html = ", ".join(L.get("synonyms", []))
                rel_html = "".join(f"<li><b>{r['word']}</b> — {r['meaning']}<br><i>{r['example']}</i></li>" for r in L.get("related_words", []))
                st.markdown(f"""
                <div class="lesson-box">
                    <h4 style="margin-top:0;color:#B8A6FF;">📘 {primary}</h4>
                    <p><b>Meaning:</b> {L.get('meaning','')}</p>
                    <p><b>Synonyms:</b> {syn_html}</p>
                    <p><b>Examples:</b></p><ul>{ex_html}</ul>
                    <p><b>Memory tip:</b> {L.get('memory_tip','')}</p>
                    {'<p><b>Related:</b></p><ul>' + rel_html + '</ul>' if rel_html else ''}
                </div>""", unsafe_allow_html=True)

        st.write("")
        if st.button("➡️ Next Question"):
            st.session_state.current_q = None
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
#  PASSAGE RECALL PAGE
# ═══════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "recall":
    client = get_client(st.session_state.api_key)

    pr_count = st.session_state.pr_count
    if st.session_state.pr_history:
        avg_score = sum(h["score"] for h in st.session_state.pr_history) / len(st.session_state.pr_history)
        score_txt = f"Avg {avg_score:.1f}/10"
    else:
        score_txt = "No passages yet"

    st.markdown(
        f'<div class="score-pill">📖 Passage {pr_count+1} &nbsp;|&nbsp; {score_txt} &nbsp;|&nbsp; {len(st.session_state.pr_history)} done</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⚡ Sentence Fill"):
            st.session_state.page = "quiz"
            st.rerun()
    with c2:
        if st.button("✉️ Email Writing"):
            reset_email_state()
            st.session_state.page = "email"
            st.rerun()
    with c3:
        if st.button("📊 History") and st.session_state.pr_history:
            st.session_state.page = "recall_summary"
            st.rerun()
    st.write("")

    phase = st.session_state.pr_phase

    # Generate passage if not loaded
    if st.session_state.pr_passage is None:
        configured_cat = st.session_state.get("category_filter")
        cat = configured_cat if configured_cat else random.choice(PASSAGE_CATEGORIES)
        with st.spinner("📝 Generating passage…"):
            data = generate_passage(client, cat)
        st.session_state.pr_passage    = data["passage"]
        st.session_state.pr_topic      = data.get("topic", "Reading Passage")
        st.session_state.pr_start_time = time.time()
        st.session_state.pr_phase      = "read"
        st.session_state.pr_live_text  = ""
        st.rerun()

    passage = st.session_state.pr_passage
    topic   = st.session_state.pr_topic

    # ════════════════════════════════════════════
    #  PHASE 1 — READ  (30 seconds — TCS spec)
    # ════════════════════════════════════════════
    if phase == "read":
        elapsed   = time.time() - st.session_state.pr_start_time
        remaining = max(0.0, READ_TIME - elapsed)

        if remaining <= 0:
            st.session_state.pr_phase      = "write"
            st.session_state.pr_start_time = time.time()
            st.rerun()

        st.markdown(
            '<div class="info-bar">📋 <b>TCS NQT Instructions:</b> Read the passage carefully. '
            'You have <b>30 seconds</b>. The passage will disappear after the timer ends. '
            'Then you will have <b>90 seconds</b> to rewrite it in your own words. '
            'Your response will be scored on <b>content accuracy</b>, not word-for-word matching.</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f'<span class="phase-badge phase-read">📖 READ PHASE — {int(remaining)}s remaining</span>', unsafe_allow_html=True)
            word_count = len(passage.split())
            st.markdown(
                f'<div class="passage-card">'
                f'<b style="color:#B8A6FF;font-size:0.85rem;">TOPIC: {topic.upper()}</b>'
                f'<div style="color:#8A8FA3;font-size:0.75rem;margin-bottom:12px;">{word_count} words</div>'
                f'<div style="font-size:1.15rem;line-height:2.0;">{passage}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with col2:
            warn_cls = "timer-warn" if remaining <= 8 else "timer-read"
            st.markdown(f'<div class="timer-box {warn_cls}">{int(remaining)}</div>', unsafe_allow_html=True)
            st.markdown('<p style="text-align:center;color:#8A8FA3;font-size:0.72rem;">sec</p>', unsafe_allow_html=True)

        time.sleep(1)
        st.rerun()

    # ════════════════════════════════════════════
    #  PHASE 2 — WRITE  (90 seconds — TCS spec)
    # ════════════════════════════════════════════
    elif phase == "write":
        elapsed   = time.time() - st.session_state.pr_start_time
        remaining = max(0.0, WRITE_TIME - elapsed)

        if remaining <= 0:
            final_text = st.session_state.pr_live_text.strip()
            st.session_state.pr_submitted_text = final_text
            with st.spinner("🔍 Scoring your response…"):
                score_data = score_recall(client, passage, final_text)
            st.session_state.pr_score_data = score_data
            st.session_state.pr_history.append({
                "passage_num": st.session_state.pr_count + 1,
                "topic":       topic,
                "score":       score_data.get("score", 0),
                "max_score":   score_data.get("max_score", 10),
                "grade":       score_data.get("grade", "—"),
                "user_text":   final_text,
                "passage":     passage,
            })
            st.session_state.pr_count += 1
            st.session_state.pr_phase = "scored"
            st.rerun()

        st.markdown(
            '<div class="info-bar">✍️ <b>Passage is now hidden.</b> '
            'Rewrite what you remember in your own words. '
            'Show that you <b>understood the content</b> — focus on the main idea and key facts. '
            'Your work saves automatically when time ends.</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f'<span class="phase-badge phase-write">✍️ WRITE PHASE — Topic: {topic}</span>', unsafe_allow_html=True)
            st.markdown('<div class="recall-card">', unsafe_allow_html=True)

            def _save_recall():
                st.session_state.pr_live_text = st.session_state._recall_input

            st.text_area(
                "Reconstruct the passage in your own words:",
                placeholder="Write what you remember — main idea + key details…",
                key="_recall_input",
                on_change=_save_recall,
                value=st.session_state.pr_live_text,
                height=160,
            )
            words_typed = len(st.session_state.pr_live_text.strip().split()) if st.session_state.pr_live_text.strip() else 0
            st.markdown(f'<p style="color:#8A8FA3;font-size:0.78rem;">Words: {words_typed}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            warn_cls = "timer-warn" if remaining <= 15 else "timer-write"
            st.markdown(f'<div class="timer-box {warn_cls}">{int(remaining)}</div>', unsafe_allow_html=True)
            st.markdown('<p style="text-align:center;color:#8A8FA3;font-size:0.72rem;">sec</p>', unsafe_allow_html=True)

        st.write("")
        if st.button("💾 Submit Early"):
            final_text = st.session_state.pr_live_text.strip()
            st.session_state.pr_submitted_text = final_text
            with st.spinner("🔍 Scoring…"):
                score_data = score_recall(client, passage, final_text)
            st.session_state.pr_score_data = score_data
            st.session_state.pr_history.append({
                "passage_num": st.session_state.pr_count + 1,
                "topic":       topic,
                "score":       score_data.get("score", 0),
                "max_score":   score_data.get("max_score", 10),
                "grade":       score_data.get("grade", "—"),
                "user_text":   final_text,
                "passage":     passage,
            })
            st.session_state.pr_count += 1
            st.session_state.pr_phase = "scored"
            st.rerun()

        time.sleep(1)
        st.rerun()

    # ════════════════════════════════════════════
    #  PHASE 3 — SCORED
    # ════════════════════════════════════════════
    elif phase == "scored":
        sd = st.session_state.pr_score_data or {}
        score     = sd.get("score", 0)
        max_score = sd.get("max_score", 10)
        grade     = sd.get("grade", "—")
        pct       = round(100 * score / max_score) if max_score else 0
        grade_color = {"A":"#00E0B8","B":"#7C5CFF","C":"#FFD700","D":"#FF9966","F":"#FF6B35"}.get(grade, "#8A8FA3")

        st.markdown(f'<span class="phase-badge phase-done">✅ SCORED — Passage {st.session_state.pr_count}</span>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="recall-score-box">
            <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
                <div style="text-align:center;">
                    <div style="font-family:'Space Grotesk',sans-serif;font-size:3rem;font-weight:700;color:{grade_color};">{grade}</div>
                    <div style="color:#8A8FA3;font-size:0.8rem;">Grade</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-family:'Space Grotesk',sans-serif;font-size:2.5rem;font-weight:700;color:{grade_color};">{score}<span style="font-size:1.2rem;color:#8A8FA3;">/{max_score}</span></div>
                    <div style="color:#8A8FA3;font-size:0.8rem;">Score ({pct}%)</div>
                </div>
                <div style="flex:1;min-width:200px;">
                    <p style="margin:0;color:#E4E4F0;"><b>Content Accuracy:</b><br>{sd.get('content_accuracy','—')}</p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        covered = sd.get("key_points_covered", [])
        missed  = sd.get("key_points_missed", [])
        if covered or missed:
            c_html = "".join(f'<li style="color:#6EE7B7;">✅ {p}</li>' for p in covered)
            m_html = "".join(f'<li style="color:#FCA5A5;">❌ {p}</li>' for p in missed)
            st.markdown(f"""
            <div class="lesson-box" style="margin-top:14px;">
                <b style="color:#B8A6FF;">Key Points</b>
                <ul style="margin-top:8px;">{c_html}{m_html}</ul>
            </div>""", unsafe_allow_html=True)

        if sd.get("feedback"):
            st.markdown(f"""
            <div class="levelup-box" style="margin-top:12px;">
                <b style="color:#00E0B8;">💡 Feedback</b><br>{sd['feedback']}
            </div>""", unsafe_allow_html=True)

        with st.expander("📄 View Original Passage"):
            st.markdown(f'<div class="passage-card">{passage}</div>', unsafe_allow_html=True)

        with st.expander("✍️ Your Reconstruction"):
            user_txt = st.session_state.pr_submitted_text or "(nothing submitted)"
            st.markdown(f'<div style="background:#12162a;border-radius:10px;padding:16px;color:#E4E4F0;line-height:1.7;">{user_txt}</div>', unsafe_allow_html=True)

        st.write("")
        if st.button("➡️ Next Passage"):
            st.session_state.pr_passage    = None
            st.session_state.pr_score_data = None
            st.session_state.pr_phase      = "read"
            st.session_state.pr_live_text  = ""
            st.session_state.pr_submitted_text = ""
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
#  EMAIL WRITING PAGE
# ═══════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "email":
    client = get_client(st.session_state.api_key)

    em_count = st.session_state.em_count
    if st.session_state.em_history:
        avg_score = sum(h["score"] for h in st.session_state.em_history) / len(st.session_state.em_history)
        score_txt = f"Avg {avg_score:.1f}/10"
    else:
        score_txt = "No emails yet"

    st.markdown(
        f'<div class="score-pill">✉️ Email {em_count+1} &nbsp;|&nbsp; {score_txt} &nbsp;|&nbsp; {len(st.session_state.em_history)} done</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⚡ Sentence Fill"):
            st.session_state.page = "quiz"
            st.rerun()
    with c2:
        if st.button("📖 Passage Recall"):
            reset_recall_state()
            st.session_state.page = "recall"
            st.rerun()
    st.write("")

    phase = st.session_state.em_phase

    # Load scenario if not loaded
    if st.session_state.em_scenario is None:
        st.session_state.em_scenario   = get_email_scenario()
        st.session_state.em_phase      = "task"
        st.session_state.em_live_text  = ""

    scenario = st.session_state.em_scenario

    # ════════════════════════════════════════════
    #  PHASE 1 — READ TASK (no timer — TCS shows it throughout)
    # ════════════════════════════════════════════
    if phase == "task":
        st.markdown(
            '<div class="info-bar">✉️ <b>TCS NQT Email Writing Instructions:</b> '
            'Read the situation carefully. You will have <b>9 minutes</b> to write an email. '
            'You must write <b>at least 100 words</b> in complete sentences. '
            'Address all aspects of the situation.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<span class="phase-badge phase-email">✉️ EMAIL WRITING</span>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="email-card">
            <b style="color:#FFD700;font-size:0.82rem;">SITUATION</b>
            <p style="color:#E4E4F0;margin-top:8px;line-height:1.8;">{scenario['situation']}</p>
            <hr style="border-color:#2e324a;margin:16px 0;">
            <b style="color:#FFD700;font-size:0.82rem;">YOUR TASK</b>
            <p style="color:#E4E4F0;margin-top:8px;line-height:1.8;">{scenario['task']}</p>
            <hr style="border-color:#2e324a;margin:16px 0;">
            <b style="color:#8A8FA3;font-size:0.78rem;">To:</b> <span style="color:#B8A6FF;">{scenario['to']}</span><br>
            <b style="color:#8A8FA3;font-size:0.78rem;">Subject hint:</b> <span style="color:#8A8FA3;font-style:italic;">{scenario['subject_hint']}</span>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        if st.button("🚀 Start Writing (9 min timer begins)"):
            st.session_state.em_phase      = "writing"
            st.session_state.em_start_time = time.time()
            st.session_state.em_live_text  = ""
            st.rerun()

    # ════════════════════════════════════════════
    #  PHASE 2 — WRITE EMAIL  (540 seconds = 9 min)
    # ════════════════════════════════════════════
    elif phase == "writing":
        elapsed   = time.time() - st.session_state.em_start_time
        remaining = max(0.0, EMAIL_TIME - elapsed)
        minutes   = int(remaining) // 60
        seconds   = int(remaining) % 60

        if remaining <= 0:
            final_text = st.session_state.em_live_text.strip()
            st.session_state.em_submitted_text = final_text
            with st.spinner("🔍 Evaluating your email…"):
                score_data = score_email(client, scenario, final_text)
            st.session_state.em_score_data = score_data
            word_count = len(final_text.split()) if final_text else 0
            st.session_state.em_history.append({
                "email_num": st.session_state.em_count + 1,
                "situation": scenario['situation'][:80] + "…",
                "score":     score_data.get("score", 0),
                "max_score": score_data.get("max_score", 10),
                "grade":     score_data.get("grade", "—"),
                "word_count": word_count,
                "user_text": final_text,
            })
            st.session_state.em_count += 1
            st.session_state.em_phase = "scored"
            st.rerun()

        # Show situation panel + writing area
        st.markdown('<span class="phase-badge phase-email">✍️ WRITING — Time Remaining</span>', unsafe_allow_html=True)

        # Situation reminder (collapsed)
        with st.expander("📋 View Situation & Task", expanded=False):
            st.markdown(f"""
            <div style="background:#12162a;border-radius:10px;padding:16px;color:#E4E4F0;">
                <b style="color:#FFD700;">Situation:</b><br>{scenario['situation']}<br><br>
                <b style="color:#FFD700;">Task:</b><br>{scenario['task']}<br><br>
                <b style="color:#8A8FA3;">To:</b> {scenario['to']}
            </div>""", unsafe_allow_html=True)

        # Timer display — larger and prominent
        col_timer, col_words = st.columns([1, 3])
        with col_timer:
            warn_cls = "timer-warn" if remaining <= 60 else "timer-email"
            st.markdown(
                f'<div style="text-align:center;">'
                f'<div class="timer-box {warn_cls}" style="width:80px;height:80px;font-size:1.5rem;border-radius:12px;">'
                f'{minutes:02d}:{seconds:02d}'
                f'</div>'
                f'<p style="text-align:center;color:#8A8FA3;font-size:0.72rem;">remaining</p>'
                f'</div>',
                unsafe_allow_html=True
            )
        with col_words:
            live_wc = len(st.session_state.em_live_text.strip().split()) if st.session_state.em_live_text.strip() else 0
            wc_color = "#00E0B8" if live_wc >= EMAIL_MIN_WORDS else "#FF9966"
            min_note = "✅ Minimum met!" if live_wc >= EMAIL_MIN_WORDS else f"⚠️ Need {EMAIL_MIN_WORDS - live_wc} more words"
            st.markdown(
                f'<div style="background:#1c1f2e;border-radius:10px;padding:14px;border:1px solid #2e324a;">'
                f'<div style="font-family:Space Grotesk,sans-serif;font-size:1.8rem;font-weight:700;color:{wc_color};">{live_wc}</div>'
                f'<div style="color:#8A8FA3;font-size:0.78rem;">words typed &nbsp;|&nbsp; <span style="color:{wc_color};">{min_note}</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.write("")

        def _save_email():
            st.session_state.em_live_text = st.session_state._email_input

        st.markdown('<div class="email-card">', unsafe_allow_html=True)
        st.text_area(
            f"Write your email to: {scenario['to']}",
            placeholder=f"Start with a proper greeting...\n\nAddress the situation: {scenario['task'][:80]}...\n\nEnd with a professional closing.",
            key="_email_input",
            on_change=_save_email,
            value=st.session_state.em_live_text,
            height=320,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("")
        if st.button("💾 Submit Email Early"):
            final_text = st.session_state.em_live_text.strip()
            st.session_state.em_submitted_text = final_text
            with st.spinner("🔍 Evaluating your email…"):
                score_data = score_email(client, scenario, final_text)
            st.session_state.em_score_data = score_data
            word_count = len(final_text.split()) if final_text else 0
            st.session_state.em_history.append({
                "email_num": st.session_state.em_count + 1,
                "situation": scenario['situation'][:80] + "…",
                "score":     score_data.get("score", 0),
                "max_score": score_data.get("max_score", 10),
                "grade":     score_data.get("grade", "—"),
                "word_count": word_count,
                "user_text": final_text,
            })
            st.session_state.em_count += 1
            st.session_state.em_phase = "scored"
            st.rerun()

        time.sleep(1)
        st.rerun()

    # ════════════════════════════════════════════
    #  PHASE 3 — SCORED
    # ════════════════════════════════════════════
    elif phase == "scored":
        sd = st.session_state.em_score_data or {}
        score     = sd.get("score", 0)
        max_score = sd.get("max_score", 10)
        grade     = sd.get("grade", "—")
        pct       = round(100 * score / max_score) if max_score else 0
        word_count = sd.get("word_count", 0)
        meets_min  = sd.get("meets_minimum", False)
        grade_color = {"A":"#00E0B8","B":"#7C5CFF","C":"#FFD700","D":"#FF9966","F":"#FF6B35"}.get(grade, "#8A8FA3")

        st.markdown(f'<span class="phase-badge phase-done">✅ EMAIL EVALUATED — Email {st.session_state.em_count}</span>', unsafe_allow_html=True)

        min_badge = (
            f'<span style="background:#0d2b1f;color:#6EE7B7;border:1px solid #1f9d6b;border-radius:999px;padding:3px 12px;font-size:0.75rem;">✅ {word_count} words — Minimum met</span>'
            if meets_min else
            f'<span style="background:#2b0d12;color:#FCA5A5;border:1px solid #c5455a;border-radius:999px;padding:3px 12px;font-size:0.75rem;">⚠️ {word_count} words — Below 100-word minimum</span>'
        )

        st.markdown(f"""
        <div class="email-score-box">
            <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;margin-bottom:12px;">
                <div style="text-align:center;">
                    <div style="font-family:'Space Grotesk',sans-serif;font-size:3rem;font-weight:700;color:{grade_color};">{grade}</div>
                    <div style="color:#8A8FA3;font-size:0.8rem;">Grade</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-family:'Space Grotesk',sans-serif;font-size:2.5rem;font-weight:700;color:{grade_color};">{score}<span style="font-size:1.2rem;color:#8A8FA3;">/{max_score}</span></div>
                    <div style="color:#8A8FA3;font-size:0.8rem;">Score ({pct}%)</div>
                </div>
                <div style="flex:1;min-width:200px;">
                    {min_badge}<br><br>
                    <p style="margin:0;color:#E4E4F0;"><b>Task Completion:</b><br>{sd.get('task_completion','—')}</p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Detailed breakdown
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="lesson-box">
                <b style="color:#B8A6FF;">📝 Tone & Structure</b>
                <p style="margin-top:8px;"><b>Tone:</b> {sd.get('tone_assessment','—')}</p>
                <p><b>Structure:</b> {sd.get('structure_assessment','—')}</p>
            </div>""", unsafe_allow_html=True)
        with col_b:
            strengths = sd.get("strengths", [])
            improvements = sd.get("improvements", [])
            s_html = "".join(f'<li style="color:#6EE7B7;">✅ {s}</li>' for s in strengths)
            i_html = "".join(f'<li style="color:#FCA5A5;">💡 {i}</li>' for i in improvements)
            st.markdown(f"""
            <div class="lesson-box">
                <b style="color:#B8A6FF;">✅ Strengths & 💡 Improvements</b>
                <ul style="margin-top:8px;">{s_html}{i_html}</ul>
            </div>""", unsafe_allow_html=True)

        if sd.get("feedback"):
            st.markdown(f"""
            <div class="levelup-box" style="margin-top:12px;">
                <b style="color:#00E0B8;">💡 Overall Feedback</b><br>{sd['feedback']}
            </div>""", unsafe_allow_html=True)

        with st.expander("📋 View Original Task"):
            st.markdown(f"""
            <div class="email-card">
                <b style="color:#FFD700;">Situation:</b><br><span style="color:#E4E4F0;">{scenario['situation']}</span><br><br>
                <b style="color:#FFD700;">Task:</b><br><span style="color:#E4E4F0;">{scenario['task']}</span>
            </div>""", unsafe_allow_html=True)

        with st.expander("✉️ Your Email"):
            user_txt = st.session_state.em_submitted_text or "(nothing submitted)"
            st.markdown(f'<div style="background:#12162a;border-radius:10px;padding:16px;color:#E4E4F0;line-height:1.8;white-space:pre-wrap;">{user_txt}</div>', unsafe_allow_html=True)

        st.write("")
        if st.button("➡️ Next Email Task"):
            st.session_state.em_scenario       = None
            st.session_state.em_score_data     = None
            st.session_state.em_phase          = "task"
            st.session_state.em_live_text      = ""
            st.session_state.em_submitted_text = ""
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
#  RECALL HISTORY PAGE
# ═══════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "recall_summary":
    history = st.session_state.pr_history
    if history:
        avg = sum(h["score"] for h in history) / len(history)
        pct = round(avg * 10)
        grade_label = "🏆 Excellent!" if pct >= 80 else "👍 Good effort!" if pct >= 50 else "📚 Keep practising!"
        st.markdown(f"""
        <div class="question-card" style="text-align:center;">
            <div class="big-title" style="font-size:2rem;">Passage Recall Summary</div>
            <p style="font-size:1.1rem;color:#E4E4F0;">{grade_label}<br>
            Average Score: <b style="color:#00E0B8;">{avg:.1f}</b>/10 across {len(history)} passages</p>
        </div>""", unsafe_allow_html=True)
        st.write("")
        for h in reversed(history):
            g_color = {"A":"#00E0B8","B":"#7C5CFF","C":"#FFD700","D":"#FF9966","F":"#FF6B35"}.get(h["grade"],"#8A8FA3")
            st.markdown(f"""
            <div style="background:#1c1f2e;border:1px solid #2e324a;border-radius:12px;padding:14px 20px;margin-bottom:10px;display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
                <div style="font-family:'Space Grotesk',sans-serif;font-size:1.8rem;font-weight:700;color:{g_color};min-width:40px;">{h['grade']}</div>
                <div>
                    <div style="color:#E4E4F0;font-weight:600;">Passage {h['passage_num']}: {h['topic']}</div>
                    <div style="color:#8A8FA3;font-size:0.82rem;">Score: {h['score']}/{h['max_score']}</div>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No passages completed yet.")
    st.write("")
    if st.button("⬅️ Back to Recall"):
        st.session_state.page = "recall"
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
#  VOCAB SPRINT SUMMARY PAGE
# ═══════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "summary":
    total = st.session_state.total
    score = st.session_state.score
    pct   = round(100 * score / total) if total else 0
    st.balloons()
    grade = "🏆 Excellent!" if pct >= 80 else "👍 Good effort!" if pct >= 50 else "📚 Keep practising!"
    st.markdown(f"""
    <div class="question-card" style="text-align:center;">
        <div class="big-title" style="font-size:2rem;">Session Summary</div>
        <p style="font-size:1.1rem;color:#E4E4F0;">{grade}<br>
        <b style="color:#00E0B8;">{score}</b> / <b>{total}</b> ({pct}%)</p>
    </div>""", unsafe_allow_html=True)

    missed = [h for h in st.session_state.history if not h["correct"]]
    if missed:
        st.write("")
        chips = "".join(f'<span class="missed-chip">{h["word"]}</span>' for h in missed)
        st.markdown(f'<div class="lesson-box"><b style="color:#B8A6FF;">📚 Revise these:</b><br><br>{chips}</div>', unsafe_allow_html=True)

    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🔁 Continue Quiz"):
            st.session_state.page = "quiz"
            st.session_state.current_q = None
            st.rerun()
    with c2:
        if st.button("📖 Passage Recall"):
            reset_recall_state()
            st.session_state.page = "recall"
            st.rerun()
    with c3:
        if st.button("✉️ Email Writing"):
            reset_email_state()
            st.session_state.page = "email"
            st.rerun()
    with c4:
        if st.button("⚙️ New Setup"):
            st.session_state.page = "setup"
            st.rerun()
