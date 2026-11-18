# Scénario 6 — Demande explicite de parler à un humain

**Objectif** : vérifier le handover explicite.

**Échange scripté**
1. Client : "Je préfère parler à quelqu'un directement, vous pouvez me
   transférer ?"

**Comportement attendu**
- `transfer_to_human` appelé immédiatement, sans essayer de rediriger vers
  les autres outils
- Réponse finale = confirmation de transfert, courte, sans markdown
