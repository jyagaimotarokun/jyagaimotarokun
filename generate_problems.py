#!/usr/bin/env python3
"""
小学2年生向け 毎日の算数問題ジェネレーター
15分程度で解ける問題セットを生成します
"""
import random
import datetime
import sys
import os


def get_seed(date: datetime.date) -> int:
    return int(date.strftime("%Y%m%d"))


def seeded_random(seed: int) -> random.Random:
    return random.Random(seed)


def addition_within_100(rng: random.Random) -> tuple[str, str]:
    a = rng.randint(10, 60)
    b = rng.randint(10, 99 - a)
    return f"{a} + {b}", str(a + b)


def subtraction_within_100(rng: random.Random) -> tuple[str, str]:
    a = rng.randint(20, 99)
    b = rng.randint(1, a - 1)
    return f"{a} - {b}", str(a - b)


def addition_carry(rng: random.Random) -> tuple[str, str]:
    """くり上がりのあるたし算"""
    while True:
        a = rng.randint(1, 9)
        b = rng.randint(10 - a, 9)
        if a + b >= 10 and a + b <= 18:
            return f"{a} + {b}", str(a + b)


def subtraction_borrow(rng: random.Random) -> tuple[str, str]:
    """くり下がりのあるひき算"""
    while True:
        a = rng.randint(11, 18)
        b = rng.randint(2, a - 1)
        if b >= 2 and a - b >= 1:
            return f"{a} - {b}", str(a - b)


def multiplication_table(rng: random.Random) -> tuple[str, str]:
    """かけ算の九九"""
    a = rng.randint(2, 9)
    b = rng.randint(1, 9)
    return f"{a} × {b}", str(a * b)


def word_problem_addition(rng: random.Random) -> tuple[str, str]:
    templates = [
        ("りんごが {a} こ あります。{b} こ もらいました。あわせて なんこ ですか？", "こ"),
        ("バスに {a} にん のっています。つぎの バスていで {b} にん のりました。あわせて なんにん ですか？", "にん"),
        ("シールが {a} まい あります。{b} まい もらいました。あわせて なんまい ですか？", "まい"),
        ("あかい はなが {a} ほん、しろい はなが {b} ほん あります。あわせて なんぼん ですか？", "ほん"),
    ]
    t, unit = rng.choice(templates)
    a = rng.randint(10, 50)
    b = rng.randint(5, 40)
    return t.format(a=a, b=b), f"{a + b}{unit}"


def word_problem_subtraction(rng: random.Random) -> tuple[str, str]:
    templates = [
        ("おかしが {a} こ あります。{b} こ たべました。なんこ のこって いますか？", "こ"),
        ("えんぴつが {a} ほん あります。{b} ほん つかいました。なんぼん のこって いますか？", "ほん"),
        ("カードが {a} まい あります。{b} まい あげました。なんまい のこって いますか？", "まい"),
    ]
    t, unit = rng.choice(templates)
    a = rng.randint(20, 80)
    b = rng.randint(5, a - 5)
    return t.format(a=a, b=b), f"{a - b}{unit}"


def word_problem_multiplication(rng: random.Random) -> tuple[str, str]:
    templates = [
        ("{a} まいの おさらに クッキーが {b} こずつ のっています。クッキーは ぜんぶで なんこ ですか？", "こ"),
        ("こどもが {a} にん います。ひとりに えんぴつを {b} ほんずつ くばります。えんぴつは なんぼん いりますか？", "ほん"),
        ("{a} れつに {b} にんずつ ならんで います。ぜんぶで なんにん ですか？", "にん"),
    ]
    t, unit = rng.choice(templates)
    a = rng.randint(2, 8)
    b = rng.randint(2, 9)
    return t.format(a=a, b=b), f"{a * b}{unit}"


