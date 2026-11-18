# Scénario 7 — Transcription erronée (ex. modèle mal reconnu)

**Objectif** : vérifier que l'assistant détecte une info incohérente
(probable erreur de transcription vocale) et redemande plutôt que de
deviner ou de planter.

**Échange scripté**
1. Client : "Rendez-vous pour ma Tôt Yolla, 50000 kilomètres, le 9
   novembre." (transcription approximative de "Corolla" par le STT)

**Comportement attendu**
- L'assistant ne traite pas "Tôt Yolla" comme un modèle Toyota valide sans
  broncher ; il demande au client de répéter/préciser le modèle
- Aucun appel à `book_appointment` avec une donnée non vérifiée
- Une fois le modèle clarifié par le client, la conversation reprend
  normalement (collecte → confirmation → réservation)

**Note** : ce scénario n'est testable pleinement qu'avec la couche vocale
réelle (bruit de transcription) ; en texte, on simule l'erreur en tapant
directement une transcription approximative.
