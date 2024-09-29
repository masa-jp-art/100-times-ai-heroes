# Google Colabで実行するためのコードです

!pip install gspread oauth2client openai==0.28 google-auth google-auth-oauthlib google-auth-httplib2 pandas --upgrade

import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import openai
import pandas as pd
from google.colab import auth
from google.auth import default
import os
import json

# Google認証
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)
# スプレッドシートとシートを開く
sheet_url = '<https://docs.google.com/spreadsheets/d/1kEezsKrw0PyAtu1nsfrJbYzHRzVGP5eXqDknDNYhU4g/>'
spreadsheet = gc.open_by_url(sheet_url)

# 各シートを取得
sheet_wants = spreadsheet.worksheet('Wants')
sheet_ability = spreadsheet.worksheet('Ability')
sheet_role = spreadsheet.worksheet('Role')
sheet_gender = spreadsheet.worksheet('Gender')
sheet_age = spreadsheet.worksheet('Age')
sheet_species = spreadsheet.worksheet('Species')
sheet_test = spreadsheet.worksheet('test')

openai.api_key = "<your_openai_api_key>"

def gpt(s):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        max_tokens=2048,
        messages=[
            {"role": "system", "content": "人間の仕事を助ける優秀なAIアシスタントとして、指示に従い、必要な情報のみを端的に出力します。"},
            {"role": "user", "content": s},
        ]
    )
    return response["choices"][0]["message"]["content"]

# 処理をn回繰り返す

