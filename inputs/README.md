# A dolgozat bemenetei

A dolgozat bemenetei találhatóak meg a mappában. Külön mappát kapott a formális és informális szövegek bemenete. ezen kívül az init mappában található a karakter szótár, amely minden get_inform.py és get_form.py futtatásakor beolvasódik.

**form mappa tartalma**
- lexikons: a lexikonokat tárolja
- norm: a letöltött normalizást szövegeket tárolja
- orig: a letöltött betűhű szövegeket tárolja

**inform mappa tartalma**
- lexikons: a lexikonokat tárolja
- tmk_all.txt: az összes szót tartalmazó fájl
- minden más: a külön fajtánkénti találatok bemeneti fájljai TSV formátumban

**init mappa**
- cahr_map.txt: karakter szótár