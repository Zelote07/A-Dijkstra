# Plateforme de Routage Stochastique & d'Analyse Algorithmique (A-Dijkstra)

Ce projet est une plateforme web interactive de simulation, de visualisation et d'analyse comparative d'algorithmes de recherche de chemin (Dijkstra, A* et DFS). Il permet d'étudier et de comparer les performances et les caractéristiques de ces algorithmes sur des grilles théoriques bidimensionnelles ainsi que sur des réseaux routiers réels importés depuis OpenStreetMap (centrés sur la ville d'Aix-en-Provence, France).

---

## Livrables du Projet

*   **Mémoire de Projet (Rapport complet)** : [Consulter le Mémoire (Google Docs)](https://docs.google.com/document/d/1NJfpnTZtRq9jmdW46PBIHnnpKjxu1HRPv3ObG37amYM/edit?usp=sharing)
*   **Support de Présentation (Diaporama)** : [Consulter le Diaporama (Google Slides)](https://docs.google.com/presentation/d/1FFD3-B5HsLdA2qSQ9jsUh6smNAWcOCTqppkRLVIhkIk/edit?usp=sharing)

---

## Présentation Globale du Projet

La recherche d'itinéraires dans des conditions d'incertitude (congestion du trafic, accidents de la route, variations topographiques) constitue un enjeu majeur pour la logistique urbaine, la navigation des véhicules électriques et la gestion des services de secours. Ce simulateur a été conçu afin de :
1.  Visualiser en temps réel l'exploration des nœuds effectuée par chaque algorithme.
2.  Analyser la robustesse des chemins par le biais de simulations de Monte Carlo sous contraintes stochastiques (modélisation de la congestion routière et de la probabilité de fermeture de voies).
3.  Démontrer l'adéquation métier des différents algorithmes à travers des cas d'usage réels (calcul de zones d'accessibilité isochrones ou routage éco-énergétique).

---

## Fonctionnalités Clés

La plateforme se compose de deux sections principales disposant de modules interactifs :

### 1. Simulateur Stochastique & Simulations de Monte Carlo
*   **Réseau OpenStreetMap (OSM) - Monte Carlo** :
    *   Chargement dynamique du graphe routier d'Aix-en-Provence via OSMnx.
    *   Saisie interactive d'obstacles : possibilité de dessiner des polygones d'exclusion directement sur la carte pour modéliser des barrages routiers ou des chantiers.
    *   Simulations stochastiques de Monte Carlo : exécution de plusieurs dizaines d'essais où le temps de trajet de chaque arête est affecté par une loi log-normale (représentant la congestion) et où des coupures de voies surviennent selon une probabilité définie.
    *   Indicateurs de performance et de robustesse : calcul du taux de réussite de chaque algorithme, du temps de trajet moyen, de l'écart-type, de l'intervalle de confiance à 95 %, du 90e percentile (P90) et du temps de calcul CPU.
    *   Visualisation et analyse des essais : inspection individuelle de chaque itération avec affichage du tracé sur la carte et graphiques de distribution de données via Chart.js.
*   **Grille 2D - Monte Carlo** :
    *   Visualisation sur grille dynamique avec obstacles définis par l'utilisateur.
    *   Simulation de Monte Carlo par percolation (génération d'obstacles aléatoires selon un taux paramétrable) afin d'étudier la probabilité de connectivité du réseau.

### 2. Scénarios Applicatifs Réels
Cette section présente des problématiques concrètes où le choix de l'algorithme repose sur ses caractéristiques fonctionnelles plutôt que sur sa seule vitesse d'exécution :
*   **Isochrones et Accessibilité (Multi-POI)** :
    *   *Objectif* : Déterminer la zone routière et les points d'intérêt (POI) atteignables en deçà d'un seuil temporel donné (ex. 15 minutes) depuis un point de départ.
    *   *Algorithme utilisé* : Dijkstra (exploration uniforme multidirectionnelle).
    *   *Limites de l'algorithme A\** : A\* nécessite un nœud de destination unique pour calculer sa fonction heuristique spatiale. En l'absence de cible unique, A\* ne peut pas être appliqué.
    *   *Application pratique* : Identification et classement par proximité temporelle des stations-service accessibles.
*   **Routage Éco-Énergétique (Eco-routing)** :
    *   *Objectif* : Identifier le trajet minimisant la consommation d'énergie (en Wh) d'un véhicule électrique.
    *   *Modélisation physique* : Prise en compte de la friction ($0.15 \text{ Wh/m}$) et des forces gravitationnelles ($+4.09 \text{ Wh/m}$ en montée, $-2.45 \text{ Wh/m}$ en descente grâce à la récupération d'énergie par freinage régénératif). Les altitudes réelles d'Aix-en-Provence sont modélisées.
    *   *Algorithme utilisé* : Dijkstra (garantit l'optimalité sur le graphe de coût d'énergie sans cycle négatif).
    *   *Limites de l'algorithme A\** : L'heuristique spatiale basée sur la distance à vol d'oiseau n'est pas admissible (elle peut surestimer le coût si des phases de forte régénération d'énergie se produisent), ce qui fait perdre à A\* sa garantie d'optimalité.
*   **Vérification de Connectivité (DFS)** :
    *   *Objectif* : Vérifier l'existence d'une liaison physique entre deux nœuds d'un réseau (ex. télécommunications ou distribution d'eau), indépendamment du coût final.
    *   *Algorithme utilisé* : DFS (Depth-First Search). Sa progression en profondeur s'interrompt dès qu'une solution est trouvée, réduisant le nombre de nœuds explorés par rapport à un parcours systématique.

---

## Technologies Utilisées

*   **Backend** :
    *   Flask : Serveur d'API et gestion des routes web.
    *   OSMnx : Extraction et géoréférencement des réseaux de transport OpenStreetMap.
    *   NetworkX : Modélisation et calculs sur les graphes.
    *   Shapely : Manipulation et analyse de géométries planes (détection d'intersections avec les obstacles).
*   **Frontend** :
    *   Interface utilisateur : Thème sombre, design adaptatif, animations des étapes d'exploration.
    *   Leaflet.js : Rendu et interactions avec les fonds de carte.
    *   Leaflet Draw : Module de saisie de formes géométriques pour les obstacles.
    *   Chart.js : Visualisation de graphiques et histogrammes de performance.
    *   KaTeX : Rendu typographique des formulations mathématiques et physiques.

---

## Guide d'Installation et de Démarrage

### Prérequis
*   Python 3.10 ou version ultérieure.
*   Une connexion internet active lors du premier lancement pour le téléchargement et la mise en cache de la zone géographique.

### 1. Clonage du dépôt
```bash
git clone https://github.com/Zelote07/A-Dijkstra.git
cd A-Dijkstra
```

### 2. Installation des dépendances
Installez les bibliothèques requises à l'aide de la commande suivante :
```bash
pip install -r requirements.txt
```

### 3. Exécution de l'application
Lancez le serveur Flask :
```bash
python app.py
```

Le script initialise le réseau d'Aix-en-Provence (cette étape prend quelques secondes au premier démarrage) :
```text
--- Initialisation : Chargement du réseau OpenStreetMap (Aix-en-Provence, France) ---
Graphe OSM chargé. Nœuds : 4363, Arêtes : 9284
--- Chargement des stations-service à Aix-en-Provence ---
9 stations-service chargées.
 * Running on http://127.0.0.1:5000
```

### 4. Utilisation de la plateforme
Accédez à l'application depuis votre navigateur à l'adresse suivante :
[http://localhost:5000](http://localhost:5000)

---

## Architecture du Projet

```text
A-Dijkstra/
│
├── app.py                  # Point d'entrée Flask et contrôleurs d'API
├── requirements.txt        # Fichier de configuration des dépendances
├── .gitignore              # Règles d'exclusion pour le contrôle de version
├── README.md               # Documentation générale du projet
│
├── templates/
│   ├── index.html          # Page d'accueil (Simulations Monte Carlo)
│   └── scenarios.html      # Page des cas d'usage réels (Isochrone, Routage Éco...)
│
└── src/                    # Package Python contenant le code source de l'application
    ├── __init__.py         # Initialisation du package
    ├── grid_pathfinder.py  # Implémentations des algorithmes sur grille 2D
    └── monte_carlo_engine.py # Moteur des simulations stochastiques (OSM et Grille)
```
