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
#  CONSTANTS — TCS NQT EXACT SPECS (from official image)
# ═══════════════════════════════════════════════════════════════════════════

READ_TIME        = 30    # 30s read (TCS spec)
WRITE_TIME       = 90    # 90s write (TCS spec)
TIME_LIMIT       = 25    # 25s per sentence completion (TCS spec)
EMAIL_TIME       = 540   # 9 minutes email writing (TCS spec)
EMAIL_MIN_WORDS  = 100   # minimum 100 words (TCS spec)
MAX_REINFORCE    = 2

CATEGORY_FILTER = {
    "All Categories": None,
    "Workplace & Professional": "Workplace & Professional",
    "Technology & Science": "Technology & Science",
    "Social & Current Affairs": "Social & Current Affairs",
    "Academic & Student Life": "Academic & Student Life",
    "Tone & Context Awareness": "Tone & Context Awareness",
}

CATEGORY_THEMES = {
    "Workplace & Professional": "office tasks, appraisals, team meetings, client communication, corporate decisions, project management, HR processes, business strategy",
    "Technology & Science": "AI research, software engineering, space missions, cybersecurity, scientific discoveries, data science, cloud computing, robotics",
    "Social & Current Affairs": "government policy, climate change, social justice, media, public health, elections, economy, environment, urban development",
    "Academic & Student Life": "exams, internships, research papers, campus life, faculty, placements, scholarships, competitions, student projects",
    "Tone & Context Awareness": "contrast sentences with positive/negative/neutral tone shifts, adjective and adverb blanks, formal vs informal register",
}

PASSAGE_CATEGORIES = list(CATEGORY_THEMES.keys())

# ── 100+ seed words per category for sentence completion generation ─────
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
        "vision","workload","workshop","SLA","roster","rotation","performance-review","exit-interview",
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
        "version-control","vulnerability","wavelength","wireless","microprocessor","overclocking",
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
        "warmly","wisely","zealously","impulsively","attentively","scrupulously",
    ],
}

# ── Email topic pool for dynamic generation (20+ diverse scenarios) ───────
EMAIL_TOPIC_POOL = [
    # Workplace
    {"context": "Workplace", "to": "Project Manager", "theme": "deadline extension request due to resource shortage and dependency delays"},
    {"context": "Workplace", "to": "HR Department", "theme": "requesting work-from-home policy clarification after new office mandate"},
    {"context": "Workplace", "to": "Department Head", "theme": "appreciating a colleague for exceptional performance during a critical product launch"},
    {"context": "Workplace", "to": "IT Support Team", "theme": "escalating an unresolved VPN and system access issue affecting productivity for a week"},
    {"context": "Workplace", "to": "Finance Department", "theme": "follow-up on pending reimbursement for certification course completed three months ago"},
    {"context": "Workplace", "to": "Senior Manager", "theme": "raising concern about unrealistic targets assigned to the team for the current quarter"},
    {"context": "Workplace", "to": "HR Business Partner", "theme": "requesting extension for mandatory cybersecurity training due to ongoing product release"},
    {"context": "Workplace", "to": "Operations Head", "theme": "proposing a new shift rotation policy to improve team morale and reduce overtime fatigue"},
    # Academic
    {"context": "Academic", "to": "Placement Coordinator", "theme": "requesting rescheduling of campus recruitment drive clashing with end-semester examinations"},
    {"context": "Academic", "to": "Professor / Faculty Advisor", "theme": "requesting deadline extension for thesis submission due to data collection delays"},
    {"context": "Academic", "to": "University Registrar", "theme": "applying for fee waiver or scholarship based on family financial hardship"},
    {"context": "Academic", "to": "Department Head", "theme": "complaint regarding unavailability of laboratory equipment during scheduled practical sessions"},
    {"context": "Academic", "to": "Internship Coordinator", "theme": "seeking permission to convert mandatory internship to a remote work arrangement"},
    # Customer / Consumer
    {"context": "Customer", "to": "Customer Support Team", "theme": "formal complaint about non-delivery of ordered laptop marked as delivered by courier"},
    {"context": "Customer", "to": "Bank Customer Service", "theme": "reporting an unauthorized transaction on bank account and requesting immediate resolution"},
    {"context": "Customer", "to": "Subscription Service Support", "theme": "requesting cancellation and refund for auto-renewed annual subscription without prior notice"},
    # Professional Communication
    {"context": "Professional", "to": "HR Department", "theme": "follow-up email after a job interview held ten days ago with no response received"},
    {"context": "Professional", "to": "Event Organising Committee", "theme": "expressing interest in volunteering for annual company picnic with availability constraints"},
    {"context": "Professional", "to": "Vendor / Supplier", "theme": "escalating repeated delays in raw material delivery impacting production schedule"},
    {"context": "Professional", "to": "Client Relations Team", "theme": "apologising for a service outage and outlining remediation steps and timelines"},
    {"context": "Professional", "to": "Marketing Head", "theme": "proposing a social media campaign to improve brand visibility among younger audiences"},
    {"context": "Professional", "to": "External Collaborator", "theme": "requesting an urgent meeting to align on revised project scope and deliverables"},
]

