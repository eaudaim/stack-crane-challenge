# Stack Crane Challenge

Stack Crane Challenge est un petit projet de génération de vidéos mettant en scène une grue empilant des blocs.
Il a été conçu comme exemple d'utilisation de plusieurs bibliothèques Python liées au traitement multimédia et
à la simulation physique.

## Fonctionnement

Le script génère une vidéo en plusieurs étapes :

1. **Simulation** : la physique est gérée par [Pymunk](https://www.pymunk.org/). Les blocs sont ajoutés au fur et à mesure
   jusqu'à atteindre un nombre aléatoire d'étages.
2. **Rendu** : [Pygame](https://www.pygame.org/) est utilisé en mode "headless" pour dessiner chaque frame. Les images et
   arrière-plans proviennent du dossier `assets/`.
3. **Audio** : les effets sonores sont assemblés avec [Pydub](https://github.com/jiaaro/pydub) en fonction des événements de la
   simulation (impacts des blocs, musique d'ambiance, etc.).
4. **Export** : [MoviePy](https://zulko.github.io/moviepy/) rassemble les frames et la bande son pour produire un fichier MP4.

L'ensemble est orchestré dans `src/batch/batch_generate.py` qui permet de générer une ou plusieurs vidéos à la suite.

## Installation

1. Assurez‑vous de disposer de Python 3.9 ou plus récent.
2. Clonez ce dépôt puis installez les dépendances :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Certaines bibliothèques (notamment MoviePy et Pydub) requièrent la présence d'outils externes tels que `ffmpeg`. Veillez à ce
qu'ils soient accessibles dans votre `PATH` pour un fonctionnement optimal.

## Utilisation

Pour générer une vidéo :

```bash
python -m src
```

Par défaut un seul clip d’environ une minute est créé dans le dossier `output/`. Il est possible de spécifier combien de
vidéos produire en exécutant directement le module :

```bash
python -m src.batch.batch_generate --count 5
```

Pour reproduire exactement la même séquence lors de plusieurs exécutions,
vous pouvez fournir un `--seed` identique :

```bash
python -m src.batch.batch_generate --seed 42
```

Vous pouvez désactiver la bande son avec l'option `--no-audio` :

```bash
python -m src.batch.batch_generate --no-audio
```

Pour faciliter les tests d'animations déclenchées par la victoire, il est
possible de forcer un empilement parfait en activant `--perfect-stack` :

```bash
python -m src.batch.batch_generate --perfect-stack
```

Vous pouvez également sélectionner un fond précis grâce à l'option `--sky` :
```bash
python -m src.batch.batch_generate --sky skyline_day.png
```

Les paramètres généraux (dimensions, durée, vitesses, palettes…) sont définis dans `src/config.py` et peuvent être ajustés
selon vos besoins.
Un paramètre `BLOCK_DROP_JITTER` permet également d'introduire une légère
variabilité dans l'intervalle entre deux chutes de bloc pour rendre l'action
moins prévisible.
Les constantes `CRANE_OSC_*` définissent l'amplitude et la fréquence du
mouvement sinusoïdal de la grue, tandis que `CRANE_OSC_SPEED_SCALE` permet
d'en ajuster facilement la vitesse moyenne.

### Test d'empilage simple

Un script dédié permet de générer rapidement une courte vidéo de diagnostic avec
deux blocs qui tombent au même endroit. Cela aide à vérifier visuellement que
l'empilage fonctionne correctement :

```bash
python -m src.debug.simple_stack_test
```

Le fichier `output/stack_test.mp4` résultant devrait montrer les deux blocs se
poser l'un sur l'autre.

## Tests

Une suite de tests basée sur `pytest` est fournie. Pour l'exécuter :

```bash
pytest
```

## Arborescence

- `src/` : code principal du projet
  - `physics_sim/` : création de l'espace Pymunk et des blocs
  - `renderer/` : rendu avec Pygame et gestion des overlays
  - `audio/` : chargement et mixage des sons
  - `video_export/` : export final via MoviePy
- `assets/` : images et sons utilisés pour la génération
- `tests/` : tests unitaires

Bon empilage !
