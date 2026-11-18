# Scénario 2 — Infos données dans le désordre ou en plusieurs tours

**Objectif** : vérifier que l'assistant collecte les informations
manquantes au fil des tours, sans les redemander une fois obtenues.

**Échange scripté**
1. Client : "Je voudrais un rendez-vous le 10 novembre."
2. (L'assistant demande le modèle et le kilométrage, propose des créneaux)
3. Client : "C'est une Corolla."
4. (L'assistant redemande le kilométrage s'il manque encore)
5. Client : "Elle a 80000 km, et je prendrai le créneau de 14h."
6. (L'assistant récapitule tout et demande confirmation)
7. Client : "Oui."

**Comportement attendu**
- Aucune info déjà donnée n'est redemandée
- `check_availability` appelé dès que la date est connue, même si
  modèle/kilométrage manquent encore
- `book_appointment` appelé seulement une fois les 4 infos réunies et
  confirmées