# ── Passage topic pool for dynamic generation ─────────────────────────────
PASSAGE_TOPIC_POOL = {
    "Workplace & Professional": [
        "impact of remote work on team collaboration and productivity",
        "importance of performance appraisals in employee retention",
        "role of mentorship programs in career development",
        "how agile methodology improves software delivery timelines",
        "effect of diversity and inclusion initiatives on company culture",
        "significance of KPIs in measuring organisational performance",
        "how upskilling programs reduce employee attrition rates",
        "benefits and challenges of cross-functional team structures",
        "role of transparent communication in crisis management at work",
        "how flexible work policies affect employee satisfaction",
    ],
    "Technology & Science": [
        "how machine learning algorithms detect fraudulent transactions",
        "impact of quantum computing on modern cryptography",
        "role of IoT devices in smart city infrastructure",
        "how CRISPR gene-editing technology works in medical research",
        "advantages of containerisation using Docker in software deployment",
        "how satellite imagery is used in disaster response operations",
        "role of neural networks in natural language processing",
        "environmental impact of e-waste from discarded electronic devices",
        "how cybersecurity professionals use ethical hacking to protect systems",
        "significance of open-source software in modern application development",
    ],
    "Social & Current Affairs": [
        "how microfinance empowers women entrepreneurs in rural communities",
        "impact of social media on voter behaviour during elections",
        "role of urban green spaces in reducing city heat island effect",
        "how universal basic income is being tested in various countries",
        "impact of air pollution on childhood respiratory health in cities",
        "why food security remains a critical global challenge",
        "role of international peacekeeping forces in post-conflict zones",
        "how climate migration is reshaping population distribution globally",
        "impact of digital literacy programs on reducing unemployment",
        "role of whistleblower protection laws in combating corruption",
    ],
    "Academic & Student Life": [
        "why internship experience improves graduate employability significantly",
        "impact of academic pressure on student mental health and wellbeing",
        "how peer learning circles enhance understanding of complex subjects",
        "role of extracurricular activities in holistic student development",
        "why plagiarism undermines the integrity of academic research",
        "impact of online education platforms on traditional classroom learning",
        "how college hackathons prepare students for real-world problem solving",
        "importance of research publications in faculty career progression",
        "why attendance policies remain controversial in higher education",
        "how scholarship programs widen access to quality education",
    ],
    "Tone & Context Awareness": [
        "how the tone of written communication affects professional relationships",
        "difference between formal and informal registers in workplace emails",
        "why word choice determines the effectiveness of persuasive writing",
        "how adverbs modify meaning and tone in journalistic writing",
        "impact of concise language in making technical documents accessible",
        "why active voice improves clarity in business communication",
        "how metaphors and analogies aid explanation in academic writing",
        "role of hedging language in scientific and research writing",
        "why proofreading reduces miscommunication in official correspondence",
        "how sentence structure affects the rhythm and readability of prose",
    ],
}

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
    st.session_state.pr_used_topics = []

def reset_email_state():
    st.session_state.em_phase = "task"
    st.session_state.em_scenario = None
    st.session_state.em_start_time = None
    st.session_state.em_live_text = ""
    st.session_state.em_submitted_text = ""
    st.session_state.em_score_data = None
    st.session_state.em_history = []
    st.session_state.em_count = 0
    st.session_state.em_used_topics = []

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
    "pr_used_topics": [],
    # email writing
    "em_phase": "task",
    "em_scenario": None, "em_start_time": None,
    "em_live_text": "", "em_submitted_text": "",
    "em_score_data": None,
    "em_history": [], "em_count": 0,
    "em_used_topics": [],
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
    raw = re.sub(r"^```json\s*|^```\s*|```\s*$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)

# ═══════════════════════════════════════════════════════════════════════════
#  SENTENCE COMPLETION — FULLY DYNAMIC
# ═══════════════════════════════════════════════════════════════════════════

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
                {"role": "system", "content": "Strict English evaluator. Reply YES or NO only."},
                {"role": "user", "content": f'Sentence: "{sentence}"\nAccepted: {accepted_answers}\nStudent: "{user_answer}"\nIs it correct or a valid synonym? YES or NO.'}
            ],
            model="llama-3.3-70b-versatile", temperature=0.1, max_tokens=5
        )
        return "YES" in resp.choices[0].message.content.upper()
    except Exception:
        return False

def generate_lesson(client, word, sentence):
    try:
        return _call(client, [
            {"role": "system", "content": "English teacher. Return valid JSON only."},
            {"role": "user", "content": f'Word missed: "{word}" in: "{sentence}"\nReturn JSON: {{"meaning":"1-line def","synonyms":["s1","s2","s3"],"examples":["ex1","ex2"],"memory_tip":"tip","related_words":[{{"word":"w","meaning":"m","example":"e"}}]}}'}
        ], max_tokens=600)
    except Exception:
        return {"meaning": f"{word}: key vocabulary word.", "synonyms": [], "examples": [], "memory_tip": "Review this word.", "related_words": []}

def generate_suggestion(client, word, sentence):
    try:
        return _call(client, [
            {"role": "system", "content": "English tutor. Return valid JSON only."},
            {"role": "user", "content": f'Student got "{word}" correct in: "{sentence}"\nReturn JSON: {{"tip":"1-2 sentence tip","advanced_word":"word","advanced_meaning":"meaning"}}'}
        ], max_tokens=200, temp=0.7)
    except Exception:
        return {"tip": f"Great use of '{word}'!", "advanced_word": "", "advanced_meaning": ""}

def _pick_seed(category: str) -> str:
    pool = SEED_WORDS.get(category, [])
    used = st.session_state.used_seeds.get(category, [])
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
    idx = st.session_state.cat_rotation_idx % len(cats)
    st.session_state.cat_rotation_idx += 1
    if idx == 0 and st.session_state.total > 0:
        random.shuffle(cats)
        st.session_state.cat_order = cats
    order = st.session_state.get("cat_order", cats)
    return order[idx % len(order)]

