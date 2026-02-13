"""
100 Times AI Heroes - Ollama版キャラクター生成システム

Usage:
    python ollama_hero_gen.py
    python ollama_hero_gen.py --iterations 10
"""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from typing import Optional

import gspread
import ollama
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials


# =============================================================================
# Configuration
# =============================================================================


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


# =============================================================================
# Ollama Inference
# =============================================================================


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
        try:
            models = self.client.list()
            model_list = models.get("models", [])

            # モデルリストの形式に対応（新旧両方）
            available = []
            for m in model_list:
                if hasattr(m, "model"):
                    available.append(m.model)
                elif isinstance(m, dict) and "name" in m:
                    available.append(m["name"])

            model_name = self.config.model

            if not any(model_name in name for name in available):
                print(f"Pulling model: {model_name}")
                self.client.pull(model_name)
        except Exception as e:
            raise ConnectionError(
                f"Ollama server not running at {self.config.host}. "
                f"Start with: ollama serve"
            ) from e

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
                    },
                )
                return response["message"]["content"].strip()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                delay = 2**attempt
                print(f"Retry {attempt + 1}/{max_retries}: {e}")
                time.sleep(delay)

        raise RuntimeError("Unreachable")


# =============================================================================
# Google Sheets Client
# =============================================================================


class SheetsClient:
    """Google Sheets クライアント"""

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self, config: Config):
        if not os.path.exists(config.credentials_path):
            raise FileNotFoundError(
                f"Credentials file not found: {config.credentials_path}\n"
                "See docs/DESIGN_SPEC_OLLAMA.md section 7.3 for setup."
            )

        creds = Credentials.from_service_account_file(
            config.credentials_path, scopes=self.SCOPES
        )
        gc = gspread.authorize(creds)

        if not config.sheet_url:
            raise ValueError("SHEET_URL not configured in .env")

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


# =============================================================================
# Prompts
# =============================================================================


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


# =============================================================================
# Image Prompt Generation
# =============================================================================


def generate_image_prompt(concept: str) -> str:
    """画像プロンプト生成（固定テンプレート）"""
    subject = (
        "The full-length character illustration from video games, "
        "likely from role-playing games(JRPG) or fighting games."
    )
    angle = "A camera angle that captures the entire body evenly from waist height."
    pose = (
        "Standing upright and looking straight ahead, his pose visually conveys "
        "role, personality, attitude, ability, cultural background and physical attractiveness."
    )
    background = "white background."
    artstyle = (
        "The art style combines delicate hand-drawn lines with exaggerated "
        "expressions influenced by Japanese manga and anime."
    )

    return f"{subject} {angle} {pose} {background} {concept}, {artstyle}"


# =============================================================================
# Main
# =============================================================================


def main(iterations: Optional[int] = None) -> None:
    config = Config.from_env()

    if iterations is not None:
        config = Config(
            model=config.model,
            host=config.host,
            sheet_url=config.sheet_url,
            credentials_path=config.credentials_path,
            num_iterations=iterations,
        )

    print(f"Starting generation with model: {config.model}")
    print(f"Iterations: {config.num_iterations}")

    llm = OllamaInference(config)
    sheets = SheetsClient(config)

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
        row = [
            name,
            profile,
            catchphrase,
            image_prompt,
            concept,
            age,
            gender,
            species,
            ability,
            wants,
            role,
        ]
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
    import argparse

    parser = argparse.ArgumentParser(description="100 Times AI Heroes - Ollama版")
    parser.add_argument(
        "--iterations", "-n", type=int, default=None, help="生成するキャラクター数"
    )
    args = parser.parse_args()

    main(iterations=args.iterations)
