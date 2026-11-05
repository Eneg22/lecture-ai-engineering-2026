# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
第一回と比べて簡潔でまとまった回答だった。また、「関連する回：第1回」という部分が追加されていた。
data/glossary.jsonの"homework-levels"の情報のみを忠実に網羅していた。

- `--trace` で見えたツール呼び出し（ツール名と引数）：
[tool call]   search_glossary({'query': 'LoRA'})
[tool call]   search_glossary({'query': 'QLoRA'})

- 1つの質問での LLM 呼び出し回数（`requests`）： 2回
[usage] RunUsage(cost=Decimal('0.0005723'), details={'text_prompt_tokens': 916}, input_text_tokens=916, input_tokens=916, output_tokens=119, **requests=2**, tool_calls=1)

- 追加したツールと、docstring に書いた説明：
ツール：similarity関数
説明：
```
"""用語集にある二つの用語を比較するための情報を返す。

    term1 と term2 には用語名、用語 ID、または別名を1つずつ指定する。
    「LoRAとQLoRAの共通点と違いは？」のように、二つの用語の比較を
    求められたときに使う。戻り値にはそれぞれの定義・回・カテゴリ・関連用語と、
    共通するカテゴリや関連用語が含まれる。これらの根拠に基づいて説明する。
    """
```

（例）
```
(lec03) $ uv run python -m app.agent --trace "LoRAとQLoRAの共通点と 相違点を教えて"
[model] gemini-3.5-flash-lite
LoRAとQLoRAの共通点と相違点は以下の通りです。

### 共通点
* **カテゴリ**: どちらも「ファインチューニング」の技術（PEFT手法）であり、大規模言語モデルの効率的な学習に用いられます。
* **LoRAの仕組み**: どちらの手法も、ベースモデルの重みを固定し、低ランク行列（アダプタ）のパラメータのみを学習する **LoRA** の仕組みを共通して採用しています。

### 相違点
* **ベースモデルの量子化**: 
  * **LoRA** は、ベースモデルの重みを通常の精度（FP16やBF16など）のまま保持して学習します。
  * **QLoRA** は、ベースモデルの重みを4ビットなどに **量子化** してメモリ消費を大幅に抑えた状態で保持し、その上でLoRAを適用します。
* **必要なGPUリソース**: 
  * QLoRAの方がメモリ節約効果が高いため、LoRAではGPUに載りきらないような、より大きなモデルを小さなGPU環境で扱うことができます。

（関係する回：第2回）

--- trace ---
[tool call]   similarity({'term1': 'LoRA', 'term2': 'QLoRA'})
[tool return] similarity -> {"terms": [{"term": "LoRA", "lecture": 2, "category": "ファインチューニング", "definition": "事前学習済みの重みは固定したまま、重みの更新分を2つの小さな行列の積（低ラ…
[usage] RunUsage(cost=Decimal('0.0011234'), details={'text_prompt_tokens': 1453}, input_text_tokens=1453, input_tokens=1453, output_tokens=275, requests=2, tool_calls=1)
```

## 宿題

- 取り組んだレベル：基礎
- やったこと：
1. 用語にある単語で、app.agentの説明「- 用語や講座に固有のことを答える前に、必ず search_glossary で用語集を確認する。」の有無による回答の変化を調べた。

2. 用語にない単語で、app.agentの説明「- 用語集に見つからないことは、推測で断定せず「用語集にはない」と伝える。」の有無による回答の変化を調べた。

- 結果：
### 実験1：用語集に登録されている単語（エポック）

「用語や講座に固有のことを答える前に、必ず search_glossary で用語集を確認する。」という説明の有無を比較。

| 項目 | 説明あり | 説明なし |
|---|---|---|
| ツール呼び出し | `search_glossary` | `search_glossary` |
| 呼び出し回数 | 1回 | 1回 |
| 引数 | `{'query': 'エポック'}` | `{'query': 'エポック'}` |
| 回答の変化 | 用語集の定義に沿って説明。過学習への注意点も説明 | 用語集を参照したうえで、Epochの英語表記やパラメータ更新、汎化性能など、より詳細に説明 |



### 実験2：用語集に登録されていない単語（国家サイバー統括室）

「用語集に見つからないことは、推測で断定せず『用語集にはない』と伝える。」という説明の有無を比較。

| 項目 | 説明あり | 説明なし |
|---|---|---|
| ツール呼び出し | `search_glossary` | `search_glossary` |
| 呼び出し回数 | 1回 | 2回 |
| 引数 | `{'query': '国家サイバー統括室'}` | `{'query': '国家サイバー統括室'}`、`{'query': 'サイバー'}` |
| 回答の変化 | 用語集に登録されていないことを明示。講座固有の用語ではない可能性を説明 | 用語集に登録されていないことを伝えたうえで、一般的な意味を推測して説明。追加情報も要求 |