def generate_llm_question(client, category, asked_sentences, seed_word, attempt_num):
    themes = CATEGORY_THEMES.get(category, "general English vocabulary")
    temp = min(0.75 + attempt_num * 0.08, 1.0)
    avoid_list = asked_sentences[-40:] if len(asked_sentences) > 40 else asked_sentences
    avoid = "\n".join(f"- {s}" for s in avoid_list) if avoid_list else "none"

    prompt = f"""Create ONE unique sentence-completion question for TCS NQT Verbal Ability exam.

Category: {category}
Theme: {themes}
Focus seed word/concept: "{seed_word}" — use it to set the context of the sentence.
Difficulty: EASY TO MEDIUM — common words a college graduate would know.

STRICT TCS NQT FORMAT:
- ONE sentence with exactly ONE blank written as ________
- Student must type ONE word (or at most two words) that best fits
- Sentence must be 10 to 20 words long
- Clear grammatical context; only one logical answer category fits
- The blank answer must NOT be "{seed_word}" itself — use it only as context
- Do NOT copy or closely resemble these previously asked sentences:
{avoid}

Return ONLY valid JSON — no markdown, no extra text:
{{
  "sentence": "The manager ________ the new employee about company policies on the first day.",
  "accepted_answers": ["briefed", "informed", "educated"],
  "category": "{category}"
}}"""

    data = _call(client, [
        {"role": "system", "content": "You write unique English sentence completion exam questions. Return valid JSON only. No markdown."},
        {"role": "user", "content": prompt}
    ], max_tokens=300, temp=temp)

    assert "sentence" in data and "accepted_answers" in data
    assert "________" in data["sentence"], "Blank marker missing"
    assert len(data["accepted_answers"]) >= 1
    data["id"] = _sentence_hash(data["sentence"])
    data.setdefault("category", category)
    return data

# Static fallback pool (only used if all LLM attempts fail)
FALLBACK_POOL = [
    {"sentence": "The intern ________ all the required documents before the interview.", "accepted_answers": ["submitted", "prepared", "organised"], "category": "Workplace & Professional"},
    {"sentence": "The scientist ________ the experiment under controlled laboratory conditions.", "accepted_answers": ["conducted", "performed", "carried out"], "category": "Technology & Science"},
    {"sentence": "The government ________ a new policy to reduce air pollution in cities.", "accepted_answers": ["introduced", "announced", "implemented"], "category": "Social & Current Affairs"},
    {"sentence": "The professor ________ the students for their outstanding research presentation.", "accepted_answers": ["praised", "commended", "appreciated"], "category": "Academic & Student Life"},
    {"sentence": "She ________ accepted the criticism and promised to improve her work.", "accepted_answers": ["graciously", "humbly", "politely"], "category": "Tone & Context Awareness"},
    {"sentence": "The team ________ the project well ahead of the scheduled deadline.", "accepted_answers": ["completed", "finished", "delivered"], "category": "Workplace & Professional"},
    {"sentence": "The developer ________ a critical security vulnerability in the application.", "accepted_answers": ["discovered", "identified", "detected"], "category": "Technology & Science"},
    {"sentence": "The charity ________ food and clothing to thousands of flood victims.", "accepted_answers": ["distributed", "provided", "supplied"], "category": "Social & Current Affairs"},
    {"sentence": "The student ________ for the entrance exam by practising daily for months.", "accepted_answers": ["prepared", "studied", "revised"], "category": "Academic & Student Life"},
    {"sentence": "The manager spoke ________ to the client despite the project delays.", "accepted_answers": ["confidently", "calmly", "professionally"], "category": "Tone & Context Awareness"},
    {"sentence": "The company ________ its profits by cutting unnecessary operational costs.", "accepted_answers": ["increased", "improved", "boosted"], "category": "Workplace & Professional"},
    {"sentence": "The engineers ________ a new prototype for the electric vehicle battery.", "accepted_answers": ["designed", "built", "developed"], "category": "Technology & Science"},
    {"sentence": "The journalist ________ corruption in the local municipal corporation.", "accepted_answers": ["exposed", "uncovered", "revealed"], "category": "Social & Current Affairs"},
    {"sentence": "The college ________ fifty merit scholarships for underprivileged students.", "accepted_answers": ["awarded", "offered", "announced"], "category": "Academic & Student Life"},
    {"sentence": "He ________ agreed to take on the extra workload during the busy season.", "accepted_answers": ["willingly", "readily", "happily"], "category": "Tone & Context Awareness"},
]

def get_next_question(client):
    configured_cat = st.session_state.get("category_filter")
    asked_hashes = st.session_state.asked_hashes
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
    # Fallback only if LLM fails after 8 attempts
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
    st.session_state.answered = True
    st.session_state.user_answer = "(timed out)" if timed_out else ans
    st.session_state.feedback = is_correct
    st.session_state.total += 1
    primary = q["accepted_answers"][0]
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
    st.session_state.history.append({"word": primary, "correct": is_correct, "qid": q["id"], "reinforce": is_reinforce})
    st.session_state.live_answer = ""

# ═══════════════════════════════════════════════════════════════════════════
#  PASSAGE RECALL — FULLY DYNAMIC (1 to 1.5 lines, 25–35 words)
# ═══════════════════════════════════════════════════════════════════════════

def _pick_passage_topic(category: str) -> str:
    """Pick an unused topic from the passage topic pool for variety."""
    pool = PASSAGE_TOPIC_POOL.get(category, [f"a general topic about {category}"])
    used = st.session_state.get("pr_used_topics", [])
    unused = [t for t in pool if t not in used]
    if not unused:
        st.session_state.pr_used_topics = []
        unused = pool
    topic = random.choice(unused)
    st.session_state.pr_used_topics.append(topic)
    return topic

