from types import SimpleNamespace

from app import ask as ask_module


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        text="回答",
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=8),
    )
    chat = SimpleNamespace(send_message=lambda question: response)

    assert ask_module.ask("質問", chat) == "回答"
    assert "入力: 12 / 出力: 8" in capsys.readouterr().out


def test_ask_handles_missing_usage_metadata(capsys):
    response = SimpleNamespace(text="回答", usage_metadata=None)
    chat = SimpleNamespace(send_message=lambda question: response)

    assert ask_module.ask("質問", chat) == "回答"
    assert "入力: 不明 / 出力: 不明" in capsys.readouterr().out


def test_run_chat_keeps_using_the_same_chat_for_follow_up(monkeypatch, capsys):
    questions = []

    def send_message(question):
        questions.append(question)
        return SimpleNamespace(text=f"回答: {question}", usage_metadata=None)

    chat = SimpleNamespace(send_message=send_message)
    follow_up = iter(["それについて詳しく", "exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(follow_up))

    ask_module.run_chat(chat, "最初の質問")

    assert questions == ["最初の質問", "それについて詳しく"]
    output = capsys.readouterr().out
    assert "回答: 最初の質問" in output
    assert "回答: それについて詳しく" in output