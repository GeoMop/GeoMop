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
Pro kontrolu se používá `pyLint <www.pylint.org>`_. V hlavním adresáři každého 
modulu je soubor pylintrc, v kterém se píší pravidla pro vyjímky. Další vyjímky
je možné napsat na začátek souboru. Pravidla pro tyto vyjímky budou vznikat 
během vývoje a budou zapisovány do :doc:`zvláštního souboru <pylint_rules>`.

Bohužel s kontrolou kódu nemám zkušenosti a některé požadavky vyplynou až během 
vývoje. Proto zde popíši oblasti, na které by jsem se chtěl při kontrole kódu 
zaměřit a to co nekontrolovat vyplyne z porovnání poměru režie/přínos. To co
nebude odpovídat mé představě o programování vyřadím. Bohužel zatím mám spíše
dojem, že to nabízenými nástroji nedokáži udělat dostatečně adresně, aby zůstalo
zachováno i co se mi líbí. Přehled kontrolovaných oblastí je 
`zde <http://docs.pylint.org/features.html>`_.

**Odsazení**

V Pythonu asi nezbytnost.

**prázné znaky na konci řádků**

Je to dost otrava
  * *zjistit zda to může něčemu vadit*
  * *zjistit zda to něco neumí udělat automaticky*

**Pravidla psaní kódu**

Jednotná pravidla psaní kódu jsou hezká a asi i něco zvýší přehlednost kódu. 
Sice to není nijak zvlášt důležité, ale předpokládám že po několika kontrolách
pylintem přejdou do krve a nebudou moc zdržovat. 

Pylint používá konvenci `PEP 0008 <https://www.python.org/dev/peps/pep-0008/>`_

**Konvence pojmenování souborů, tříd, proměnných ...**

Pylint pro kontrolu názvů používá tuto 
`konvenci <http://pylint-messages.wikidot.com/messages:c0103>`_. O tomto platí
to samé jako o předcházejícím. Mě nedělá problém číst kód napsaný jakoukoliv
konvencí, spíš jí mám problém udržet. Doufám že pomocí pylintu bude můj kód, 
co se týká jednotnosti pojmenování, konzistentní. Škoda že to neumí hledat
české názvy.

Trochu mě vadí pravidlo, že globální proměnná mimo třídu má být konstatnta
  * *zjistit zda to lze vypnout globálně a ponechat kontrolu ostatních názvů*
  * *zjistit proč je to považováno za problém*

**Kontrola použití lokální proměnné (_xxx) jiného modulu**

  * *zjistit zda to pylint dělá*

**Starý styl vytvoření třídy**

super-on-old-class (E1002)
  * *s někým se poradit a zjistit co to dělá*

Vývojářska Dokumentace
======================
Dokumentace je psaná v `reStructuredText <http://sphinx-doc.org/rest.html#paragraphs>`_ 
a do finální podoby generována pomocí `sphinx <http://sphinx-doc.org/index.htmls>`_.
`reStructuredText <http://sphinx-doc.org/rest.html#paragraphs>`_ je docstring formát a 
`sphinx <http://sphinx-doc.org/index.htmls>`_ pak umožnuje dodat pěkné formátování textu 
a vygenerovat požadovaný formát dokumentu. Generovat celou vývojářskou dokumentaci je možné
z adresáře doc/src/ pomocí make a požadovaného formátu. Například::
  make html

Dokumentace se skládá z organizačních pokynů v adresáři doc/src/organization a z dokumentace 
zdrojových kódů. Ta je automaticky generována po jednotlivých GeoMop modulech pomocí sphinx modulu 
`sphinx <http://sphinx-doc.org/man/sphinx-apidoc.html>`_ příkazem umístěným v Makefile::
  modules.lib.rst: 
	  sphinx-apidoc -o ./aut -s .rst ../../src/lib/
	  mv aut/modules.rst aut/lib.rst
a začleněna do index.rst (odkaz na soubor aut/lib.rst)

