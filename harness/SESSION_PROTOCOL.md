# セッション開始プロトコル

このドキュメントは、各開発セッション開始時に実行すべき手順を定義します。

## セッション開始チェックリスト

### 1. 環境確認
```bash
# 作業ディレクトリ確認
pwd

# Ollamaサーバー確認
curl -s http://localhost:11434/api/tags | head -5
```

### 2. 状態確認
```bash
# Gitステータス確認
git status

# 最近のコミット確認
git log --oneline -5

# 進捗ファイル確認
cat harness/claude-progress.txt
```

### 3. 機能リスト確認
```bash
# 機能サマリー表示
python -c "
import json
with open('harness/features.json') as f:
    data = json.load(f)
total = len(data['features'])
passed = sum(1 for f in data['features'] if f['passes'])
print(f'Progress: {passed}/{total} features passing')
"
```

### 4. 次のタスク選定

機能リストから `"passes": false` の機能を1つ選び、そのテストをパスさせることに集中する。

**優先順位**:
1. environment (ENV001-ENV002) - 基盤
2. ollama (OLL001-OLL005) - 推論
3. prompts (PRM001-PRM007) - プロンプト
4. sheets (SHT001-SHT006) - データ連携
5. generation (GEN001-GEN005) - 生成ロジック
6. error (ERR001-ERR003) - エラー処理
7. integration (INT001-INT003) - 統合テスト

## セッション中のルール

### DO (やるべきこと)
- 一度に1機能のみに集中する
- テストをパスさせてから次へ進む
- 各機能完了時にGitコミットする
- `claude-progress.txt` を更新する
- `features.json` の passes を更新する

### DON'T (やってはいけないこと)
- 複数機能を同時に実装しない
- テスト未通過で次に進まない
- コミットなしで長時間作業しない
- 過度に複雑な実装をしない

## セッション終了チェックリスト

### 1. 変更をコミット
```bash
git add -A
git commit -m "feat: <完了した機能の説明>"
```

### 2. 進捗ファイル更新
`harness/claude-progress.txt` に以下を追記:
- 完了したタスク
- 作成/変更したファイル
- 次のセッションでやること
- メモ

### 3. 機能リスト更新
テストを実行して `features.json` を更新:
```bash
python harness/test_harness.py
```

## クイックリファレンス

### ファイル構成
```
harness/
├── features.json        # 機能リスト（31機能）
├── claude-progress.txt  # 進捗ログ
├── init.sh             # 初期化スクリプト
├── test_harness.py     # テストハーネス
└── SESSION_PROTOCOL.md # 本ドキュメント
```

### テスト実行
```bash
# 全テスト
pytest harness/test_harness.py -v

# カテゴリ別
pytest harness/test_harness.py -v -k "environment"
pytest harness/test_harness.py -v -k "ollama"

# 機能リスト更新付き
python harness/test_harness.py
```

### 実装ファイル
```
ollama_hero_gen.py  # メインスクリプト（単一ファイル）
```

## トラブルシューティング

### Ollamaが起動しない
```bash
ollama serve
```

### モデルがない
```bash
ollama pull gpt-oss-20b
```

### テストがスキップされる
`ollama_hero_gen.py` が未実装の場合、多くのテストがスキップされます。
実装を進めることでテストが有効になります。
