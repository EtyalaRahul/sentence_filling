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

TIME_LIMIT = 25
MAX_REINFORCE = 2

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
    st.session_state.asked_ids = set()
    st.session_state.asked_sentences = []

for k in ["page","score","total","current_q","start_time","answered","user_answer",
          "feedback","lesson","suggestion","history","missed_bank","is_reinforce",
          "asked_ids","asked_sentences"]:
    if k not in st.session_state:
        st.session_state[k] = None if k in ["page","current_q","start_time","feedback","lesson","suggestion"] else (
            set() if k == "asked_ids" else ([] if k in ["history","missed_bank","asked_sentences"] else
            (False if k in ["answered","is_reinforce"] else (0 if k in ["score","total"] else ""))))

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

def _sentence_key(sentence: str) -> str:
    return "llm-" + hashlib.md5(sentence.strip().lower().encode()).hexdigest()[:12]

def generate_llm_question(client, category, asked_sentences):
    """Generate one easy-to-medium question via Groq, deduped by sentence hash."""
    themes = CATEGORY_THEMES.get(category, "general English vocabulary")
    avoid = "\n".join(f"- {s}" for s in asked_sentences[-15:]) if asked_sentences else "none"
    prompt = f"""Create ONE sentence-completion question for TCS NQT Verbal Ability exam.

Category: {category}
Theme: {themes}
Difficulty: EASY TO MEDIUM — use common, everyday words a college student would know.
             The answer should be a word like: submitted, organised, identified, praised,
             conducted, improved, designed, completed, launched, supported, etc.
             Do NOT use rare or advanced vocabulary.

Rules:
- ONE simple sentence with exactly ONE blank written as ________
- The blank answer must be a common verb, adjective, or noun (1–2 words max)
- Sentence must have clear grammatical clues so the answer is obvious from context
- Keep it short: 10–20 words ideally
- DO NOT reuse or closely paraphrase any of these:
{avoid}

Return ONLY valid JSON, no markdown:
{{
  "sentence": "The manager ________ the new employee for her excellent work.",
  "accepted_answers": ["praised", "commended", "appreciated"],
  "category": "{category}"
}}"""
    data = _call(client, [
        {"role": "system", "content": "You write easy English vocabulary exam questions for Indian engineering students. Return valid JSON only."},
        {"role": "user", "content": prompt}
    ], max_tokens=300, temp=0.9)
    key = _sentence_key(data["sentence"])
    data["id"] = key
    return data

def get_next_question(client):
    """Generate a fresh LLM question, retrying on dupes/errors, with a hard fallback."""
    cat = st.session_state.get("category_filter")
    asked_sentences = st.session_state.get("asked_sentences", [])
    chosen_cat = cat if cat else random.choice(list(CATEGORY_THEMES.keys()))

    for _ in range(5):
        try:
            q = generate_llm_question(client, chosen_cat, asked_sentences)
            if q["id"] not in st.session_state.asked_ids:
                return q
        except Exception:
            continue

    # Hard fallback if Groq keeps failing — generic question so app never breaks
    fallback_sentence = f"The team {'________'} the project well ahead of the scheduled deadline."
    q = {
        "sentence": fallback_sentence,
        "accepted_answers": ["completed", "finished", "delivered"],
        "category": chosen_cat,
    }
    q["id"] = _sentence_key(q["sentence"] + str(random.random()))
    return q

# ── HEADER ───────────────────────────────────────────────────────────────
st.markdown('<div class="big-title">⚡ TCS NQT Vocab Sprint</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-generated questions · 30s timer · missed words reinforced automatically</div>', unsafe_allow_html=True)

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
    total_asked = len(st.session_state.asked_ids)

    st.markdown(
        f'<div class="score-pill">✅ {st.session_state.score}/{st.session_state.total} &nbsp;|&nbsp; '
        f'Q{st.session_state.total+1} &nbsp;|&nbsp; {total_asked} generated &nbsp;|&nbsp; 🔁 {missed_count} pending</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("🛑 End Quiz"):
        st.session_state.page = "summary"
        st.rerun()
    st.write("")

    # ── Pick question ────────────────────────────────────────────────────
    if st.session_state.current_q is None:
        # Every 4th question: reinforce a missed word
        pull_reinforce = (
            st.session_state.missed_bank and
            st.session_state.total > 0 and
            st.session_state.total % 4 == 0
        )

        if pull_reinforce:
            entry = st.session_state.missed_bank[0]
            q = {"id": entry["id"], "sentence": entry["sentence"],
                 "accepted_answers": entry["accepted_answers"], "category": entry["category"]}
            st.session_state.is_reinforce = True
        else:
            with st.spinner("✨ Generating question…"):
                q = get_next_question(client)
            st.session_state.is_reinforce = False

        st.session_state.asked_ids.add(q["id"])
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
            q_label = f'Question {st.session_state.total+1}'
            st.markdown(
                f'<div class="question-card">{tags}'
                f'<div class="q-num">{q_label}</div>'
                f'<div class="q-text">{q["sentence"]}</div></div>',
                unsafe_allow_html=True
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
                    existing_ids = [e["id"] for e in st.session_state.missed_bank]
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

            st.session_state.history.append({"word": primary, "correct": is_correct, "qid": q["id"], "reinforce": is_reinforce})
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
            unsafe_allow_html=True
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
            reinforce_note = '' if is_reinforce else '<br><span style="font-size:0.8rem;color:#FF9966;">🔁 Will come back for reinforcement.</span>'
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