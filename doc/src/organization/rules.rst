GeoMop Development Rules (czech)
================================
Vývoj aplikace GeoMop podléhá následujícím pravidlum.

Psaní kódu
==========
Nejdůležitějším pravidlem pro tuto aplikaci je psát **jednoduchý**, ve všem co 
má dělat protestovaný kód jež dělá jen a pouze to co má.

Poznámka:
  Pokud bude mít někdo dojem, že to jde udělat se skoro stejným usilím a vyprodukovat 
  univerzální kód, který půjde využít jinde, nebo později, může to zkusit. Podmínkou však 
  je, že tento kód bude ve všech větvých otestovaný. Z mé zkušenosti však 
  takovýto kód bude ponějaké změně požadavků, optimalizaci, nebo opravách změněn,
  rezignuje se na otestování všeho a bude spíš na závadu. Takže pokud to nastane,
  musí dojít k zjednodušení (přepsání) kódu a k úplnému otestování. 

Kód připravený pro použitý v budoucnosti je lépe nechat nedopsaný a v místě
budoucího kódu vyvolat vyjímku::

  raise NotImplementedError

Všechny texty připravovat pro pozdější :doc:`lokalizaci <procedures>`..

Přednostně se použijí knihovny používané již jinou částí aplikace. Přidání nové
knihovny, mimo té jež se považuje za standartní součást pythonu musí předcházet
důkladné rozvážení. Pokud by úspora času získanám přidání knihovny byla malá,
je doporučené psát vlastní kód.

Knihovny třetích stran jsou umístěny ve zvláštním adresáři. K jejich úpravě se vždy
používá nějaká mezivrstva umístěná vně knihoven, například třída jež je obalí. Pokud
to není možné, je to velký problém a takovýto postup musí být schválen vedoucím 
projektu.

Kontrola kódu
=============

Před commitem kódu na server je nutné provéct kontrolu pyLintem. Pokud bude nalezena
chyba, kterou nelze okamžitě vyřešit opravou, nebo v souladu s :doc:`doporučeným řešením 
<pylint_rules>`, předá se vedoucímu projektu.

Testování kódu
==============

Před commitem kódu na server je nutné je nutné zkontrolovat kód již :doc:`vytvořenými 
automatickímu testy <procedures>`

Před uzavřením úkolu musí být vytvořeny i automatické testy v souladu s doporučeným
postupen


Uchovávání kódu
===============

Používá se git na adrese::

  https://github.com/GeoMop/GeoMop

Commituje se jen funkční kód.
