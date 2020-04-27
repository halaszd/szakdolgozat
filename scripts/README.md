# Szakdolgozathoz használt szkriptek

## Informális szövegek feldolgozása: get_inform.py

**Használata:** `python3 get_inform.py <bemeneti útvonalak> -c <karakter szótár útvonala> -d <kimeneti mappa útvonala> -e <szótárat hozzon létre vagy ne> -f <kimeneti fájlnév> -m <lexikon útvonala> -r <corpusz útvonala, amiben benne van az össze szó> -t <múlt idő típusa>`

**Perfektum + volt szótár létrehozása:**
`python3 get_inform.py ../inputs/inform/tmk_perf_volt.txt -d ../inputs/inform/lexicons -f perf_volt.txt -e -t inform.,perf.,volt`

**Imperfektum + volt szótár létrehozása:**
`python3 get_inform.py ../inputs/inform/tmk_imp_volt.txt -d ../inputs/inform/lexicons -f imp_volt.txt -e -t inform.,imp.,volt`

**Perfektum + vala szótár létrehozása:**
`python3 get_inform.py ../inputs/inform/tmk_perf_vala.txt -d ../inputs/inform/lexicons -f perf_vala.txt -e -t inform.,perf.,vala`

**Imperfektum + vala szótár létrehozása:**
`python3 get_inform.py ../inputs/inform/tmk_imp_vala.txt -d ../inputs/inform/lexicons -f imp_vala.txt -e -t inform.,imp.,vala`

**Diszkriminatív volt frekvencia lista:**
`python3 get_inform.py ../inputs/inform/tmk_volt.txt -d ../outputs/inform/freqs -f volt_discr.txt -t inform,,volt -m "../outputs/inform/lexicons/*_volt.txt"`

**Non diszkriminatív volt frekvencia lista:**
`python3 get_inform.py ../inputs/inform/tmk_volt.txt -d ../outputs/inform/freqs -f volt_nondiscr.txt -t inform,,volt`

**Diszkriminatív vala frekvencia lista:**
`python3 get_inform.py ../inputs/inform/tmk_vala.txt -d ../outputs/inform/freqs -f vala_discr.txt -t inform,,vala -m "../outputs/inform/lexicons/*_vala.txt"`

**Non diszkriminatív vala frekvencia lista:**
`python3 get_inform.py ../inputs/inform/tmk_vala.txt -d ../outputs/inform/freqs -f vala_nondiscr.txt -t inform,,vala`

**Perfektum + volt frekvencia lista:**
`python3 get_inform.py ../inputs/inform/tmk_perf_volt.txt -d ../outputs/inform/freqs -f perf_volt.txt -t inform,perf,volt`

**Imerfektum + volt frekvencia lista:**
`python3 get_inform.py ../inputs/inform/tmk_imp_volt.txt -d ../outputs/inform/freqs -f imp_volt.txt -t inform,imp,volt`

**Perfektum + vala frekvencia lista:**
`python3 get_inform.py ../inputs/inform/tmk_perf_vala.txt -d ../outputs/inform/freqs -f perf_vala.txt -t inform,perf,vala`

**Imperfektum + vala frekvencia lista:**
`python3 get_inform.py ../inputs/inform/tmk_imp_vala.txt -d ../outputs/inform/freqs -f imp_vala.txt -t inform,imp,vala`


## formális szövegek feldolgozása: get_form.py

**Használata:** `python3 get_form.py <bemeneti útvonalak> -c <karakter szótár útvonala> -d <kimeneti mappa útvonala> -e <szótárat hozzon létre vagy ne> -f <kimeneti fájlnév> -l <default lexikonok használata> -m <opcionális lexikon útvonala> -t <múlt idő típusa> -x <A lexikont kizáró értelemben használja-e>`

**Perfektum + volt kézileg ellenőrizendő szótár létrehozása:**
`python3 get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../inputs/form/lexicons -f perf_volt.txt -e -t form.,perf.,volt`

**Imperfektum + volt kézileg ellenőrizendő szótár létrehozása:**
`python3 get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../inputs/form/lexicons -f imp_volt.txt -e -t form.,imp.,volt -m "../outputs/form/lexicons/*perf_volt.txt" -x`

**Perfektum + vala kézileg ellenőrizendő szótár létrehozása:**
`python3 python get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../inputs/form/lexicons -f perf_vala.txt -e -t form.,perf.,vala`

**Imperfektum + vala kézileg ellenőrizendő szótár létrehozása:**
`python3 get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../inputs/form/lexicons -f imp_vala.txt -e -t form.,imp.,vala -m "../outputs/form/lexicons/*perf_vala.txt" -`

**Diszkriminatív volt frekvencia lista:**
`python3 get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../outputs/form/freqs -f volt_discr.txt -t form,,volt -m "../outputs/form/lexicons/*_volt.txt" -x`

**Non diszkriminatív volt frekvencia lista:**
`python3 get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../outputs/form/freqs -f volt_nondiscr.txt -t inform,,volt`

**Diszkriminatív vala frekvencia lista:**
`python3 get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../outputs/form/freqs -f vala_discr.txt -t form,,vala -m "../outputs/inform/lexicons/*_vala.txt" -x`

**Non diszkriminatív vala frekvencia lista:**
`python3 get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../outputs/form/freqs -f vala_nondiscr.txt -t form,,vala`

**Perfektum + volt frekvencia lista:**
`python3 get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../outputs/form/freqs -f perf_volt.txt -t form,perf,volt -l`

**Imerfektum + volt frekvencia lista:**
`python3 get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../outputs/form/freqs -f imp_volt.txt -t form,imp,volt -l`

**Perfektum + vala frekvencia lista:**
`python3 get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../outputs/form/freqs -f perf_vala.txt -t form,perf,vala -l`

**Imperfektum + vala frekvencia lista:**
`python3 get_form.py ../inputs/form/orig/* ..inputs/form/norm/* -d ../outputs/form/freqs -f imp_vala.txt -t form,imp,vala -l`


## diagramok létrehozása: create_plot.py

**Használata:** `python3 <bemeneti útvonalak> -i <éves bontás> -m <eltérő kezdeti és/vagy utolsó évszámok>`

**Informális perfektum/imperfektum + vala/volt**
`python3 create_plot.py ../outputs/inform/freqs/_v*.txt -i 50`

**Informális puszta vala/volt**
`python3 create_plot.py ../outputs/inform/freqs/*_discr.txt -i 50`

**Informális összes vala/volt**
`python3 create_plot.py ../outputs/inform/freqs/*_nondiscr.txt -i 50`


**Formális perfektum/imperfektum + vala/volt**
`python3 create_plot.py ../outputs/form/freqs/_v*.txt -i 50`

**Formális puszta vala/volt**
`python3 create_plot.py ../outputs/form/freqs/*_discr.txt -i 50`

**Formális összes vala/volt**
`python3 create_plot.py ../outputs/form/freqs/*_nondiscr.txt -i 50`


**Informális és formális: perfektum**
`python3 create_plot.py ../outputs/inform/freqs/perf_*.txt ../outputs/form/freqs/perf_*.txt -i 30 -m`

**Informális és formális: puszta vala/volt**
`python3 create_plot.py ../outputs/inform/freqs/*_discr.txt ../outputs/form/freqs/*_discr.txt -i 30 -m`


## A get_form.py és get_inform.py közös függvényei: common.py

## Az Unicode-karakterek összegyüjtéséért felelős szkript: find_chars.py