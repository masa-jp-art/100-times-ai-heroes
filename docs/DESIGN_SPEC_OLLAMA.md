# 100 Times AI Heroes - Ollama版 設計仕様書

## 1. 概要

### 1.1 目的
「100 Times AI Heroes」プロジェクトの推論部分をOpenAI APIからOllama（ローカルLLM）に移行し、完全にローカル環境で動作するバージョンを作成する。

### 1.2 移行メリット
| 項目 | OpenAI API | Ollama |
|------|------------|--------|
| コスト | 従量課金 | 無料 |
| プライバシー | クラウド送信 | 完全ローカル |
| オフライン | 不可 | 可能 |
| レート制限 | あり | なし |
| APIキー管理 | 必要 | 不要 |

---

## 2. システムアーキテクチャ

### 2.1 動作環境
- **ハードウェア**: M4 MacBook Pro (128GB)
- **OS**: macOS
- **Python**: 3.10+

### 2.2 全体構成
```
┌─────────────────────────────────────────────────────────────┐
│                    ローカル実行環境                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐     ┌─────────────────────────┐      │
│  │  main.py         │     │    Ollama Server        │      │
│  │  (Python 3.10+)  │────►│  localhost:11434        │      │
│  └──────────────────┘     │                         │      │
│           │               │  Model: gpt-oss-20b     │      │
│           │               └─────────────────────────┘      │
│           │                                                 │
│           ▼                                                 │
│  ┌──────────────────┐                                      │
│  │ Google Sheets    │ ◄── サービスアカウント認証            │
│  │ (入力/出力)      │                                      │
│  └──────────────────┘                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 推論タスク（7種類）
| # | タスク | 入力言語 | 出力言語 | 用途 |
|---|--------|----------|----------|------|
| 1 | CharacterConcept | 日本語 | 英語 | キャラ設定の要約 |
| 2 | Name | 英語 | 英語 | キャラ名生成 |
| 3 | Profile | 英語 | 日本語 | プロフィール文 |
| 4 | Seriff | 英語 | 日本語 | 決め台詞 |
| 5 | NewAbility | 英語 | 英語 | 対キャラの能力 |
| 6 | NewWants | 英語 | 英語 | 対キャラの願望 |
| 7 | NewRole | 英語 | 英語 | 対キャラの役割 |

---

## 3. ファイル構成

```
100-times-ai-heroes/
├── ollama_hero_gen.py           # メインスクリプト（単一ファイル）
├── credentials.json             # Google サービスアカウント認証（.gitignore）
├── .env                         # 環境変数（.gitignore）
├── requirements.txt             # 依存パッケージ
├── 20240916-AI-Art-GP-3-Charactor-v1.0.py  # 既存（OpenAI版・参照用）
├── README.md
└── docs/
    └── DESIGN_SPEC_OLLAMA.md
```

**設計方針**: 単一ファイル構成でシンプルに保つ

---

## 4. モデル選定

### 4.1 要件
- 日本語プロンプト理解・日本語出力
- 英語出力（名前・能力説明）
- キャラクター設定の創造性
- 制約事項・出力形式の遵守

### 4.2 推奨モデル

| モデル | VRAM | 日本語 | 創造性 | 推奨度 |
|--------|------|--------|--------|--------|
| **gpt-oss-20b** | 12GB | ◎ | ◎ | ★★★ |
| gemma2:9b | 6GB | ◎ | ◎ | ★★☆ |
| qwen2.5:7b | 5GB | ◎ | ○ | ★☆☆ |

**プライマリ**: `gpt-oss-20b`

---

## 5. 実装仕様

### 5.1 環境変数 (.env)
```bash
OLLAMA_MODEL=gpt-oss-20b
OLLAMA_HOST=http://localhost:11434
SHEET_URL=https://docs.google.com/spreadsheets/d/xxxxx
CREDENTIALS_PATH=./credentials.json
```

### 5.2 コア実装

```python
import os
import random
import time
from dataclasses import dataclass

import gspread
import ollama
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials


@dataclass(frozen=True)
class Config:
    """不変の設定オブジェクト"""
    model: str
    host: str
    sheet_url: str
    credentials_path: str
    num_iterations: int = 100

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()
        return cls(
            model=os.getenv("OLLAMA_MODEL", "gpt-oss-20b"),
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            sheet_url=os.getenv("SHEET_URL", ""),
            credentials_path=os.getenv("CREDENTIALS_PATH", "./credentials.json"),
        )


