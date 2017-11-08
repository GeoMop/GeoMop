Analysis - Converters
=====================

It serves only to merge, select and reorganize data, does not make any calculations.
It is primarily used in action connectors, but one converter can also be used inside another converter,
especially for Ensemble and Sequence operations.

Reformatting
------------

Converters allow data reorganization, renaming, regrouping.

An example::

    # chose Struct items, from Struct(a=Int(), b=Int(), c=Int()) creates Struct with only item "a"
    Converter(Struct(a=Input(0).a))

    # rename Struct items, from Struct(a=Int(), b=Int()) creates Struct with same items,
    # but different item's names
    Converter(Struct(x=Input(0).a, y=Input(0).b))

    # convert Struct to Tuple, from Struct(a=Int(), b=Int()) creates Tuple with same items
    Converter(Tuple(Input(0).a, Input(0).b))

    # convert Tuple to Struct, from Tuple(Int(), Int()) creates Struct with same items
    Converter(Struct(a=Input(0)[0], b=Input(0)[1]))

Each
----

Is used to apply the converter to each item of Ensemble.
The converter, which is the 'each' parameter, must have just one Input(0) input.

An example::

    # from Ensemble(Struct(a=Int(), b=Int()) creates Ensemble of type Tuple(Int(), Int())
    Converter(Input(0).each(Adapter(Tuple(Input(0).a, Input(0).b))))

Select
------

The 'select' operation selects Ensamble/Sequence only for features accomplish predicate.
The predicate supports all selection operations as a converter, but does not allow the creation of Structs and Tuples,
on the other hand, it allows the comparison of scalar values and the application of logical operators.
The output is an Ensemble containing a subset of data.
The predicate must have just one input again, resulting in a Bool value.

An example::

    # from Ensemble(Int(), Int(1), Int(2), Int(3), Int(4), Int(5))
    # creates Ensemble(Int(), Int(1), Int(2))
    Converter(Input(0).select(Predicate(Input(0) < 3)))

    # from Ensemble(Int(), Int(1), Int(2), Int(3), Int(4), Int(5))
    # creates Ensemble(Int(), Int(2), Int(3))
    Converter(Input(0).select(Predicate(And(Input(0) >= 2, Input(0) < 4))))

    # from Ensemble(Struct(a=Int(), b=String()),
                    Struct(a=Int(1), b=String("y")),
                    Struct(a=Int(2), b=String("n")),
                    Struct(a=Int(3), b=String("y")))
    # creates Ensemble(Int(), Int(1), Int(3))
    Converter(Input(0).select(Predicate(Input(0).b == "y"))).each(Adapter(Input(0).a))

    # from Ensemble(Struct(a=Int(), b=String()),
                    Struct(a=Int(1), b=String("y")),
                    Struct(a=Int(2), b=String("n")),
                    Struct(a=Int(3), b=String("y")))
    # creates Ensemble(Int(), Int(3))
    pred = Predicate(And(Input(0).b == "y", Input(0).a > 2))
    Converter(Input(0).select()).each(Adapter(Input(0).a))

Sort
----

The 'sort' operation performs an Ensemble/Sequence arrangement and results in a Sequence.
The parameter of the operation is a converter that returns a scalar (or, more generally, a comparable type),
this type of converter is called Selector.
The selector also has just one input.

An example::

    # from Ensemble(Int(), Int(2), Int(3), Int(1)) creates Sequence(Int(), Int(1), Int(2), Int(3))
    Converter(Input(0).sort(KeyConvertor(Input(0))))

    # from Ensemble(Struct(a=Int(), b=Int()),
                    Struct(a=Int(1), b=Int(2)),
                    Struct(a=Int(2), b=Int(1)),
                    Struct(a=Int(3), b=Int(3)))
    # creates Sequence(Int(), Int(2), Int(1), Int(3))
    Converter(Input(0).sort(KeyConvertor(Input(0).b))).each(Adapter(Input(0).a))
