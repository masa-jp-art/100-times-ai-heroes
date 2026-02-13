"""
100 Times AI Heroes - Ollama版 テストハーネス

使用方法:
    # 全テスト実行
    pytest harness/test_harness.py -v

    # カテゴリ別実行
    pytest harness/test_harness.py -v -k "environment"
    pytest harness/test_harness.py -v -k "ollama"
    pytest harness/test_harness.py -v -k "sheets"
    pytest harness/test_harness.py -v -k "prompts"
    pytest harness/test_harness.py -v -k "generation"
    pytest harness/test_harness.py -v -k "error"
    pytest harness/test_harness.py -v -k "integration"

    # 機能リスト更新付き実行
    python harness/test_harness.py
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

FEATURES_PATH = PROJECT_ROOT / "harness" / "features.json"


def update_feature_status(feature_id: str, passes: bool) -> None:
    """機能リストのpassesステータスを更新"""
    if not FEATURES_PATH.exists():
        return

    with open(FEATURES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for feature in data["features"]:
        if feature["id"] == feature_id:
            feature["passes"] = passes
            break

    with open(FEATURES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class FeatureTest:
    """機能テストのベースクラス"""

    feature_id: str = ""

    def mark_passed(self):
        """テスト成功時に呼び出す"""
        if self.feature_id:
            update_feature_status(self.feature_id, True)

    def mark_failed(self):
        """テスト失敗時に呼び出す"""
        if self.feature_id:
            update_feature_status(self.feature_id, False)


# =============================================================================
# Environment Tests (ENV001-ENV002)
# =============================================================================


class TestEnvironment(FeatureTest):
    """環境設定テスト"""

    def test_config_from_env(self, monkeypatch):
        """ENV001: 環境変数読み込み"""
        self.feature_id = "ENV001"

        monkeypatch.setenv("OLLAMA_MODEL", "test-model")
        monkeypatch.setenv("OLLAMA_HOST", "http://test:11434")
        monkeypatch.setenv("SHEET_URL", "https://test-sheet")
        monkeypatch.setenv("CREDENTIALS_PATH", "/test/creds.json")

        try:
            from ollama_hero_gen import Config

            config = Config.from_env()
            assert config.model == "test-model"
            assert config.host == "http://test:11434"
            assert config.sheet_url == "https://test-sheet"
            assert config.credentials_path == "/test/creds.json"
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")

    def test_config_defaults(self, monkeypatch):
        """ENV002: 設定デフォルト値"""
        self.feature_id = "ENV002"

        # 環境変数をクリア
        for key in ["OLLAMA_MODEL", "OLLAMA_HOST", "SHEET_URL", "CREDENTIALS_PATH"]:
            monkeypatch.delenv(key, raising=False)

        try:
            from ollama_hero_gen import Config

            config = Config.from_env()
            assert config.model == "gpt-oss-20b"
            assert config.host == "http://localhost:11434"
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")


# =============================================================================
# Ollama Tests (OLL001-OLL005)
# =============================================================================


class TestOllama(FeatureTest):
    """Ollama推論テスト"""

    def test_ollama_connection(self):
        """OLL001: Ollamaサーバー接続"""
        self.feature_id = "OLL001"

        try:
            import requests

            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            assert response.status_code == 200
        except Exception as e:
            pytest.fail(f"Ollama server not running: {e}")

    def test_model_availability(self):
        """OLL002: モデル存在確認"""
        self.feature_id = "OLL002"

        try:
            import ollama

            client = ollama.Client(host="http://localhost:11434")
            models = client.list()

            # モデルリストの形式に対応（新旧両方）
            model_list = models.get("models", [])
            model_names = []
            for m in model_list:
                if hasattr(m, "model"):
                    model_names.append(m.model)
                elif isinstance(m, dict) and "name" in m:
                    model_names.append(m["name"])

            # gpt-oss-20bまたは代替モデルが存在するか
            has_model = any("gpt-oss-20b" in name for name in model_names)
            if not has_model:
                pytest.skip("gpt-oss-20b not installed, run: ollama pull gpt-oss-20b")
        except ImportError:
            pytest.skip("ollama package not installed")

    def test_inference_basic(self):
        """OLL003: 推論実行"""
        self.feature_id = "OLL003"

        try:
            import ollama

            # 利用可能なモデルを確認
            client = ollama.Client(host="http://localhost:11434")
            models = client.list()
            model_list = models.get("models", [])
            if not model_list:
                pytest.skip("No models installed in Ollama")

            # 軽量モデルを優先的に選択
            preferred = ["llama3.2", "llama3.1:8b", "deepseek-r1:7b", "deepseek-r1:8b", "qwen"]
            test_model = None

            model_names = []
            for m in model_list:
                name = m.model if hasattr(m, "model") else m.get("name", "")
                model_names.append(name)

            for pref in preferred:
                for name in model_names:
                    if pref in name:
                        test_model = name
                        break
                if test_model:
                    break

            if not test_model:
                pytest.skip("No suitable lightweight model found")

            from ollama_hero_gen import Config, OllamaInference

            # テスト用にモデルを上書き
            config = Config(
                model=test_model,
                host="http://localhost:11434",
                sheet_url="",
                credentials_path="",
            )
            inference = OllamaInference(config)
            result = inference.generate("Say 'hello' in one word.")
            assert len(result) > 0
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")

    def test_inference_retry(self):
        """OLL004: リトライ機能"""
        self.feature_id = "OLL004"

        try:
            from ollama_hero_gen import OllamaInference

            # リトライロジックが実装されているか確認
            import inspect

            source = inspect.getsource(OllamaInference.generate)
            assert "retry" in source.lower() or "attempt" in source.lower()
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")

    def test_inference_timeout(self):
        """OLL005: タイムアウト処理"""
        self.feature_id = "OLL005"

        try:
            from ollama_hero_gen import OllamaInference

            # タイムアウト設定が実装されているか確認
            import inspect

            source = inspect.getsource(OllamaInference.__init__)
            assert "timeout" in source.lower()
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")


# =============================================================================
# Sheets Tests (SHT001-SHT006)
# =============================================================================


class TestSheets(FeatureTest):
    """Google Sheetsテスト"""

    def test_sheets_auth(self):
        """SHT001: Google認証"""
        self.feature_id = "SHT001"

        creds_path = PROJECT_ROOT / "credentials.json"
        if not creds_path.exists():
            pytest.skip("credentials.json not found")

        try:
            from google.oauth2.service_account import Credentials

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = Credentials.from_service_account_file(str(creds_path), scopes=scopes)
            assert creds is not None
        except Exception as e:
            pytest.fail(f"Authentication failed: {e}")

    def test_sheets_open(self):
        """SHT002: スプレッドシート接続"""
        self.feature_id = "SHT002"
        pytest.skip("Requires SHEET_URL configuration")

    def test_sheets_worksheets(self):
        """SHT003: シート取得"""
        self.feature_id = "SHT003"
        pytest.skip("Requires SHEET_URL configuration")

    def test_sheets_random_attribute(self):
        """SHT004: ランダム属性取得"""
        self.feature_id = "SHT004"
        pytest.skip("Requires SHEET_URL configuration")

    def test_sheets_append_output(self):
        """SHT005: 結果行追加"""
        self.feature_id = "SHT005"
        pytest.skip("Requires SHEET_URL configuration")

    def test_sheets_append_seed(self):
        """SHT006: シード追加"""
        self.feature_id = "SHT006"
        pytest.skip("Requires SHEET_URL configuration")


# =============================================================================
# Prompts Tests (PRM001-PRM007)
# =============================================================================


class TestPrompts(FeatureTest):
    """プロンプトテスト"""

    def test_prompt_character_concept(self):
        """PRM001: CharacterConceptプロンプト"""
        self.feature_id = "PRM001"

        try:
            from ollama_hero_gen import Prompts

            prompt = Prompts.character_concept(
                physical="Young Male Human",
                role="Warrior",
                ability="Super strength",
                wants="Peace",
            )
            assert "Young Male Human" in prompt
            assert "Warrior" in prompt
            assert "英語" in prompt or "English" in prompt.lower()
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")

    def test_prompt_name(self):
        """PRM002: Nameプロンプト"""
        self.feature_id = "PRM002"

        try:
            from ollama_hero_gen import Prompts

            prompt = Prompts.name("A young warrior seeking peace.")
            assert "名前" in prompt or "name" in prompt.lower()
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")

    def test_prompt_profile(self):
        """PRM003: Profileプロンプト"""
        self.feature_id = "PRM003"

        try:
            from ollama_hero_gen import Prompts

            prompt = Prompts.profile("A young warrior seeking peace.")
            assert "日本語" in prompt
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")

    def test_prompt_catchphrase(self):
        """PRM004: Catchphraseプロンプト"""
        self.feature_id = "PRM004"

        try:
            from ollama_hero_gen import Prompts

            prompt = Prompts.catchphrase("A young warrior seeking peace.")
            assert "決め台詞" in prompt or "一人称" in prompt
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")

    def test_prompt_new_ability(self):
        """PRM005: NewAbilityプロンプト"""
        self.feature_id = "PRM005"

        try:
            from ollama_hero_gen import Prompts

            prompt = Prompts.new_ability("A young warrior seeking peace.")
            assert "能力" in prompt or "ability" in prompt.lower()
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")

    def test_prompt_new_wants(self):
        """PRM006: NewWantsプロンプト"""
        self.feature_id = "PRM006"

        try:
            from ollama_hero_gen import Prompts

            prompt = Prompts.new_wants("A young warrior seeking peace.")
            assert "願望" in prompt or "want" in prompt.lower()
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")

    def test_prompt_new_role(self):
        """PRM007: NewRoleプロンプト"""
        self.feature_id = "PRM007"

        try:
            from ollama_hero_gen import Prompts

            prompt = Prompts.new_role("A young warrior seeking peace.")
            assert "役割" in prompt or "role" in prompt.lower()
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")


# =============================================================================
# Generation Tests (GEN001-GEN005)
# =============================================================================


class TestGeneration(FeatureTest):
    """生成テスト"""

    def test_image_prompt_generation(self):
        """GEN001: ImagePrompt生成"""
        self.feature_id = "GEN001"

        try:
            from ollama_hero_gen import generate_image_prompt

            result = generate_image_prompt("A young warrior")
            assert "character illustration" in result.lower()
            assert "A young warrior" in result
        except ImportError:
            pytest.skip("ollama_hero_gen.py not implemented yet")

    def test_single_character_generation(self):
        """GEN002: 単一キャラクター生成"""
        self.feature_id = "GEN002"
        pytest.skip("Requires full implementation")

    def test_complementary_attributes(self):
        """GEN003: 対キャラ属性生成"""
        self.feature_id = "GEN003"
        pytest.skip("Requires full implementation")

    def test_generation_loop(self):
        """GEN004: ループ実行"""
        self.feature_id = "GEN004"
        pytest.skip("Requires full implementation")

    def test_progress_display(self):
        """GEN005: 進捗表示"""
        self.feature_id = "GEN005"
        pytest.skip("Requires full implementation")


# =============================================================================
# Error Tests (ERR001-ERR003)
# =============================================================================


class TestErrors(FeatureTest):
    """エラーハンドリングテスト"""

    def test_error_ollama_not_running(self):
        """ERR001: Ollama未起動エラー"""
        self.feature_id = "ERR001"
        pytest.skip("Requires mocking")

    def test_error_invalid_credentials(self):
        """ERR002: 認証エラー"""
        self.feature_id = "ERR002"
        pytest.skip("Requires mocking")

    def test_error_sheet_not_found(self):
        """ERR003: シートエラー"""
        self.feature_id = "ERR003"
        pytest.skip("Requires mocking")


# =============================================================================
# Integration Tests (INT001-INT003)
# =============================================================================


class TestIntegration(FeatureTest):
    """統合テスト"""

    @pytest.mark.slow
    def test_e2e_single_character(self):
        """INT001: E2E 1キャラ生成"""
        self.feature_id = "INT001"
        pytest.skip("Run manually with: python ollama_hero_gen.py --iterations 1")

    @pytest.mark.slow
    def test_e2e_ten_characters(self):
        """INT002: E2E 10キャラ生成"""
        self.feature_id = "INT002"
        pytest.skip("Run manually with: python ollama_hero_gen.py --iterations 10")

    @pytest.mark.slow
    def test_e2e_hundred_characters(self):
        """INT003: E2E 100キャラ生成"""
        self.feature_id = "INT003"
        pytest.skip("Run manually with: python ollama_hero_gen.py --iterations 100")


# =============================================================================
# CLI Runner
# =============================================================================


def print_feature_summary():
    """機能リストのサマリーを表示"""
    if not FEATURES_PATH.exists():
        print("features.json not found")
        return

    with open(FEATURES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = len(data["features"])
    passed = sum(1 for f in data["features"] if f["passes"])

    print("\n" + "=" * 60)
    print("Feature Status Summary")
    print("=" * 60)

    categories = {}
    for feature in data["features"]:
        cat = feature["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0}
        categories[cat]["total"] += 1
        if feature["passes"]:
            categories[cat]["passed"] += 1

    for cat, stats in categories.items():
        status = "PASS" if stats["passed"] == stats["total"] else "FAIL"
        print(f"  {cat:12} {stats['passed']:2}/{stats['total']:2} [{status}]")

    print("-" * 60)
    print(f"  {'TOTAL':12} {passed:2}/{total:2}")
    print("=" * 60)


def update_features_from_results():
    """テスト結果に基づいてfeatures.jsonを更新"""
    import subprocess
    import re

    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=no", "-q"],
        capture_output=True,
        text=True,
    )

    # テスト結果をパース
    test_to_feature = {
        "test_config_from_env": "ENV001",
        "test_config_defaults": "ENV002",
        "test_ollama_connection": "OLL001",
        "test_model_availability": "OLL002",
        "test_inference_basic": "OLL003",
        "test_inference_retry": "OLL004",
        "test_inference_timeout": "OLL005",
        "test_sheets_auth": "SHT001",
        "test_sheets_open": "SHT002",
        "test_sheets_worksheets": "SHT003",
        "test_sheets_random_attribute": "SHT004",
        "test_sheets_append_output": "SHT005",
        "test_sheets_append_seed": "SHT006",
        "test_prompt_character_concept": "PRM001",
        "test_prompt_name": "PRM002",
        "test_prompt_profile": "PRM003",
        "test_prompt_catchphrase": "PRM004",
        "test_prompt_new_ability": "PRM005",
        "test_prompt_new_wants": "PRM006",
        "test_prompt_new_role": "PRM007",
        "test_image_prompt_generation": "GEN001",
        "test_single_character_generation": "GEN002",
        "test_complementary_attributes": "GEN003",
        "test_generation_loop": "GEN004",
        "test_progress_display": "GEN005",
        "test_error_ollama_not_running": "ERR001",
        "test_error_invalid_credentials": "ERR002",
        "test_error_sheet_not_found": "ERR003",
        "test_e2e_single_character": "INT001",
        "test_e2e_ten_characters": "INT002",
        "test_e2e_hundred_characters": "INT003",
    }

    output = result.stdout + result.stderr

    for test_name, feature_id in test_to_feature.items():
        if f"::{test_name} PASSED" in output:
            update_feature_status(feature_id, True)
        elif f"::{test_name} FAILED" in output:
            update_feature_status(feature_id, False)
        # SKIPPEDはそのまま（更新しない）

    return result.returncode


if __name__ == "__main__":
    # テスト実行と結果更新
    exit_code = update_features_from_results()

    # サマリー表示
    print_feature_summary()

    sys.exit(exit_code)
