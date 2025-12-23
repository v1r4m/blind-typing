import random

KOREAN_SENTENCES = [
    "빠른 갈색 여우가 게으른 개를 뛰어넘습니다",
    "오늘 날씨가 정말 좋습니다",
    "프로그래밍은 재미있는 활동입니다",
    "커피 한 잔의 여유를 즐기세요",
    "인생은 짧고 예술은 길다",
    "천 리 길도 한 걸음부터 시작한다",
    "호랑이에게 물려가도 정신만 차리면 산다",
    "가는 말이 고와야 오는 말이 곱다",
    "낮말은 새가 듣고 밤말은 쥐가 듣는다",
    "백문이 불여일견이라는 말이 있다",
]

ENGLISH_SENTENCES = [
    "The quick brown fox jumps over the lazy dog",
    "Hello world this is a typing test",
    "Programming is fun and creative",
    "Practice makes perfect every day",
    "Life is short art is long",
    "A journey of a thousand miles begins with a single step",
    "To be or not to be that is the question",
    "All that glitters is not gold",
    "Better late than never they say",
    "Actions speak louder than words",
]


def get_random_sentence(language: str = "korean") -> str:
    if language == "english":
        return random.choice(ENGLISH_SENTENCES)
    elif language == "korean":
        return random.choice(KOREAN_SENTENCES)
    else:
        return random.choice(KOREAN_SENTENCES + ENGLISH_SENTENCES)
