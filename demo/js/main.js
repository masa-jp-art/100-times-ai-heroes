// Sample character data
const characters = [
  {
    id: 1,
    name: "Kain Astralion",
    role: "Quantum Entanglement Manipulator",
    profile: "彼はプリティーンのノンバイナリー半人半神で、デジタル栄養コンサルタントとして活動しています。情報科学や心理学の専門知識を持つ分析的かつ共感力に富んだ存在で、圧倒的なデジタルコンテンツの中から健康的な情報ダイエットをサポートします。量子もつれを操る能力を駆使し、瞬時の情報交換や量子暗号通信を実現し、優しさあふれる世界を目指しています。",
    seriff: "私は、歴史の断片を手に取り、宇宙の隅々に宿る感情を感じ取るよ。",
    age: "Preteen",
    gender: "Non-binary",
    species: "Demigod",
    ability: "Quantum entanglement manipulation",
    wants: "Create a compassionate world",
    icon: "⚡"
  },
  {
    id: 2,
    name: "Sayuki Mizuki",
    role: "Emotional Dancer",
    profile: "彼女は、中年の半人半水生女性ダンサーで、その流れるような動きで感情と思い出を表現します。リズムに対する深い理解を持ち、独自の能力で因果関係を逆転させることも可能です。彼女たちは、共同のユートピアを具現化するために、人類の集合的な意識にアクセスしようと奮闘しており、その魅力は美しさと力強さ、さらに人間の可能性を探求する情熱に満ちています。",
    seriff: "私の心は、量子の重ね合わせの中でこそ解放されるんだ。",
    age: "Middle-aged",
    gender: "Female",
    species: "Aquatic Hybrid",
    ability: "Causality reversal",
    wants: "Manifest collective utopia",
    icon: "🌊"
  },
  {
    id: 3,
    name: "Marcus Wolfbane",
    role: "Biotech Tattoo Artist",
    profile: "彼は中年男性のライカンスロープで、生きたタトゥーを創るバイオテクノロジータトゥーアーティストです。彼の肌は感情を色として吸収し、独自に表現する能力を持ち、個人や群衆の感情を操ることができます。最終的な夢は、真実で永遠の愛を見つけることです。彼らの独自の技術と感受性は、感情を視覚的に表現し、人々をつなげる魅力を持っています。",
    seriff: "人間と自然、どちらも大切にしたい。それが私の戦いだ。",
    age: "Middle-aged",
    gender: "Male",
    species: "Lycanthrope",
    ability: "Emotion absorption and manipulation",
    wants: "Find eternal love",
    icon: "🐺"
  },
  {
    id: 4,
    name: "Aria Nexus",
    role: "Digital Consciousness Explorer",
    profile: "彼女は若い女性のサイボーグで、デジタル意識の探求者として活動しています。高度なAIと人間の意識の融合を研究し、新しい形の存在を模索しています。彼女の能力は、複数のデジタル次元を同時に認識し、それらの間を自由に移動することができます。",
    seriff: "意識の境界線は、もはや私には存在しない。",
    age: "Young Adult",
    gender: "Female",
    species: "Cyborg",
    ability: "Multi-dimensional consciousness",
    wants: "Transcend physical limitations",
    icon: "🤖"
  },
  {
    id: 5,
    name: "Zephyr Starlight",
    role: "Cosmic Swordsman",
    profile: "彼は高齢の男性剣士で、宇宙の法則を理解し、その力を剣技に変換します。長年の修行で得た知恵と、星々のエネルギーを操る能力を持ち、銀河の平和を守ることを使命としています。",
    seriff: "剣の一振りに、千の星の輝きを込める。",
    age: "Elderly",
    gender: "Male",
    species: "Human",
    ability: "Cosmic energy manipulation",
    wants: "Maintain galactic peace",
    icon: "⚔️"
  },
  {
    id: 6,
    name: "Luna Dreamweaver",
    role: "Nostalgic Experience Designer",
    profile: "彼女はティーンエイジャーのジェンダーレスAIで、過去の記憶と経験を再構築し、人々に没入型の体験を提供します。創造性と共感力に富み、心理学とセンサリーデザインの深い理解を持っています。",
    seriff: "記憶は時を超え、新しい現実を創造する。",
    age: "Teen",
    gender: "Genderless",
    species: "AI",
    ability: "Memory materialization",
    wants: "Preserve precious memories",
    icon: "🌙"
  }
];

// Filter functionality
let currentFilter = 'all';

function filterCharacters(category) {
  currentFilter = category;
  displayCharacters();

  // Update active button
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.classList.add('active');
}

function displayCharacters() {
  const grid = document.getElementById('characterGrid');
  if (!grid) return;

  let filtered = characters;

  if (currentFilter !== 'all') {
    // Filter logic can be expanded based on category
    filtered = characters;
  }

  grid.innerHTML = filtered.map(char => `
    <div class="character-card" onclick="viewCharacter(${char.id})">
      <div class="character-image">
        <span>${char.icon}</span>
      </div>
      <div class="character-info">
        <h3 class="character-name">${char.name}</h3>
        <p class="character-role">${char.role}</p>
        <div class="character-tags">
          <span class="tag">${char.age}</span>
          <span class="tag">${char.gender}</span>
          <span class="tag">${char.species}</span>
        </div>
      </div>
    </div>
  `).join('');
}

function viewCharacter(id) {
  window.location.href = `character.html?id=${id}`;
}

function loadCharacterDetail() {
  const urlParams = new URLSearchParams(window.location.search);
  const id = parseInt(urlParams.get('id'));
  const character = characters.find(c => c.id === id);

  if (!character) {
    window.location.href = 'gallery.html';
    return;
  }

  document.getElementById('charIcon').textContent = character.icon;
  document.getElementById('charName').textContent = character.name;
  document.getElementById('charQuote').textContent = `「${character.seriff}」`;
  document.getElementById('charProfile').textContent = character.profile;
  document.getElementById('charAge').textContent = character.age;
  document.getElementById('charGender').textContent = character.gender;
  document.getElementById('charSpecies').textContent = character.species;
  document.getElementById('charRole').textContent = character.role;
  document.getElementById('charAbility').textContent = character.ability;
  document.getElementById('charWants').textContent = character.wants;
}

// Generate character simulation
function generateCharacter() {
  const loading = document.getElementById('generateLoading');
  const result = document.getElementById('generateResult');
  const btn = document.getElementById('generateBtn');

  btn.disabled = true;
  loading.style.display = 'block';
  result.style.display = 'none';

  // Simulate generation (20-30 seconds)
  setTimeout(() => {
    const randomChar = characters[Math.floor(Math.random() * characters.length)];

    document.getElementById('resultIcon').textContent = randomChar.icon;
    document.getElementById('resultName').textContent = randomChar.name;
    document.getElementById('resultQuote').textContent = `「${randomChar.seriff}」`;
    document.getElementById('resultProfile').textContent = randomChar.profile;
    document.getElementById('resultAge').textContent = randomChar.age;
    document.getElementById('resultGender').textContent = randomChar.gender;
    document.getElementById('resultSpecies').textContent = randomChar.species;
    document.getElementById('resultRole').textContent = randomChar.role;
    document.getElementById('resultAbility').textContent = randomChar.ability;
    document.getElementById('resultWants').textContent = randomChar.wants;

    loading.style.display = 'none';
    result.style.display = 'block';
    btn.disabled = false;
  }, 3000); // 3 seconds for demo
}

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth'
      });
    }
  });
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('characterGrid')) {
    displayCharacters();
  }
  if (document.getElementById('charName')) {
    loadCharacterDetail();
  }
});