- 気づき・疑問：
実験1では、説明の有無にかかわらず、用語集の検索が1回実行され、回答内容も大きくは変わらなかった。ただし、説明なしの場合のほうが補足説明が多く、より詳細な回答となった。
実験2では、説明ありの場合は、用語集にないことを伝えるだけにとどまった。一方、説明なしの場合は追加検索を行い、用語集にないにもかかわらず、一般的な意味を補足して回答した。




- 詳細なログ

1. 用語あり
説明あり
```
(lec03) $ uv run python -m app.agent --trace  "「エポック」とは何ですか？"
[model] gemini-3.5-flash-lite
「エポック」とは、**機械学習の訓練において、学習データ全体をすべて1回ずつモデルに学習させること**を指します。

例えば、1000枚の画像データを使ってモデルを訓練する場合、その1000枚すべてを1回ずつ網羅して学習が終わった状態が「1エポック」です。これを繰り返すことで、モデルの精度を高めていきます。

ただし、エポック数をやみくもに増やしすぎると、訓練データに過剰に適応してしまう「過学習（オーバーフィッティング）」を起こしやすくなるため注意が必要です。

（関係する回：第2回）

--- trace ---
[tool call]   search_glossary({'query': 'エポック'})
[tool return] search_glossary -> [{"term": "エポック", "lecture": 2,"definition": "学習データ全体を1周学習することを1エポックと数える。回数を増やしすぎると過学習しやすい。", "related": ["overfitting"…
[usage] RunUsage(cost=Decimal('0.0007667'), details={'text_prompt_tokens': 1239}, input_text_tokens=1239, input_tokens=1239, output_tokens=158, requests=2, tool_calls=1)
```

説明なし
```
(lec03) $ uv run python -m app.agent --trace  "「エポック」とは何ですか？"
[model] gemini-3.5-flash-lite
「エポック（Epoch）」とは、機械学習やディープラーニングのトレーニングにおいて、**訓練データ（学習データ）の全体が1回すべてもれなくモデルに学習された状態、またはその1周分のサイクル**のことです。

例えば、1,000枚の画像データを使ってモデルを学習させる際、その1,000枚すべてを1回ずつ入力してパラメータの更新を完了させると、「1エポック」となります。

### 注意点
エポック数をやみくもに増やしすぎると、モデルがその訓練データに過剰に適応してしまい、未知のデータに対する予測性能（汎化性能）が落ちる「**過学習（オーバーフィッティング）**」を起こしやすくなるため注意が必要です。

（関係する回：第2回）

--- trace ---
[tool call]   search_glossary({'query': 'エポック'})
[tool return] search_glossary -> [{"term": "エポック", "lecture": 2,"definition": "学習データ全体を1周学習することを1エポックと数える。回数を増やしすぎると過学習しやすい。", "related": ["overfitting"…
[usage] RunUsage(cost=Decimal('0.0008448'), details={'text_prompt_tokens': 1191}, input_text_tokens=1191, input_tokens=1191, output_tokens=195, requests=2, tool_calls=1)

```
1. 用語なし
説明あり
```
(lec03) $ uv run python -m app.agent --trace  "「国家サイバー統括室」とは何ですか？"
[model] gemini-3.5-flash-lite
「国家サイバー統括室」という用語は、この講座の用語集には登録されていません。AIエンジニアリング講座（AIE2026）の文脈における特定の用語や概念ではない可能性があります。

--- trace ---
[tool call]   search_glossary({'query': '国家サイバー統括室'})
[tool return] search_glossary -> 用語集に「国家サイバー統括室」は見つかりませんでした。…
[usage] RunUsage(cost=Decimal('0.0005318'), details={'text_prompt_tokens': 1206}, input_text_tokens=1206, input_tokens=1206, output_tokens=68, requests=2, tool_calls=1)
```

説明なし
```
(lec03) $ uv run python -m app.agent --trace  "「国家サイバー統括室 」とは何ですか？"
[model] gemini-3.5-flash-lite
「国家サイバー統括室」について講座の用語集を確認いたしましたが、該当する用語は登録されていないようです。

なお、一般的な文脈において「国家サイバー統括室（National Cyber Director など）」は、国のサイバーセキュリティ政策や戦略の立案・調整を統括する政府機関を指すことが多いです。AIエンジニアリングやセキュリティに関する講義内容や、もしこの言葉が出てきた具体的な回（第○回など）がお分かりでしたら、追加で教えていただけますと幸いです。

--- trace ---
[tool call]   search_glossary({'query': '国家サイバー統括室'})
[tool return] search_glossary -> 用語集に「国家サイバー統括室」は見つかりませんでした。…
[tool call]   search_glossary({'query': 'サイバー'})
[tool return] search_glossary -> 用語集に「サイバー」は見つかりませんでした。…
[usage] RunUsage(cost=Decimal('0.0009146'), details={'text_prompt_tokens': 1807}, input_text_tokens=1807, input_tokens=1807, output_tokens=149, requests=3, tool_calls=2)
```



