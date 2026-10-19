"""第1回: 会話履歴を保ちながら素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 既定の質問から開始する

ツールは持たないが、同じ会話の履歴を保って続けて質問できる。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str, chat) -> str:
    response = chat.send_message(question)
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count if usage else "不明"
    output_tokens = usage.candidates_token_count if usage else "不明"
    print(f"[tokens] 入力: {input_tokens} / 出力: {output_tokens}")

    return response.text


def run_chat(chat, first_question: str) -> None:
    question = first_question
    while True:
        print(f"[質問] {question}\n")
        print(ask(question, chat))
        try:
            question = input("\n続けて質問してください（終了: exit）: ").strip()
        except EOFError:
            print()
            break
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue


def main() -> None:
    parser = argparse.ArgumentParser(description="会話履歴を保ちながら素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)
    try:
        run_chat(chat, args.question)
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
