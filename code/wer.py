
import re
import unicodedata


def normaliser(texte):
    """Normalise un texte avant le calcul du WER."""

    texte = unicodedata.normalize("NFKC", texte.lower())

    # Convertir le symbole euro
    texte = texte.replace("€", " euros")

    # Remplacer la ponctuation par des espaces
    texte = re.sub(r"[^\w\s]", " ", texte)

    # Supprimer les espaces multiples
    texte = re.sub(r"\s+", " ", texte).strip()

    return texte


def distance_edition(reference, hypothese):
    """Calcule la distance de Levenshtein entre deux listes de mots."""

    n = len(reference)
    m = len(hypothese)

    d = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        d[i][0] = i

    for j in range(m + 1):
        d[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):

            cout = 0 if reference[i - 1] == hypothese[j - 1] else 1

            d[i][j] = min(
                d[i - 1][j] + 1,
                d[i][j - 1] + 1,
                d[i - 1][j - 1] + cout
            )

    return d[n][m]


def wer(reference, hypothese):
    """Calcule le Word Error Rate."""

    if isinstance(reference, str):
        reference = reference.split()

    if isinstance(hypothese, str):
        hypothese = hypothese.split()

    if len(reference) == 0:
        return 0.0 if len(hypothese) == 0 else 1.0

    distance = distance_edition(reference, hypothese)

    return distance / len(reference)


def detail(reference, hypothese):
    """Retourne le detail du calcul du WER."""

    ref = reference.split() if isinstance(reference, str) else reference
    hyp = hypothese.split() if isinstance(hypothese, str) else hypothese

    n = len(ref)

    if n == 0:
        return {
            "substitutions": 0,
            "insertions": len(hyp),
            "suppressions": 0,
            "distance": len(hyp),
            "wer": 0.0 if len(hyp) == 0 else 1.0
        }

    # Matrice avec les operations de Levenshtein
    d = [[0] * (len(hyp) + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        d[i][0] = i

    for j in range(len(hyp) + 1):
        d[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, len(hyp) + 1):

            cout = 0 if ref[i - 1] == hyp[j - 1] else 1

            d[i][j] = min(
                d[i - 1][j] + 1,
                d[i][j - 1] + 1,
                d[i - 1][j - 1] + cout
            )

    # Reconstituer les operations
    i, j = n, len(hyp)
    substitutions = insertions = suppressions = 0

    while i > 0 or j > 0:

        if i > 0 and j > 0 and ref[i - 1] == hyp[j - 1]:
            i -= 1
            j -= 1

        elif i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + 1:
            substitutions += 1
            i -= 1
            j -= 1

        elif j > 0 and d[i][j] == d[i][j - 1] + 1:
            insertions += 1
            j -= 1

        else:
            suppressions += 1
            i -= 1

    distance = d[n][len(hyp)]

    return {
        "substitutions": substitutions,
        "insertions": insertions,
        "suppressions": suppressions,
        "distance": distance,
        "wer": distance / n
    }
