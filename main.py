
import random
import re
import streamlit as st

st.set_page_config(
    page_title="간편 닉네임 작명소",
    page_icon="✦",
    layout="centered",
)

# 한글 완성형 음절의 초성, 중성, 종성 목록
CHOSEONG = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ",
    "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

JUNGSEONG = [
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ",
    "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ",
    "ㅡ", "ㅢ", "ㅣ"
]

JONGSEONG = [
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ",
    "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ",
    "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]


# 화면 디자인
st.markdown(
    """
    <style>
    .stApp {
        background-color: #fffaf2;
    }

    .block-container {
        max-width: 760px;
        padding-top: 2.5rem;
    }

    h1, h2, h3 {
        color: #594331;
    }

    .intro {
        color: #806d5b;
        font-size: 1.05rem;
        line-height: 1.8;
    }

    .nickname-card {
        background-color: white;
        border: 1px solid #ead8c2;
        border-radius: 16px;
        padding: 18px;
        margin: 12px 0;
        box-shadow: 0 3px 10px #00000008;
    }

    .nickname-number {
        color: #a17b4b;
        font-size: 0.9rem;
    }

    .nickname-name {
        color: #49382b;
        font-size: 1.6rem;
        font-weight: bold;
        margin-top: 5px;
    }

    div.stButton > button[kind="primary"] {
        background-color: #b88752;
        color: white;
        border: none;
        border-radius: 12px;
        min-height: 3rem;
        font-weight: bold;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #946b3e;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def decompose_syllable(char):
    """한글 음절을 초성, 중성, 종성으로 분해한다."""

    code = ord(char) - 0xAC00

    if code < 0 or code > 11171:
        return None

    cho = code // 588
    jung = (code % 588) // 28
    jong = code % 28

    return (
        CHOSEONG[cho],
        JUNGSEONG[jung],
        JONGSEONG[jong],
    )


def extract_syllables(text):
    """입력한 글자 중 한글 음절만 추출한다."""

    return re.findall(r"[가-힣]", text)


def pronunciation_score(name):
    """
    간단한 규칙으로 닉네임의 발음 점수를 계산한다.
    실제 한국어 발음의 자연스러움을 완벽하게 판정하지는 못한다.
    """

    score = 50

    parts = [decompose_syllable(char) for char in name]

    # 2~3글자 닉네임에 소폭 가점
    if len(name) in (2, 3):
        score += 8

    # 같은 음절이 연속되면 감점
    for i in range(1, len(name)):
        if name[i] == name[i - 1]:
            score -= 8

    # 받침이 있는 음절이 연속되면 소폭 감점
    for i in range(1, len(parts)):
        if parts[i - 1][2] and parts[i][2]:
            score -= 4

    # 초성이 모두 같으면 단조로울 수 있어 감점
    initials = [part[0] for part in parts]

    if len(set(initials)) == 1 and len(name) > 1:
        score -= 5

    # 모음이 모두 같으면 단조로울 수 있어 감점
    vowels = [part[1] for part in parts]

    if len(set(vowels)) == 1 and len(name) > 1:
        score -= 5

    # 받침이 있는 음절과 없는 음절이 섞이면 소폭 가점
    finals = [bool(part[2]) for part in parts]

    if any(finals) and not all(finals):
        score += 3

    return score


def generate_nicknames(words, length, seed):
    """입력 단어에서 추출한 음절을 조합해 닉네임을 만든다."""

    rng = random.Random(seed)

    syllables = []
    chunks = []

    for word in words:
        chars = extract_syllables(word)

        syllables.extend(chars)

        # 원래 단어의 연속된 음절 조각도 후보로 활용
        for size in (2, 3):
            for start in range(len(chars) - size + 1):
                chunk = "".join(chars[start:start + size])
                chunks.append(chunk)

    # 중복 음절 제거
    syllables = list(dict.fromkeys(syllables))
    chunks = list(dict.fromkeys(chunks))

    candidates = set()

    # 입력 단어에서 추출한 음절 조각 활용
    for chunk in chunks:
        if len(chunk) == length:
            candidates.add(chunk)

    # 음절을 조합해 새로운 후보 생성
    if syllables:
        for _ in range(10000):
            name = "".join(
                rng.choice(syllables)
                for _ in range(length)
            )

            candidates.add(name)

            if len(candidates) >= 3000:
                break

    # 발음 점수가 높은 후보부터 정렬
    scored = [
        (pronunciation_score(name), name)
        for name in candidates
    ]

    rng.shuffle(scored)
    scored.sort(key=lambda item: item[0], reverse=True)

    return [name for score, name in scored[:5]]


# 사이트 제목과 설명
st.title("✦ 간편 닉네임 작명소")

st.markdown(
    """
    <p class="intro">
    닉네임을 정하기 어렵다면 단어를 입력해 보세요.<br>
    입력한 단어의 음절을 활용해 새로운 닉네임을 추천해 드려요!
    </p>
    """,
    unsafe_allow_html=True,
)

# 입력 영역
with st.container(border=True):

    words_text = st.text_area(
        "닉네임 재료가 될 단어",
        placeholder="예: 하늘, 구름, 별빛",
        help="여러 단어는 쉼표, 공백 또는 줄바꿈으로 구분하세요.",
        height=110,
    )

    # 닉네임 길이를 2~9글자까지 선택
    length = st.selectbox(
        "닉네임 길이",
        options=list(range(2, 10)),
        format_func=lambda value: f"{value}글자",
    )

    generate = st.button(
        "닉네임 5개 만들기",
        type="primary",
        use_container_width=True,
    )


# 버튼을 눌렀을 때 닉네임 생성
if generate:

    words = [
        word.strip()
        for word in re.split(r"[,，\s]+", words_text)
        if word.strip()
    ]

    if not words_text.strip():

        st.warning("먼저 닉네임 재료가 될 단어를 입력해 주세요.")
        st.session_state.pop("nickname_results", None)

    elif not extract_syllables(words_text):

        st.warning("한글 단어를 입력해 주세요. 현재 버전은 한글 음절만 활용해요.")
        st.session_state.pop("nickname_results", None)

    else:

        seed = st.session_state.get("generation_seed", 0) + 1
        st.session_state["generation_seed"] = seed

        results = generate_nicknames(words, length, seed)

        st.session_state["nickname_results"] = results

        if len(results) < 5:
            st.info(
                "서로 다른 후보가 5개보다 적어요. "
                "재료가 될 단어를 더 입력해 보세요."
            )


# 생성 결과 표시
results = st.session_state.get("nickname_results", [])

if results:

    st.markdown("## 추천 닉네임")

    st.caption(
        "마음에 드는 닉네임 아래의 복사 버튼을 눌러 복사할 수 있어요."
    )

    for index, nickname in enumerate(results, start=1):

        st.markdown(
            f"""
            <div class="nickname-card">
                <div class="nickname-number">추천 {index}</div>
                <div class="nickname-name">{nickname}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 코드 상자 오른쪽의 복사 버튼 이용
        st.code(nickname, language=None)


st.divider()

st.caption(
    "닉네임은 입력한 한글 음절을 조합해 생성합니다. "
    "발음 평가는 간단한 규칙에 따른 참고 점수이며, "
    "실제 발음의 자연스러움을 완벽하게 판단하지는 못해요."
)
