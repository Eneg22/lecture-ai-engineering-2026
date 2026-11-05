"""第3回: エージェントに持たせるツール。

ここに書いた関数の docstring と型ヒントが、そのままモデルへの「ツールの説明文」になる。
説明文を書き換えると、モデルがツールを使うかどうか・どんな引数で呼ぶかが変わる。
"""

import json
import random
from functools import cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MAX_RESULTS = 3


@cache
def load_glossary() -> list[dict]:
    with open(DATA_DIR / "glossary.json", encoding="utf-8") as f:
        return json.load(f)["terms"]


def _normalize(text: str) -> str:
    return text.casefold().replace(" ", "").replace("　", "")


def _names(entry: dict) -> list[str]:
    return [_normalize(entry["term"]), _normalize(entry["id"])] + [
        _normalize(a) for a in entry["aliases"]
    ]


def search_glossary(query: str) -> str:
    """講座の用語集から用語を検索し、定義と、どの回で扱うかを返す。

    AIエンジニアリングの用語や、この講座（AIE2026）に固有の言葉について
    答える前に使うこと。query には調べたい用語を1つだけ入れる（例: "LoRA"）。
    """
    q = _normalize(query)
    if not q:
        return "検索語が空です。調べたい用語を1つ指定してください。"
    glossary = load_glossary()

    exact = [e for e in glossary if q in _names(e)]
    # 「r」のような短い別名が何にでも当たらないよう、名前側が短いものは除く
    partial = [
        e for e in glossary
        if e not in exact and any(q in n or (len(n) >= 3 and n in q) for n in _names(e))
    ]
    in_definition = [
        e for e in glossary
        if e not in exact and e not in partial and q in _normalize(e["definition"])
    ]
    hits = (exact + partial + in_definition)[:MAX_RESULTS]

    if not hits:
        return f"用語集に「{query}」は見つかりませんでした。"
    return json.dumps(
        [
            {
                "term": e["term"],
                "lecture": e["lecture"],
                "definition": e["definition"],
                "related": e["related"],
            }
            for e in hits
        ],
        ensure_ascii=False,
    )


def get_lecture_summary(lecture: int) -> str:
    """指定した回（1始まりの整数）の講義の要点を返す。

    「第3回では何を学ぶ？」のように、回の内容や関係を聞かれたときに使う。
    """
    path = DATA_DIR / "lectures" / f"{lecture:02d}.md"
    if not path.exists():
        available = sorted(p.stem for p in (DATA_DIR / "lectures").glob("*.md"))
        return f"第{lecture}回の要点はまだありません。用意されている回: {', '.join(available)}"
    return path.read_text(encoding="utf-8")

def make_quiz(lecture: int) -> str:
    """指定した回の用語から 1つを選び、
    確認問題と答えを返す。
    「第2回の確認問題を出して」のように、
    復習用の問題を求められたときに使う。
    """
    terms = [term for term in load_glossary() if term["lecture"] == lecture]
    if not terms:
        return f"第{lecture}回の用語が用語集にありません。"

    term = random.choice(terms)
    return json.dumps(
        {
            "question": f"次の説明に当てはまる用語は何ですか？\n{term['definition']}",
            "answer": term["term"],
        },
        ensure_ascii=False,
    )

def similarity(term1: str, term2: str) -> str:
    """用語集にある二つの用語を比較するための情報を返す。

    term1 と term2 には用語名、用語 ID、または別名を1つずつ指定する。
    「LoRAとQLoRAの共通点と違いは？」のように、二つの用語の比較を
    求められたときに使う。戻り値にはそれぞれの定義・回・カテゴリ・関連用語と、
    共通するカテゴリや関連用語が含まれる。これらの根拠に基づいて説明する。
    """
    queries = [_normalize(term1), _normalize(term2)]
    if not all(queries):
        return "比較する用語を2つ指定してください。"

    glossary = load_glossary()
    matches = []
    for query, original in zip(queries, (term1, term2)):
        found = [entry for entry in glossary if query in _names(entry)]
        if not found:
            return f"用語集から「{original}」を特定できませんでした。用語名を確認してください。"
        if len(found) > 1:
            names = "、".join(entry["term"] for entry in found)
            return f"「{original}」に複数の用語が一致しました。用語名を指定してください: {names}"
        matches.append(found[0])

    entries_by_id = {entry["id"]: entry for entry in glossary}

    def related_names(entry: dict) -> list[str]:
        return [
            entries_by_id[related_id]["term"]
            for related_id in entry["related"]
            if related_id in entries_by_id
        ]

    shared_related_ids = set(matches[0]["related"]) & set(matches[1]["related"])
    return json.dumps(
        {
            "terms": [
                {
                    "term": entry["term"],
                    "lecture": entry["lecture"],
                    "category": entry["category"],
                    "definition": entry["definition"],
                    "related": related_names(entry),
                }
                for entry in matches
            ],
            "shared_category": (
                matches[0]["category"]
                if matches[0]["category"] == matches[1]["category"]
                else None
            ),
            "shared_related_terms": [
                entries_by_id[related_id]["term"]
                for related_id in shared_related_ids
                if related_id in entries_by_id
            ],
        },
        ensure_ascii=False,
    )