def generate_passage(client, category):
    """
    Generates a SHORT passage (25–35 words / 1 to 1.5 lines) per TCS NQT spec.
    Every call to this function generates a NEW passage using LLM — no hardcoding.
    """
    cat_theme = CATEGORY_THEMES.get(category, "general knowledge")
    topic = _pick_passage_topic(category)

    prompt = f"""Write ONE short factual passage for a TCS NQT Verbal Ability passage recall test.

Topic: {topic}
Category theme: {cat_theme}

STRICT REQUIREMENTS:
- Word count: EXACTLY 25 to 35 words — this is a 1 to 1.5 line passage as used in actual TCS NQT
- Self-contained: all key facts must be stated inside the passage itself
- Flowing prose — no bullet points, no headings, no lists
- Include at least 2 to 3 specific, distinct facts or details (numbers, names, percentages, or concrete outcomes work well)
- These details are what the student must recall — make them meaningful
- Suitable for a college student
- Do NOT start with "This passage" or "The following"
- Write naturally as a single continuous sentence or two short sentences

Return ONLY valid JSON — no markdown:
{{"topic": "short 4-6 word title", "passage": "the full passage text here"}}"""

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You write short factual English passages for reading comprehension tests. Return valid JSON only. No markdown backticks."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.75 + attempt * 0.1,
                max_tokens=200,
            )
            raw = resp.choices[0].message.content.strip()
            raw = re.sub(r"^```json\s*|^```\s*|```\s*$", "", raw, flags=re.MULTILINE).strip()
            data = json.loads(raw)
            assert "passage" in data and "topic" in data
            words = len(data["passage"].split())
            # Accept 20–50 words (slightly relaxed to handle LLM variance)
            assert 20 <= words <= 55, f"Word count {words} out of range"
            return data
        except Exception:
            time.sleep(0.5)

    # Last-resort fallback: generate a simple passage inline without JSON
    fallback_passages = [
        {"topic": "Remote Work Trends", "passage": "Remote work increased by 140% between 2019 and 2023, boosting employee satisfaction by 22% while reducing office operational costs for most large organisations significantly."},
        {"topic": "Urban Air Pollution", "passage": "Air pollution causes 7 million premature deaths annually worldwide, with particulate matter from vehicles and industries being the leading contributor in densely populated cities."},
        {"topic": "Machine Learning Growth", "passage": "The global machine learning market reached 21 billion dollars in 2022 and is projected to grow at 38% annually, driven by demand in healthcare, finance, and retail sectors."},
        {"topic": "Student Mental Health", "passage": "A 2023 survey found that 45% of university students reported high academic stress, with examination pressure and financial concerns cited as the two most common contributing factors."},
        {"topic": "Email Communication", "passage": "Studies show that professionals spend an average of 2.5 hours daily reading and writing emails, making clear and concise written communication an essential workplace skill today."},
    ]
    return random.choice(fallback_passages)

def score_recall(client, original_passage, user_response):
    """Score recall per TCS NQT criteria — content accuracy over verbatim matching."""
    if not user_response.strip():
        return {
            "score": 0, "max_score": 10,
            "content_accuracy": "No response submitted.",
            "key_points_covered": [],
            "key_points_missed": ["No response — all key facts missed."],
            "feedback": "You did not write anything. Try to recall at least the main idea and one key fact next time.",
            "grade": "F"
        }

    prompt = f"""You are evaluating a TCS NQT Verbal Ability passage recall answer.

ORIGINAL PASSAGE (25–35 words):
\"\"\"{original_passage}\"\"\"

STUDENT'S RECONSTRUCTION:
\"\"\"{user_response}\"\"\"

TCS NQT Scoring Criteria (total = 10 points):
- Main idea captured accurately: 0–4 points
- Specific facts / numbers / details recalled correctly: 0–4 points
- Clarity and readability of student's writing: 0–2 points

Scoring guidance:
- Since the passage is very short (1–1.5 lines), every specific detail matters greatly
- Award high marks only if the student captured the core facts accurately
- The student must SHOW understanding — NOT copy word-for-word
- Partial credit is allowed for partially correct facts
- A student who captures the main idea but misses specific numbers/names gets 5–6 out of 10

Return ONLY valid JSON — no markdown:
{{
  "score": 7,
  "max_score": 10,
  "content_accuracy": "One sentence summary of how accurately the student recalled the passage",
  "key_points_covered": ["specific fact or detail they recalled correctly"],
  "key_points_missed": ["specific fact or detail they missed or got wrong"],
  "feedback": "2–3 sentence constructive feedback for improvement",
  "grade": "B"
}}
Grade scale: 9–10 = A, 7–8 = B, 5–6 = C, 3–4 = D, 0–2 = F"""

    try:
        return _call(client, [
            {"role": "system", "content": "You are a strict TCS NQT verbal ability examiner. Return valid JSON only. No markdown."},
            {"role": "user", "content": prompt}
        ], max_tokens=500, temp=0.3)
    except Exception:
        words_written = len(user_response.strip().split())
        rough_score = min(10, max(0, words_written // 3))
        return {
            "score": rough_score, "max_score": 10,
            "content_accuracy": "Could not evaluate automatically.",
            "key_points_covered": [],
            "key_points_missed": [],
            "feedback": f"You wrote {words_written} words. Compare your response with the original passage carefully.",
            "grade": "—"
        }

# ═══════════════════════════════════════════════════════════════════════════
#  EMAIL WRITING — FULLY DYNAMIC SCENARIO GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def _pick_email_topic() -> dict:
    """Pick an unused email topic from the pool for variety."""
    pool = EMAIL_TOPIC_POOL
    used = st.session_state.get("em_used_topics", [])
    unused = [t for t in pool if t["theme"] not in used]
    if not unused:
        st.session_state.em_used_topics = []
        unused = pool
    topic = random.choice(unused)
    st.session_state.em_used_topics.append(topic["theme"])
    return topic

def generate_email_scenario(client) -> dict:
    """
    Generate a FULLY DYNAMIC email writing scenario per TCS NQT spec.
    Every call generates a new, unique, realistic scenario using LLM.
    """
    topic = _pick_email_topic()

    prompt = f"""Create ONE realistic TCS NQT Email Writing scenario for a college student or young professional.

Context type: {topic["context"]}
Recipient: {topic["to"]}
Core theme: {topic["theme"]}

REQUIREMENTS:
- The situation must be 3–5 sentences: specific, realistic, with enough detail that a student can write a full email
- Include specific context (e.g. exact duration, specific role, concrete problem) — not vague
- The task instruction must clearly tell the student WHAT to do and WHAT to include in the email
- Make it something a real TCS employee or college student would face
- Provide a realistic subject line hint (not generic)
- The email should require AT LEAST 100 words to address properly

Return ONLY valid JSON — no markdown:
{{
  "situation": "3–5 sentence description of the situation with specific context",
  "task": "Clear instruction: Write an email to [recipient] doing X, Y, Z. Include these points...",
  "to": "{topic["to"]}",
  "subject_hint": "Specific Subject Line Example"
}}"""

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You create realistic professional and academic email writing scenarios for TCS NQT exam preparation. Return valid JSON only. No markdown."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.8 + attempt * 0.05,
                max_tokens=500,
            )
            raw = resp.choices[0].message.content.strip()
            raw = re.sub(r"^```json\s*|^```\s*|```\s*$", "", raw, flags=re.MULTILINE).strip()
            data = json.loads(raw)
            assert "situation" in data and "task" in data and "to" in data and "subject_hint" in data
            assert len(data["situation"]) > 80, "Situation too short"
            return data
        except Exception:
            time.sleep(0.5)

    # Fallback if LLM fails
    return {
        "situation": f"You are dealing with a situation related to {topic['theme']}. This has been ongoing for some time and requires formal written communication to resolve it. You have already tried informal channels without success and need to escalate the matter through a professional email.",
        "task": f"Write a formal professional email to {topic['to']} explaining the situation clearly, stating what action you require, providing any relevant background details, and suggesting a reasonable timeline for resolution.",
        "to": topic["to"],
        "subject_hint": f"Regarding: {topic['theme'].title()[:50]}"
    }

def score_email(client, scenario, user_email):
    """Score email per TCS NQT criteria."""
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
            "feedback": "You did not write a sufficient response. TCS NQT requires at least 100 words in complete sentences addressing all aspects of the situation.",
            "grade": "F"
        }

    meets_min_str = "true" if word_count >= EMAIL_MIN_WORDS else "false"

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
1. Task completion — does the email address ALL aspects of the situation? (0–3 pts)
2. Language and vocabulary — appropriate word choice, no major grammatical errors? (0–2 pts)
3. Tone and register — professional, polite, and appropriate for the recipient and context? (0–2 pts)
4. Structure and organisation — clear subject line reference, greeting, organised body, professional closing? (0–2 pts)
5. Word count compliance — at least 100 words in complete sentences? (0–1 pt)

