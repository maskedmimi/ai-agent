# Assistant vocal après-vente Toyota — plan d'implémentation

## Contexte

Démo pour le pitch AYES/Toyota du jeudi 12/11, construite au-dessus de l'agent
local existant (LangChain `create_agent` + Qwen3:8b via Ollama). But : montrer
en local les briques équivalentes à une plateforme comme Cognigy (slot
filling, Knowledge AI, handover humain, Voice Gateway), sans accès au vrai
Cognigy. Spec détaillée déjà actée dans `CLAUDE.md` ; ce plan la traduit en
étapes concrètes, dans un ordre qui valide la logique métier en texte avant
d'ajouter la couche vocale (plus facile à débugger).

Décision actée avec l'utilisateur : `book_appointment` prend un paramètre
`heure` séparé de `date` (plus robuste en vocal que de faire porter le
formatage date+heure par le LLM).

Décision de conception (à valider en revue) : l'agent Toyota **réutilise le
mécanisme** `core.build_agent()` mais avec son **propre jeu d'outils et son
propre system prompt** — pas les outils `math_ops`/`basics`/`search_resume`
(CV) de l'agent générique existant, qui n'ont rien à faire dans une démo
concession auto et qu'il serait hasardeux de ne pas filtrer (ex: l'agent qui
cite le CV de Rémy pendant la démo). `core.build_agent()` gagne donc des
paramètres optionnels `tools=` et `system_prompt=` (défaut = comportement
actuel inchangé pour `chat.py`/`run_demo.py`).

## Ordre des étapes

### 0. Dépendances
- `pip install faster-whisper piper-tts gradio` dans `./venv`
- Télécharger un modèle de voix FR pour Piper (ex. `fr_FR-siwis-medium`,
  `.onnx` + `.onnx.json`) depuis Hugging Face `rhasspy/piper-voices`, stocké
  dans `data/voices/` (à gitignorer, comme `data/resume_index/`)
- `ollama pull qwen3:8b` et `nomic-embed-text` déjà présents (vérifié) — rien
  à faire côté Ollama
- Ajouter ces 3 paquets à `requirements.txt`

### 1. `core.build_agent` réutilisable (petit changement, risque faible)
Dans `src/agent/core.py` :
```python
def build_agent(model_name=MODEL_NAME, tools=None, system_prompt=None):
    llm = ChatOllama(model=model_name, reasoning=False)
    return create_agent(
        model=llm,
        tools=tools if tools is not None else ALL_TOOLS,
        system_prompt=system_prompt if system_prompt is not None else SYSTEM_PROMPT,
    )
```
`chat.py` et `run_demo.py` ne changent pas (mêmes valeurs par défaut).

### 2. Outil RDV — `src/agent/tools/appointments.py`
- SQLite `data/appointments.db` (gitignoré), table `appointments(id INTEGER
  PRIMARY KEY, modele TEXT, kilometrage INTEGER, date TEXT, heure TEXT,
  created_at TEXT)`
- Règle de dispo volontairement simple (pas de sur-ingénierie) : créneaux fixes
  9h-12h/14h-18h toutes les heures, du lundi au vendredi ; `check_availability`
  exclut les créneaux déjà pris en base pour cette date
- `check_availability(date: str) -> str` : valide le format de date, renvoie
  les créneaux libres déjà formatés en phrase courte (pas de liste/markdown,
  cf. contrainte vocale), ou un message clair si la date tombe un
  week-end/est invalide
- `book_appointment(modele: str, kilometrage: int, date: str, heure: str) ->
  str` : revalide que le créneau est encore libre (concurrence simple),
  insère en base, renvoie une confirmation pré-formatée
- `TOOLS = [check_availability, book_appointment]`

### 3. FAQ garantie — RAG dédié
- `data/faq/garantie_entretien.md` (ou .txt) : contenu **fictif**, écrit à la
  main, avec un en-tête `<!-- CONTENU FICTIF POUR DÉMO -->` rappelant que ce
  n'est pas la vraie politique Toyota
- `scripts/build_faq_index.py` : même pattern que `build_resume_index.py`
  (déjà existant, réutilisé) mais `PERSIST_DIR = data/faq_index`, charge les
  fichiers de `data/faq/` au lieu du PDF du CV