class OllamaInference:
    """Ollama推論クライアント"""

    SYSTEM_PROMPT = (
        "人間の仕事を助ける優秀なAIアシスタントとして、"
        "指示に従い、必要な情報のみを端的に出力します。"
    )

    def __init__(self, config: Config):
        self.config = config
        self.client = ollama.Client(host=config.host, timeout=120)
        self._ensure_model_available()

    def _ensure_model_available(self) -> None:
        """モデルの存在確認、なければpull"""
        models = self.client.list()
        available = [m["name"] for m in models.get("models", [])]
        model_name = self.config.model

        if not any(model_name in name for name in available):
            print(f"Pulling model: {model_name}")
            self.client.pull(model_name)

    def generate(self, prompt: str, max_retries: int = 3) -> str:
        """リトライ付き推論"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    options={
                        "num_predict": 2048,
                        "temperature": 0.8,
                    }
                )
                return response["message"]["content"].strip()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                delay = 2 ** attempt
                print(f"Retry {attempt + 1}/{max_retries}: {e}")
                time.sleep(delay)

        raise RuntimeError("Unreachable")


class SheetsClient:
    """Google Sheets クライアント"""

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self, config: Config):
        creds = Credentials.from_service_account_file(
            config.credentials_path, scopes=self.SCOPES
        )
        gc = gspread.authorize(creds)
        self.spreadsheet = gc.open_by_url(config.sheet_url)

        # シート取得
        self.wants = self.spreadsheet.worksheet("Wants")
        self.ability = self.spreadsheet.worksheet("Ability")
        self.role = self.spreadsheet.worksheet("Role")
        self.gender = self.spreadsheet.worksheet("Gender")
        self.age = self.spreadsheet.worksheet("Age")
        self.species = self.spreadsheet.worksheet("Species")
        self.output = self.spreadsheet.worksheet("test")

    def get_random_attribute(self, sheet: gspread.Worksheet) -> str:
        """シートからランダムに値を取得"""
        values = sheet.col_values(1)[1:]  # ヘッダー除外
        return random.choice(values)

    def append_output(self, row: list) -> None:
        """結果を出力シートに追加"""
        self.output.append_row(row)

    def append_seed(self, sheet: gspread.Worksheet, value: str) -> None:
        """シードデータを追加"""
        sheet.append_row([value])
```

### 5.3 プロンプトテンプレート

```python
class Prompts:
    """Ollama最適化プロンプト"""

    @staticmethod
    def character_concept(physical: str, role: str, ability: str, wants: str) -> str:
        return f"""以下のキャラクター属性を、重要な要素を損なわないように要約し、英文1段落で出力してください。

## 属性
- 身体的特徴: {physical}
- 役割: {role}
- 能力: {ability}
- 願望: {wants}

## ルール
- 英語で出力
- 1段落のみ
- 説明や補足は不要

## 出力"""

    @staticmethod
    def name(concept: str) -> str:
        return f"""以下のキャラクター設定にふさわしい人名を1つ生成してください。

## キャラクター設定
{concept}

## ルール
- 名前のみを出力（説明不要）
- 英語表記
- 国籍・文化・架空言語の名前も可
- 1行のみ

## 出力例
Kain Astralion
Yuichi Aihara

## 出力"""

    @staticmethod
    def profile(concept: str) -> str:
        return f"""以下のキャラクター設定を日本語で説明してください。

## キャラクター設定
{concept}

## ルール
- 日本語で出力
- 性別不明・They の場合は「彼は」を使用
- 1段落のみ

## 出力例
彼はプリティーンのノンバイナリー半人半神で、デジタル栄養コンサルタントとして活動しています。

## 出力"""

    @staticmethod
    def catchphrase(concept: str) -> str:
        return f"""以下のキャラクターの意思を表す印象的な決め台詞を生成してください。

## キャラクター設定
{concept}

## ルール
- 日本語で出力
- キャラクターにふさわしい口調
- 一人称から始める
- 1文のみ

## 出力例
私は、歴史の断片を手に取り、宇宙の隅々に宿る感情を感じ取るよ。

## 出力"""

    @staticmethod
    def new_ability(concept: str) -> str:
        return f"""以下のキャラクターと対になるキャラクターが持つ特殊能力を1つ生成してください。

## 元キャラクター
{concept}

## ルール
- 英語で出力
- 能力名と説明を1文で
- 1つのみ

## 出力例
Has the ability to materialize memories: Can share past events with others.

## 出力"""

    @staticmethod
    def new_wants(concept: str) -> str:
        return f"""以下のキャラクターと対になるキャラクターの切実な願望を1つ生成してください。

## 元キャラクター
{concept}

## ルール
- 英語で出力
- "I want to..." の形式
- 1文のみ

## 出力例
I want to establish a new human settlement in space.

## 出力"""

    @staticmethod
    def new_role(concept: str) -> str:
        return f"""以下のキャラクターと対になるキャラクターのユニークな役割を1つ生成してください。

## 元キャラクター
{concept}

## ルール
- 英語で出力
- 役割名と説明
- 1つのみ

## 出力例
Swordsman. Skilled in the art of swordsmanship with a strong sense of duty.

## 出力"""
```

### 5.4 メイン処理

```python
def generate_image_prompt(concept: str) -> str:
    """画像プロンプト生成（固定テンプレート）"""
    subject = "The full-length character illustration from video games, likely from role-playing games(JRPG) or fighting games."
    angle = "A camera angle that captures the entire body evenly from waist height."
    pose = "Standing upright and looking straight ahead, his pose visually conveys role, personality, attitude, ability, cultural background and physical attractiveness."
    background = "white background."
    artstyle = "The art style combines delicate hand-drawn lines with exaggerated expressions influenced by Japanese manga and anime."

    return f"{subject} {angle} {pose} {background} {concept}, {artstyle}"


