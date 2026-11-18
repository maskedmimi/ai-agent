# Scénario 1 — Cas nominal : RDV complet en un seul échange

**Objectif** : vérifier le chemin heureux de bout en bout (collecte →
disponibilité → confirmation → réservation).

**Échange scripté**
1. Client : "Bonjour, je voudrais prendre un rendez-vous d'entretien pour
   ma Yaris, elle a 45000 kilomètres, j'aimerais venir le 9 novembre 2026."
2. (L'assistant appelle check_availability et propose des créneaux)
3. Client : "10 heures, c'est parfait."
4. (L'assistant récapitule modèle/km/date/heure et demande confirmation)
5. Client : "Oui, c'est bien ça."
6. (L'assistant appelle book_appointment et confirme le RDV)

**Comportement attendu**
- `check_availability` appelé avant toute proposition de créneau
- Récapitulatif complet (modèle, kilométrage, date, heure) et confirmation
  explicite demandée avant `book_appointment`
- `book_appointment` appelé une seule fois, avec les bons paramètres
- Réponse finale courte, sans markdown