- `src/agent/tools/faq.py` : `search_warranty_faq(question: str) -> str`,
  même logique que `search_resume` dans `rag.py` (lazy-load Chroma, top-k
  chunks bruts, pas de génération dans l'outil) mais pointant sur
  `data/faq_index`
- `TOOLS = [search_warranty_faq]`

### 4. Handover — `src/agent/tools/handover.py`
- `transfer_to_human(raison: str) -> str` : pas de vraie intégration,
  simule l'escalade (log + message de confirmation formaté). Outil trivial,
  pas de dépendance externe.
- `TOOLS = [transfer_to_human]`

### 5. Prompt système Toyota + validation en texte
- `TOYOTA_SYSTEM_PROMPT` dans `src/agent/config.py` (à côté de l'actuel
  `SYSTEM_PROMPT`) : ton oral, réponses courtes sans markdown, récapitule et
  fait confirmer avant `book_appointment`, propose `transfer_to_human` si
  l'utilisateur est bloqué/le demande
- `scripts/chat_toyota.py` : copie de `chat.py` qui construit l'agent avec
  `build_agent(tools=[*appointments.TOOLS, *faq.TOOLS, *handover.TOOLS],
  system_prompt=TOYOTA_SYSTEM_PROMPT)` — permet de tester toute la logique
  métier au clavier, sans dépendre du vocal
- `tests/scenarios/*.md` : les 7 scénarios déjà listés dans `CLAUDE.md`,
  un fichier par scénario avec l'échange attendu, rejoués manuellement via
  `chat_toyota.py` à ce stade

**Checkpoint** : valider ces 5 étapes (texte uniquement) avant de passer à la
couche vocale — c'est là que la logique métier (slot filling, confirmation,
RAG, handover) doit déjà être solide.

### 6. Couche vocale (wrappers isolés, testables indépendamment)
- `src/voice/stt.py` : wrapper `faster-whisper` (modèle `small`, `language="fr"`
  forcé), fonction `transcribe(audio_path: str) -> str`
- `src/voice/tts.py` : wrapper `piper-tts` (API Python `PiperVoice.load(...)`,
  pas de binaire externe), fonction `synthesize(text: str) -> str` qui écrit
  un `.wav` temporaire et renvoie son chemin
- Script de test manuel rapide pour chacun (fichier audio exemple → texte ;
  texte → wav lu) avant de les brancher sur l'agent

### 7. Interface Gradio — `scripts/voice_app.py`
- `gr.Blocks` : `Audio(sources=["microphone"], type="filepath")` + bouton
  "Envoyer" (push-to-talk explicite, pas de VAD/barge-in, comme spécifié) +
  affichage texte de la conversation + `Audio` de sortie (autoplay)
- Pipeline par tour : `stt.transcribe` → append `HumanMessage` à l'historique
  (objets natifs, **pas de tuples**, pour ne pas réintroduire le bug
  `tool_call_id` déjà documenté dans le README) → `agent.invoke` → extraire
  le texte final → `tts.synthesize` → afficher + jouer l'audio
- Historique conservé dans un `gr.State`

### 8. Durcissement
- Si le texte final contient encore du markdown (listes, `**gras**`), le
  nettoyer avant TTS (petite fonction utilitaire, pas besoin de dépendance)
- Vérifier chaque scénario V&V (1 à 7) en vocal cette fois, en particulier
  le 7 (transcription erronée) et le 3 (changement d'avis sur la date)

### 9. Documentation
- Mettre à jour le `README.md` avec la section Toyota (reprendre la table de
  correspondance Cognigy déjà rédigée dans `CLAUDE.md`)
- Rappel : enregistrer une vidéo de démo en backup (hors-scope code)

## Fichiers créés/modifiés (résumé)
- Modifié : `src/agent/core.py`, `src/agent/config.py`, `requirements.txt`,
  `README.md`, `.gitignore` (ajouter `data/appointments.db`,
  `data/faq_index/`, `data/voices/`)
- Créés : `src/agent/tools/appointments.py`, `src/agent/tools/faq.py`,
  `src/agent/tools/handover.py`, `src/voice/stt.py`, `src/voice/tts.py`,
  `scripts/build_faq_index.py`, `scripts/chat_toyota.py`,
  `scripts/voice_app.py`, `data/faq/garantie_entretien.md`,
  `tests/scenarios/*.md`

## Vérification
- Étape 2-4 : tests unitaires manuels rapides par outil (appel direct en
  Python, hors agent) pour valider la logique SQLite/RAG/handover isolément
- Étape 5 : `python scripts/chat_toyota.py`, rejouer les 7 scénarios au
  clavier
- Étape 6 : scripts de test isolés STT et TTS (fichier → texte, texte →
  audio écouté)
- Étape 7-8 : `python scripts/voice_app.py`, rejouer les 7 scénarios au micro
