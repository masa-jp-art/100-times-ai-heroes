# 100 TIMES AI HEROES - Demo Website

このディレクトリには、「100 TIMES AI HEROES」プロジェクトのHTMLデモが含まれています。

## 📁 ファイル構成

```
demo/
├── index.html          # ホームページ
├── gallery.html        # ギャラリーページ
├── character.html      # キャラクター詳細ページ
├── generate.html       # キャラクター生成ページ
├── concept.html        # コンセプト説明ページ
├── workflow.html       # ワークフロー説明ページ
├── css/
│   └── style.css      # メインスタイルシート
├── js/
│   └── main.js        # JavaScript機能
└── images/            # 画像ディレクトリ（今後追加予定）
```

## 🚀 使い方

### ローカルで表示する方法

#### 方法1: シンプルなHTTPサーバー

Pythonがインストールされている場合:

```bash
cd demo
python3 -m http.server 8000
```

ブラウザで `http://localhost:8000` にアクセス

#### 方法2: Node.jsのhttp-server

```bash
cd demo
npx http-server -p 8000
```

#### 方法3: VS Code Live Server

VS Codeの拡張機能「Live Server」をインストールし、`index.html`を右クリックして「Open with Live Server」を選択

### ブラウザで直接開く

`index.html`をダブルクリックして、ブラウザで直接開くこともできます。

## 🎨 機能

### 実装済み機能

- ✅ **ホームページ**: プロジェクト紹介とYouTube動画埋め込み
- ✅ **ギャラリーページ**: 6つのサンプルキャラクターをグリッド表示
- ✅ **キャラクター詳細**: 個別キャラクターの詳細情報表示
- ✅ **生成シミュレーション**: キャラクター生成のデモ（3秒でシミュレート）
- ✅ **コンセプトページ**: プロジェクトの背景と哲学
- ✅ **ワークフローページ**: Mermaidダイアグラムによるプロセス可視化
- ✅ **レスポンシブデザイン**: モバイル対応
- ✅ **サイバーパンク風UI**: ネオングロー、グラスモーフィズム効果

### デモ版の制限

- 🔸 キャラクター画像は絵文字アイコンで代用
- 🔸 実際のAPI呼び出しなし（シミュレーション）
- 🔸 6キャラクターのみ表示（本番は100キャラクター）
- 🔸 データベース接続なし（JavaScript配列でモックデータ）

## 🎯 ページ別機能

### 1. ホームページ (index.html)
- プロジェクトの概要
- 主要機能の紹介
- YouTube動画ギャラリー（v1.0, v1.1, v1.2）
- CTAボタン

### 2. ギャラリー (gallery.html)
- キャラクターグリッド表示
- フィルターボタン（種族別）
- キャラクードカードホバーエフェクト
- キャラクター詳細へのリンク

### 3. キャラクター詳細 (character.html)
- 大きなキャラクター表示
- プロフィール情報
- 属性（年齢、性別、種族、役割）
- 特殊能力と願望
- ソーシャルシェアボタン

### 4. 生成ページ (generate.html)
- 生成オプション選択（年齢、性別、種族）
- ローディングアニメーション
- 生成結果表示
- 再生成機能

### 5. コンセプト (concept.html)
- プロジェクトの哲学
- AIと人間の創造性についての考察
- 受賞情報
- 技術的アプローチ

### 6. ワークフロー (workflow.html)
- Mermaidによるフローチャート
- 8ステップの詳細説明
- 主要技術の解説

## 🎨 デザイン要素

### カラースキーム
- **Primary**: `#00f0ff` (サイバーブルー)
- **Secondary**: `#ff00ff` (ネオンピンク)
- **Accent**: `#ffff00` (ネオンイエロー)
- **Background**: `#0a0a0f` (ダークブルー)
- **Card**: `#1a1a2e` (カードバックグラウンド)

### エフェクト
- ネオングロー
- グラスモーフィズム
- ホバーアニメーション
- グラデーションテキスト
- ローディングスピナー

## 🔧 カスタマイズ

### キャラクターデータの追加

`js/main.js`の`characters`配列に新しいキャラクターを追加:

```javascript
{
  id: 7,
  name: "New Character",
  role: "Role Name",
  profile: "Profile text...",
  seriff: "Quote...",
  age: "Young Adult",
  gender: "Male",
  species: "Human",
  ability: "Special ability",
  wants: "Character goal",
  icon: "🎭"
}
```

### スタイルの変更

`css/style.css`の`:root`セクションでカラー変数を変更:

```css
:root {
  --primary: #your-color;
  --secondary: #your-color;
  /* ... */
}
```

## 📱 対応ブラウザ

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🚀 次のステップ（本番実装）

このデモを本番環境に移行する場合:

1. **フレームワーク移行**: Next.js/React への移行
2. **バックエンド実装**: API Routes、データベース接続
3. **AI統合**: OpenAI API、DALL-E 3
4. **画像管理**: 実際のキャラクター画像の保存と表示
5. **認証**: ユーザーアカウント機能
6. **デプロイ**: Vercel/Netlifyへのデプロイ

詳細は親ディレクトリの `WEB_DEPLOYMENT_PLAN.md` を参照してください。

## 📝 ライセンス

このデモは「100 TIMES AI HEROES」プロジェクトの一部です。

---

**作成者**: Claude (AI Assistant)
**プロジェクト**: 100 TIMES AI HEROES
**受賞**: 第3回AIアートグランプリ 審査委員特別賞
