#!/usr/bin/env python3
"""Re-categorize all CARDS in index.html into expanded category set."""
import re
import sys
from pathlib import Path

HTML = Path(__file__).parent.parent / 'index.html'
src = HTML.read_text()

# Extract CARDS array
m = re.search(r'const CARDS = \[\n(.*?)\n\];', src, re.DOTALL)
if not m:
    sys.exit('CARDS not found')
body = m.group(1)

# Parse each card line
card_re = re.compile(
    r"\{\s*word:'([^']+)',\s*article:'([^']+)',\s*en:'([^']+)',\s*cat:'([^']+)',\s*diff:'([^']+)'\s*\}"
)
cards = []
for line in body.splitlines():
    cm = card_re.search(line)
    if cm:
        cards.append({
            'word':    cm.group(1),
            'article': cm.group(2),
            'en':      cm.group(3),
            'cat':     cm.group(4),
            'diff':    cm.group(5),
        })

# Re-categorize mapping
# Keep these as-is when already correct
KEEP = {'animals', 'food', 'colors', 'numbers'}

# Word → new category overrides (specific words)
OVERRIDES = {
    # Home / house / furniture / hotel room
    'Haus': 'home', 'Bett': 'home', 'Lampe': 'home', 'Stuhl': 'home',
    'Sessel': 'home', 'Fenster': 'home', 'Tür': 'home', 'Tisch': 'home',
    'Schreibtisch': 'home', 'Regal': 'home', 'Zimmer': 'home',
    'Balkon': 'home', 'Dusche': 'home', 'Handtuch': 'home',
    'Toilettenpapier': 'home', 'Zimmersafe': 'home', 'Haartrockner': 'home',
    'Hosenbügler': 'home', 'WLAN': 'home', 'Wellnessbereich': 'home',
    'Rezeption': 'home', 'Schlüssel': 'home', 'Schwimmbad': 'home',

    # Office / work / school / tech
    'Buch': 'office', 'Stift': 'office', 'Heft': 'office',
    'Drucker': 'office', 'Computer': 'office', 'Bildschirm': 'office',
    'Kopierer': 'office', 'Scanner': 'office', 'Tablet': 'office',
    'Telefon': 'office', 'Handy': 'office', 'Bürostuhl': 'office',
    'Brille': 'office', 'Terminkalender': 'office', 'Kaffeemaschine': 'office',
    'Papierkorb': 'office', 'Verwaltung': 'office', 'Sekretariat': 'office',
    'Bibliothek': 'office', 'Schule': 'office', 'Universität': 'office',
    'Kurs': 'office', 'Beruf': 'office', 'Rechnung': 'office',
    'Problem': 'office', 'Zeitung': 'office', 'Literatur': 'office',
    'Gedicht': 'office', 'Bild': 'office', 'Saxofon': 'leisure',  # moved below
    'Uhr': 'office',

    # City / places / buildings / transport
    'Stadt': 'city', 'Straße': 'city', 'Bahnhof': 'city',
    'Geschäft': 'city', 'Platz': 'city', 'Park': 'city',
    'Tiefgarage': 'city', 'Parkplatz': 'city', 'Adresse': 'city',
    'Museum': 'city', 'Theater': 'city', 'Oper': 'city',
    'Kino': 'city', 'Rathaus': 'city', 'Bank': 'city',
    'Post': 'city', 'Apotheke': 'city', 'Café': 'city',
    'Supermarkt': 'city', 'Fitnesscenter': 'city', 'Sporthalle': 'city',
    'Auto': 'city', 'Motorrad': 'city', 'Fahrrad': 'city',
    'Baum': 'city', 'Blume': 'city',

    # Leisure / sports / music / hobbies
    'Sport': 'leisure', 'Fußball': 'leisure', 'Tennis': 'leisure',
    'Pingpong': 'leisure', 'Ski': 'leisure', 'Golf': 'leisure',
    'Gymnastik': 'leisure', 'Spielkarte': 'leisure', 'Schach': 'leisure',
    'Yoga': 'leisure', 'Gitarre': 'leisure', 'Trompete': 'leisure',
    'Klavier': 'leisure', 'Saxofon': 'leisure', 'Tango': 'leisure',
    'Salsa': 'leisure', 'Walzer': 'leisure',

    # People / time / abstract
    'Mann': 'people', 'Frau': 'people', 'Kind': 'people', 'Chef': 'people',
    'Name': 'people', 'Nummer': 'people', 'Tag': 'people',
    'Nacht': 'people', 'Zeit': 'people', 'Jahr': 'people',
    'Woche': 'people', 'Preis': 'people',

    # Food (places that belong to food: canteens, cafés)
    'Kantine': 'food', 'Mensa': 'food', 'Cafeteria': 'food',
    'Kreditkarte': 'office',
}

# Override water → put in food (drinks)
OVERRIDES['Wasser'] = 'food'

# Food (kitchen tools fall here too — they're food-adjacent)
FOOD_WORDS = {
    'Tasse', 'Suppenteller', 'Wischtuch', 'Serviette', 'Gabel', 'Salz',
    'Wasserglas', 'Weinglas', 'Kaffeelöffel', 'Messer', 'Kochbuch',
    'Küchenmesser', 'Pfanne', 'Schüssel', 'Teller', 'Löffel', 'Pfeffer', 'Topf',
}
for w in FOOD_WORDS:
    OVERRIDES[w] = 'food'

# Apply mapping
for c in cards:
    if c['cat'] in KEEP:
        # food category: keep, but words like utensils were already there
        new_cat = OVERRIDES.get(c['word'], c['cat'])
    else:
        new_cat = OVERRIDES.get(c['word'], 'people')  # fallback: people for unmapped 'everyday'
    c['new_cat'] = new_cat

# Group by new cat for output
from collections import defaultdict
by_cat = defaultdict(list)
for c in cards:
    by_cat[c['new_cat']].append(c)

# Order: animals, food, colors, numbers, home, office, city, leisure, people
ORDER = ['animals', 'food', 'colors', 'numbers', 'home', 'office', 'city', 'leisure', 'people']

# Build new CARDS body
max_word = max(len(c['word']) for c in cards)
max_en = max(len(c['en']) for c in cards)
max_cat = max(len(c['new_cat']) for c in cards)

lines = []
for cat in ORDER:
    if cat not in by_cat:
        continue
    items = by_cat[cat]
    # sort by difficulty then word
    items.sort(key=lambda c: (c['diff'], c['word']))
    lines.append(f"  // {cat.capitalize()}")
    for c in items:
        wp = (f"'{c['word']}',").ljust(max_word + 3)
        ap = f"article:'{c['article']}',"
        ep = (f"'{c['en']}',").ljust(max_en + 3)
        cp = (f"'{c['new_cat']}',").ljust(max_cat + 3)
        lines.append(
            f"  {{ word:{wp} {ap} en:{ep} cat:{cp} diff:'{c['diff']}' }},"
        )

new_body = "\n".join(lines)
new_src = src[:m.start()] + f"const CARDS = [\n{new_body}\n];" + src[m.end():]
HTML.write_text(new_src)

# Report
print(f"Re-categorized {len(cards)} cards", file=sys.stderr)
for cat in ORDER:
    if cat in by_cat:
        print(f"  {cat}: {len(by_cat[cat])}", file=sys.stderr)
unmapped = [c['word'] for c in cards if c['new_cat'] == 'people' and c['cat'] == 'everyday']
if unmapped:
    print(f"\nFell back to 'people' (verify): {unmapped}", file=sys.stderr)
