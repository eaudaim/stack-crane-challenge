"""Constantes globales de configuration pour Stack Crane Challenge."""

import os
import math

# ============================================================================
# Paramètres de la fenêtre et de la simulation
# ============================================================================

# Dimensions de la fenêtre
WIDTH = 1080
HEIGHT = 1920

# Images par seconde utilisées pour la physique et le rendu
FPS = 30

# Durée de l'écran d'introduction avant le démarrage de la simulation (secondes)
INTRO_DURATION = 3

# Durée totale du défi. Si la tour n'atteint pas la hauteur requise avant la
# fin du compte à rebours, la partie est perdue.
TIME_LIMIT = 60

# Durée totale utilisée lors de l'export vidéo (intro + défi + marge finale)
DURATION = INTRO_DURATION + TIME_LIMIT + 3

# ============================================================================
# Paramètres liés aux blocs
# ============================================================================

# Dimensions en pixels d'un bloc (sprite et corps physique)
BLOCK_SIZE = (150, 220)

# Temps qu'un bloc au repos reste sur le sol avant de disparaître s'il n'est pas
# supporté (secondes)
BLOCK_DESPAWN_DELAY = 4.2

# Permettre la suppression automatique des blocs non supportés. Si ``False``,
# la logique de disparition est ignorée et tous les blocs restent présents.
BLOCK_DESPAWN_ENABLED = True

# Angle (en radians) au-delà duquel un bloc est considéré comme posé sur le
# côté et doit disparaître après ``BLOCK_DESPAWN_DELAY`` s'il n'est pas
# supporté.
BLOCK_SIDE_ANGLE = 0.4

# Position verticale du sol dans l'espace physique
FLOOR_Y = 10

# Injection volontaire de forces parasites pour déstabiliser la pile.
# Une valeur de 0 désactive l'effet.
BUG_SIDE_IMPULSE = 0.0  # impulsion horizontale appliquée à chaque frame

# Vitesse angulaire aléatoire ajoutée chaque frame. Mettre à 0 pour désactiver.
BUG_SPIN_VELOCITY = 0.0

# Force d'adhésion verticale entre blocs adjacents. A 0 l'effet est inactif et
# sert à réduire les glissements indésirables.
BLOCK_ADHESION_FORCE = 3

# ---------------------------------------------------------------------------
# Options de debug / test
# ---------------------------------------------------------------------------
# Lorsque ``PERFECT_STACK`` est activé, la grue reste immobile et chaque bloc
# est lâché exactement à la verticale afin de faciliter les tests dépendant de
# la condition de victoire.
PERFECT_STACK = False


# ============================================================================
# Paramètres de génération et de déplacement des blocs
# ============================================================================

# Textures possibles pour les blocs qui tombent
BLOCK_VARIANTS = [
    "block.png",
    "block_variant1.png",
    "block_variant2.png",
    "block_variant3.png",
]

# Nombre de blocs pouvant être lâchés durant une vidéo
BLOCK_COUNT_RANGE = (10, 20)

# Vitesse de déplacement de la grue en pixels/seconde
GRUE_SPEED_RANGE = (80, 120)

# Fraction de la vitesse horizontale de la grue transmise au bloc lors du
# lâcher. 1.0 signifie que le bloc démarre avec la même vitesse horizontale que
# le crochet, alors que 0 le fait apparaître sans élan latéral.
DROP_HORIZONTAL_SPEED_FACTOR = 1.0

# Hauteur de génération des blocs depuis le bas de l'écran
CRANE_DROP_HEIGHT = 635
# Hauteur depuis le bas où l'aperçu du prochain bloc est affiché. Par défaut
# elle correspond à ``CRANE_DROP_HEIGHT`` pour montrer l'emplacement exact de
# la génération.
PREVIEW_HEIGHT = CRANE_DROP_HEIGHT

# Durée pendant laquelle l'aperçu est caché après la création d'un bloc. Cela
# évite d'avoir un bloc affiché en permanence à l'écran.
PREVIEW_HIDE_DURATION = 1.0

# Marge horizontale délimitant les mouvements de la grue
CRANE_MOVEMENT_BOUNDS = 340

# Paramètres de l'oscillation automatique de la grue
CRANE_OSC_AMPLITUDE_RANGE = (
    80,
    WIDTH // 2 - CRANE_MOVEMENT_BOUNDS,
)
CRANE_OSC_FREQUENCY_RANGE = (0.4, 0.8)
CRANE_OSC_PHASE_RANGE = (0.0, 2 * math.pi)

# Variation aléatoire appliquée à la position X du lâcher
DROP_VARIATION_RANGE = (-10, 10)

# Décalage du crochet par rapport au haut de la barre de grue. L'image de la
# barre contient une grande marge transparente au-dessus de la partie visible.
# Pour garder le crochet 80 px sous la barre malgré cette marge (394 px de
# tête transparente), on compense ici.
HOOK_Y_OFFSET = 400

# Position verticale de la barre de grue. On la décale vers le haut pour que la
# partie visible soit à quelques pixels du bord supérieur de la fenêtre.
CRANE_BAR_Y = -389

