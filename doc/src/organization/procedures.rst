GeoMop Development Procedures (czech)
=====================================

Tento dokument popisuje postupy používané pri vývoji aplikace

Adresářová struktura
====================

..
   doc
      src
   po
   src
      LayerEditor
      lib
      locale
   testing

Popis:
   doc/src - vývojářská dokumentace
   po - adresář s překlady
   src/LayerEditor - Modul pro zobrazení a úpravu vrstev
   src/lib - Modul s knihovnami používanými ostatními moduly
   src/locale - Adresář s překlady (mo soubory) generovanými v po adresáři
   testing - Automatické testy 

Kontrola kódu
=============
Pro kontrolu se používá _`pyLint <www.pylint.org>`. V hlavním adresáři každého 
modulu je soubor pylintrc, v kterém se píší pravidla pro vyjímky. Další vyjímky
je možné napsat na začátek souboru. Pravidla pro tyto vyjímky budou vznikat 
během vývoje a budou zapisovány do :doc:`zvláštního souboru <pylint_rules>`.

Bohužel s kontrolou kódu nemám zkušenosti a některé požadavky vyplynou až během 
vývoje. Proto zde popíši oblasti, na které by jsem se chtěl při kontrole kódu 
zaměřit a to co nekontrolovat vyplyne z porovnání poměru režie/přínos. To co
nebude odpovídat mé představě o programování vyřadím. Bohužel zatím mám spíše
dojem, že to nabízenými nástroji nedokáži udělat dostatečně adresně, aby zůstalo
zachováno i co se mi líbí. Přehled kontrolovaných oblastí je 
_`zde <http://docs.pylint.org/features.html>`.

**Odsazení**
V Pythonu asi nezbytnost.

**prázné znaky na konci řádků**
Je to dost otrava
* zjistit zda to může něčemu vadit
* zjistit zda to něco neumí udělat automaticky

**Pravidla psaní kódu**
Jednotná pravidla psaní kódu jsou hezká a asi i něco zvýší přehlednost kódu. 
Sice to není nijak zvlášt důležité, ale předpokládám že po několika kontrolách
pylintem přejdou do krve a nebudou moc zdržovat. 

Pylint používá konvenci _`PEP 0008 <https://www.python.org/dev/peps/pep-0008/>`

**Konvence pojmenování souborů, tříd, proměnných ...**
Pylint pro kontrolu názvů používá tuto 
_`konvenci <http://pylint-messages.wikidot.com/messages:c0103>'. O tomto platí
to samé jako o předcházejícím. Mě nedělá problém číst kód napsaný jakoukoliv
konvencí, spíš jí mám problém udržet. Doufám že pomocí pylintu bude můj kód, 
co se týká jednotnosti pojmenování, konzistentní. Škoda že to neumí hledat
české názvy.

Trochu mě vadí pravidlo, že globální proměnná mimo třídu má být konstatnta
* zjistit zda to lze vypnout globálně a ponechat kontrolu ostatních názvů
* zjistit proč je to považováno za problém

**Kontrola použití lokální proměnné (_xxx) jiného modulu**
* zjistit zda to pylint dělá

**Starý styl vytvoření třídy**
super-on-old-class (E1002)
* s někým se poradit a zjistit co to dělá

Vývojářska Dokumentace
======================
Část Dokumentace je psaná v _`reStructuredText <http://sphinx-doc.org/rest.html#paragraphs>`
V sou4asnosti jde o organizační pokyny v adresáři doc/src/organization

Uživatelská Dokumentace
=======================
Dokumentace je psaná v _`reStructuredText <http://sphinx-doc.org/rest.html#paragraphs>`


Lokalizace
==========

Testování
=========

Build
=====


