Creating new action (czech)
===========================

Tento dokument popisuje vytvoření akce FunctionAction. Akce slouží k vyhodnocení
funkce zadané jako parametr akce na základě předaných parametrů.

Předek třídy
------------

Třída byla odvozena ze třídy ParametrizedActionType, protože jde o třídu která je
parametrizovaná.

::

  class FunctionAction(ParametrizedActionType):

Jméno a popis akce
------------------

Definujeme jméno a popis třídy.

::

    name = "Function"
    """Display name of action"""
    description = "Function"
    """Display description of action"""

Metoda __init__
---------------

Metoda __init__ bude přebírat parametry Params a Expressions. Dále je volána
metoda __init__ předka.

::

    def __init__(self, **kwargs):
        """
        :param list of str Params: input parameters
            example:
            ["x1", "x2", "x3"]
        :param list of srt Expressions: function prescription
            example:
            ["y1 = 1 * x1 + 2 * x2", "y2 = 3 * x1 + 4 * x2", "y3 = sin(x3)"]
        :param action or DTT Input: action DTT variable
        """
        super().__init__(**kwargs)

Metoda _inicialize
------------------

Metoda _inicialize inicializuje proměné akce. Nastaví stav akce na ActionStateType.initialized.

::

    self._set_state(ActionStateType.initialized)

Zavolá metodu self._process_base_hash() pro vytvoření hashe ze základních údajů o třídě.

::

    self._process_base_hash()

Přidá vlastní parametry do hashe.

::

        if 'Params' in self._variables and \
                isinstance(self._variables['Params'], list):
            for par in self._variables['Params']:
                self._hash.update(bytes(par, "utf-8"))
        if 'Expressions' in self._variables and \
                isinstance(self._variables['Expressions'], list):
            for ex in self._variables['Expressions']:
                self._hash.update(bytes(ex, "utf-8"))


A nastaví výstup akce.

::

    self._output = self.__func_output()

Metoda _get_variables_script
----------------------------

Metoda slouží k vygenerování pythoního skriptu seznamu "_variables".
Nejprve je volána metoda předka.

::

    var = super()._get_variables_script()

Dále jsou přidány proměné vlastní akce a výsledek je vrácen jako návratová hodnota.

Metoda _update
--------------

Tato metoda řeší vlastní provedení akce. V našem případě zavolá výpočet funkce.

::

    self._output = self.__func_result()

Následně vrátí None.

Metoda _check_params
--------------------

Metoda zkontroluje správnost zadání parametrů, včetně jejich typů.
Vrátí seznam chyb, které nastaly při kontrole.

Metoda validate
---------------

Tato metoda slouží ke kontrole, jestli předchozí akce poskytuje na svém výstupu
správný typ dat. Nejprve zavolá metodu předka.

::

    err = super().validate()

Dále pak zkontroluje typ vrácený předchozí akcí. Vrací seznam zjistěných chyb.

Metoda __get_require_params
---------------------------

Slouží ke zjištění seznamu parametrů, které budou očekávány na vstupu akce.
Tyto parametry získá z proměné "Params".

Metoda __parse_expressions
--------------------------

Metoda slouží k předpřipravení předpisu funkce. Předpis rozdělí na výstupní proměnou
a vlastní předpis. Metoda vrací seznam tuplů (výstupní proměná, předpis funkce).

Metoda __func_output
--------------------

Tato metoda vygeneruje z předpisu funkce výstupní datový typ akce.

Metoda __func_result
--------------------

Provede vlatní vyhodnocení funkce na základě parametrů předaných předchozí třídou.
