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
    font-size: 1.1rem; color: #E8E8F8; line-height: 1.9;
}
.recall-card {
    background: #0f1a18; border: 2px solid #00E0B855;
    border-radius: 16px; padding: 22px;
    box-shadow: 0 4px 32px rgba(0,224,184,0.1);
}
.phase-badge {
    display: inline-block; border-radius: 999px;
    padding: 5px 18px; font-size: 0.78rem; font-weight: 700;
    letter-spacing: 0.08em; margin-bottom: 16px;
}
.phase-read  { background: #7C5CFF22; color: #B8A6FF; border: 1px solid #7C5CFF55; }
.phase-write { background: #00E0B822; color: #00E0B8;  border: 1px solid #00E0B855; }
.phase-done  { background: #FF6B3522; color: #FF9966;  border: 1px solid #FF6B3555; }
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
.correct-box { background: #0d2b1f; border: 1px solid #1f9d6b; border-radius: 12px; padding: 18px; color: #6EE7B7; }
.wrong-box   { background: #2b0d12; border: 1px solid #c5455a; border-radius: 12px; padding: 18px; color: #FCA5A5; }
.lesson-box  { background: #1a1f2e; border-left: 4px solid #7C5CFF; border-radius: 8px; padding: 18px 22px; margin-top: 14px; color: #E4E4F0; }
.levelup-box { background: #1a2e1f; border-left: 4px solid #00E0B8;  border-radius: 8px; padding: 18px 22px; margin-top: 14px; color: #E4E4F0; }
.recall-score-box { background: #12162a; border: 2px solid #7C5CFF55; border-radius: 14px; padding: 22px; margin-top: 14px; color: #E4E4F0; }
.score-pill  { background: #1c1f2e; border-radius: 999px; padding: 8px 20px; display: inline-block; font-size: 0.85rem; color: #00E0B8; border: 1px solid #2e324a; }
.missed-chip { display: inline-block; background: #2b0d12; color: #FCA5A5; border: 1px solid #c5455a55; border-radius: 8px; padding: 4px 12px; margin: 4px; font-size: 0.8rem; }
.info-bar { background: #1a1f2e; border-radius: 10px; padding: 12px 18px; color: #8A8FA3; font-size: 0.82rem; margin-bottom: 12px; border: 1px solid #2e324a; }
.stButton > button { background: linear-gradient(90deg, #7C5CFF, #00E0B8); color: #0f1117; font-weight: 700; border: none; border-radius: 10px; padding: 0.6rem 1.4rem; transition: transform 0.15s ease; }
.stButton > button:hover { transform: scale(1.03); }
.stTextArea textarea { background: #12162a !important; color: #E8E8F8 !important; border: 1px solid #2e324a !important; border-radius: 10px !important; font-family: 'IBM Plex Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

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

# 130+ seed words per category for maximum question variety
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
        "induction","infrastructure","integration","inventory","job-description","jurisdiction",
        "KPI","liaison","logistics","mandate","mediation","merger","minutes","morale",
        "motivation","networking","objective","operations","outsourcing","overtime","partnership",
        "payroll","pipeline","planning","policy","portfolio","probation","procurement","profit",
        "project","proposal","protocol","punctuality","quarter","quota","recognition","redundancy",
        "reimbursement","reporting","retention","revenue","review","risk","roadmap","roster",
        "rotation","schedule","shortlisting","skillset","SLA","staffing","succession","survey",
        "sustainability","target","teamwork","tenure","termination","timeline","training","transfer",
        "transparency","turnaround","upskilling","vendor","vision","workload","workshop",
    ],
    "Technology & Science": [
        "algorithm","bandwidth","debugging","encryption","firmware","deployment","prototype",
        "simulation","hypothesis","calibration","automation","integration","optimization",
        "cybersecurity","satellite","genome","telescope","semiconductor","neural","database",
        "latency","virtualization","repository","compiler","authentication","quantum","sensor",
        "abstraction","agile","analytics","anomaly","API","architecture","artificial-intelligence",
        "backup","benchmark","bioinformatics","blockchain","botnet","cache","checksum","circuit",
        "cloning","cloud","code-review","cognitive","collision","compilation","concurrency",
        "configuration","connectivity","container","data-mining","debugging","decryption",
        "deep-learning","dependency","diagnosis","distributed","DNS","docker","ecosystem",
        "electromagnetism","endpoint","entropy","environment","experiment","extrapolation",
        "fiber-optic","forensics","frequency","functionality","GPU","hashing","hosting",
        "hypothesis","inference","innovation","input","interface","interpolation","IoT",
        "iteration","kernel","lab","library","load-balancing","logging","machine-learning",
        "malware","middleware","migration","modeling","module","monitoring","nanotechnology",
        "network","neural-network","node","observation","open-source","output","parameter",
        "patch","payload","performance","physics","pipeline","platform","plugin","port",
        "prediction","protocol","proxy","radiation","regression","rendering","replication",
        "research","response","robotics","runtime","scalability","schema","scripting",
        "security","server","signal","software","spectrum","stack","storage","streaming",
        "syntax","testing","thread","topology","transaction","transmission","update","upload",
        "validation","variable","version-control","vulnerability","wavelength","wireless",
    ],
    "Social & Current Affairs": [
        "legislation","advocacy","referendum","humanitarian","infrastructure","sanitation",
        "deforestation","migration","pandemic","unemployment","subsidy","transparency","reform",
        "inequality","censorship","vaccination","welfare","climate","diplomacy","sovereignty",
        "nutrition","corruption","education","poverty","governance","regulation","protest",
        "accountability","activism","addiction","affirmative-action","agriculture","aid",
        "alienation","allocation","amnesty","anarchy","apartheid","asylum","austerity",
        "authoritarianism","bias","biodiversity","border","boycott","bureaucracy","capitalism",
        "carbon-footprint","caste","child-labour","citizenship","civil-rights","coalition",
        "communalism","community","compensation","conflict","conservation","constitution",
        "consumption","controversy","coup","crime","crisis","cultural","cybercrime","debt",
        "decentralization","deficit","democracy","demographic","deprivation","development",
        "dignity","disability","discrimination","disparity","displacement","drought","dynasty",
        "economic","election","embargo","emission","empowerment","environment","epidemic",
        "equity","ethnicity","evacuation","exploitation","extremism","famine","federalism",
        "feminism","flooding","food-security","foreign-policy","freedom","gender","geopolitics",
        "globalization","health","homelessness","human-rights","identity","immigration",
        "impeachment","incarceration","inclusion","indigenous","inflation","injustice",
        "insurgency","integration","judicial","justice","labour","land-rights","law",
        "leadership","lobbying","manifesto","media","minority","nationalism","natural-disaster",
        "NGO","obesity","oppression","parliament","patriarchy","peacekeeping","polarization",
        "policy","pollution","population","privilege","propaganda","public-health","racism",
        "radicalization","recession","reconciliation","rehabilitation","religion","representation",
        "resilience","revenue","rights","rural","secularism","segregation","social-media",
        "strike","suffrage","surveillance","sustainable","taxation","terrorism","treaty",
        "tribunal","urbanization","violence","voter","water","xenophobia","youth",
    ],
    "Academic & Student Life": [
        "dissertation","plagiarism","scholarship","internship","assessment","curriculum",
        "semester","attendance","fellowship","thesis","examination","placement","faculty",
        "laboratory","assignment","enrollment","competition","elective","graduation","project",
        "research","seminar","workshop","presentation","deadline","revision","mentorship",
        "absenteeism","academic-integrity","accreditation","achievement","activity","admission",
        "advisement","affiliation","alumni","annotation","aptitude","archive","aspiration",
        "assignment","backlogs","campus","career","certificate","chapter","citation","class",
        "classroom","club","coaching","cohort","collaboration","college","comprehension",
        "concentration","conference","convocation","copy","course","credit","debate","degree",
        "demonstration","department","detention","diploma","discipline","discussion","distinction",
        "dormitory","dropout","elective","eligibility","essay","evaluation","examination",
        "experiment","extracurricular","fail","fees","fieldwork","final-exam","foundation",
        "CGPA","grade","group-study","guidance","hackathon","hall-ticket","honor","hostel",
        "hypothesis","index","institution","interview","journal","knowledge","language","lecture",
        "library","literature","marks","memo","model","module","notes","objective","olympiad",
        "orientation","outline","peer","performance","portfolio","practical","professor","quiz",
        "rank","reading","reasoning","record","reference","registration","report","result",
        "review","role","roster","schedule","session","skill","study","subject","submission",
        "syllabus","talent","task","teacher","team","test","textbook","theory","timetable",
        "topic","training","transcript","tutorial","university","viva","vocabulary","writing",
    ],
    "Tone & Context Awareness": [
        "reluctantly","enthusiastically","cautiously","abruptly","sincerely","meticulously",
        "consistently","unexpectedly","gradually","firmly","politely","passionately",
        "desperately","efficiently","temporarily","remarkably","significantly","precisely",
        "calmly","boldly","deliberately","rapidly","quietly","graciously","diligently",
        "abruptly","accurately","aggressively","ambiguously","anxiously","apologetically",
        "assertively","attentively","awkwardly","briefly","briskly","candidly","carefully",
        "cheerfully","clearly","cleverly","coldly","compassionately","competently",
        "concisely","condescendingly","confusingly","constructively","contentedly","critically",
        "curiously","cynically","decisively","defensively","defiantly","dependably","directly",
        "discreetly","dismissively","dutifully","eagerly","earnestly","elegantly","empathetically",
        "equally","evasively","explicitly","expressively","fairly","faithfully","fearlessly",
        "ferociously","fluently","forcefully","formally","frankly","freely","generously",
        "gently","gratefully","harshly","helpfully","honestly","humbly","impatiently",
        "impeccably","impressively","indifferently","informally","insistently","intently",
        "ironically","justly","keenly","kindly","logically","loyally","meekly","mindfully",
        "modestly","naively","neutrally","obediently","objectively","openly","optimistically",
        "patiently","perceptively","persistently","pessimistically","pointedly","powerfully",
        "proactively","professionally","promptly","proudly","prudently","rationally",
        "reasonably","reassuringly","recklessly","reluctantly","remorsefully","respectfully",
        "responsibly","ruthlessly","sarcastically","sensibly","sharply","skillfully","slowly",
        "smoothly","softly","spontaneously","sternly","straightforwardly","stubbornly",
        "subtly","suddenly","swiftly","tactfully","thoughtfully","timidly","transparently",
        "trustworthily","unapologetically","uncomfortably","urgently","vaguely","vigorously",
        "warmly","wisely","zealously",
    ],
}

READ_TIME   = 30   # seconds to read passage
WRITE_TIME  = 90   # seconds to reconstruct
TIME_LIMIT  = 25   # seconds for sentence fill
MAX_REINFORCE = 2

PASSAGE_CATEGORIES = list(CATEGORY_THEMES.keys())

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
    st.session_state.pr_phase = "read"          # "read" | "write" | "scored"
    st.session_state.pr_passage = None
    st.session_state.pr_topic = None
    st.session_state.pr_start_time = None
    st.session_state.pr_live_text = ""
    st.session_state.pr_submitted_text = ""
    st.session_state.pr_score_data = None
    st.session_state.pr_history = []
    st.session_state.pr_count = 0

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
    "mode": "vocab",   # "vocab" | "recall"
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
Focus on the concept / topic: "{seed_word}"  ← MUST incorporate this into the sentence context
Difficulty: EASY TO MEDIUM — use common, everyday words a college student would know.
            The answer should be a common verb, adjective, or noun (1–2 words).

Strict rules:
1. ONE sentence with exactly ONE blank written as ________
2. Sentence MUST relate to "{seed_word}" in some meaningful way
3. Clear grammatical context so the correct answer is obvious
4. 10–20 words ideally; never more than 25 words
5. The blank answer MUST NOT be "{seed_word}" itself — use it as context, not the answer
6. Do NOT copy, paraphrase, or closely resemble ANY sentence below:
{avoid}

Return ONLY valid JSON (no markdown, no explanation):
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
    """Generate a 80-120 word factual paragraph for passage recall."""
    cat_theme = CATEGORY_THEMES.get(category, "general knowledge")
    try:
        resp = client.chat.completions.create(
            messages=[
                {"role":"system","content":"You write clear, factual English paragraphs for reading comprehension tests. Return valid JSON only. No markdown."},
                {"role":"user","content":f"""Write ONE factual paragraph (80–120 words) on a topic from: {cat_theme}.
Rules:
- Self-contained: all key facts inside the paragraph itself
- No bullet points, no headings — flowing prose only
- Mix of simple and moderately complex sentences
- Suitable for a college student
Return ONLY JSON: {{"topic":"short topic title","passage":"full paragraph text"}}"""}
            ],
            model="llama-3.3-70b-versatile", temperature=0.8, max_tokens=350
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
        data = json.loads(raw)
        assert "passage" in data and len(data["passage"].split()) >= 60
        return data
    except Exception:
        return {
            "topic": "Remote Work Trends",
            "passage": (
                "Remote work has transformed the modern workplace significantly. "
                "Since 2020, millions of employees worldwide shifted to working from home, "
                "driven largely by the global pandemic. Companies quickly adopted video "
                "conferencing tools, cloud platforms, and project management software to "
                "maintain productivity. Studies show that remote workers often report higher "
                "job satisfaction due to flexible schedules and reduced commuting time. "
                "However, challenges such as isolation, blurred work-life boundaries, and "
                "communication gaps remain concerns. Many organisations now follow a hybrid "
                "model, blending office and remote work to balance collaboration with flexibility."
            )
        }

def score_recall(client, original_passage, user_response):
    """Score the user's recall response on content accuracy (not verbatim match)."""
    if not user_response.strip():
        return {
            "score": 0, "max_score": 10,
            "content_accuracy": "No response submitted.",
            "key_points_covered": [],
            "key_points_missed": ["All key points were missed — no response provided."],
            "feedback": "You did not write anything. Try to recall at least the main idea next time.",
            "grade": "F"
        }
    prompt = f"""You are evaluating a student's passage recall for a verbal ability exam.

ORIGINAL PASSAGE:
\"\"\"{original_passage}\"\"\"

STUDENT'S RECONSTRUCTION:
\"\"\"{user_response}\"\"\"

Scoring criteria (total = 10 points):
- Content accuracy: did they capture the main idea? (0–4 pts)
- Key facts/details recalled: how many supporting facts are present? (0–3 pts)
- Clarity and coherence: is the reconstruction readable and logical? (0–2 pts)
- Completeness: did they cover the full scope of the passage? (0–1 pt)

Return ONLY valid JSON:
{{
  "score": 7,
  "max_score": 10,
  "content_accuracy": "One sentence summary of how accurate the content was",
  "key_points_covered": ["point 1", "point 2"],
  "key_points_missed": ["missed point 1"],
  "feedback": "2-3 sentence constructive feedback for the student",
  "grade": "B"
}}
Grade scale: 9-10=A, 7-8=B, 5-6=C, 3-4=D, 0-2=F"""

    try:
        return _call(client, [
            {"role":"system","content":"You are a strict but fair verbal ability examiner. Return valid JSON only."},
            {"role":"user","content":prompt}
        ], max_tokens=500, temp=0.3)
    except Exception:
        words_written = len(user_response.strip().split())
        rough_score = min(10, max(0, words_written // 8))
        return {
            "score": rough_score, "max_score": 10,
            "content_accuracy": "Could not evaluate automatically.",
            "key_points_covered": [],
            "key_points_missed": [],
            "feedback": f"You wrote {words_written} words. Manual review recommended.",
            "grade": "—"
        }

# ═══════════════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="big-title">⚡ TCS NQT Verbal Prep</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Sentence Fill · Passage Recall · AI-powered feedback</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  SETUP PAGE
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.page == "setup":
    with st.form("setup_form"):
        api_key  = st.text_input("Groq API Key", type="password", help="Free at console.groq.com")
        mode     = st.radio("Select Mode", ["⚡ Sentence Fill (Vocab Sprint)", "📖 Passage Recall"], horizontal=True)
        cat_choice = st.selectbox("Category", list(CATEGORY_FILTER.keys()))
        submitted = st.form_submit_button("🚀 Start")

    if submitted:
        if not api_key.strip():
            st.error("Please enter your Groq API key.")
        else:
            is_recall = "Passage" in mode
            reset_vocab_state()
            reset_recall_state()
            st.session_state.api_key        = api_key
            st.session_state.category_filter = CATEGORY_FILTER[cat_choice]
            st.session_state.mode           = "recall" if is_recall else "vocab"
            st.session_state.page           = "recall" if is_recall else "quiz"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
#  VOCAB SPRINT PAGE
# ═══════════════════════════════════════════════════════════════════════════

elif st.session_state.page == "quiz":
    client       = get_client(st.session_state.api_key)
    missed_count = len(st.session_state.missed_bank)
    total_gen    = len(st.session_state.asked_hashes)

    st.markdown(
        f'<div class="score-pill">✅ {st.session_state.score}/{st.session_state.total} &nbsp;|&nbsp; '
        f'Q{st.session_state.total+1} &nbsp;|&nbsp; {total_gen} generated &nbsp;|&nbsp; 🔁 {missed_count} pending</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    c_end, c_switch = st.columns(2)
    with c_end:
        if st.button("🛑 End Quiz"):
            st.session_state.page = "summary"
            st.rerun()
    with c_switch:
        if st.button("📖 Switch to Passage Recall"):
            reset_recall_state()
            st.session_state.page = "recall"
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
        # Auto-submit on timeout
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
            q_label = f'Question {st.session_state.total + 1}'
            st.markdown(
                f'<div class="question-card">{tags}'
                f'<div class="q-num">{q_label}</div>'
                f'<div class="q-text">{q["sentence"]}</div></div>',
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
            "Fill in the blank:",
            placeholder="Type your answer…",
            key="_answer_input",
            on_change=_save_live,
            value=st.session_state.live_answer,
        )
        if st.button("✅ Submit"):
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
            timeout_note   = '<br><span style="font-size:0.8rem;color:#FF6B35;">⏰ Time ran out — auto-submitted.</span>' if st.session_state.user_answer == "(timed out)" else ""
            reinforce_note = "" if is_reinforce else '<br><span style="font-size:0.8rem;color:#FF9966;">🔁 Will come back for reinforcement.</span>'
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

    # Top bar
    pr_count = st.session_state.pr_count
    if st.session_state.pr_history:
        avg_score = sum(h["score"] for h in st.session_state.pr_history) / len(st.session_state.pr_history)
        score_txt = f"Avg {avg_score:.1f}/10"
    else:
        score_txt = "No passages yet"

    st.markdown(
        f'<div class="score-pill">📖 Passage {pr_count+1} &nbsp;|&nbsp; {score_txt} &nbsp;|&nbsp; {len(st.session_state.pr_history)} completed</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⚡ Switch to Sentence Fill"):
            st.session_state.page = "quiz"
            st.rerun()
    with c2:
        if st.button("📊 View Recall History") and st.session_state.pr_history:
            st.session_state.page = "recall_summary"
            st.rerun()
    st.write("")

    phase = st.session_state.pr_phase

    # ── Generate passage if not yet loaded ──────────────────────────────
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

    # ════════════════════════════════════════════════
    #  PHASE 1 — READ  (30 seconds)
    # ════════════════════════════════════════════════
    if phase == "read":
        elapsed   = time.time() - st.session_state.pr_start_time
        remaining = max(0.0, READ_TIME - elapsed)

        if remaining <= 0:
            st.session_state.pr_phase      = "write"
            st.session_state.pr_start_time = time.time()
            st.rerun()

        # Instructions banner
        st.markdown(
            '<div class="info-bar">📋 <b>Instructions:</b> Read the passage carefully. '
            'You have <b>30 seconds</b>. After the timer ends, the passage will disappear '
            'and you will have <b>90 seconds</b> to reconstruct it in your own words.</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([5, 1])
        with col1:
            warn_cls = "timer-warn" if remaining <= 8 else "timer-read"
            st.markdown(f'<span class="phase-badge phase-read">📖 READ PHASE</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="passage-card"><b style="color:#B8A6FF;font-size:0.85rem;">TOPIC: {topic.upper()}</b><br><br>{passage}</div>', unsafe_allow_html=True)
        with col2:
            warn_cls = "timer-warn" if remaining <= 8 else "timer-read"
            st.markdown(f'<div class="timer-box {warn_cls}">{int(remaining)}</div>', unsafe_allow_html=True)
            st.markdown('<p style="text-align:center;color:#8A8FA3;font-size:0.72rem;">sec left</p>', unsafe_allow_html=True)

        time.sleep(1)
        st.rerun()

    # ════════════════════════════════════════════════
    #  PHASE 2 — WRITE  (90 seconds)
    # ════════════════════════════════════════════════
    elif phase == "write":
        elapsed   = time.time() - st.session_state.pr_start_time
        remaining = max(0.0, WRITE_TIME - elapsed)

        # Auto-save & score on timeout
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

        # Instructions banner
        st.markdown(
            '<div class="info-bar">✍️ <b>Reconstruct the passage in your own words.</b> '
            'The passage is now hidden. Write as much as you remember — focus on the <b>main ideas and key facts</b>, '
            'not word-for-word memorisation. Your work saves automatically when time ends.</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f'<span class="phase-badge phase-write">✍️ WRITE PHASE — Topic: {topic}</span>', unsafe_allow_html=True)
            st.markdown('<div class="recall-card">', unsafe_allow_html=True)

            def _save_recall():
                st.session_state.pr_live_text = st.session_state._recall_input

            st.text_area(
                "Rewrite the passage in your own words:",
                placeholder="Start typing here… recall the main idea, key facts, and details you remember.",
                key="_recall_input",
                on_change=_save_recall,
                value=st.session_state.pr_live_text,
                height=200,
            )
            words_typed = len(st.session_state.pr_live_text.strip().split()) if st.session_state.pr_live_text.strip() else 0
            st.markdown(f'<p style="color:#8A8FA3;font-size:0.78rem;">Words typed: {words_typed}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            warn_cls = "timer-warn" if remaining <= 15 else "timer-write"
            st.markdown(f'<div class="timer-box {warn_cls}">{int(remaining)}</div>', unsafe_allow_html=True)
            st.markdown('<p style="text-align:center;color:#8A8FA3;font-size:0.72rem;">sec left</p>', unsafe_allow_html=True)

        st.write("")
        if st.button("💾 Submit Early"):
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

        time.sleep(1)
        st.rerun()

    # ════════════════════════════════════════════════
    #  PHASE 3 — SCORED  (show results)
    # ════════════════════════════════════════════════
    elif phase == "scored":
        sd = st.session_state.pr_score_data or {}
        score     = sd.get("score", 0)
        max_score = sd.get("max_score", 10)
        grade     = sd.get("grade", "—")
        pct       = round(100 * score / max_score) if max_score else 0

        grade_color = {"A":"#00E0B8","B":"#7C5CFF","C":"#FFD700","D":"#FF9966","F":"#FF6B35"}.get(grade, "#8A8FA3")

        st.markdown(f'<span class="phase-badge phase-done">✅ SCORED — Passage {st.session_state.pr_count}</span>', unsafe_allow_html=True)

        # Score card
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

        # Points covered / missed
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

        # Feedback
        if sd.get("feedback"):
            st.markdown(f"""
            <div class="levelup-box" style="margin-top:12px;">
                <b style="color:#00E0B8;">💡 Feedback</b><br>{sd['feedback']}
            </div>""", unsafe_allow_html=True)

        # Reveal original passage
        with st.expander("📄 View Original Passage"):
            st.markdown(f'<div class="passage-card">{passage}</div>', unsafe_allow_html=True)

        # User's reconstruction
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
#  RECALL HISTORY / SUMMARY PAGE
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
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔁 Continue Quiz"):
            st.session_state.page = "quiz"
            st.session_state.current_q = None
            st.rerun()
    with c2:
        if st.button("📖 Try Passage Recall"):
            reset_recall_state()
            st.session_state.page = "recall"
            st.rerun()
    with c3:
        if st.button("⚙️ New Setup"):
            st.session_state.page = "setup"
            st.rerun()
