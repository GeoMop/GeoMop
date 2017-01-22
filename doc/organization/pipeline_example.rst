Pipeline example (czech)
========================

Tento dokument popisuje vytvoření ukázkové pipeline.

VariableGenerator
-----------------

Vytvoříme akci VariableGenerator, která bude na svém výstupu poskytovat ensemble typu Float,
obsahující tři hodnoty typu Float.

::

    vg = VariableGenerator(Variable=Ensemble(Float(), Float(1.0), Float(2.0), Float(3.0)))

Workflow
--------

Část pipeliny budeme chtít vykonávat opakovaně, vložíme ji tedy do akce Workflow.

::

    w = Workflow()

Connector
---------

Do workflow budou vstupovat položky typu Float, na vstupu FunctionAction musí být typ
Struct, použijeme tedy konektor, který typ upraví.

::

    c1 = Connector()
    c1.set_inputs([w.input()])
    c1.set_config(Convertor = Convertor(Struct(x=Input(0))))

FunctionAction
--------------

Uvnitř workflow umístíme akci FunctionAction.
Jako vstup do této akce bude sloužit vstup do akce workflou.
Pro akci FunctionAction definujeme vstupní parametry a vlastní předpis funkce.

::

    f = FunctionAction(
        Inputs=[c1],
        Params=["x"],
        Expressions=["y = 2 * x + 3"]
    )

Connector
---------

Budeme požadovat, aby na výstupu z workflou byl Struct s polozkou "z",
výstup z akce FunctionAction je Struct s polozkou y, použijeme tedy příslušný konvertor.

::

    c2 = Connector()
    c2.set_inputs([f])
    c2.set_config(Convertor = Convertor(Struct(z=Input(0).y)))

Nastavíme vstup a výstup workflow.

::

    w.set_config(
        OutputAction=c2,
        InputAction=c1
    )

ForEach
-------

Celý workflow budeme opakovaně vykonávat pomocí akce ForEach.

::

    fe = ForEach(
        Inputs=[vg],
        WrappedAction=w
    )

PrintDTTAction
--------------

Výstup budeme chtít uložit do souboru, použijeme tedy akci PrintDTTAction.

::

    pa = PrintDTTAction(Inputs=[fe], OutputFile="output.txt")

Pipeline
--------

Celá pipeline je umístěna v akci Pipeline.

::

    p = Pipeline(ResultActions=[fe])

Výsledná pipeline
-----------------

Zdrojový kód celé pipeliny vypadá tedy následovně.

::

    vg = VariableGenerator(Variable=Ensemble(Float(), Float(1.0), Float(2.0), Float(3.0)))
    w = Workflow()
    c1 = Connector()
    c1.set_inputs([w.input()])
    c1.set_config(Convertor = Convertor(Struct(x=Input(0))))
    f = FunctionAction(
        Inputs=[c1],
        Params=["x"],
        Expressions=["y = 2 * x + 3"]
    )
    c2 = Connector()
    c2.set_inputs([f])
    c2.set_config(Convertor = Convertor(Struct(z=Input(0).y)))
    w.set_config(
        OutputAction=c2,
        InputAction=c1
    )
    fe = ForEach(
        Inputs=[vg],
        WrappedAction=w
    )
    pa = PrintDTTAction(Inputs=[fe], OutputFile="output.txt")
    p = Pipeline(ResultActions=[pa])
