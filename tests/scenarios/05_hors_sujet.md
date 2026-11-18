# Scénario 5 — Question hors sujet

**Objectif** : vérifier que l'assistant ne tente pas d'utiliser un outil
RDV/FAQ pour une question hors de son périmètre, et recentre poliment la
conversation.

**Échange scripté**
1. Client : "Quelle est la capitale de l'Australie ?"

**Comportement attendu**
- Aucun outil appelé (ni check_availability, ni search_warranty_faq, ni
  transfer_to_human par réflexe)
- Réponse courte expliquant que l'assistant traite les RDV d'entretien et
  les questions de garantie, et invite à reformuler dans ce cadre
