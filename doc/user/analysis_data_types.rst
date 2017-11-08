Analysis - Data types
=====================

Data types in the analysis are used for type checking and data transfer between actions.

Basic data types
----------------

Bool
~~~~

::

    # type definition
    a = Bool()

    # value definition
    b = Bool(True)

Int
~~~

::

    # type definition
    a = Int()

    # value definition
    b = Int(2)

Float
~~~~~

::

    # type definition
    a = Float()

    # value definition
    b = Float(2.0)

String
~~~~~~

::

    # type definition
    a = String()

    # value definition
    b = String("text")

Enum
~~~~

Enum is a descendant of String.
In addition, it contains a list of values that may be assigned to it.

::

    # type definition
    a = Enum(["option1", "option2"])

    # value definition
    b = Enum(["option1", "option2"], "option1")



Composite data types
--------------------

Composite types allow data to be organized into larger units.

Struct
~~~~~~

It is like a Python dictionary where the keys are string-only.
The specific type of struct is given by the names of its keys and the types of their values.

::

    # type definition
    a = Struct(x=Int(), y=String())

    # value definition
    b = Struct(x=Int(1), y=String("text"))

    # access to items
    bx = b.x
    by = b.y

Tuple
~~~~~

Python tuple, fixed length and fixed (but possibly different) types.
It is like the Struct type, where natural numbers (from zero) are used as keys.

::

    # type definition
    a = Tuple(Int(), String())

    # value definition
    b = Tuple(Int(1), String("text"))

    # access to items
    b0 = b[0]
    b1 = b[1]

Ensemble
~~~~~~~~

Data set of the same type without any order. Output of some generators.
Input of reduction operations.
Operations for all elements using the ForEach action.
For a type tree, it contains only one type with an internal type.

::

    # type definition
    a = Ensemble(Int())

    # value definition
    b = Ensemble(Int(), Int(1), Int(2), Int(3))

Sequence
~~~~~~~~

He's a descendant of Ensemble.
Additionally, the order of elements is defined and has operations:

- head - selects the first element
- tail - selects the last element

::

    # type definition
    a = Sequence(Int())

    # value definition
    b = Sequence(Int(), Int(1), Int(2), Int(3))

    # access to items
    head = b.head()
    tail = b.tail()

Examples of more complicated data structures
--------------------------------------------

::

    # Ensemble of struct with item "a" of type Int and item "b" with type String
    en = Ensemble(Struct(a=Int(), b=String()),
                  Struct(a=Int(1), b=String("t1"))
                  Struct(a=Int(2), b=String("t2"))
                  Struct(a=Int(3), b=String("t3"))

     # type of "en" is:
     t = Ensemble(Struct(a=Int(), b=String()))
