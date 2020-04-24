# Szakdolgozathoz használt szkriptek

## Informális szövegek feldolgozása: get_inform.py

**Perfektum + volt szótár létrehozása:**
`python get_inform.py ../inputs/inform/tmk_perf_volt.txt -d ../inputs/inform/lexicons -f perf_volt.txt -e -t inform.,perf.,volt`

**Imperfektum + volt szótár létrehozása:**
`python get_inform.py ../inputs/inform/tmk_imp_volt.txt -d ../inputs/inform/lexicons -f imp_volt.txt -e -t inform.,imp.,volt`

**Perfektum + vala szótár létrehozása:**
`python get_inform.py ../inputs/inform/tmk_perf_vala.txt -d ../inputs/inform/lexicons -f perf_vala.txt -e -t inform.,perf.,vala`

**Imperfektum + vala szótár létrehozása:**
`python get_inform.py ../inputs/inform/tmk_imp_vala.txt -d ../inputs/inform/lexicons -f imp_vala.txt -e -t inform.,imp.,vala`

**Diszkriminatív volt frekvencia lista:**
`python get_inform.py ../inputs/inform/tmk_volt.txt -d ../outputs/inform/freqs -f volt_discr.txt -t inform,,volt -m "../outputs/inform/lexicons/*_volt.txt"`

**Non diszkriminatív volt frekvencia lista:**
`python get_inform.py ../inputs/inform/tmk_volt.txt -d ../outputs/inform/freqs -f volt_nondiscr.txt -t inform,,volt`

**Diszkriminatív vala frekvencia lista:**
`python get_inform.py ../inputs/inform/tmk_vala.txt -d ../outputs/inform/freqs -f vala_discr.txt -t inform,,vala -m "../outputs/inform/lexicons/*_vala.txt"`

**Non diszkriminatív vala frekvencia lista:**
`python get_inform.py ../inputs/inform/tmk_vala.txt -d ../outputs/inform/freqs -f vala_nondiscr.txt -t inform,,vala`

**Perfektum + volt frekvencia lista:**
`python get_inform.py ../inputs/inform/tmk_perf_volt.txt -d ../outputs/inform/freqs -f perf_volt.txt -t inform,perf,volt`

**Imerfektum + volt frekvencia lista:**
`python get_inform.py ../inputs/inform/tmk_imp_volt.txt -d ../outputs/inform/freqs -f imp_volt.txt -t inform,imp,volt`

**Perfektum + vala frekvencia lista:**
`python get_inform.py ../inputs/inform/tmk_perf_vala.txt -d ../outputs/inform/freqs -f perf_vala.txt -t inform,perf,vala`

**Imperfektum + vala frekvencia lista:**
`python get_inform.py ../inputs/inform/tmk_imp_vala.txt -d ../outputs/inform/freqs -f imp_vala.txt -t inform,imp,vala`


## formális szövegek feldolgozása: get_form.py


