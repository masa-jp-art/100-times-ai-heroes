# 100 TIMES AI HEROES
![20240915-100-TIMES-AI-HEROES-v1 0-1920](https://github.com/user-attachments/assets/4bedc96b-0139-4838-8fe9-251ddee41220)
- 3rd AI Art Grand Prix Entry Art-Works

## Concept
In this artwork, "100 TIMES AI HEROES," I broke down the thought flow and work process I use when creating characters in my own manga and reproduced it using generative AI, accelerating the speed at which characters are created.
It is expected that by utilizing the capabilities of generative AI, I can improve the productivity of character creation and enable manga production that focuses more on my own artistic creativity.
However, at the same time, I also realized that even the reflection of my own artistic creativity might be replaced by generative AI. If generative AI could autonomously create characters and stories, humans might only be left with the role of appreciating them.
And perhaps that function could be replaced someday.
Through our exploration of creation using generative AI, we must continue to look at the significance, meaning, and fundamental desire of human creation.

この作品「100 TIMES AI HEROES」では、私自身のマンガ制作におけるキャラクター創出の際の思考フローと作業プロセスを分解し、生成AIを用いて再現することで、キャラクターが生み出されるスピードを加速させました。
生成AIの能力を活かして、キャラクター創出の生産性を向上し、より私自身の作家性にフォーカスしたマンガ制作を可能にすることが期待されます。
しかし一方で、私自身の作家性の反映すら、生成AIに代替できてしまうのではないか？という気づきもありました。キャラクターやストーリーを生成AIが自律的に創作することができたら、人間には鑑賞する役割しか残らないかもしれません。
そしてそれも、いつか代替されうる機能ではないでしょうか。
私たちは、生成AIによる創作の探求を通じて、人間が創作することの意義、意味、その根源たる欲求を見つめ続けなければならないでしょう。

## v1.1 Generated images
![AI-Art-GP-3-generated-images-v1 1](https://github.com/user-attachments/assets/217688a2-952b-4f6f-8d36-607a40ad7afe)

## Concept & Gallery page
- https://portfolio.foti.jp/100-times-ai-heroes

## Concept Video (Japanese)
- https://youtu.be/_2SVlF7QJnQ

## Code
- https://github.com/masa-jp-art/100-times-ai-heroes/blob/main/20240916-AI-Art-GP-3-Charactor.py
- Spread Sheet 20240915 snapshot
  - https://docs.google.com/spreadsheets/d/1cxKgkkW2GjupXP1B1Hp5QgcfJg5_DXzbyBiqQE7EFpk/edit?usp=sharing
 
## Workflow
```mermaid
flowchart LR
	Human((Human)) --> SeedsSheet[(Seeds Sheet)] 
	SeedsSheet --> |t2t-Few-Shot| SeedsSheet
	Human --> WantsSheet[(Wants Sheet)] 
	WantsSheet --> |t2t-Few-Shot| WantsSheet
	Human --> GenderSheet[(Gender Sheet)] 
	Human --> AgeSheet[(Age Sheet)] 
	Human --> SpeciesSheet[(Species Sheet)] 
	ReferenceImage -->|i2t| Subject
	ReferenceImage -->|i2t| Angle
	ReferenceImage -->|i2t| Pose
	ReferenceImage -->|i2t| Background
	ReferenceImage -->|i2t| ArtStyle 
	ReferenceImage -->|i2t| 1[Role] 
	1 --> RoleSheet[(Role Sheet)] 
	RoleSheet --> |t2t-Few-Shot| RoleSheet
	GenderSheet -->|RAG| PhysicalCharacteristics 
	AgeSheet -->|RAG| PhysicalCharacteristics 
	SpeciesSheet -->|RAG| PhysicalCharacteristics 
	SeedsSheet -->|RAG| Seeds 
	WantsSheet -->|RAG| Wants 
	RoleSheet -->|RAG| Role 
	BasePrompt -->|t2t| ImagePrompt
	Seeds --> CharacterPrompt
	Wants -->CharacterPrompt
	Role --> CharacterPrompt
	PhysicalCharacteristics --> CharacterPrompt
	CharacterPrompt -->|t2t| ImagePrompt
	Subject -->|t2t| ImagePrompt
	Angle -->|t2t| ImagePrompt
	Pose -->|t2t| ImagePrompt
	Background -->|t2t| ImagePrompt
	ArtStyle -->|t2t| ImagePrompt
	ImagePrompt -->|t2i| Image
	CharacterPrompt -->|t2t| Name
  CharacterPrompt -->|t2t| Profile
	CharacterPrompt -->|t2t| Seriff
	Image --> Artwork
	Human --> Artwork
	Artwork --> Character
	Image --> Character
	Name --> Character
	Profile --> Character
	Seriff --> Character
```
