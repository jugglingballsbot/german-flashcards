#!/usr/bin/env python3
"""Parse Antonio's word list (Kapitel 1-4) and emit JS lines."""

EXISTING = {
    'Haus', 'Tür', 'Tisch', 'Fenster', 'Apfel', 'Banane',
    'Milch', 'Käse', 'Maus', 'Gemüse', 'Straße',
}

ENTRIES = [
    # Kapitel 1
    ('das Bett', 'bed', 'everyday'),

    # Kapitel 2
    ('das Buch', 'book', 'everyday'),
    ('der Stift', 'pen', 'everyday'),
    ('das Telefon', 'telephone', 'everyday'),
    ('die Tasse', 'cup', 'food'),
    ('das Heft', 'notebook', 'everyday'),
    ('die Lampe', 'lamp', 'everyday'),
    ('der Drucker', 'printer', 'everyday'),
    ('der Stuhl', 'chair', 'everyday'),
    ('der Schreibtisch', 'desk', 'everyday'),
    ('der Computer', 'computer', 'everyday'),
    ('der Schlüssel', 'key', 'everyday'),
    ('die Brille', 'glasses', 'everyday'),
    ('der Terminkalender', 'planner', 'everyday'),
    ('das Handy', 'mobile phone', 'everyday'),
    ('die Kaffeemaschine', 'coffee machine', 'everyday'),
    ('der Bürostuhl', 'office chair', 'everyday'),
    ('der Bildschirm', 'screen', 'everyday'),
    ('der Kopierer', 'copier', 'everyday'),
    ('das Regal', 'shelf', 'everyday'),
    ('der Papierkorb', 'wastebasket', 'everyday'),
    ('der Scanner', 'scanner', 'everyday'),
    ('das Tablet', 'tablet', 'everyday'),
    ('die Uhr', 'clock/watch', 'everyday'),
    ('das Auto', 'car', 'everyday'),
    ('die Verwaltung', 'administration', 'everyday'),
    ('die Kantine', 'company canteen', 'everyday'),
    ('die Mensa', 'university canteen', 'everyday'),
    ('die Cafeteria', 'cafeteria', 'everyday'),
    ('die Bibliothek', 'library', 'everyday'),
    ('das Sekretariat', 'secretariat', 'everyday'),
    ('die Sporthalle', 'gym hall', 'everyday'),
    ('die Zeitung', 'newspaper', 'everyday'),
    ('die Gymnastik', 'gymnastics', 'everyday'),
    ('der Sport', 'sport', 'everyday'),
    ('der Fußball', 'football', 'everyday'),
    ('das Fahrrad', 'bicycle', 'everyday'),
    ('das Tennis', 'tennis', 'everyday'),
    ('das Pingpong', 'ping pong', 'everyday'),
    ('der Tango', 'tango', 'everyday'),
    ('die Spielkarte', 'playing card', 'everyday'),
    ('der Ski', 'ski', 'everyday'),
    ('der Golf', 'golf', 'everyday'),
    ('die Gitarre', 'guitar', 'everyday'),
    ('die Trompete', 'trumpet', 'everyday'),
    ('das Klavier', 'piano', 'everyday'),
    ('das Schach', 'chess', 'everyday'),
    ('die Literatur', 'literature', 'everyday'),
    ('der Salsa', 'salsa', 'everyday'),
    ('das Motorrad', 'motorcycle', 'everyday'),
    ('das Gedicht', 'poem', 'everyday'),
    ('das Yoga', 'yoga', 'everyday'),
    ('der Walzer', 'waltz', 'everyday'),
    ('die Nummer', 'number', 'everyday'),
    ('der Name', 'name', 'everyday'),
    ('das Bild', 'picture', 'everyday'),
    ('das Problem', 'problem', 'everyday'),
    ('der Kurs', 'course', 'everyday'),
    ('das Saxofon', 'saxophone', 'everyday'),
    ('die Rechnung', 'bill', 'everyday'),
    ('der Beruf', 'profession', 'everyday'),

    # Kapitel 3
    ('der Bahnhof', 'train station', 'everyday'),
    ('das Geschäft', 'shop', 'everyday'),
    ('der Platz', 'square', 'everyday'),
    ('der Park', 'park', 'everyday'),
    ('der Preis', 'price', 'everyday'),
    ('die Tiefgarage', 'underground garage', 'everyday'),
    ('der Parkplatz', 'parking lot', 'everyday'),
    ('das Fitnesscenter', 'fitness center', 'everyday'),
    ('die Adresse', 'address', 'everyday'),
    ('der Haartrockner', 'hair dryer', 'everyday'),
    ('die Dusche', 'shower', 'everyday'),
    ('die Kreditkarte', 'credit card', 'everyday'),
    ('der Zimmersafe', 'room safe', 'everyday'),
    ('der Balkon', 'balcony', 'everyday'),
    ('der Hosenbügler', 'trouser press', 'everyday'),
    ('das WLAN', 'Wi-Fi', 'everyday'),
    ('das Zimmer', 'room', 'everyday'),
    ('der Sessel', 'armchair', 'everyday'),
    ('das Handtuch', 'towel', 'everyday'),
    ('das Toilettenpapier', 'toilet paper', 'everyday'),
    ('der Wellnessbereich', 'wellness area', 'everyday'),
    ('die Rezeption', 'reception', 'everyday'),
    ('das Schwimmbad', 'swimming pool', 'everyday'),
    ('das Museum', 'museum', 'everyday'),
    ('das Theater', 'theater', 'everyday'),
    ('die Oper', 'opera', 'everyday'),
    ('das Kino', 'cinema', 'everyday'),
    ('das Rathaus', 'town hall', 'everyday'),
    ('die Bank', 'bank', 'everyday'),
    ('die Post', 'post office', 'everyday'),
    ('die Universität', 'university', 'everyday'),
    ('die Apotheke', 'pharmacy', 'everyday'),
    ('das Café', 'café', 'everyday'),
    ('der Supermarkt', 'supermarket', 'everyday'),

    # Kapitel 4 — food
    ('der Orangensaft', 'orange juice', 'food'),
    ('der Kaffee', 'coffee', 'food'),
    ('der Kräutertee', 'herbal tea', 'food'),
    ('das Brötchen', 'bread roll', 'food'),
    ('das Vollkornbrot', 'whole grain bread', 'food'),
    ('das Weißbrot', 'white bread', 'food'),
    ('das Toastbrot', 'toast bread', 'food'),
    ('der Schinken', 'ham', 'food'),
    ('die Salami', 'salami', 'food'),
    ('die Leberwurst', 'liver sausage', 'food'),
    ('der Lachs', 'salmon', 'food'),
    ('das Rührei', 'scrambled eggs', 'food'),
    ('die Pflaume', 'plum', 'food'),
    ('die Aprikose', 'apricot', 'food'),
    ('die Birne', 'pear', 'food'),
    ('die Butter', 'butter', 'food'),
    ('die Margarine', 'margarine', 'food'),
    ('der Frischkäse', 'cream cheese', 'food'),
    ('die Marmelade', 'jam', 'food'),
    ('der Honig', 'honey', 'food'),
    ('der Suppenteller', 'soup plate', 'food'),
    ('das Wischtuch', 'dishcloth', 'food'),
    ('die Serviette', 'napkin', 'food'),
    ('die Gabel', 'fork', 'food'),
    ('das Salz', 'salt', 'food'),
    ('das Wasserglas', 'water glass', 'food'),
    ('das Weinglas', 'wine glass', 'food'),
    ('der Kaffeelöffel', 'coffee spoon', 'food'),
    ('das Messer', 'knife', 'food'),
    ('das Kochbuch', 'cookbook', 'food'),
    ('das Küchenmesser', 'kitchen knife', 'food'),
    ('die Pfanne', 'pan', 'food'),
    ('die Schüssel', 'bowl', 'food'),
    ('der Teller', 'plate', 'food'),
    ('der Löffel', 'spoon', 'food'),
    ('der Pfeffer', 'pepper', 'food'),
    ('der Topf', 'pot', 'food'),
    ('die Tomatensuppe', 'tomato soup', 'food'),
    ('das Schnitzel', 'schnitzel', 'food'),
    ('der Rindergulasch', 'beef goulash', 'food'),
    ('der Steinbutt', 'turbot', 'food'),
    ('der Obstsalat', 'fruit salad', 'food'),
    ('die Erdbeere', 'strawberry', 'food'),
    ('die Gemüsesuppe', 'vegetable soup', 'food'),
    ('der Schweinebraten', 'pork roast', 'food'),
    ('die Forelle', 'trout', 'food'),
    ('der Apfelkuchen', 'apple cake', 'food'),
    ('der Chef', 'chef/boss', 'everyday'),
]

