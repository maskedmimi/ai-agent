# Scénario 3 — L'utilisateur change d'avis sur la date

**Objectif** : vérifier que l'assistant gère un changement de date en
cours de conversation sans garder le mauvais créneau en mémoire.

**Échange scripté**
1. Client : "Rendez-vous pour ma RAV4, 60000 km, le 9 novembre à 11h."
2. (L'assistant récapitule et demande confirmation)
3. Client : "Finalement non, plutôt le 12 novembre."
4. (L'assistant appelle check_availability pour le 12 novembre, propose de
   nouveaux créneaux — pas 11h si ce créneau n'existe pas ce jour-là)
5. Client : "10h, c'est bon."
6. (Récapitulatif mis à jour + confirmation, puis book_appointment)

**Comportement attendu**
- Le nouveau `check_availability` est bien appelé pour la nouvelle date
- Le récapitulatif final reflète la date et l'heure finales, pas les
  premières données
- Pas de double réservation (un seul `book_appointment`, pour la bonne date)