def main() -> None:
    config = Config.from_env()
    llm = OllamaInference(config)
    sheets = SheetsClient(config)

    print(f"Starting generation with model: {config.model}")
    print(f"Iterations: {config.num_iterations}")

    for i in range(config.num_iterations):
        print(f"\n[{i + 1}/{config.num_iterations}] Generating character...")

        # 属性取得
        age = sheets.get_random_attribute(sheets.age)
        gender = sheets.get_random_attribute(sheets.gender)
        species = sheets.get_random_attribute(sheets.species)
        physical = f"{age}{gender}{species}"
        ability = sheets.get_random_attribute(sheets.ability)
        wants = sheets.get_random_attribute(sheets.wants)
        role = sheets.get_random_attribute(sheets.role)

        # 推論
        concept = llm.generate(Prompts.character_concept(physical, role, ability, wants))
        name = llm.generate(Prompts.name(concept))
        profile = llm.generate(Prompts.profile(concept))
        catchphrase = llm.generate(Prompts.catchphrase(concept))
        image_prompt = generate_image_prompt(concept)

        # 出力
        row = [name, profile, catchphrase, image_prompt, concept, age, gender, species, ability, wants, role]
        sheets.append_output(row)

        # 対キャラの属性生成
        new_ability = llm.generate(Prompts.new_ability(concept))
        new_wants = llm.generate(Prompts.new_wants(concept))
        new_role = llm.generate(Prompts.new_role(concept))

        sheets.append_seed(sheets.ability, new_ability)
        sheets.append_seed(sheets.wants, new_wants)
        sheets.append_seed(sheets.role, new_role)

        print(f"  Name: {name}")

    print("\n処理が完了しました。")


if __name__ == "__main__":
    main()
```

---

## 6. エラーハンドリング

| エラー | 原因 | 対処 |
|--------|------|------|
| ConnectionError | Ollama未起動 | 起動確認メッセージ表示 |
| TimeoutError | 推論タイムアウト | 自動リトライ（最大3回） |
| ModelNotFound | モデル未DL | 自動pull |
| 認証エラー | credentials.json不正 | エラーメッセージで案内 |

---

## 7. セットアップ手順

### 7.1 Ollamaインストール（macOS）

```bash
brew install ollama
```

### 7.2 モデルダウンロード

```bash
# Ollamaサーバー起動（別ターミナルまたはバックグラウンド）
ollama serve

# モデルダウンロード（約12GB）
ollama pull gpt-oss-20b
```

**M4 MacBook Pro (128GB) の場合**:
- メモリ十分のため、フルモデル（gpt-oss-20b）推奨
- 量子化版（q4_K_M等）は不要

### 7.3 Google認証設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. Google Sheets API を有効化
3. サービスアカウント作成 → JSON キーをダウンロード
4. `credentials.json` として保存
5. スプレッドシートをサービスアカウントのメールアドレスに共有

### 7.4 実行

```bash
# 依存インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .env を編集してSHEET_URLを設定

# 実行
python ollama_hero_gen.py
```

---

## 8. パフォーマンス

### 8.1 推定処理時間（gpt-oss-20b）

**動作環境**: M4 MacBook Pro (128GB)

| 構成 | メモリ | 1キャラあたり | 100キャラ |
|------|--------|---------------|-----------|
| **M4 Pro/Max (128GB)** | 128GB | 10-15秒 | 17-25分 |

- Apple Silicon の統合メモリによりVRAM制限なし
- 128GBメモリで gpt-oss-20b を余裕で実行可能
- Metal GPUアクセラレーション対応

### 8.2 軽量化オプション（参考）

M4 MacBook Pro (128GB) では不要。他環境向け参考情報:

```bash
# 軽量モデル（6GB以下環境向け）
OLLAMA_MODEL=gemma2:9b

# 量子化版（12GB以下環境向け）
ollama pull gpt-oss-20b:q4_K_M
```

---

## 9. 実装フェーズ

### Phase 1: 基盤
- [ ] `ollama_hero_gen.py` 作成
- [ ] Config / OllamaInference / SheetsClient 実装
- [ ] エラーハンドリング実装

### Phase 2: 推論
- [ ] Prompts クラス実装
- [ ] メイン処理ループ実装
- [ ] 動作確認（1キャラ生成）

### Phase 3: テスト
- [ ] 10キャラ生成テスト
- [ ] 100キャラ完走確認
- [ ] 生成品質確認

### Phase 4: 完成
- [ ] README更新
- [ ] requirements.txt 整備
- [ ] .env.example 作成

---

## 改訂履歴

| Ver | 日付 | 変更 |
|-----|------|------|
| 1.0 | 2026-02-11 | 初版 |
| 1.1 | 2026-02-11 | ローカル実行特化版に改訂 |
