Development Rules (czech)
=========================
Vývoj aplikace GeoMop podléhá následujícím pravidlům.

Psaní kódu
----------
Nejdůležitějším pravidlem pro tuto aplikaci je psát **jednoduchý**, ve všem co 
má dělat protestovaný kód jež dělá jen a pouze to co má.

Poznámka:
  Pokud bude mít někdo dojem, že to jde udělat se skoro stejným usilím a vyprodukovat 
  univerzální kód, který půjde využít jinde, nebo později, může to zkusit. Podmínkou však 
  je, že tento kód bude ve všech větvých otestovaný. Z mé zkušenosti však 
  takovýto kód bude po nějaké změně požadavků, optimalizaci, nebo opravách změněn,
  bude do něj problematické přidat požaduvané vlastnosti a zachovat obsaženou univerzálnost. 
  A to už vůbec nemluvým o případu, kdy i novou vlastnost přidáváme v duchu univerzálnosti
  jako tu předchozí. Důsledné otestování se stane velkou komplikací, popisek nad funkcí 
  či třídou začne narůstat do závratné velikosti a všichni se budou bát do kódu šáhnout.
  Takže pokud tu budou náznaky že tato situace nastává, musí okamžitě dojít k zjednodušení 
  (přepsání) kódu a k úplnému otestování. 

Kód připravený pro použitý v budoucnosti je lépe nechat nedopsaný a v místě
budoucího kódu vyvolat vyjímku::

  raise NotImplementedError

Aplikace musí být vždy v konzistentním stavu. Je lepší pokud aplikace spadne,
než když zůstane nekonzistentní. Zvlášt nebezpečný je kód, kdy aplikace 
snaží spravovat samu sebe a opravý jen část stavových proměnných. Kde není
pád applikace možný, je nutný zalogovat problém a vymyslet nějakou formu
částečného, nebo úplný restart. Pro pád applikace je možné využít vyjímky.

Přednostně se použijí knihovny používané již jinou částí aplikace. Přidání nové
knihovny, mimo té jež se považuje za standartní součást pythonu musí předcházet
důkladné rozvážení. Pokud by úspora času získanám přidání knihovny byla malá,
je doporučené psát vlastní kód.

Knihovny třetích stran jsou umístěny ve zvláštním adresáři. K jejich úpravě se vždy
používá nějaká mezivrstva umístěná vně knihoven, například třída jež je obalí. Pokud
to není možné a upravuje se kód knohovny, je to velký problém a takovýto postup musí 
být schválen vedoucím projektu.

Kontrola kódu
-------------

Před commitem kódu na server je nutné provéct kontrolu pyLintem. Pokud bude nalezena
chyba, kterou nelze okamžitě vyřešit opravou, nebo v souladu s :doc:`doporučeným řešením 
<pylint_rules>`, předá se vedoucímu projektu.

Testování kódu
--------------

Před commitem kódu na server je nutné kontrolovat kód již :doc:`vytvořenými 
automatickými testy <procedures>`. Pokud by toto bylo v budoucnu časově náročné, 
napíší se skripty pouštící pouze vlastní modul, nebo jeho část.

Před uzavřením úkolu musí být vytvořeny i automatické testy v souladu s doporučeným
postupen

Uchovávání kódu
---------------

Používá se git na adrese::

  https://github.com/GeoMop/GeoMop

Commituje se jen funkční kód.
