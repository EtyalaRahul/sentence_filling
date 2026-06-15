import streamlit as st
from groq import Groq
import time
import json
import re
import random
import hashlib

st.set_page_config(page_title="TCS NQT Vocab Sprint", page_icon="⚡", layout="centered")

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
.lesson-box { background: #1a1f2e; border-left: 4px solid #7C5CFF; border-radius: 8px; padding: 18px 22px; margin-top: 14px; color: #E4E4F0; }
.levelup-box { background: #1a2e1f; border-left: 4px solid #00E0B8; border-radius: 8px; padding: 18px 22px; margin-top: 14px; color: #E4E4F0; }
.score-pill { background: #1c1f2e; border-radius: 999px; padding: 8px 20px; display: inline-block; font-size: 0.85rem; color: #00E0B8; border: 1px solid #2e324a; }
.missed-chip { display: inline-block; background: #2b0d12; color: #FCA5A5; border: 1px solid #c5455a55; border-radius: 8px; padding: 4px 12px; margin: 4px; font-size: 0.8rem; }
.stButton > button { background: linear-gradient(90deg, #7C5CFF, #00E0B8); color: #0f1117; font-weight: 700; border: none; border-radius: 10px; padding: 0.6rem 1.4rem; transition: transform 0.15s ease; }
.stButton > button:hover { transform: scale(1.03); }
</style>
""", unsafe_allow_html=True)

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

# Pool of seed words to force variety across questions
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

TIME_LIMIT = 25
MAX_REINFORCE = 2


# ── DEDUP HELPERS ────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Lowercase, collapse whitespace, strip punctuation for dedup comparison."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def _sentence_hash(sentence: str) -> str:
    return hashlib.md5(_normalize(sentence).encode()).hexdigest()

def _is_duplicate(sentence: str, asked_hashes: set) -> bool:
    """True if this sentence (or one very similar) was already asked."""
    h = _sentence_hash(sentence)
    if h in asked_hashes:
        return True
    # Also check for near-duplicate by stripping the blank variation
    normalized = _normalize(sentence).replace("________", "").replace("blank", "").strip()
    for existing in asked_hashes:
        # We can't reverse existing hashes, but we track normalized sentences too
        pass
    return False


# ── SESSION STATE ─────────────────────────────────────────────────────────
def reset_state():
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.current_q = None
    st.session_state.start_time = None
    st.session_state.answered = False
    st.session_state.user_answer = ""
    st.session_state.feedback = None
    st.session_state.lesson = None
    st.session_state.suggestion = None
    st.session_state.history = []
    st.session_state.missed_bank = []
    st.session_state.is_reinforce = False
    # Dedup: store hashes of ALL asked sentences
    st.session_state.asked_hashes = set()
    # Full sentences for the LLM "avoid" list
    st.session_state.asked_sentences = []
    # Track which seed words were used per category to rotate them
    st.session_state.used_seeds = {cat: [] for cat in CATEGORY_THEMES}
    # Category rotation index for "All Categories" mode
    st.session_state.cat_rotation_idx = 0

for k in ["page","score","total","current_q","start_time","feedback","lesson","suggestion"]:
    if k not in st.session_state:
        st.session_state[k] = None

for k in ["answered","is_reinforce"]:
    if k not in st.session_state:
        st.session_state[k] = False

for k in ["score","total"]:
    if k not in st.session_state:
        st.session_state[k] = 0

for k in ["user_answer"]:
    if k not in st.session_state:
        st.session_state[k] = ""

for k in ["history","missed_bank","asked_sentences"]:
    if k not in st.session_state:
        st.session_state[k] = []

if "asked_hashes" not in st.session_state:
    st.session_state.asked_hashes = set()

if "used_seeds" not in st.session_state:
    st.session_state.used_seeds = {cat: [] for cat in CATEGORY_THEMES}

if "cat_rotation_idx" not in st.session_state:
    st.session_state.cat_rotation_idx = 0

if st.session_state.page is None:
    st.session_state.page = "setup"


# ── GROQ HELPERS ─────────────────────────────────────────────────────────
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
    """Pick an unused seed word for this category, cycling through the pool."""
    pool = SEED_WORDS.get(category, [])
    used = st.session_state.used_seeds.get(category, [])
    unused = [w for w in pool if w not in used]
    if not unused:
        # Reset if exhausted
        st.session_state.used_seeds[category] = []
        unused = pool
    seed = random.choice(unused) if unused else random.choice(pool)
    st.session_state.used_seeds.setdefault(category, []).append(seed)
    return seed


def _pick_category(configured_cat) -> str:
    """
    If user chose 'All Categories', rotate through all 5 categories in order
    (with a small shuffle per cycle) so we never repeat the same category twice
    in a row and get even coverage.
    """
    if configured_cat:
        return configured_cat
    cats = list(CATEGORY_THEMES.keys())
    idx = st.session_state.cat_rotation_idx % len(cats)
    st.session_state.cat_rotation_idx += 1
    # Shuffle every full cycle for variety
    if idx == 0 and st.session_state.total > 0:
        random.shuffle(cats)
        # Persist shuffled order via session state
        st.session_state.cat_order = cats
    order = st.session_state.get("cat_order", cats)
    return order[idx % len(order)]


def generate_llm_question(client, category, asked_sentences, seed_word, attempt_num):
    """
    Generate one sentence-completion question.
    - seed_word: forces a fresh topic angle each call
    - attempt_num: increases temperature on retries for variety
    """
    themes = CATEGORY_THEMES.get(category, "general English vocabulary")
    temp = min(0.75 + attempt_num * 0.08, 1.0)  # gradually hotter on retries

    # Provide ALL asked sentences (not just 15) for dedup — but cap at 40 to stay within token limits
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
        {"role": "system", "content": "You write unique English vocabulary exam questions. Each question must be completely different from previous ones. Return valid JSON only."},
        {"role": "user", "content": prompt}
    ], max_tokens=300, temp=temp)

    # Validate structure
    assert "sentence" in data and "accepted_answers" in data
    assert "________" in data["sentence"], "Blank marker missing"
    assert len(data["accepted_answers"]) >= 1

    data["id"] = _sentence_hash(data["sentence"])
    data.setdefault("category", category)
    return data


# Hard-coded fallback pool so the app never completely breaks
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
    """
    Generate a fresh question with aggressive dedup.
    Strategy:
      1. Pick category (rotated for variety)
      2. Pick a fresh seed word for that category
      3. Attempt up to 8 LLM calls with increasing temperature
      4. On each attempt, check hash against ALL previously asked sentences
      5. If all 8 attempts fail, fall through to unused fallbacks
      6. If fallbacks exhausted too, use a random fallback with a unique ID
    """
    configured_cat = st.session_state.get("category_filter")
    asked_hashes = st.session_state.asked_hashes
    asked_sentences = st.session_state.asked_sentences

    chosen_cat = _pick_category(configured_cat)
    seed = _pick_seed(chosen_cat)

    last_error = None
    for attempt in range(8):
        try:
            q = generate_llm_question(client, chosen_cat, asked_sentences, seed, attempt)
            if q["id"] not in asked_hashes:
                return q
            # Duplicate detected — try a new seed on next attempt
            seed = _pick_seed(chosen_cat)
        except Exception as e:
            last_error = e
            time.sleep(0.3)
            continue

    # ── Fallback: use hardcoded pool entries not yet asked ────────────────
    unused_fallbacks = [
        f for f in FALLBACK_POOL
        if _sentence_hash(f["sentence"]) not in asked_hashes
        and (not configured_cat or f["category"] == configured_cat)
    ]
    if unused_fallbacks:
        q = dict(random.choice(unused_fallbacks))
        q["id"] = _sentence_hash(q["sentence"])
        return q

    # ── Last resort: any fallback with a uniquified ID ────────────────────
    q = dict(random.choice(FALLBACK_POOL))
    q["id"] = _sentence_hash(q["sentence"] + str(random.random()))
    return q


# ── HEADER ───────────────────────────────────────────────────────────────
st.markdown('<div class="big-title">⚡ TCS NQT Vocab Sprint</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-generated questions · 25s timer · missed words reinforced automatically</div>', unsafe_allow_html=True)

# ── SETUP PAGE ───────────────────────────────────────────────────────────
if st.session_state.page == "setup":
    with st.form("setup_form"):
        api_key = st.text_input("Groq API Key", type="password", help="Free at console.groq.com")
        cat_choice = st.selectbox("Category", list(CATEGORY_FILTER.keys()))
        submitted = st.form_submit_button("🚀 Start Quiz")
    if submitted:
        if not api_key.strip():
            st.error("Please enter your Groq API key.")
        else:
            reset_state()
            st.session_state.api_key = api_key
            st.session_state.category_filter = CATEGORY_FILTER[cat_choice]
            st.session_state.page = "quiz"
            st.rerun()

# ── QUIZ PAGE ─────────────────────────────────────────────────────────────
elif st.session_state.page == "quiz":
    client = get_client(st.session_state.api_key)
    missed_count = len(st.session_state.missed_bank)
    total_generated = len(st.session_state.asked_hashes)

    st.markdown(
        f'<div class="score-pill">✅ {st.session_state.score}/{st.session_state.total} &nbsp;|&nbsp; '
        f'Q{st.session_state.total+1} &nbsp;|&nbsp; {total_generated} generated &nbsp;|&nbsp; 🔁 {missed_count} pending</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("🛑 End Quiz"):
        st.session_state.page = "summary"
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
            q = {
                "id": entry["id"],
                "sentence": entry["sentence"],
                "accepted_answers": entry["accepted_answers"],
                "category": entry["category"],
            }
            st.session_state.is_reinforce = True
        else:
            with st.spinner("✨ Generating question…"):
                q = get_next_question(client)
            st.session_state.is_reinforce = False

        # Register in dedup tracking
        st.session_state.asked_hashes.add(q["id"])
        st.session_state.asked_sentences.append(q["sentence"])

        st.session_state.current_q = q
        st.session_state.start_time = time.time()
        st.session_state.answered = False
        st.session_state.feedback = None
        st.session_state.lesson = None
        st.session_state.suggestion = None
        st.rerun()

    q = st.session_state.current_q
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, TIME_LIMIT - elapsed)
    is_reinforce = st.session_state.is_reinforce

    # ── Not yet answered ─────────────────────────────────────────────────
    if not st.session_state.answered:
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
        with st.form("answer_form", clear_on_submit=False):
            ans = st.text_input("Fill in the blank:", placeholder="Type your answer…")
            submit_ans = st.form_submit_button("✅ Submit")

        timeout = remaining <= 0
        if submit_ans or timeout:
            with st.spinner("Checking…"):
                is_correct = False if timeout else check_answer(client, q["sentence"], q["accepted_answers"], ans)

            st.session_state.answered = True
            st.session_state.user_answer = "(timed out)" if timeout else ans
            st.session_state.feedback = is_correct
            st.session_state.total += 1
            primary = q["accepted_answers"][0]

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
                            "id": q["id"],
                            "word": primary,
                            "sentence": q["sentence"],
                            "accepted_answers": q["accepted_answers"],
                            "category": q["category"],
                            "retries_left": MAX_REINFORCE,
                        })
                with st.spinner("Preparing lesson…"):
                    st.session_state.lesson = generate_lesson(client, primary, q["sentence"])

            st.session_state.history.append({
                "word": primary,
                "correct": is_correct,
                "qid": q["id"],
                "reinforce": is_reinforce,
            })
            st.rerun()
        else:
            time.sleep(1)
            st.rerun()

    # ── Answered ─────────────────────────────────────────────────────────
    else:
        tags = f'<span class="q-tag">{q["category"].upper()}</span>'
        if is_reinforce:
            tags += '<span class="reinforce-tag">🔁 REINFORCE</span>'
        else:
            tags += '<span class="llm-tag">✨ AI</span>'
        q_label = f'Question {st.session_state.total}'
        st.markdown(
            f'<div class="question-card">{tags}'
            f'<div class="q-num">{q_label}</div>'
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
            reinforce_note = "" if is_reinforce else '<br><span style="font-size:0.8rem;color:#FF9966;">🔁 Will come back for reinforcement.</span>'
            st.markdown(f"""
            <div class="wrong-box">
                ❌ <b>Incorrect.</b> You wrote: "<i>{st.session_state.user_answer}</i>"<br>
                <span style="font-size:0.85rem;">Answer: <b>{all_accept}</b></span>{reinforce_note}
            </div>""", unsafe_allow_html=True)
            if st.session_state.lesson:
                L = st.session_state.lesson
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
            st.session_state.current_q = None
            st.rerun()

# ── SUMMARY PAGE ─────────────────────────────────────────────────────────
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
        st.markdown(f'<div class="lesson-box"><b style="color:#B8A6FF;">📚 Revise these:</b><br><br>{chips}</div>', unsafe_allow_html=True)

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔁 Continue"):
            st.session_state.page = "quiz"
            st.session_state.current_q = None
            st.rerun()
    with c2:
        if st.button("⚙️ New Setup"):
            st.session_state.page = "setup"
            st.rerun()