for _ in range(100):

    # シートからランダムに値を取得
    Age = random.choice(sheet_age.col_values(1)[1:])  # ヘッダーを除外
    Gender = random.choice(sheet_gender.col_values(1)[1:])
    Species = random.choice(sheet_species.col_values(1)[1:])
    PhysicalCharacteristics = f"{Age}{Gender}{Species}"
    Ability = random.choice(sheet_ability.col_values(1)[1:])
    Wants = random.choice(sheet_wants.col_values(1)[1:])
    Role = random.choice(sheet_role.col_values(1)[1:])

    # CharacterConceptを生成
    CharacterConcept = gpt(f"""
    下記のテキストを、重要な要素を損なわないように要約し、英文で出力します 
    \nCharacteristics {PhysicalCharacteristics}, 
    \nRole: {Role}, 
    \nAbility: {Ability}, 
    \nWants: {Wants}.
    """
    )

    # ImagePromptを生成
    Subject = "The full-length character illustration from video games, likely from role-playiggames(JRPG) or fighting games."
    Angle = "A camera angle that captures the entire body evenly from waist height. "
    Pose = "Standing upright and looking straight ahead, his pose visually conveys role, personality, attitude, ability, cultural background and physical attractiveness, and acts as a condensed visual narrative of presence and meaning."
    Background = "white background."
    Artstyle = "The art style combines delicate hand-drawn lines and attention to detail with exaggerated expressions influenced by Japanese manga and anime. It employs a wide range of colors while maintaining realistic proportions and textures. It uses shading to create a sense of volume and depth, emphasizing the sophisticated haute couture fashion and edgy character design. The clever combination of classic vibes and contemporary pop culture elements creates a unique visual identity with a focus on individuality."
    ImagePrompt = f"{Subject}{Angle}{Pose}{Background}{CharacterConcept},{Artstyle}"

    # 名前、プロフィール、セリフを生成
    Name = gpt(f"""
    下記のテキストから連想される人名をひとつ英語で出力します: {CharacterConcept}
    \n
    \n### 制約事項：人名は英語名に制限されず、さまざまな国籍、文化、また架空の言語体系による命名が可能です
    \n
    \n###出力例
    \nKain Astralion
    \nYuichi Aihara
    \nSayuki Mizuki
    """)

    Profile = gpt(f"""
    下記のテキストを日本語で出力します: {CharacterConcept}
    \n
    \n### 制約事項：性別が不明な場合や、Theyを訳する場合、日本語訳の二人称表現は「彼は」とし、単数表現のみ使用できます
    \n
    \n###出力例
    \n彼はプリティーンのノンバイナリー半人半神で、デジタル栄養コンサルタントとして活動しています。情報科学や心理学の専門知識を持つ分析的かつ共感力に富んだ存在で、圧倒的なデジタルコンテンツの中から健康的な情報ダイエットをサポートします。量子もつれを操る能力を駆使し、瞬時の情報交換や量子暗号通信を実現し、優しさあふれる世界を目指しています。
    \n彼女は、中年の半人半水生女性ダンサーで、その流れるような動きで感情と思い出を表現します。リズムに対する深い理解を持ち、独自の能力で因果関係を逆転させることも可能です。彼女たちは、共同のユートピアを具現化するために、人類の集合的な意識にアクセスしようと奮闘しており、その魅力は美しさと力強さ、さらに人間の可能性を探求する情熱に満ちています。
    \n彼は中年男性のライカンスロープで、生きたタトゥーを創るバイオテクノロジータトゥーアーティストです。彼の肌は感情を色として吸収し、独自に表現する能力を持ち、個人や群衆の感情を操ることができます。最終的な夢は、真実で永遠の愛を見つけることです。彼らの独自の技術と感受性は、感情を視覚的に表現し、人々をつなげる魅力を持っています。
    """)

    Seriff = gpt(f"""
    下記のテキストを抽象的に解釈して、キャラクターの意思を表す印象的な決め台詞を、日本語で出力します: {CharacterConcept}
    \n
    \n### 制約事項
    \nセリフは、このキャラクターに相応しい口調で表現します
    \nセリフは、一人称から始まります
    \nセリフは、一文のみ出力できます
    \n
    \n###出力例
    \n私は、歴史の断片を手に取り、宇宙の隅々に宿る感情を感じ取るよ。
    \n私の心は、量子の重ね合わせの中でこそ解放されるんだ。
    \n人間と自然、どちらも大切にしたい。それが私の戦いだ。
    """)

    # sheet_testに新しい行を追加
    new_row = [Name, Profile, Seriff, ImagePrompt, CharacterConcept, Age, Gender, Species, Ability, Wants, Role, ]
    sheet_test.append_row(new_row)

    # 新しいAbility,Wants,Rollを追加

    NewAbility = gpt(f"""下記の特徴を持つキャラクターと対になるキャラクターの持っている特殊な能力をひとつ英語で出力します: {CharacterConcept}
    \n
    \n### 出力例：
    \nHas the ability to materialize memories: Can share past events with others or preserve them as evidence.
    \nPossesses a voice that can materialize words: Can generate spoken words as tangible objects, manipulating or utilizing them.
    \nHas the ability to materialize memories: Can share past events with others or preserve them as evidence.
    """)

    NewWants = gpt(f"""下記の特徴を持つキャラクターと対になるキャラクターの切実な願望をひとつ英語で出力します: {CharacterConcept}
    \n
    \n### 出力例：
    \nI want to establish a new human settlement in space.
    \nI want to live free from existing frameworks, guided only by my own beliefs.
    \nI want to devote everything to the human woman I've fallen in love with.
    """)

    NewRole = gpt(f"""下記の特徴を持つキャラクターと対になるキャラクターが担っているユニークな役割をひとつ英語で出力します: {CharacterConcept}
    \n
    \n### 出力例：
    \nSwordsman. Skilled in the art of swordsmanship expected to uphold a code of honor Often stoic and disciplined with a strong sense of duty
    \nNostalgic Experience Designer. Creators of immersive experiences that recreate past eras or personal memories Creative and empathetic with a deep understanding of psychology and sensory design
    \nDigital Nutrition Consultant. Specialists helping individuals maintain a healthy information diet in the age of overwhelming digital content Analytical and empathetic with expertise in information science psychology and digital wellness
    """)

    def append_row(sheet, value):
      sheet.append_row([value])
       
    append_row(sheet_wants, NewWants)
    append_row(sheet_ability, NewAbility)
    append_row(sheet_role, NewRole)



print("処理が完了しました。")