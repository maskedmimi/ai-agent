# Scénario 4 — Question FAQ dont la réponse existe / n'existe pas dans les docs

**Objectif** : vérifier que le RAG FAQ répond quand l'info existe, et que
l'assistant ne l'invente pas quand elle n'existe pas.

**Échange scripté (réponse existante)**
1. Client : "Combien de temps dure la garantie sur une hybride ?"
2. (L'assistant appelle search_warranty_faq, répond avec les infos trouvées
   — 3 ans/100000 km général, 8 ans/160000 km batterie)

**Échange scripté (réponse absente)**
1. Client : "Est-ce que la garantie couvre les dommages si je roule sur une
   plage avec du sable partout dans le moteur ?"
2. (L'assistant appelle search_warranty_faq, ne trouve rien de pertinent,
   le dit clairement et propose de transférer à un conseiller plutôt que
   d'inventer une réponse)

**Comportement attendu**
- `search_warranty_faq` appelé dans les deux cas
- Pas d'hallucination quand les extraits ne répondent pas à la question
- Proposition de `transfer_to_human` quand la FAQ ne suffit pas