`sphinx <http://sphinx-doc.org/index.htmls>`_ není úplně jednoduchý nástroj na osvojení a je 
primárně určený na psaní dokumentace obecně. Naopak jako nástroj pro generování dokumentace 
ze zdrojových kódů není ideální a má mnoho much. Ale alternativy již nejsou zrovna aktivně
vyvíjený a `sphinx <http://sphinx-doc.org/index.htmls>`_ následně můžeme použít i na psaní
uživatelské dokumentace.

  * *Je potřeba ujasnit co bude šířený spolu s programem (Podle licencování celého programu)*
  * *Asi by bylo dobré ji vždy přegenerovat ve formátu html a někam vystavit*

Uživatelská Dokumentace
=======================
Dokumentace bude asi psaná v `reStructuredText <http://sphinx-doc.org/rest.html#paragraphs>`_ a 
do finální podoby generována pomocí `sphinx <http://sphinx-doc.org/index.htmls>`_.

Lokalizace
==========

**Překlady**

Ve zdrojovém kódu jsou texty uzavřeny funkcí _() a překlad zajištěn pomocí::
  from lang_le import gettext as _
  _messageSplitter.setWindowTitle(_("GeoMop Layer Editor"))
lang_le je pak modul specifik soubor umístěný do kořenového adresáře GeoMop modulu.

Překlady je pak možné získat ze zdrojáků příkazem::
  make po
Po přeložení po souborů, umístěných v jazyk specifik adresářích je možné vygenerovat
mo soubory příkazem::
  make mo
nebo vygenerovat a nakopírovat do lokálního adresáře src/locale příkazem::
  make copy
po nakopírování souborů do lokálního adresáře by měli být překlady funkční na lokálním
prostředí.

  * *dodělat do po/Makefile globální slovník, který bude překlady šoupat mezi moduli*
  * *dodělat do po/Makefile mechanizmus pro vytvoření jednoho po souboru s nepřeloženými 
    texty a zakomponování překladů z tohoto souboru po překladu zpět do po souborů*

Testování
=========

Pro psaní automatických testů je použit `pyTest <http://pytest.org/latest/>`_. Testy
je možné lokálně spustit z testing adresáře příkazem::
  RunTests.sh
V budoucnu je třeba spouštět testy automaticky po každém poslání do gitu nejlépe na 
deployi ve virtuálním prostředí.

  * *Určitě by se měla testovat přítomnost a inicializace všech částí aplikace a kde to
    jde by se měl udělat i integrační test. U unit testů si nejsem jist jak definovat
    požadovaný stav co testovat. Zatímco u některých částí je velmi přínosné pokoušet
    se o úplné testy, jinde to může být velice neefektivní a nevím zda si to můžeme
    z časového hlediska dovolit. Zatím to studui.*
  * *Zjistit jak dělat a co umí UI Testy a podle výsledku se rozhodnout co dělat.*

Požadavky na vývojový PC
========================

Vše je psané pro Linux. Pokud by se mělo vyvíjet i na window, je nutné tam nainstalovat
maketool a asi napsat nějaké alternativy k sh skriptům, ale ten je použit jen pro testy.
  * *dodělat, dohodnout se zda podporovat windows*
  * *dopsat posat postup instalace na vývojový stroj (asi instalace požadavků pro GeoMop +
    požadavků pro vývoj)*

IDE
===
Je možné používat IDE dle uvážení. Projektové soubory se do Gitem neverzují. Každý je 
zodpovědný za to aby mu to fungovalo na jeho Počítači.

Možnosti:
  * Eclipse + `PyDev <http://pydev.org/manual_101_root.html>`_ - netestoval jsem, eclipse 
    nemám rád
  * `PyCharm <https://www.jetbrains.com/pycharm/>`_ - měl problémy s qt a nenašel jsem 
    rychle přijatelné řešení , ale jinak docela dobré
  * `Eric IDE <https://www.jetbrains.com/pycharm/>`_ - není s ním úplně jednoduché začít
    vyvíjet, ale když si na něj člověk zvykne ... . Tento nástroj budu používat asi já,
    takže budu schopný poradit a asi v něm půjde i generovat z docstringů i bublinková
    nápověda pro náš kód.

Build
=====

  * *rozhodnout jaké instalační balíčky a systémy podporovat a dopsat*