# Délai entre deux lâchers successifs (secondes). ``BLOCK_DROP_JITTER`` ajoute
# une petite variation aléatoire pour éviter un rythme trop mécanique sans
# provoquer de gros écarts ni de lâchers multiples.
BLOCK_DROP_INTERVAL = 2
# Variation maximale appliquée à l'intervalle. Le délai réel sera donc
# ``BLOCK_DROP_INTERVAL`` plus ou moins une valeur prise dans cette plage.
BLOCK_DROP_JITTER = 0.4

# ============================================================================
# Palettes de couleurs et styles d'introduction
# ============================================================================
#
# "timer" reprend les couleurs du compte à rebours. Les autres palettes
# permettent de styliser le texte d'intro avec différents rendus.
PALETTES = {
    "default": {
        "text": (255, 255, 255),
        "shadow": (0, 0, 0),
    },
    # Même texte blanc et ombre noire que pour le timer
    "timer": {
        "text": (255, 255, 255),
        "shadow": (0, 0, 0),
    },
    # Style rétro : vert sur fond noir
    "retro": {
        "text": (0, 255, 0),
        "shadow": (0, 0, 0),
    },
    # Effet néon : texte magenta avec ombre cyan
    "neon": {
        "text": (255, 0, 255),
        "shadow": (0, 255, 255),
    },
    # Style BD : jaune avec ombre bleu foncé
    "comic": {
        "text": (255, 255, 0),
        "shadow": (0, 0, 128),
    },
}

# Styles d'intro préconfigurés combinant polices, couleurs et décalages d'ombre
INTRO_STYLES = {
    # Identique au compte à rebours
    "timer": {
        "font_name": None,  # police par défaut
        "font_size": 120,
        "y_pos": HEIGHT // 4,
        "shadow_offset": (2, 2),
        "palette": "timer",
    },
    # Look terminal rétro vert
    "retro": {
        "font_name": "courier",
        "font_size": 100,
        "y_pos": HEIGHT // 4,
        "shadow_offset": (4, 4),
        "palette": "retro",
    },
    # Couleurs néon avec ombre marquée
    "neon": {
        "font_name": "arial",
        "font_size": 110,
        "y_pos": HEIGHT // 4,
        "shadow_offset": (6, 6),
        "palette": "neon",
    },
    # Style bande dessinée avec Comic Sans et ombre contrastée
    "comic": {
        "font_name": "comicsansms",
        "font_size": 120,
        "y_pos": HEIGHT // 4,
        "shadow_offset": (5, 5),
        "palette": "comic",
    },
}

# Texte affiché au début de la vidéo et ses options de style
INTRO_TEXT = "TERMINE CETTE TOUR EN 60s"
INTRO_STYLE = {
    "font_size": 100,
    # Position verticale du texte (plus la valeur est petite, plus le texte est haut)
    "y_pos": HEIGHT // 4,
    "shadow_offset": (4, 4),
    # Clé de palette utilisée pour les couleurs du texte et de l'ombre
    "palette": "neon",
}

# Arrières-plans du ciel disponibles dans ``assets/sky``
SKY_OPTIONS = [
    "skyline_day.png",
    "skyline_night.png",
    "skyline_dusk.png",
]

ASSET_PATHS = {
    "sky": os.path.join("assets", "sky"),
    "crane": os.path.join("assets", "crane"),
    "block": os.path.join("assets", "block"),
    "sounds": os.path.join("assets", "sounds"),
}

OUTPUT_DIR = "output"

# ============================================================================
# Configuration des effets visuels (VFX)
# ============================================================================

# Durée du flash coloré après un impact (secondes)
IMPACT_FLASH_DURATION = 0.07
# Opacité maximale du flash
IMPACT_FLASH_ALPHA = 80
# Couleur appliquée lors du flash d'impact
IMPACT_FLASH_COLOR = (255, 160, 40)

# Paramètres des confettis affichés lors d'une victoire
CONFETTI_COUNT = 40
CONFETTI_COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 150, 255),
    (255, 255, 0),
    (255, 0, 200),
]
CONFETTI_LIFETIME = 1.0
CONFETTI_GRAVITY = 400

# Halo lumineux affiché quand la tour est terminée
GLOW_DURATION = 1.0
GLOW_COLOR = (255, 255, 0)
GLOW_ALPHA = 80

# ============================================================================
# Paramètres de mouvement de la caméra
# ============================================================================

# Activer ou non les effets de caméra (shake, zoom, oscillation)
CAMERA_EFFECTS_ENABLED = True

# Durée (en secondes) du shake appliqué lors d'un impact
CAMERA_SHAKE_DURATION = 0.3
# Amplitude maximale du shake en pixels
CAMERA_SHAKE_INTENSITY = 8

# Facteur de zoom appliqué lors d'une victoire (0.1 = +10%)
VICTORY_ZOOM_FACTOR = 0.1
# Durée du zoom de victoire (secondes)
VICTORY_ZOOM_DURATION = 1.2

# Oscillation douce de la caméra pendant la partie
CAMERA_OSC_AMPLITUDE_RANGE = (5, 10)
CAMERA_OSC_FREQUENCY_RANGE = (0.03, 0.07)