def clock_problem(rng: random.Random) -> tuple[str, str]:
    """時計の問題"""
    hour = rng.randint(7, 20)
    minute = rng.choice([0, 15, 30, 45])
    duration = rng.choice([30, 60, 90, 120])

    start_total = hour * 60 + minute
    end_total = start_total + duration
    end_hour = (end_total // 60) % 24
    end_minute = end_total % 60

    if minute == 0:
        start_str = f"{hour}じ ちょうど"
    else:
        start_str = f"{hour}じ {minute}ふん"

    if end_minute == 0:
        end_str = f"{end_hour}じ ちょうど"
    else:
        end_str = f"{end_hour}じ {end_minute}ふん"

    dur_h = duration // 60
    dur_m = duration % 60
    if dur_h == 0:
        dur_str = f"{dur_m}ふん"
    elif dur_m == 0:
        dur_str = f"{dur_h}じかん"
    else:
        dur_str = f"{dur_h}じかん{dur_m}ふん"

    question = f"{start_str} から {dur_str} たつと なんじ なんふん ですか？"
    return question, end_str


def length_problem(rng: random.Random) -> tuple[str, str]:
    """長さの問題"""
    a = rng.randint(12, 20)
    b = rng.randint(3, a - 4)
    q = (
        f"えんぴつの ながさは {a}cm です。"
        f"けしごむの ながさは {b}cm です。"
        f"えんぴつは けしごむより なんcm ながい ですか？"
    )
    return q, f"{a - b}cm"


def generate_problems(date: datetime.date) -> str:
    rng = seeded_random(get_seed(date))
    date_str = date.strftime("%Y年%-m月%-d日")

    lines = []
    lines.append(f"# {date_str}の さんすう もんだい")
    lines.append("")
    lines.append("> 今日も がんばろう！ 🌟")
    lines.append("")

    # Section 1: 計算問題 (8問)
    lines.append("## 1. けいさん しよう (8もん)")
    lines.append("")

    calc_problems: list[tuple[str, str]] = []
    for _ in range(2):
        calc_problems.append(addition_carry(rng))
    for _ in range(2):
        calc_problems.append(subtraction_borrow(rng))
    for _ in range(2):
        calc_problems.append(addition_within_100(rng))
    for _ in range(2):
        calc_problems.append(subtraction_within_100(rng))
    rng.shuffle(calc_problems)

    for i, (q, _) in enumerate(calc_problems, 1):
        lines.append(f"({i})  {q}  ＝  ＿＿＿")
    lines.append("")

    # Section 2: 九九 (5問)
    lines.append("## 2. かけざん (5もん)")
    lines.append("")
    mult_problems: list[tuple[str, str]] = []
    for _ in range(5):
        mult_problems.append(multiplication_table(rng))
    for i, (q, _) in enumerate(mult_problems, 1):
        lines.append(f"({i})  {q}  ＝  ＿＿＿")
    lines.append("")

    # Section 3: 文章題 (4問)
    lines.append("## 3. ぶんしょうだい (4もん)")
    lines.append("")

    word_problems: list[tuple[str, str]] = []
    word_problems.append(word_problem_addition(rng))
    word_problems.append(word_problem_subtraction(rng))
    word_problems.append(word_problem_multiplication(rng))
    word_problems.append(word_problem_addition(rng))

    for i, (q, _) in enumerate(word_problems, 1):
        lines.append(f"**({i})** {q}")
        lines.append("")
        lines.append("　こたえ：＿＿＿＿＿")
        lines.append("")

    # Section 4: 時計 (1問)
    lines.append("## 4. とけい (1もん)")
    lines.append("")
    clock_q, clock_a = clock_problem(rng)
    lines.append(f"**(1)** {clock_q}")
    lines.append("")
    lines.append("　こたえ：＿＿＿＿＿")
    lines.append("")

    # Section 5: 長さ (1問)
    lines.append("## 5. ながさ (1もん)")
    lines.append("")
    len_q, len_a = length_problem(rng)
    lines.append(f"**(1)** {len_q}")
    lines.append("")
    lines.append("　こたえ：＿＿＿＿＿")
    lines.append("")

    # Answers
    lines.append("---")
    lines.append("")
    lines.append("<details>")
    lines.append("<summary>こたえ（クリックして ひらく）</summary>")
    lines.append("")
    lines.append("### 1. けいさん")
    lines.append("")
    for i, (q, a) in enumerate(calc_problems, 1):
        lines.append(f"({i}) {q} ＝ **{a}**")
    lines.append("")
    lines.append("### 2. かけざん")
    lines.append("")
    for i, (q, a) in enumerate(mult_problems, 1):
        lines.append(f"({i}) {q} ＝ **{a}**")
    lines.append("")
    lines.append("### 3. ぶんしょうだい")
    lines.append("")
    for i, (_, a) in enumerate(word_problems, 1):
        lines.append(f"({i}) **{a}**")
    lines.append("")
    lines.append("### 4. とけい")
    lines.append("")
    lines.append(f"(1) **{clock_a}**")
    lines.append("")
    lines.append("### 5. ながさ")
    lines.append("")
    lines.append(f"(1) **{len_a}**")
    lines.append("")
    lines.append("</details>")

    return "\n".join(lines)


def _generate_all_sections(date: datetime.date):
    """全セクションの問題と答えを同じ順序で生成して返す（内部用）"""
    rng = seeded_random(get_seed(date))

    calc_problems: list[tuple[str, str]] = []
    for _ in range(2):
        calc_problems.append(addition_carry(rng))
    for _ in range(2):
        calc_problems.append(subtraction_borrow(rng))
    for _ in range(2):
        calc_problems.append(addition_within_100(rng))
    for _ in range(2):
        calc_problems.append(subtraction_within_100(rng))
    rng.shuffle(calc_problems)

    mult_problems: list[tuple[str, str]] = []
    for _ in range(5):
        mult_problems.append(multiplication_table(rng))

    word_problems: list[tuple[str, str]] = []
    word_problems.append(word_problem_addition(rng))
    word_problems.append(word_problem_subtraction(rng))
    word_problems.append(word_problem_multiplication(rng))
    word_problems.append(word_problem_addition(rng))

    clock = clock_problem(rng)
    length = length_problem(rng)

    return calc_problems, mult_problems, word_problems, clock, length


def build_line_problem_text(date: datetime.date) -> str:
    """LINE送信用：問題のみ（答えなし）"""
    date_str = date.strftime("%-m月%-d日")
    calc, mult, word, (clock_q, _), (len_q, _) = _generate_all_sections(date)

    lines = [f"📚 {date_str}の さんすう もんだい", "今日も がんばろう！", ""]

    lines.append("【1】けいさん (8もん)")
    for i, (q, _) in enumerate(calc, 1):
        lines.append(f"({i}) {q} =")
    lines.append("")

    lines.append("【2】かけざん (5もん)")
    for i, (q, _) in enumerate(mult, 1):
        lines.append(f"({i}) {q} =")
    lines.append("")

    lines.append("【3】ぶんしょうだい (4もん)")
    for i, (q, _) in enumerate(word, 1):
        lines.append(f"({i}) {q}")
    lines.append("")

    lines.append("【4】とけい (1もん)")
    lines.append(f"(1) {clock_q}")
    lines.append("")

    lines.append("【5】ながさ (1もん)")
    lines.append(f"(1) {len_q}")
    lines.append("")
    lines.append("「できた」と送ると こたえが みられるよ！")

    return "\n".join(lines)


def build_line_answer_text(date: datetime.date) -> str:
    """LINE送信用：答えのみ"""
    date_str = date.strftime("%-m月%-d日")
    calc, mult, word, (_, clock_a), (_, len_a) = _generate_all_sections(date)

    lines = [f"✅ {date_str}の こたえ", ""]

    lines.append("[けいさん]")
    for i, (q, a) in enumerate(calc, 1):
        lines.append(f"({i}) {q} = {a}")
    lines.append("")

    lines.append("[かけざん]")
    for i, (q, a) in enumerate(mult, 1):
        lines.append(f"({i}) {q} = {a}")
    lines.append("")

    lines.append("[ぶんしょうだい]")
    for i, (_, a) in enumerate(word, 1):
        lines.append(f"({i}) {a}")
    lines.append("")

    lines.append(f"[とけい] (1) {clock_a}")
    lines.append(f"[ながさ] (1) {len_a}")
    lines.append("")
    lines.append("よくできました！🌟")

    return "\n".join(lines)


def main():
    if len(sys.argv) > 1:
        date = datetime.date.fromisoformat(sys.argv[1])
    else:
        date = datetime.date.today()

    content = generate_problems(date)

    out_dir = "problems"
    os.makedirs(out_dir, exist_ok=True)
    filename = os.path.join(out_dir, f"{date.strftime('%Y-%m-%d')}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {filename}")


if __name__ == "__main__":
    main()
