GeoMop Development Procedures (czech)
=====================================

Tento dokument popisuje postupy používané pri vývoji aplikace

Adresářová struktura
====================
Adresářová struktura 
je::

  doc
  	src
  src
  	LayerEditor
  	lib
  testing

Popis:
  * doc/src - vývojářská dokumentace
  * src/LayerEditor - Modul pro zobrazení a úpravu vrstev
  * src/lib - Modul s knihovnami používanými ostatními moduly
  * testing - Automatické testy 

Kontrola kódu
=============
Pro kontrolu se používá `pyLint <www.pylint.org>`_. V hlavním adresáři každého 
modulu je soubor pylintrc, v kterém se píší pravidla pro vyjímky. Další vyjímky
je možné napsat na začátek souboru, nebo nad vyjmutý řádek. Pravidla pro tyto 
vyjímky budou vznikat během vývoje a budou zapisovány do :doc:`samostatného souboru 
<pylint_rules>`.

Bohužel s kontrolou kódu nemám zkušenosti a některé požadavky vyplynou až během 
vývoje. Proto zde popíši oblasti, na které by jsem se chtěl při kontrole kódu 
zaměřit a to co nekontrolovat vyplyne z porovnání poměru režie/přínos. To co
nebude odpovídat mé představě o programování vyřadím. Bohužel zatím mám spíše
dojem, že to nabízenými nástroji nedokáži udělat dostatečně adresně, aby zůstalo
zachováno i co se mi líbí. Přehled pylintem kontrolovaných oblastí (lze použít 
pro vypnutí testu) je `zde <http://docs.pylint.org/features.html>`_.

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

**Kontrola použití lokální proměnné (_xxx) jiného modulu**

Python nemá žádnou přímou cestu jak schovat proměnnou. (Jedině jí dát do souboru
který je schovaný pomocí __init__.py) Osobně si myslím že bez nějaký formy 
``zapouzdření`` to větším projektu nejde. Proto bych poprosil o důsledné rozlišení
a označování lokálních proměnných pomocí _. A doufám že chybu 
``protected-access (W0212): Access to a protected member ...`` nikde neuvidím.
Jen kromě testů, kde je testování lokálních proměnných praktické.

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
`sphinx-apidoc <http://sphinx-doc.org/man/sphinx-apidoc.html>`_ příkazem umístěným v Makefile::

  modules.lib.rst: 
	  sphinx-apidoc -o ./aut -s .rst ../../src/lib/
	  mv aut/modules.rst aut/lib.rst

a začleněna do index.rst (odkaz na soubor aut/lib.rst)

`sphinx <http://sphinx-doc.org/index.htmls>`_ není úplně jednoduchý nástroj na osvojení a je 
primárně určený na psaní dokumentace obecně. Naopak jako nástroj pro generování dokumentace 
ze zdrojových kódů není ideální a má mnoho much. Ale alternativy již nejsou zrovna aktivně
vyvíjený a `sphinx <http://sphinx-doc.org/index.htmls>`_ následně můžeme použít i na psaní
uživatelské dokumentace.

Uživatelská Dokumentace
=======================
Dokumentace bude asi psaná v `reStructuredText <http://sphinx-doc.org/rest.html#paragraphs>`_ a 
do finální podoby generována pomocí `sphinx <http://sphinx-doc.org/index.htmls>`_.

Testování kódu po sobě
======================

Kód je nutné otestova kompletně a pokud víme že ovlivní i jiné části programu, pak i ty.
Tam kde jsou psané kompletní testy stačí zběžně, v jiném případě by mělo být testování
kompletnější.

Testování - automatické testy
=============================

Pro psaní automatických testů je použit `pyTest <http://pytest.org/latest/>`_. Testy
je možné lokálně spustit z testing adresáře příkazem::

  RunTests.sh

UI testy qt částí aplikace je možné dělat pomocí qt knihovny 
`QTest <http://doc.qt.io/qt-5/qtest.html>`_ (Jen Qt dokumentace). Testování je popsáno 
`v tomto článku <http://johnnado.com/pyqt-qtest-example/>`_.

V budoucnu je třeba spouštět testy automaticky po každém poslání do gitu nejlépe na 
deployi ve virtuálním prostředí.

**Co se musí aut. testovat**:
  * přítomnost souboru v prostředí (z každého souboru zavolat nějakou funkci)
  * pokud je kód souboru závislý na nějakém resourci, knihově, nebo na něčem jiném, pak 
    otestovat jejich přítomnost (zavolat část kódu, která danou závislost načte, nebo kde
    proběhne inicializace)
  * pokud jde o qt třídu, která obsahuje signál, pak otestovat signál

**Co je dobré aut. testovat**:
  * Psaní automatických testů může být činnost, jež ušetří mnoho práce v budoucnosti,
    naopak muže být i velmi časově náročné a výsledek nevalný. Něco se testuje lépe a
    něco hůře. Na každém z nás je aby našel tu hranici, kde je to výhoddné.
  * Některý kód vede na něco jako úplné testy. Například implementujeme-li něco, co se
    může během vývoje (přidávání nové vlastnosti) lehce rozbít. Přičemž lze relativně 
    lehce otestovat, že se nezměnila již nainplementovaná část. Pokud tomu tak je, 
    určitě se o takovýto test pokusit. Do popisu třídy se pak poznačí, že jsou k ní k
    dispozici úplné testy
  
Požadavky na vývojový PC
========================

Vše je psané pro Linux. Pokud by se mělo vyvíjet i na window, je nutné tam nainstalovat
maketool a asi napsat nějaké alternativy k sh skriptům, ale ten je použit jen pro testy.
Pokud by se našel někdo, kdo by chtěl vyvíjet na windows, je to v zásadě vítané, ale bude 
to znamenat vyřešit a zdokumentovat instalaci prostředí a přidání alternativních skriptů.

Požadavky:
  * Python3
  * PyQt5
  * PyTest
  * PyLint
  * Sphinx

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
