# Claude Code Instructions

## プロジェクト概要
100 Times AI Heroes - Ollama版キャラクター生成システム

## セッション開始時の必須タスク

**毎セッション開始時に以下を実行すること:**

1. **DEV_LOG.mdを読む** - 前回の作業内容と「次回TODO」を確認
2. `git log --oneline -5` で最近のコミット確認
3. `git status` で現在の状態確認
4. 「次回TODO」の内容をユーザーに報告し、作業を開始

### セッション開始時の報告テンプレート
```
前回の作業: [DEV_LOG.mdから要約]
次回TODO:
- [ ] タスク1
- [ ] タスク2

上記の作業を続けますか？
```

## 開発ルール

### 一度に1機能のみ
- features.json から `"passes": false` の機能を1つ選ぶ
- その機能のテストをパスさせることだけに集中
- パスしたら次の機能へ

### テスト駆動
```bash
# テスト実行
pytest harness/test_harness.py -v -k "<category>"

# 機能リスト自動更新
python harness/test_harness.py
```

### コミット粒度
- 1機能完了 = 1コミット
- コミットメッセージ: `feat: <機能ID> <説明>`

## ファイル構成

```
ollama_hero_gen.py      # メイン実装（単一ファイル）
harness/
├── features.json       # 機能リスト（passes を更新）
├── claude-progress.txt # 進捗ログ（セッション終了時に追記）
├── test_harness.py     # テストハーネス
├── init.sh            # 環境初期化
└── SESSION_PROTOCOL.md # 詳細プロトコル
```

## 技術スタック
- Python 3.10+
- Ollama (gpt-oss-20b)
- Google Sheets API (サービスアカウント認証)
- M4 MacBook Pro (128GB)

## 設計仕様
詳細は `docs/DESIGN_SPEC_OLLAMA.md` を参照

## 開発ログ（必須）

**DEV_LOG.md はGitHubに同期されないローカル専用ログです。**

### セッション中の更新タイミング
以下のタイミングで必ず DEV_LOG.md を更新すること:

1. **作業開始時**: 日付と作業内容の見出しを追加
2. **コミット時**: コミット内容を記録
3. **重要な変更時**: 設定変更、バグ修正、機能追加など
4. **問題発生時**: エラー、コンフリクト、解決方法
5. **セッション終了時**: 作業サマリーと次回のTODO

### ログ形式
```markdown
## YYYY-MM-DD

### [作業内容]
- 変更点1
- 変更点2

### コミット
- `abc1234` feat: 説明

### 問題と解決
- 問題: xxx
- 解決: yyy

### 次回TODO
- [ ] タスク1
```
