Pylint Exception (czech)
========================

**Design checker**
u některých voleb pochybuji o významu, u jiných má pylint asi problém
načíst metody předka a hlášení je chybné

V ``pylintrc`` jsou odpovídající hlášení vypnuta::
    disable = R0901,R0902,R0903,R0904,R0911,R0912,R0913,R0914,R0915,
**Newstyle checker**
U některých massage je v dokumentaci:
    This message can’t be emitted when using Python >= 3.0.

V ``pylintrc`` jsou vypnuta pomocí::
    disable = C1001,W1001,E1002,E1001,E1004

**no-member (E1101):**
U některých modulů a tříd (převážně qt a z nich odvozených) má pylint problém
najít jejich funkce.
V ``pylintrc`` je pak nutné přidat tento modul, nebo třídu::
   [typecheck]
   ignored-modules=PyQt5.QtWidgets,PyQt5.QtCore
   ignored-classes=AddPictureWidget,CanvasWidget