IMPORTANT: If word count is below 100, cap total score at 5 regardless of quality.

Return ONLY valid JSON — no markdown:
{{
  "score": 7,
  "max_score": 10,
  "word_count": {word_count},
  "meets_minimum": {meets_min_str},
  "task_completion": "One sentence about how well all aspects of the task were addressed",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["specific improvement area 1", "specific improvement area 2"],
  "tone_assessment": "One sentence assessment of tone and register",
  "structure_assessment": "One sentence about email structure and organisation",
  "feedback": "3–4 sentence overall constructive feedback",
  "grade": "B"
}}
Grade scale: 9–10 = A, 7–8 = B, 5–6 = C, 3–4 = D, 0–2 = F"""

    try:
        return _call(client, [
            {"role": "system", "content": "You are a strict TCS NQT email writing examiner. Return valid JSON only. No markdown."},
            {"role": "user", "content": prompt}
        ], max_tokens=600, temp=0.3)
    except Exception:
        rough = min(10, max(0, word_count // 20)) if word_count >= EMAIL_MIN_WORDS else min(5, word_count // 20)
        return {
            "score": rough, "max_score": 10, "word_count": word_count,
            "meets_minimum": word_count >= EMAIL_MIN_WORDS,
            "task_completion": "Could not evaluate automatically.",
            "strengths": [], "improvements": [],
            "tone_assessment": "—", "structure_assessment": "—",
            "feedback": f"You wrote {word_count} words. {'Meets the 100-word minimum.' if word_count >= EMAIL_MIN_WORDS else 'Below the required 100-word minimum.'}",
            "grade": "—"
        }

# ═══════════════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="big-title">⚡ TCS NQT Verbal Prep</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Sentence Completion · Passage Recall · Email Writing — 100% AI-generated questions, TCS NQT spec</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  SETUP PAGE
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.page == "setup":
    st.markdown("""
    <div class="question-card" style="margin-bottom:20px;">
        <b style="color:#B8A6FF;">📋 TCS NQT Verbal Ability — Official Structure</b><br><br>
        <table style="width:100%;border-collapse:collapse;font-size:0.82rem;color:#E4E4F0;">
            <tr style="background:#2e324a;">
                <th style="padding:8px;text-align:left;">Section</th>
                <th style="padding:8px;text-align:center;">Items</th>
                <th style="padding:8px;text-align:center;">Time per Item</th>
            </tr>
            <tr><td style="padding:8px;">Sentence Completion</td><td style="padding:8px;text-align:center;">20</td><td style="padding:8px;text-align:center;">25 seconds each</td></tr>
            <tr style="background:#1a1f2e;"><td style="padding:8px;">Instruction (Sentence Completion)</td><td style="padding:8px;text-align:center;">1</td><td style="padding:8px;text-align:center;">25 seconds</td></tr>
            <tr><td style="padding:8px;">Passage Recall (4 passages × 2 parts)</td><td style="padding:8px;text-align:center;">4+4</td><td style="padding:8px;text-align:center;">30s read + 90s write</td></tr>
            <tr style="background:#1a1f2e;"><td style="padding:8px;">Instruction (Passage Recall)</td><td style="padding:8px;text-align:center;">1</td><td style="padding:8px;text-align:center;">15 seconds</td></tr>
            <tr><td style="padding:8px;">Email Writing</td><td style="padding:8px;text-align:center;">1</td><td style="padding:8px;text-align:center;">540 seconds (9 min), min 100 words</td></tr>
        </table>
        <br>
        <span style="color:#00E0B8;font-size:0.8rem;">✨ All questions are generated fresh by AI — no two sessions are the same.</span>
    </div>
    """, unsafe_allow_html=True)

    with st.form("setup_form"):
        api_key = st.text_input("Groq API Key", type="password", help="Free at console.groq.com")
        mode = st.radio(
            "Select Practice Mode",
            ["⚡ Sentence Completion", "📖 Passage Recall", "✉️ Email Writing"],
            horizontal=True
        )
        cat_choice = st.selectbox("Category (Sentence Completion & Passage Recall)", list(CATEGORY_FILTER.keys()))
        submitted = st.form_submit_button("🚀 Start Practice")

    if submitted:
        if not api_key.strip():
            st.error("Please enter your Groq API key.")
        else:
            reset_vocab_state()
            reset_recall_state()
            reset_email_state()
            st.session_state.api_key = api_key
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
    client = get_client(st.session_state.api_key)
    missed_count = len(st.session_state.missed_bank)

    st.markdown(
        f'<div class="score-pill">✅ {st.session_state.score}/{st.session_state.total} &nbsp;|&nbsp; '
        f'Q{st.session_state.total + 1}/20 &nbsp;|&nbsp; 🔁 {missed_count} pending</div>',
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

    # Pick question
    if st.session_state.current_q is None:
        pull_reinforce = (
            st.session_state.missed_bank and
            st.session_state.total > 0 and
            st.session_state.total % 4 == 0
        )
        if pull_reinforce:
            entry = st.session_state.missed_bank[0]
            q = {
                "id": entry["id"], "sentence": entry["sentence"],
                "accepted_answers": entry["accepted_answers"], "category": entry["category"]
            }
            st.session_state.is_reinforce = True
        else:
            with st.spinner("✨ Generating question…"):
                q = get_next_question(client)
            st.session_state.is_reinforce = False

        st.session_state.asked_hashes.add(q["id"])
        st.session_state.asked_sentences.append(q["sentence"])
        st.session_state.current_q = q
        st.session_state.start_time = time.time()
        st.session_state.answered = False
        st.session_state.feedback = None
        st.session_state.lesson = None
        st.session_state.suggestion = None
        st.session_state.live_answer = ""
        st.rerun()

    q = st.session_state.current_q
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0.0, TIME_LIMIT - elapsed)
    is_reinforce = st.session_state.is_reinforce

    if not st.session_state.answered:
        if remaining <= 0:
            captured = st.session_state.live_answer.strip()
            timed_out = captured == ""
            process_submission(client, q, captured, timed_out=timed_out)
            st.rerun()

        col1, col2 = st.columns([4, 1])
        with col1:
            tags = f'<span class="q-tag">{q["category"].upper()}</span>'
            if is_reinforce:
                tags += '<span class="reinforce-tag">🔁 REINFORCE</span>'
            else:
                tags += '<span class="llm-tag">✨ AI Generated</span>'
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
        if is_reinforce:
            tags += '<span class="reinforce-tag">🔁 REINFORCE</span>'
        else:
            tags += '<span class="llm-tag">✨ AI Generated</span>'
        st.markdown(
            f'<div class="question-card">{tags}'
            f'<div class="q-num">Question {st.session_state.total}</div>'
            f'<div class="q-text">{q["sentence"]}</div></div>',
            unsafe_allow_html=True,
        )
        primary = q["accepted_answers"][0]
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
            timeout_note = '<br><span style="font-size:0.8rem;color:#FF6B35;">⏰ Time ran out.</span>' if st.session_state.user_answer == "(timed out)" else ""
            reinforce_note = "" if is_reinforce else '<br><span style="font-size:0.8rem;color:#FF9966;">🔁 Will revisit for reinforcement.</span>'
            st.markdown(f"""
            <div class="wrong-box">
                ❌ <b>Incorrect.</b> You wrote: "<i>{st.session_state.user_answer}</i>"<br>
                <span style="font-size:0.85rem;">Answer: <b>{all_accept}</b></span>{timeout_note}{reinforce_note}
            </div>""", unsafe_allow_html=True)
            if st.session_state.lesson:
                L = st.session_state.lesson
                ex_html = "".join(f"<li>{e}</li>" for e in L.get("examples", []))
                syn_html = ", ".join(L.get("synonyms", []))
                rel_html = "".join(f"<li><b>{r['word']}</b> — {r['meaning']}<br><i>{r['example']}</i></li>" for r in L.get("related_words", []))
                st.markdown(f"""
                <div class="lesson-box">
                    <h4 style="margin-top:0;color:#B8A6FF;">📘 {primary}</h4>
                    <p><b>Meaning:</b> {L.get('meaning', '')}</p>
                    <p><b>Synonyms:</b> {syn_html}</p>
                    <p><b>Examples:</b></p><ul>{ex_html}</ul>
                    <p><b>Memory tip:</b> {L.get('memory_tip', '')}</p>
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
        f'<div class="score-pill">📖 Passage {pr_count + 1} &nbsp;|&nbsp; {score_txt} &nbsp;|&nbsp; {len(st.session_state.pr_history)} done</div>',
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

    # Generate a NEW passage every time pr_passage is None
    if st.session_state.pr_passage is None:
        configured_cat = st.session_state.get("category_filter")
        cat = configured_cat if configured_cat else random.choice(PASSAGE_CATEGORIES)
        with st.spinner("📝 Generating new passage…"):
            data = generate_passage(client, cat)
        st.session_state.pr_passage = data["passage"]
        st.session_state.pr_topic = data.get("topic", "Reading Passage")
        st.session_state.pr_start_time = time.time()
        st.session_state.pr_phase = "read"
        st.session_state.pr_live_text = ""
        st.rerun()

    passage = st.session_state.pr_passage
    topic = st.session_state.pr_topic

    # ── PHASE 1 — READ (30 seconds per TCS spec) ───────────────────────────
    if phase == "read":
        elapsed = time.time() - st.session_state.pr_start_time
        remaining = max(0.0, READ_TIME - elapsed)

        if remaining <= 0:
            st.session_state.pr_phase = "write"
            st.session_state.pr_start_time = time.time()
            st.rerun()

        st.markdown(
            '<div class="info-bar">📋 <b>TCS NQT Instructions:</b> Read the passage carefully. '
            'You have <b>30 seconds</b>. The passage disappears when the timer ends. '
            'Then you have <b>90 seconds</b> to rewrite it in your own words. '
            'You are scored on <b>content accuracy and understanding</b>, not word-for-word matching.</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f'<span class="phase-badge phase-read">📖 READ PHASE — {int(remaining)}s remaining</span>', unsafe_allow_html=True)
            word_count = len(passage.split())
            st.markdown(
                f'<div class="passage-card">'
                f'<b style="color:#B8A6FF;font-size:0.85rem;">TOPIC: {topic.upper()}</b>'
                f'<div style="color:#8A8FA3;font-size:0.75rem;margin-bottom:12px;">{word_count} words · AI-generated · TCS NQT format (1–1.5 lines)</div>'
                f'<div style="font-size:1.18rem;line-height:2.1;">{passage}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        with col2:
            warn_cls = "timer-warn" if remaining <= 8 else "timer-read"
            st.markdown(f'<div class="timer-box {warn_cls}">{int(remaining)}</div>', unsafe_allow_html=True)
            st.markdown('<p style="text-align:center;color:#8A8FA3;font-size:0.72rem;">sec</p>', unsafe_allow_html=True)

        time.sleep(1)
        st.rerun()

    # ── PHASE 2 — WRITE (90 seconds per TCS spec) ─────────────────────────
    elif phase == "write":
        elapsed = time.time() - st.session_state.pr_start_time
        remaining = max(0.0, WRITE_TIME - elapsed)

        if remaining <= 0:
            final_text = st.session_state.pr_live_text.strip()
            st.session_state.pr_submitted_text = final_text
            with st.spinner("🔍 Scoring your response…"):
                score_data = score_recall(client, passage, final_text)
            st.session_state.pr_score_data = score_data
            st.session_state.pr_history.append({
                "passage_num": st.session_state.pr_count + 1,
                "topic": topic,
                "score": score_data.get("score", 0),
                "max_score": score_data.get("max_score", 10),
                "grade": score_data.get("grade", "—"),
                "user_text": final_text,
                "passage": passage,
            })
            st.session_state.pr_count += 1
            st.session_state.pr_phase = "scored"
            st.rerun()

        st.markdown(
            '<div class="info-bar">✍️ <b>Passage is now hidden.</b> '
            'Rewrite what you remember in your own words. '
            'Focus on the <b>main idea and key facts</b> — specific numbers and details matter. '
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
                placeholder="Write what you remember — the main idea, key facts, numbers, names…",
                key="_recall_input",
                on_change=_save_recall,
                value=st.session_state.pr_live_text,
                height=160,
            )
            words_typed = len(st.session_state.pr_live_text.strip().split()) if st.session_state.pr_live_text.strip() else 0
            st.markdown(f'<p style="color:#8A8FA3;font-size:0.78rem;">Words typed: {words_typed}</p>', unsafe_allow_html=True)
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
                "topic": topic,
                "score": score_data.get("score", 0),
                "max_score": score_data.get("max_score", 10),
                "grade": score_data.get("grade", "—"),
                "user_text": final_text,
                "passage": passage,
            })
            st.session_state.pr_count += 1
            st.session_state.pr_phase = "scored"
            st.rerun()

        time.sleep(1)
        st.rerun()

    # ── PHASE 3 — SCORED ───────────────────────────────────────────────────
    elif phase == "scored":
        sd = st.session_state.pr_score_data or {}
        score = sd.get("score", 0)
        max_score = sd.get("max_score", 10)
        grade = sd.get("grade", "—")
        pct = round(100 * score / max_score) if max_score else 0
        grade_color = {"A": "#00E0B8", "B": "#7C5CFF", "C": "#FFD700", "D": "#FF9966", "F": "#FF6B35"}.get(grade, "#8A8FA3")

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
                    <p style="margin:0;color:#E4E4F0;"><b>Content Accuracy:</b><br>{sd.get('content_accuracy', '—')}</p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        covered = sd.get("key_points_covered", [])
        missed = sd.get("key_points_missed", [])
        if covered or missed:
            c_html = "".join(f'<li style="color:#6EE7B7;">✅ {p}</li>' for p in covered)
            m_html = "".join(f'<li style="color:#FCA5A5;">❌ {p}</li>' for p in missed)
            st.markdown(f"""
            <div class="lesson-box" style="margin-top:14px;">
                <b style="color:#B8A6FF;">Key Points Breakdown</b>
                <ul style="margin-top:8px;">{c_html}{m_html}</ul>
            </div>""", unsafe_allow_html=True)

        if sd.get("feedback"):
            st.markdown(f"""
            <div class="levelup-box" style="margin-top:12px;">
                <b style="color:#00E0B8;">💡 Feedback</b><br>{sd['feedback']}
            </div>""", unsafe_allow_html=True)

        with st.expander("📄 View Original Passage"):
            st.markdown(
                f'<div class="passage-card">'
                f'<b style="color:#B8A6FF;font-size:0.85rem;">ORIGINAL — {topic.upper()}</b>'
                f'<div style="font-size:1.1rem;line-height:2.0;margin-top:10px;">{passage}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        with st.expander("✍️ Your Reconstruction"):
            user_txt = st.session_state.pr_submitted_text or "(nothing submitted)"
            st.markdown(f'<div style="background:#12162a;border-radius:10px;padding:16px;color:#E4E4F0;line-height:1.7;">{user_txt}</div>', unsafe_allow_html=True)

        st.write("")
        if st.button("➡️ Next Passage"):
            # Clear passage — new one will be generated fresh by LLM
            st.session_state.pr_passage = None
            st.session_state.pr_score_data = None
            st.session_state.pr_phase = "read"
            st.session_state.pr_live_text = ""
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
        f'<div class="score-pill">✉️ Email {em_count + 1} &nbsp;|&nbsp; {score_txt} &nbsp;|&nbsp; {len(st.session_state.em_history)} done</div>',
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

    # Generate a NEW scenario every time em_scenario is None
    if st.session_state.em_scenario is None:
        with st.spinner("✉️ Generating email scenario…"):
            st.session_state.em_scenario = generate_email_scenario(client)
        st.session_state.em_phase = "task"
        st.session_state.em_live_text = ""

    scenario = st.session_state.em_scenario

    # ── PHASE 1 — READ TASK ────────────────────────────────────────────────
    if phase == "task":
        st.markdown(
            '<div class="info-bar">✉️ <b>TCS NQT Email Writing Instructions:</b> '
            'Read the situation carefully. You will have <b>9 minutes</b> to write an email. '
            'Write <b>at least 100 words</b> in complete sentences. '
            'Address ALL aspects of the situation professionally.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<span class="phase-badge phase-email">✉️ AI-GENERATED EMAIL TASK</span>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="email-card">
            <b style="color:#FFD700;font-size:0.82rem;">📋 SITUATION</b>
            <p style="color:#E4E4F0;margin-top:8px;line-height:1.85;">{scenario['situation']}</p>
            <hr style="border-color:#2e324a;margin:16px 0;">
            <b style="color:#FFD700;font-size:0.82rem;">📝 YOUR TASK</b>
            <p style="color:#E4E4F0;margin-top:8px;line-height:1.85;">{scenario['task']}</p>
            <hr style="border-color:#2e324a;margin:16px 0;">
            <b style="color:#8A8FA3;font-size:0.78rem;">To:</b> <span style="color:#B8A6FF;">{scenario['to']}</span><br>
            <b style="color:#8A8FA3;font-size:0.78rem;">Subject hint:</b> <span style="color:#8A8FA3;font-style:italic;">{scenario['subject_hint']}</span>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        if st.button("🚀 Start Writing (9-minute timer begins now)"):
            st.session_state.em_phase = "writing"
            st.session_state.em_start_time = time.time()
            st.session_state.em_live_text = ""
            st.rerun()

    # ── PHASE 2 — WRITE EMAIL (540 seconds = 9 minutes) ───────────────────
    elif phase == "writing":
        elapsed = time.time() - st.session_state.em_start_time
        remaining = max(0.0, EMAIL_TIME - elapsed)
        minutes = int(remaining) // 60
        seconds = int(remaining) % 60

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
                "score": score_data.get("score", 0),
                "max_score": score_data.get("max_score", 10),
                "grade": score_data.get("grade", "—"),
                "word_count": word_count,
                "user_text": final_text,
            })
            st.session_state.em_count += 1
            st.session_state.em_phase = "scored"
            st.rerun()

        st.markdown('<span class="phase-badge phase-email">✍️ WRITING — Timer Running</span>', unsafe_allow_html=True)

        with st.expander("📋 View Situation & Task", expanded=False):
            st.markdown(f"""
            <div style="background:#12162a;border-radius:10px;padding:16px;color:#E4E4F0;">
                <b style="color:#FFD700;">Situation:</b><br>{scenario['situation']}<br><br>
                <b style="color:#FFD700;">Task:</b><br>{scenario['task']}<br><br>
                <b style="color:#8A8FA3;">To:</b> {scenario['to']}
            </div>""", unsafe_allow_html=True)

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
            placeholder=f"Start with a proper greeting...\n\nAddress: {scenario['task'][:100]}...\n\nEnd with a professional closing and your name.",
            key="_email_input",
            on_change=_save_email,
            value=st.session_state.em_live_text,
            height=340,
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
                "score": score_data.get("score", 0),
                "max_score": score_data.get("max_score", 10),
                "grade": score_data.get("grade", "—"),
                "word_count": word_count,
                "user_text": final_text,
            })
            st.session_state.em_count += 1
            st.session_state.em_phase = "scored"
            st.rerun()

        time.sleep(1)
        st.rerun()

    # ── PHASE 3 — SCORED ───────────────────────────────────────────────────
    elif phase == "scored":
        sd = st.session_state.em_score_data or {}
        score = sd.get("score", 0)
        max_score = sd.get("max_score", 10)
        grade = sd.get("grade", "—")
        pct = round(100 * score / max_score) if max_score else 0
        word_count = sd.get("word_count", 0)
        meets_min = sd.get("meets_minimum", False)
        grade_color = {"A": "#00E0B8", "B": "#7C5CFF", "C": "#FFD700", "D": "#FF9966", "F": "#FF6B35"}.get(grade, "#8A8FA3")

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
                    <p style="margin:0;color:#E4E4F0;"><b>Task Completion:</b><br>{sd.get('task_completion', '—')}</p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="lesson-box">
                <b style="color:#B8A6FF;">📝 Tone & Structure</b>
                <p style="margin-top:8px;"><b>Tone:</b> {sd.get('tone_assessment', '—')}</p>
                <p><b>Structure:</b> {sd.get('structure_assessment', '—')}</p>
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
            # Clear scenario — new one will be generated fresh by LLM
            st.session_state.em_scenario = None
            st.session_state.em_score_data = None
            st.session_state.em_phase = "task"
            st.session_state.em_live_text = ""
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
            <div class="big-title" style="font-size:2rem;">Passage Recall History</div>
            <p style="font-size:1.1rem;color:#E4E4F0;">{grade_label}<br>
            Average Score: <b style="color:#00E0B8;">{avg:.1f}</b>/10 across {len(history)} passages</p>
        </div>""", unsafe_allow_html=True)
        st.write("")
        for h in reversed(history):
            g_color = {"A": "#00E0B8", "B": "#7C5CFF", "C": "#FFD700", "D": "#FF9966", "F": "#FF6B35"}.get(h["grade"], "#8A8FA3")
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
    pct = round(100 * score / total) if total else 0
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
        st.markdown(f'<div class="lesson-box"><b style="color:#B8A6FF;">📚 Revise these words:</b><br><br>{chips}</div>', unsafe_allow_html=True)

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
st.markdown("""
<hr>
<div style="text-align:center; padding:10px;">
    <span style="color:#00E0B8; font-weight:bold;">
        🚀 Designed & Developed by Rahul Etyala
    </span>
</div>
""", unsafe_allow_html=True)
