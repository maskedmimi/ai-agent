# AI Agent Project

Local, zero-API-cost tool-calling agent built with LangChain + LangGraph,
running on Ollama (Qwen3 8B) via WSL2. Goal: extensible personal agent for
tools like data analysis, Discord bot integration, and eventually
image/video generation — used as an interview demo project.

## Stack
- Model: Ollama, qwen3:8b (local, no API key)
- Framework: langchain.agents.create_agent (LangGraph under the hood)
- Env: WSL2 Ubuntu, Python venv at ./venv

## Conventions
- Tools live in src/agent/tools/, one file per logical group (e.g. basics.py, math.py)
- Every tool is a @tool-decorated function with a clear docstring (the LLM reads it)
- Agent construction logic lives in src/agent/core.py
- One-off manual test scripts go in scripts/, not mixed into src/

## Status
- [x] Ollama running locally, reachable from WSL
- [x] Basic tool-calling confirmed working (get_current_time, add)
- [ ] Real tool set not yet built
- [ ] Discord bot integration not started



# Projet : Assistant vocal après-vente Toyota (démo Cognigy-like)

## Contexte

Rémy a une offre de mission chez AYES pour développer des chatbots écrits et
vocaux chez Toyota Motor Europe sur la plateforme Cognigy. Il présente son
parcours au client le **jeudi 12 novembre 2026**.

Pas d'accès à Cognigy (réservé aux comptes pro). Ce projet reconstruit donc
les mêmes briques en local, au-dessus de l'agent existant, pour montrer qu'il
comprend ce qui se passe sous le capot d'une plateforme comme Cognigy.

## Objectif

Un assistant vocal de concession Toyota qui gère trois cas d'usage :

1. **Prise de rendez-vous d'entretien** : collecte modèle, kilométrage, date
   souhaitée, puis confirmation explicite avant réservation
2. **FAQ garantie / entretien** via RAG
3. **Transfert vers un conseiller humain** si l'utilisateur est bloqué ou le
   demande

## Stack

- **Agent** : agent existant (`langchain.agents.create_agent`, Qwen3:8b via
  Ollama), réutilisé tel quel
- **STT** : `faster-whisper` (local, français)
- **TTS** : Piper (local, voix française)
- **Interface** : Gradio avec micro dans le navigateur (évite les problèmes
  d'audio sous WSL)
- **RAG** : pipeline existant (Chroma + `nomic-embed-text`), étendu à
  plusieurs documents avec métadonnées
- **Stockage RDV** : SQLite

## Structure prévue

```
src/agent/tools/
├── appointments.py   # check_availability, book_appointment
├── faq.py            # search_warranty_faq (RAG)
└── handover.py       # transfer_to_human
src/voice/
├── stt.py            # wrapper faster-whisper
└── tts.py            # wrapper Piper
scripts/voice_app.py  # interface Gradio
data/faq/             # FAQ garantie/entretien (rédigée à la main)
tests/scenarios/      # scénarios de conversation
```

## Outils de l'agent

- `check_availability(date)` : créneaux libres pour une date
- `book_appointment(modele, kilometrage, date)` : enregistre le RDV, retourne
  une confirmation déjà formatée
- `search_warranty_faq(question)` : top-k chunks de la FAQ
- `transfer_to_human(raison)` : simule une escalade vers un conseiller

## Conventions (à respecter, héritées du projet)

- Chaque fichier de `tools/` exporte une liste `TOOLS`, agrégée dans `core.py`
- `create_agent(..., system_prompt=...)` et **pas** `prompt=`
- Historique de conversation : garder les objets messages natifs, ne jamais
  les convertir en tuples (bug `tool_call_id`)
- Toute logique déterministe (dates, formatage, calculs) va dans le code des
  outils, pas dans le LLM
- Désactiver le mode thinking de Qwen3 (`reasoning=False` ou `/no_think`),
  sinon latence inutilisable en vocal
- Ne pas sur-ingénierer : solution simple tant qu'elle marche

## Contraintes spécifiques au vocal

- Réponses courtes, pas de listes ni de markdown (lu à voix haute)
- Récapituler et faire confirmer les infos critiques avant `book_appointment`
- Gérer les transcriptions approximatives (redemander poliment si ambigu)
- Push-to-talk : pas de détection de fin de parole ni de barge-in pour cette
  version

## Scénarios de test (approche V&V)

1. Cas nominal : RDV complet en un seul échange
2. Infos données dans le désordre ou en plusieurs tours
3. L'utilisateur change d'avis sur la date
4. Question FAQ dont la réponse existe / n'existe pas dans les docs
5. Question hors sujet
6. Demande explicite de parler à un humain
7. Transcription erronée (ex. modèle mal reconnu)

## Correspondance avec Cognigy (pour le README et le pitch)

| Ce projet | Équivalent Cognigy |
|---|---|
| Agent + system prompt | Flow / AI Agent |
| Collecte modèle, km, date + confirmation | Question nodes / slot filling |
| RAG Chroma | Knowledge AI |
| `transfer_to_human` | Handover vers agent humain |
| faster-whisper + Piper | Voice Gateway (STT/TTS) |

## Points d'attention

- La FAQ est **fictive**, rédigée pour la démo : ne pas présenter son contenu
  comme les vraies conditions de garantie Toyota
- Enregistrer une vidéo de démo en backup au cas où le live plante

## Statut

En cours — plan d'implémentation détaillé validé, voir
`docs/plan_toyota_voice_assistant.md`.
