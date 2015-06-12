GeoMop Development Rules
========================

**invalid-name (C0103):**
U globální proměnný mimo třídu je možné zkontrolovat zda má opodstatnění a 
pokud ano, nad touto proměnnou ji vypnout.
Příklad::
   # pylint: disable=C0103
   _d=os.path.dirname(os.path.realpath(__file__))

**no-member (E1101):**
U některých modulů a tříd (převážně qt a z nich odvozených) má pylint problém
najít jejich funkce.
V ``pylintrc`` je pak nutné přidat tento modul, nebo třídu::
   [typecheck]
   ignored-modules=PyQt5.QtWidgets,PyQt5.QtCore
   ignored-classes=AddPictureWidget,CanvasWidget


