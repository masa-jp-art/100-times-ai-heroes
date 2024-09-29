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