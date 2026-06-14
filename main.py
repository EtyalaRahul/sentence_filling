import streamlit as st
from groq import Groq
import time
import json
import re
import random
import hashlib

st.set_page_config(page_title="TCS NQT Sprint", page_icon="⚡", layout="centered")

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
.section-card {
    background: #1c1f2e; border: 1px solid #2e324a;
    border-radius: 16px; padding: 28px; margin-bottom: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.question-card {
    background: #1c1f2e; border: 1px solid #2e324a;
    border-radius: 16px; padding: 28px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
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
.q-num { font-size: 0.75rem; color: #8A8FA3; margin-bottom: 10px; }
.timer-box {
    text-align: center; font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem; font-weight: 700; color: #00E0B8;
    border: 2px solid #00E0B8; border-radius: 50%;
    width: 65px; height: 65px; display: flex; align-items: center; justify-content: center; margin: 0 auto;
}
.timer-warn { color: #FF6B35 !important; border-color: #FF6B35 !important; }
.correct-box { background: #0d2b1f; border: 1px solid #1f9d6b; border-radius: 12px; padding: 18px; color: #6EE7B7; }
.wrong-box { background: #2b0d12; border: 1px solid #c5455a; border-radius: 12px; padding: 18px; color: #FCA5A5; }
.info-box { background: #0d1f2b; border: 1px solid #1f6b9d; border-radius: 12px; padding: 18px; color: #7EC8F7; }
.lesson-box { background: #1a1f2e; border-left: 4px solid #7C5CFF; border-radius: 8px; padding: 18px 22px; margin-top: 14px; color: #E4E4F0; }
.levelup-box { background: #1a2e1f; border-left: 4px solid #00E0B8; border-radius: 8px; padding: 18px 22px; margin-top: 14px; color: #E4E4F0; }
.passage-box {
    background: #12151f; border: 2px solid #7C5CFF55;
    border-radius: 14px; padding: 28px;
    font-family: 'Space Grotesk', sans-serif; font-size: 1.15rem;
    color: #F3F3F7; line-height: 1.8;
    box-shadow: 0 0 24px #7C5CFF22;
}
.hidden-box {
    background: #12151f; border: 2px dashed #2e324a;
    border-radius: 14px; padding: 28px; text-align: center;
    color: #8A8FA3; font-size: 0.95rem;
}
.score-pill { background: #1c1f2e; border-radius: 999px; padding: 8px 20px; display: inline-block; font-size: 0.85rem; color: #00E0B8; border: 1px solid #2e324a; }
.missed-chip { display: inline-block; background: #2b0d12; color: #FCA5A5; border: 1px solid #c5455a55; border-radius: 8px; padding: 4px 12px; margin: 4px; font-size: 0.8rem; }
.section-btn {
    background: #1c1f2e; border: 1px solid #2e324a; border-radius: 12px;
    padding: 20px; text-align: center; color: #E4E4F0; cursor: pointer;
    transition: border-color 0.2s;
}
.stButton > button { background: linear-gradient(90deg, #7C5CFF, #00E0B8); color: #0f1117; font-weight: 700; border: none; border-radius: 10px; padding: 0.6rem 1.4rem; transition: transform 0.15s ease; }
.stButton > button:hover { transform: scale(1.03); }
.stTextArea > div > textarea { background: #12151f !important; color: #F3F3F7 !important; border: 1px solid #2e324a !important; border-radius: 10px !important; font-family: 'IBM Plex Mono', monospace !important; }
.eval-point-good { color: #6EE7B7; margin: 4px 0; }
.eval-point-miss { color: #FCA5A5; margin: 4px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — VOCAB SPRINT CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

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

SEED_WORDS = {
    "Workplace & Professional": [
        "deadline","appraisal","promotion","resignation","delegation","collaboration","efficiency",
        "presentation","invoice","feedback","onboarding","negotiation","compliance","recruitment",
        "strategy","budget","milestone","stakeholder","performance","productivity","initiative",
        "leadership","mentorship","workflow","approval","supervision","restructuring","incentive",
    ],
    "Technology & Science": [
        "algorithm","bandwidth","debugging","encryption","firmware","deployment","prototype",
        "simulation","hypothesis","calibration","automation","integration","optimization",
        "cybersecurity","satellite","genome","telescope","semiconductor","neural","database",
        "latency","virtualization","repository","compiler","authentication","quantum","sensor",
    ],
    "Social & Current Affairs": [
        "legislation","advocacy","referendum","humanitarian","infrastructure","sanitation",
        "deforestation","migration","pandemic","unemployment","subsidy","transparency","reform",
        "inequality","censorship","vaccination","welfare","climate","diplomacy","sovereignty",
        "nutrition","corruption","education","poverty","governance","regulation","protest",
    ],
    "Academic & Student Life": [
        "dissertation","plagiarism","scholarship","internship","assessment","curriculum",
        "semester","attendance","fellowship","thesis","examination","placement","faculty",
        "laboratory","assignment","enrollment","competition","elective","graduation","project",
        "research","seminar","workshop","presentation","deadline","revision","mentorship",
    ],
    "Tone & Context Awareness": [
        "reluctantly","enthusiastically","cautiously","abruptly","sincerely","meticulously",
        "consistently","unexpectedly","gradually","firmly","politely","passionately",
        "desperately","efficiently","temporarily","remarkably","significantly","precisely",
        "calmly","boldly","deliberately","rapidly","quietly","graciously","diligently",
    ],
}

VOCAB_TIME_LIMIT = 25
MAX_REINFORCE    = 2

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — PASSAGE RECALL CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

PASSAGE_READ_TIME   = 30   # seconds to read the passage
PASSAGE_WRITE_TIME  = 90   # seconds to rewrite from memory

PASSAGES = [
    "Artificial intelligence is transforming industries by automating repetitive tasks and enabling faster decision-making. Companies are investing heavily in AI tools to improve productivity and reduce operational costs across all sectors.",
    "Climate change poses a significant threat to global ecosystems. Rising temperatures are causing glaciers to melt, sea levels to rise, and extreme weather events to become more frequent, affecting millions of people worldwide.",
    "Remote work has reshaped the modern workplace by giving employees greater flexibility and reducing commute times. However, it also presents challenges such as maintaining team cohesion, communication gaps, and work-life balance.",
    "India's startup ecosystem has grown rapidly over the past decade, producing numerous unicorns in sectors like fintech, edtech, and healthtech. Government initiatives and venture capital funding have played a crucial role in this growth.",
    "Effective communication is the cornerstone of professional success. Being able to express ideas clearly, listen actively, and adapt your tone to different audiences can significantly enhance your career prospects and workplace relationships.",
    "The human brain is remarkably adaptable, a quality known as neuroplasticity. Regular learning, physical exercise, and quality sleep are proven strategies to strengthen neural connections and maintain cognitive sharpness over time.",
    "Renewable energy sources such as solar and wind power are becoming increasingly cost-competitive with fossil fuels. This transition is critical for reducing carbon emissions and achieving global sustainability targets by 2050.",
    "Cybersecurity threats are growing in sophistication, targeting individuals, corporations, and governments alike. Implementing strong passwords, multi-factor authentication, and regular software updates are essential defences in today's digital landscape.",
    "The gig economy has created new opportunities for freelancers and independent contractors, offering flexibility and diverse income streams. However, it also raises concerns about job security, benefits, and worker protections.",
    "Space exploration has entered a new era with private companies competing alongside national agencies. Innovations like reusable rockets have dramatically reduced launch costs, opening possibilities for satellite deployment, tourism, and eventual Mars missions.",
]

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — EMAIL WRITING CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

EMAIL_TIME_LIMIT = 9 * 60  # 9 minutes in seconds

EMAIL_PROMPTS = [
    {
        "title": "Project Delay Notification",
        "scenario": "You are a software developer at TechCorp. The project deadline is tomorrow but your team needs 3 more days due to an unexpected bug in the payment module. Write a professional email to your manager, Mr. Ramesh Kumar, explaining the delay, the reason, the revised timeline, and your mitigation plan.",
        "key_points": ["Greet manager professionally", "Explain the specific reason for delay (payment module bug)", "Mention revised timeline (3 more days)", "Provide a mitigation/action plan", "Apologise for inconvenience", "Professional closing"],
    },
    {
        "title": "Leave Application",
        "scenario": "You need to apply for 3 days of casual leave (15th–17th of this month) to attend your cousin's wedding in another city. Write a formal leave application email to your HR manager, Ms. Priya Singh, ensuring your responsibilities are covered during your absence.",
        "key_points": ["State the leave dates clearly (15th–17th)", "Mention the reason (cousin's wedding)", "Explain how work will be covered during absence", "Request approval", "Professional tone and closing"],
    },
    {
        "title": "Client Complaint Response",
        "scenario": "A client, Mr. Arjun Mehta, emailed a complaint that the software product delivered last week has a login issue affecting all users. You are the project lead. Write a professional response acknowledging the issue, apologising, providing an immediate workaround, and committing to a permanent fix within 48 hours.",
        "key_points": ["Acknowledge the client's complaint", "Apologise sincerely", "Provide an immediate workaround", "Commit to permanent fix within 48 hours", "Thank the client for reporting", "Professional and reassuring tone"],
    },
    {
        "title": "Meeting Request Email",
        "scenario": "You want to schedule a project kickoff meeting with your cross-functional team (development, design, QA) for next Monday at 10 AM. Write a professional email to all team leads — Arun (Dev), Sneha (Design), and Kiran (QA) — sharing the agenda and requesting confirmation.",
        "key_points": ["State meeting purpose (project kickoff)", "Mention date and time (Monday 10 AM)", "List agenda points", "Address all three team leads", "Request RSVP/confirmation", "Attach or mention agenda document"],
    },
    {
        "title": "Internship Thank-You Email",
        "scenario": "You have just completed a 2-month internship at DataSoft Solutions. Write a thank-you email to your internship supervisor, Dr. Kavya Reddy, expressing gratitude for the learning experience, mentioning two specific skills you gained, and expressing interest in future opportunities.",
        "key_points": ["Thank the supervisor genuinely", "Mention two specific skills gained", "Reference a memorable project or experience", "Express interest in future opportunities", "Professional and warm tone", "Proper email closing"],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# DEDUP HELPERS (Vocab Sprint)
# ─────────────────────────────────────────────────────────────────────────────

def _normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def _sentence_hash(sentence):
    return hashlib.md5(_normalize(sentence).encode()).hexdigest()

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────

def _def(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

# Global
_def("page", "home")
_def("api_key", "")

# Vocab Sprint
_def("vs_score", 0)
_def("vs_total", 0)
_def("vs_current_q", None)
_def("vs_start_time", None)
_def("vs_answered", False)
_def("vs_user_answer", "")
_def("vs_feedback", None)
_def("vs_lesson", None)
_def("vs_suggestion", None)
_def("vs_history", [])
_def("vs_missed_bank", [])
_def("vs_is_reinforce", False)
_def("vs_asked_hashes", set())
_def("vs_asked_sentences", [])
_def("vs_used_seeds", {cat: [] for cat in CATEGORY_THEMES})
_def("vs_cat_rotation_idx", 0)
_def("vs_category_filter", None)

# Passage Recall
_def("pr_phase", "idle")        # idle | reading | writing | result
_def("pr_passage", "")
_def("pr_timer_start", None)
_def("pr_user_text", "")
_def("pr_feedback", None)
_def("pr_score", 0)
_def("pr_total", 0)

# Email Writing
_def("em_phase", "idle")        # idle | writing | result
_def("em_prompt", None)
_def("em_timer_start", None)
_def("em_user_email", "")
_def("em_feedback", None)
_def("em_score", 0)
_def("em_total", 0)

# ─────────────────────────────────────────────────────────────────────────────
# GROQ HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_client():
    return Groq(api_key=st.session_state.api_key)

def _call(client, messages, max_tokens=600, temp=0.7):
    resp = client.chat.completions.create(
        messages=messages, model="llama-3.3-70b-versatile",
        temperature=temp, max_tokens=max_tokens,
    )
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)

# ─────────────────────────────────────────────────────────────────────────────
# VOCAB SPRINT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def vs_reset():
    st.session_state.vs_score = 0
    st.session_state.vs_total = 0
    st.session_state.vs_current_q = None
    st.session_state.vs_start_time = None
    st.session_state.vs_answered = False
    st.session_state.vs_user_answer = ""
    st.session_state.vs_feedback = None
    st.session_state.vs_lesson = None
    st.session_state.vs_suggestion = None
    st.session_state.vs_history = []
    st.session_state.vs_missed_bank = []
    st.session_state.vs_is_reinforce = False
    st.session_state.vs_asked_hashes = set()
    st.session_state.vs_asked_sentences = []
    st.session_state.vs_used_seeds = {cat: [] for cat in CATEGORY_THEMES}
    st.session_state.vs_cat_rotation_idx = 0

def vs_check_answer(client, sentence, accepted_answers, user_answer):
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
                {"role": "user", "content": f'Sentence: "{sentence}"\nAccepted: {accepted_answers}\nStudent: "{user_answer}"\nIs it correct? YES or NO.'}
            ],
            model="llama-3.3-70b-versatile", temperature=0.1, max_tokens=5,
        )
        return "YES" in resp.choices[0].message.content.upper()
    except Exception:
        return False

def vs_generate_lesson(client, word, sentence):
    try:
        return _call(client, [
            {"role": "system", "content": "English teacher. Return valid JSON only."},
            {"role": "user", "content": f'Word missed: "{word}" in: "{sentence}"\nReturn JSON: {{"meaning":"1-line def","synonyms":["s1","s2","s3"],"examples":["ex1","ex2"],"memory_tip":"tip","related_words":[{{"word":"w","meaning":"m","example":"e"}}]}}'},
        ], max_tokens=600)
    except Exception:
        return {"meaning": f"{word}: key vocabulary word.", "synonyms": [], "examples": [], "memory_tip": "Review this word.", "related_words": []}

def vs_generate_suggestion(client, word, sentence):
    try:
        return _call(client, [
            {"role": "system", "content": "English tutor. Return valid JSON only."},
            {"role": "user", "content": f'Student got "{word}" correct in: "{sentence}"\nReturn JSON: {{"tip":"1-2 sentence tip","advanced_word":"word","advanced_meaning":"meaning"}}'},
        ], max_tokens=200, temp=0.7)
    except Exception:
        return {"tip": f"Great use of '{word}'!", "advanced_word": "", "advanced_meaning": ""}

def _vs_pick_seed(category):
    pool  = SEED_WORDS.get(category, [])
    used  = st.session_state.vs_used_seeds.get(category, [])
    unused = [w for w in pool if w not in used]
    if not unused:
        st.session_state.vs_used_seeds[category] = []
        unused = pool
    seed = random.choice(unused) if unused else random.choice(pool)
    st.session_state.vs_used_seeds.setdefault(category, []).append(seed)
    return seed

def _vs_pick_category():
    configured_cat = st.session_state.vs_category_filter
    if configured_cat:
        return configured_cat
    cats = list(CATEGORY_THEMES.keys())
    idx  = st.session_state.vs_cat_rotation_idx % len(cats)
    st.session_state.vs_cat_rotation_idx += 1
    if idx == 0 and st.session_state.vs_total > 0:
        random.shuffle(cats)
        st.session_state.vs_cat_order = cats
    order = st.session_state.get("vs_cat_order", cats)
    return order[idx % len(order)]

def _vs_generate_llm_question(client, category, asked_sentences, seed_word, attempt_num):
    themes = CATEGORY_THEMES.get(category, "general English vocabulary")
    temp   = min(0.75 + attempt_num * 0.08, 1.0)
    avoid_list = asked_sentences[-40:] if len(asked_sentences) > 40 else asked_sentences
    avoid  = "\n".join(f"- {s}" for s in avoid_list) if avoid_list else "none"

    prompt = f"""Create ONE unique sentence-completion question for TCS NQT Verbal Ability exam.

Category: {category}
Theme: {themes}
Focus on the concept / topic: "{seed_word}"
Difficulty: EASY TO MEDIUM — common words a college student would know.
Answer: a common verb, adjective, or noun (1–2 words).

Rules:
1. ONE sentence with exactly ONE blank written as ________
2. Sentence MUST relate to "{seed_word}" meaningfully
3. Clear grammatical context; correct answer is obvious
4. 10–20 words; never more than 25
5. Blank answer MUST NOT be "{seed_word}" itself
6. Do NOT resemble ANY sentence below:
{avoid}

Return ONLY valid JSON:
{{
  "sentence": "The software engineer ________ the bug before the product launch.",
  "accepted_answers": ["fixed", "resolved", "identified"],
  "category": "{category}"
}}"""

    data = _call(client, [
        {"role": "system", "content": "You write unique English vocab exam questions. Return valid JSON only."},
        {"role": "user", "content": prompt},
    ], max_tokens=300, temp=temp)

    assert "sentence" in data and "accepted_answers" in data
    assert "________" in data["sentence"]
    assert len(data["accepted_answers"]) >= 1
    data["id"] = _sentence_hash(data["sentence"])
    data.setdefault("category", category)
    return data

VS_FALLBACK_POOL = [
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

def vs_get_next_question(client):
    asked_hashes    = st.session_state.vs_asked_hashes
    asked_sentences = st.session_state.vs_asked_sentences
    chosen_cat      = _vs_pick_category()
    seed            = _vs_pick_seed(chosen_cat)

    for attempt in range(8):
        try:
            q = _vs_generate_llm_question(client, chosen_cat, asked_sentences, seed, attempt)
            if q["id"] not in asked_hashes:
                return q
            seed = _vs_pick_seed(chosen_cat)
        except Exception:
            time.sleep(0.3)

    configured_cat = st.session_state.vs_category_filter
    unused = [f for f in VS_FALLBACK_POOL
              if _sentence_hash(f["sentence"]) not in asked_hashes
              and (not configured_cat or f["category"] == configured_cat)]
    if unused:
        q = dict(random.choice(unused))
        q["id"] = _sentence_hash(q["sentence"])
        return q

    q = dict(random.choice(VS_FALLBACK_POOL))
    q["id"] = _sentence_hash(q["sentence"] + str(random.random()))
    return q

# ─────────────────────────────────────────────────────────────────────────────
# PASSAGE RECALL HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def pr_evaluate(client, original, user_text):
    """Use LLM to evaluate how many key points from the passage the user captured."""
    try:
        return _call(client, [
            {"role": "system", "content": "You are an English evaluator. Return valid JSON only."},
            {"role": "user", "content": f"""Original passage:
\"{original}\"

Student's rewrite:
\"{user_text}\"

Evaluate how well the student captured the key ideas. Identify 4-6 key points from the original.
For each point mark whether the student covered it (fully / partially / missed).

Return JSON:
{{
  "score": <integer 0-10>,
  "summary": "2-sentence overall feedback",
  "key_points": [
    {{"point": "Key idea text", "status": "covered" | "partial" | "missed"}}
  ],
  "grammar_note": "1 sentence about grammar/language quality"
}}"""},
        ], max_tokens=600, temp=0.2)
    except Exception:
        return {
            "score": 0,
            "summary": "Could not evaluate. Please try again.",
            "key_points": [],
            "grammar_note": "",
        }

def pr_pick_passage():
    return random.choice(PASSAGES)

# ─────────────────────────────────────────────────────────────────────────────
# EMAIL WRITING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def em_evaluate(client, prompt_data, user_email):
    """Evaluate the user's email against the key points."""
    key_points_str = "\n".join(f"- {kp}" for kp in prompt_data["key_points"])
    try:
        return _call(client, [
            {"role": "system", "content": "You are a professional English writing evaluator. Return valid JSON only."},
            {"role": "user", "content": f"""Email scenario: {prompt_data['scenario']}

Expected key points to cover:
{key_points_str}

Student's email:
\"{user_email}\"

Evaluate the email strictly for a TCS NQT exam context.

Return JSON:
{{
  "score": <integer 0-10>,
  "summary": "2-3 sentence overall feedback",
  "key_points": [
    {{"point": "Key point text", "status": "covered" | "partial" | "missed", "note": "brief comment"}}
  ],
  "language_quality": "1-2 sentences on grammar, tone, and professionalism",
  "subject_line": "Was the subject line appropriate? 1 sentence.",
  "improvements": ["improvement 1", "improvement 2", "improvement 3"]
}}"""},
        ], max_tokens=700, temp=0.2)
    except Exception:
        return {
            "score": 0,
            "summary": "Could not evaluate. Please try again.",
            "key_points": [],
            "language_quality": "",
            "subject_line": "",
            "improvements": [],
        }

def em_pick_prompt():
    return random.choice(EMAIL_PROMPTS)

# ─────────────────────────────────────────────────────────────────────────────
# SHARED HEADER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="big-title">⚡ TCS NQT Sprint</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Vocab Fill-in · Passage Recall · Email Writing — all in one place</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HOME / SETUP PAGE
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.page == "home":
    with st.form("setup_form"):
        api_key = st.text_input("Groq API Key", type="password", help="Free at console.groq.com")
        submitted = st.form_submit_button("🚀 Enter")
    if submitted:
        if not api_key.strip():
            st.error("Please enter your Groq API key.")
        else:
            st.session_state.api_key = api_key
            st.session_state.page = "section_select"
            st.rerun()

elif st.session_state.page == "section_select":
    st.markdown("### Choose a Section")
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="section-card"><b style="color:#B8A6FF;">📝 Section 1</b><br><b>Vocab Sprint</b><br><span style="font-size:0.8rem;color:#8A8FA3;">Fill-in-the-blank · 25s/q · AI-generated · Reinforcement</span></div>', unsafe_allow_html=True)
        if st.button("Start Vocab Sprint", key="btn_vs"):
            st.session_state.page = "vs_setup"
            st.rerun()
    with c2:
        st.markdown('<div class="section-card"><b style="color:#00E0B8;">👁️ Section 2</b><br><b>Passage Recall</b><br><span style="font-size:0.8rem;color:#8A8FA3;">Read 30s · Write from memory 90s · AI-evaluated</span></div>', unsafe_allow_html=True)
        if st.button("Start Passage Recall", key="btn_pr"):
            st.session_state.page = "pr_main"
            st.session_state.pr_phase = "idle"
            st.rerun()
    with c3:
        st.markdown('<div class="section-card"><b style="color:#FF9966;">✉️ Section 3</b><br><b>Email Writing</b><br><span style="font-size:0.8rem;color:#8A8FA3;">Scenario · 9 min timer · AI-scored</span></div>', unsafe_allow_html=True)
        if st.button("Start Email Writing", key="btn_em"):
            st.session_state.page = "em_main"
            st.session_state.em_phase = "idle"
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — VOCAB SPRINT
# ─────────────────────────────────────────────────────────────────────────────

elif st.session_state.page == "vs_setup":
    st.markdown("### ⚡ Vocab Sprint — Setup")
    with st.form("vs_setup_form"):
        cat_choice = st.selectbox("Category", list(CATEGORY_FILTER.keys()))
        submitted  = st.form_submit_button("🚀 Start")
    if submitted:
        vs_reset()
        st.session_state.vs_category_filter = CATEGORY_FILTER[cat_choice]
        st.session_state.page = "vs_quiz"
        st.rerun()
    st.write("")
    if st.button("← Back to Sections"):
        st.session_state.page = "section_select"
        st.rerun()

elif st.session_state.page == "vs_quiz":
    client = get_client()
    missed_count    = len(st.session_state.vs_missed_bank)
    total_generated = len(st.session_state.vs_asked_hashes)

    st.markdown(
        f'<div class="score-pill">✅ {st.session_state.vs_score}/{st.session_state.vs_total} &nbsp;|&nbsp; '
        f'Q{st.session_state.vs_total+1} &nbsp;|&nbsp; {total_generated} generated &nbsp;|&nbsp; 🔁 {missed_count} pending</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    col_end, col_back = st.columns([1, 1])
    with col_end:
        if st.button("🛑 End Quiz"):
            st.session_state.page = "vs_summary"
            st.rerun()
    with col_back:
        if st.button("← Sections"):
            st.session_state.page = "section_select"
            st.rerun()
    st.write("")

    # Pick question
    if st.session_state.vs_current_q is None:
        pull_reinforce = (
            st.session_state.vs_missed_bank and
            st.session_state.vs_total > 0 and
            st.session_state.vs_total % 4 == 0
        )
        if pull_reinforce:
            entry = st.session_state.vs_missed_bank[0]
            q = {"id": entry["id"], "sentence": entry["sentence"],
                 "accepted_answers": entry["accepted_answers"], "category": entry["category"]}
            st.session_state.vs_is_reinforce = True
        else:
            with st.spinner("✨ Generating question…"):
                q = vs_get_next_question(client)
            st.session_state.vs_is_reinforce = False

        st.session_state.vs_asked_hashes.add(q["id"])
        st.session_state.vs_asked_sentences.append(q["sentence"])
        st.session_state.vs_current_q   = q
        st.session_state.vs_start_time  = time.time()
        st.session_state.vs_answered    = False
        st.session_state.vs_feedback    = None
        st.session_state.vs_lesson      = None
        st.session_state.vs_suggestion  = None
        st.rerun()

    q          = st.session_state.vs_current_q
    elapsed    = time.time() - st.session_state.vs_start_time
    remaining  = max(0, VOCAB_TIME_LIMIT - elapsed)
    is_reinforce = st.session_state.vs_is_reinforce

    if not st.session_state.vs_answered:
        col1, col2 = st.columns([4, 1])
        with col1:
            tags = f'<span class="q-tag">{q["category"].upper()}</span>'
            tags += '<span class="reinforce-tag">🔁 REINFORCE</span>' if is_reinforce else '<span class="llm-tag">✨ AI</span>'
            st.markdown(
                f'<div class="question-card">{tags}'
                f'<div class="q-num">Question {st.session_state.vs_total + 1}</div>'
                f'<div class="q-text">{q["sentence"]}</div></div>',
                unsafe_allow_html=True,
            )
        with col2:
            warn = "timer-warn" if remaining <= 8 else ""
            st.markdown(f'<div class="timer-box {warn}">{int(remaining)}</div>', unsafe_allow_html=True)
            st.markdown('<p style="text-align:center;color:#8A8FA3;font-size:0.72rem;">sec</p>', unsafe_allow_html=True)

        st.write("")
        with st.form("vs_answer_form", clear_on_submit=False):
            ans        = st.text_input("Fill in the blank:", placeholder="Type your answer…")
            submit_ans = st.form_submit_button("✅ Submit")

        timeout = remaining <= 0
        if submit_ans or timeout:
            with st.spinner("Checking…"):
                is_correct = False if timeout else vs_check_answer(client, q["sentence"], q["accepted_answers"], ans)
            st.session_state.vs_answered     = True
            st.session_state.vs_user_answer  = "(timed out)" if timeout else ans
            st.session_state.vs_feedback     = is_correct
            st.session_state.vs_total       += 1
            primary = q["accepted_answers"][0]

            if is_correct:
                st.session_state.vs_score += 1
                if is_reinforce and st.session_state.vs_missed_bank:
                    if st.session_state.vs_missed_bank[0]["id"] == q["id"]:
                        st.session_state.vs_missed_bank.pop(0)
                with st.spinner("Preparing tip…"):
                    st.session_state.vs_suggestion = vs_generate_suggestion(client, primary, q["sentence"])
            else:
                if is_reinforce and st.session_state.vs_missed_bank:
                    if st.session_state.vs_missed_bank[0]["id"] == q["id"]:
                        st.session_state.vs_missed_bank[0]["retries_left"] -= 1
                        if st.session_state.vs_missed_bank[0]["retries_left"] <= 0:
                            st.session_state.vs_missed_bank.pop(0)
                else:
                    existing_ids = {e["id"] for e in st.session_state.vs_missed_bank}
                    if q["id"] not in existing_ids:
                        st.session_state.vs_missed_bank.append({
                            "id": q["id"], "word": primary,
                            "sentence": q["sentence"],
                            "accepted_answers": q["accepted_answers"],
                            "category": q["category"],
                            "retries_left": MAX_REINFORCE,
                        })
                with st.spinner("Preparing lesson…"):
                    st.session_state.vs_lesson = vs_generate_lesson(client, primary, q["sentence"])

            st.session_state.vs_history.append({
                "word": primary, "correct": is_correct,
                "qid": q["id"], "reinforce": is_reinforce,
            })
            st.rerun()
        else:
            time.sleep(1)
            st.rerun()

    else:
        tags = f'<span class="q-tag">{q["category"].upper()}</span>'
        tags += '<span class="reinforce-tag">🔁 REINFORCE</span>' if is_reinforce else '<span class="llm-tag">✨ AI</span>'
        st.markdown(
            f'<div class="question-card">{tags}'
            f'<div class="q-num">Question {st.session_state.vs_total}</div>'
            f'<div class="q-text">{q["sentence"]}</div></div>',
            unsafe_allow_html=True,
        )
        primary    = q["accepted_answers"][0]
        all_accept = " / ".join(q["accepted_answers"])

        if st.session_state.vs_feedback:
            st.markdown(f'<div class="correct-box">✅ <b>Correct!</b> "<i>{st.session_state.vs_user_answer}</i>" — well done.<br><span style="font-size:0.85rem;">Accepted: <b>{all_accept}</b></span></div>', unsafe_allow_html=True)
            if st.session_state.vs_suggestion:
                sug = st.session_state.vs_suggestion
                adv = f"<br><b>Try next:</b> <i>{sug['advanced_word']}</i> — {sug['advanced_meaning']}" if sug.get("advanced_word") else ""
                st.markdown(f'<div class="levelup-box"><b style="color:#00E0B8;">💡 Tip</b><br>{sug["tip"]}{adv}</div>', unsafe_allow_html=True)
        else:
            reinforce_note = "" if is_reinforce else '<br><span style="font-size:0.8rem;color:#FF9966;">🔁 Will come back for reinforcement.</span>'
            st.markdown(f'<div class="wrong-box">❌ <b>Incorrect.</b> You wrote: "<i>{st.session_state.vs_user_answer}</i>"<br><span style="font-size:0.85rem;">Answer: <b>{all_accept}</b></span>{reinforce_note}</div>', unsafe_allow_html=True)
            if st.session_state.vs_lesson:
                L       = st.session_state.vs_lesson
                ex_html = "".join(f"<li>{e}</li>" for e in L.get("examples", []))
                syn_html = ", ".join(L.get("synonyms", []))
                rel_html = "".join(
                    f"<li><b>{r['word']}</b> — {r['meaning']}<br><i>{r['example']}</i></li>"
                    for r in L.get("related_words", [])
                )
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
            st.session_state.vs_current_q = None
            st.rerun()

elif st.session_state.page == "vs_summary":
    total = st.session_state.vs_total
    score = st.session_state.vs_score
    pct   = round(100 * score / total) if total else 0
    st.balloons()
    grade = "🏆 Excellent!" if pct >= 80 else "👍 Good effort!" if pct >= 50 else "📚 Keep practising!"
    st.markdown(f"""
    <div class="question-card" style="text-align:center;">
        <div class="big-title" style="font-size:2rem;">Vocab Sprint — Summary</div>
        <p style="font-size:1.1rem;color:#E4E4F0;">{grade}<br>
        <b style="color:#00E0B8;">{score}</b> / <b>{total}</b> ({pct}%)</p>
    </div>""", unsafe_allow_html=True)

    missed = [h for h in st.session_state.vs_history if not h["correct"]]
    if missed:
        st.write("")
        chips = "".join(f'<span class="missed-chip">{h["word"]}</span>' for h in missed)
        st.markdown(f'<div class="lesson-box"><b style="color:#B8A6FF;">📚 Revise these:</b><br><br>{chips}</div>', unsafe_allow_html=True)

    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔁 Continue Quiz"):
            st.session_state.page = "vs_quiz"
            st.session_state.vs_current_q = None
            st.rerun()
    with c2:
        if st.button("⚙️ New Setup"):
            st.session_state.page = "vs_setup"
            st.rerun()
    with c3:
        if st.button("← All Sections"):
            st.session_state.page = "section_select"
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — PASSAGE RECALL
# ─────────────────────────────────────────────────────────────────────────────

elif st.session_state.page == "pr_main":
    client = get_client()
    st.markdown("### 👁️ Passage Recall")
    st.markdown(f'<div class="score-pill">Score: {st.session_state.pr_score}/{st.session_state.pr_total}</div>', unsafe_allow_html=True)
    st.write("")

    phase = st.session_state.pr_phase

    # ── IDLE ──────────────────────────────────────────────────────────────
    if phase == "idle":
        st.markdown("""
        <div class="section-card">
            <b style="color:#00E0B8;">How it works:</b><br>
            1️⃣ A short passage appears for <b>30 seconds</b> — read it carefully.<br>
            2️⃣ The passage disappears. You have <b>90 seconds</b> to rewrite it from memory.<br>
            3️⃣ AI evaluates how many key points you captured.<br><br>
            <span style="color:#8A8FA3;font-size:0.85rem;">Focus on main ideas, not word-for-word copying.</span>
        </div>""", unsafe_allow_html=True)
        st.write("")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("▶️ Start Passage"):
                st.session_state.pr_passage     = pr_pick_passage()
                st.session_state.pr_timer_start = time.time()
                st.session_state.pr_phase       = "reading"
                st.session_state.pr_user_text   = ""
                st.session_state.pr_feedback    = None
                st.rerun()
        with col2:
            if st.button("← Back to Sections"):
                st.session_state.page = "section_select"
                st.rerun()

    # ── READING ───────────────────────────────────────────────────────────
    elif phase == "reading":
        elapsed   = time.time() - st.session_state.pr_timer_start
        remaining = max(0, PASSAGE_READ_TIME - elapsed)

        st.markdown(f'<div style="text-align:right;color:#00E0B8;font-size:1.2rem;font-weight:700;">📖 Reading — {int(remaining)}s left</div>', unsafe_allow_html=True)
        st.write("")
        st.markdown(f'<div class="passage-box">{st.session_state.pr_passage}</div>', unsafe_allow_html=True)
        st.write("")
        st.info("Read carefully. The passage will disappear in a few seconds and you will rewrite from memory.")

        if remaining <= 0:
            st.session_state.pr_phase       = "writing"
            st.session_state.pr_timer_start = time.time()
            st.rerun()
        else:
            time.sleep(1)
            st.rerun()

    # ── WRITING ───────────────────────────────────────────────────────────
    elif phase == "writing":
        elapsed   = time.time() - st.session_state.pr_timer_start
        remaining = max(0, PASSAGE_WRITE_TIME - elapsed)

        warn_color = "#FF6B35" if remaining <= 20 else "#00E0B8"
        st.markdown(f'<div style="text-align:right;color:{warn_color};font-size:1.2rem;font-weight:700;">✍️ Rewrite from memory — {int(remaining)}s left</div>', unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="hidden-box">🙈 Passage hidden — write what you remember below.</div>', unsafe_allow_html=True)
        st.write("")

        with st.form("pr_write_form"):
            user_text  = st.text_area(
                "Your rewrite:",
                placeholder="Write the passage as you remember it…",
                height=180,
            )
            submit_btn = st.form_submit_button("✅ Submit Rewrite")

        timeout = remaining <= 0
        if submit_btn or timeout:
            text_to_eval = user_text.strip() if not timeout else st.session_state.get("pr_user_text", "")
            st.session_state.pr_user_text = text_to_eval
            with st.spinner("AI evaluating your rewrite…"):
                fb = pr_evaluate(client, st.session_state.pr_passage, text_to_eval)
            st.session_state.pr_feedback = fb
            st.session_state.pr_total   += 1
            st.session_state.pr_score   += max(0, round(fb.get("score", 0) / 2))  # scale to 5 for display
            st.session_state.pr_phase    = "result"
            st.rerun()
        else:
            if remaining <= 0:
                st.session_state.pr_phase       = "result"
                st.session_state.pr_timer_start = time.time()
                st.rerun()
            time.sleep(1)
            st.rerun()

    # ── RESULT ────────────────────────────────────────────────────────────
    elif phase == "result":
        fb = st.session_state.pr_feedback
        if not fb:
            st.session_state.pr_phase = "idle"
            st.rerun()

        score_val = fb.get("score", 0)
        grade     = "🏆 Excellent!" if score_val >= 8 else "👍 Good!" if score_val >= 5 else "📚 Keep practising!"

        st.markdown(f"""
        <div class="question-card" style="text-align:center;">
            <b style="font-size:1.5rem;color:#00E0B8;">{grade}</b><br>
            <span style="font-size:2rem;font-weight:700;color:#F3F3F7;">{score_val}/10</span>
        </div>""", unsafe_allow_html=True)
        st.write("")

        st.markdown('<div class="lesson-box">', unsafe_allow_html=True)
        st.markdown(f"**Overall feedback:** {fb.get('summary', '')}")
        st.write("")
        st.markdown("**Key Points Coverage:**")
        for kp in fb.get("key_points", []):
            status = kp.get("status", "missed")
            icon   = "✅" if status == "covered" else "🟡" if status == "partial" else "❌"
            st.markdown(f"{icon} {kp['point']}")
        st.write("")
        if fb.get("grammar_note"):
            st.markdown(f"**Language:** {fb['grammar_note']}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("")
        st.markdown("**Original Passage:**")
        st.markdown(f'<div class="passage-box" style="font-size:1rem;">{st.session_state.pr_passage}</div>', unsafe_allow_html=True)

        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("▶️ Next Passage"):
                st.session_state.pr_phase = "idle"
                st.rerun()
        with c2:
            if st.button("← Back to Sections"):
                st.session_state.page = "section_select"
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — EMAIL WRITING
# ─────────────────────────────────────────────────────────────────────────────

elif st.session_state.page == "em_main":
    client = get_client()
    st.markdown("### ✉️ Email Writing")
    st.markdown(f'<div class="score-pill">Score: {st.session_state.em_score}/{st.session_state.em_total * 10 if st.session_state.em_total else "—"}</div>', unsafe_allow_html=True)
    st.write("")

    phase = st.session_state.em_phase

    # ── IDLE ──────────────────────────────────────────────────────────────
    if phase == "idle":
        st.markdown("""
        <div class="section-card">
            <b style="color:#FF9966;">How it works:</b><br>
            1️⃣ A professional email scenario is presented.<br>
            2️⃣ You have <b>9 minutes</b> to write a complete professional email.<br>
            3️⃣ AI scores your email on key points covered, tone, grammar, and structure.<br><br>
            <span style="color:#8A8FA3;font-size:0.85rem;">Include: Subject line · Greeting · Body · Closing · Signature</span>
        </div>""", unsafe_allow_html=True)
        st.write("")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("▶️ Start Email Task"):
                st.session_state.em_prompt      = em_pick_prompt()
                st.session_state.em_timer_start = time.time()
                st.session_state.em_phase       = "writing"
                st.session_state.em_user_email  = ""
                st.session_state.em_feedback    = None
                st.rerun()
        with col2:
            if st.button("← Back to Sections"):
                st.session_state.page = "section_select"
                st.rerun()

    # ── WRITING ───────────────────────────────────────────────────────────
    elif phase == "writing":
        elapsed   = time.time() - st.session_state.em_timer_start
        remaining = max(0, EMAIL_TIME_LIMIT - elapsed)
        mins      = int(remaining) // 60
        secs      = int(remaining) % 60
        warn_color = "#FF6B35" if remaining <= 60 else "#00E0B8"

        prompt_data = st.session_state.em_prompt
        st.markdown(f'<div style="text-align:right;color:{warn_color};font-size:1.2rem;font-weight:700;">⏱️ {mins}:{secs:02d} remaining</div>', unsafe_allow_html=True)
        st.write("")

        st.markdown(f"""
        <div class="question-card">
            <span class="q-tag">EMAIL TASK</span><span class="llm-tag">✉️ {prompt_data['title']}</span>
            <div class="q-num">Scenario</div>
            <div class="q-text" style="font-size:1.05rem;">{prompt_data['scenario']}</div>
        </div>""", unsafe_allow_html=True)
        st.write("")

        st.markdown("**Key points to cover:**")
        for kp in prompt_data["key_points"]:
            st.markdown(f"  • {kp}")
        st.write("")

        with st.form("em_write_form"):
            user_email = st.text_area(
                "Write your email here:",
                placeholder="Subject: ...\n\nDear [Name],\n\n[Your email body]\n\nRegards,\n[Your Name]",
                height=320,
            )
            submit_btn = st.form_submit_button("✅ Submit Email")

        timeout = remaining <= 0
        if submit_btn or timeout:
            email_to_eval = user_email.strip() if user_email.strip() else "(No email written — timed out)"
            st.session_state.em_user_email = email_to_eval
            with st.spinner("AI evaluating your email…"):
                fb = em_evaluate(client, prompt_data, email_to_eval)
            st.session_state.em_feedback = fb
            st.session_state.em_total   += 1
            st.session_state.em_score   += fb.get("score", 0)
            st.session_state.em_phase    = "result"
            st.rerun()
        else:
            if remaining <= 0:
                st.session_state.em_phase = "result"
                st.rerun()
            time.sleep(1)
            st.rerun()

    # ── RESULT ────────────────────────────────────────────────────────────
    elif phase == "result":
        fb = st.session_state.em_feedback
        if not fb:
            st.session_state.em_phase = "idle"
            st.rerun()

        score_val = fb.get("score", 0)
        grade     = "🏆 Excellent!" if score_val >= 8 else "👍 Good effort!" if score_val >= 5 else "📚 Needs improvement."

        st.markdown(f"""
        <div class="question-card" style="text-align:center;">
            <b style="font-size:1.5rem;color:#FF9966;">{grade}</b><br>
            <span style="font-size:2rem;font-weight:700;color:#F3F3F7;">{score_val}/10</span>
        </div>""", unsafe_allow_html=True)
        st.write("")

        st.markdown('<div class="lesson-box">', unsafe_allow_html=True)
        st.markdown(f"**Overall:** {fb.get('summary', '')}")
        st.write("")

        st.markdown("**Key Points Coverage:**")
        for kp in fb.get("key_points", []):
            status = kp.get("status", "missed")
            icon   = "✅" if status == "covered" else "🟡" if status == "partial" else "❌"
            note   = f" — *{kp['note']}*" if kp.get("note") else ""
            st.markdown(f"{icon} {kp['point']}{note}")

        st.write("")
        if fb.get("language_quality"):
            st.markdown(f"**Language & Tone:** {fb['language_quality']}")
        if fb.get("subject_line"):
            st.markdown(f"**Subject Line:** {fb['subject_line']}")

        improvements = fb.get("improvements", [])
        if improvements:
            st.write("")
            st.markdown("**How to improve:**")
            for imp in improvements:
                st.markdown(f"  • {imp}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("")
        st.markdown("**Your submitted email:**")
        st.text_area("", value=st.session_state.em_user_email, height=200, disabled=True)

        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("▶️ Next Email Task"):
                st.session_state.em_phase = "idle"
                st.rerun()
        with c2:
            if st.button("← Back to Sections"):
                st.session_state.page = "section_select"
                st.rerun()