clean = []
for de_full, en, cat in ENTRIES:
    article, _, word = de_full.partition(' ')
    if not word or word in EXISTING or article not in ('der', 'die', 'das'):
        continue
    clean.append((word, article, en, cat))

seen = set()
unique = []
for e in clean:
    if e[0] in seen:
        continue
    seen.add(e[0])
    unique.append(e)

max_word = max(len(e[0]) for e in unique)
max_en = max(len(e[2]) for e in unique)

from collections import defaultdict
groups = defaultdict(list)
for w, a, en, cat in unique:
    groups[cat].append((w, a, en))

lines = []
for cat in ['everyday', 'food']:
    if cat not in groups:
        continue
    lines.append(f"  // --- {cat} (added 2026-06-14, Kapitel 1-4) ---")
    for w, a, en in groups[cat]:
        wp = (f"'{w}',").ljust(max_word + 3)
        ap = f"article:'{a}',"
        ep = (f"'{en}',").ljust(max_en + 3)
        lines.append(f"  {{ word:{wp} {ap} en:{ep} cat:'{cat}', diff:'A1' }},")

print("\n".join(lines))
import sys
print(f"\n# Total added: {len(unique)} ({len(groups['everyday'])} everyday, {len(groups['food'])} food)", file=sys.stderr)
