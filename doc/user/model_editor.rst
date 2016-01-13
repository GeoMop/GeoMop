Model Editor
========================

The ModelEditor context serves as an interactive text editor for the YAML configuration files.

Main features of the editor include:

   - validation of the configuration files (notification window)
   - context-sensitive help widget describing the data types (documentation window)
   - visual representation of the data structure (tree window)
   - autocompletion of keys and values while typing
   - import of old-format (CON) configuration files
   - data structure transformations of the edited files
   - basic text editor functions

Getting Started
---------------

The editor has three main components that are interconnected and change dynamically as you navigate
through or modify the configuration file.

   - Text Editor

      It displays the contents of the opened file and allows it to be edited as text. The editor
      offers a context-sensitive autocompletion feature that can be activated by pressing
      :kbd:`Ctrl+Space`.

   - Data Visualization Tree

      This widget displays the loaded structure of the edited document. Please note that the
      displayed structure may be slightly different from the written configuration file, because
      the structure is shown after all the automatic conversions are applied. As of version 1.0.0,
      the Data Visualization Tree does not allow any user input and all changes must be made by
      editing the text in the Text Editor.

   - Information Tabs

      This widget contains multiple components. The Structure Info displays the documentation for
      the current cursor position in the configuration file. Click on different parts of the
      file or use the links to explore the documentation. Next, the Messages widget contains
      any notifications, warning or errors that were detected during the validation process, which
      happens automatically as you edit the file.

Exploring a configuration file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the `File` menu, select `Open File...` or press :kbd:`Ctrl+O`. If you don't have any
YAML configuration files, you can check out the samples that are a part of the ModelEditor
installation. Under Windows, these are located in
``C:\Program Files (x86)\GeoMop\sample\ModelEditor\YamlFiles``. You can try and open the
``flow_implicit_fields_gmsh.yaml`` file.

Once you open the file, you will see any validation notifications in the Messages window. Click the
Structure Info tab and try clicking on different keys and values in the Text Editor. The Structure
Info should displays all the relevant information to the particular node you're editing.

Next, you can check out the file structure in the Data Visualization Tree. If you click on any of
the keys or values in the Tree, the relevant part of the configuration file is highlighted in the
Text Editor (unless it is not present in the file and was added by an automatic conversion).

Finally, you can try the autocompletion feature. It is very handy to speed up typing and prevent
typing errors. For example, select a value from the Data Visualization Tree. If you scroll up, you
should see `pressure_p1` as item with index `1` in the `output_fields` (about half way down the
component). If you click the `pressure_p1` in the Tree, the value will be highlighted in the Text
Editor.

Delete the text and trigger the autocompletion feature by pressing :kbd:`Ctrl+Space`.
You will see a window pop up with possible values. You can choose a value with arrows keys and
select it by pressing :kbd:`Enter` or :kbd:`Tab`. The autocompletion is automatically filtered as
you type. The autocompletion has to be triggered by the keypress by default, but you can change it
in the Settings to display automatically, if you prefer.

Once you're done editing the file, you can save your changes by choosing `Save File` or `Save As...`
from the `File` menu. You can also check out the editor features in the `Edit` menu. In the
`Settings` -> `Options` menu, you can turn on automatic autocompletion or change some keyboard
shortcuts.


YAML Format
-----------

Instead of the old CON format, the configuration files for Flow123d since version 2 use YAML.
This guide briefly describes the most common use cases and some key differences from the old CON
format.

Here is an example of a CON file.

.. code-block:: json

   {
     // Example
     problem = {
       TYPE = "SequentialCoupling",
       description = "Steady flow + transport with source",
       mesh = {
         mesh_file = "./input/test16.msh"
       },
       primary_equation = {
         TYPE = "Steady_MH",
         input_fields= [
           {
             r_set = "BOUNDARY",
             bc_type = "dirichlet",
             bc_pressure = {
               TYPE="FieldFormula",
               value="y"
             }
           },
           {
             r_set = "BULK",
             cross_section = 1,
             conductivity = 1
           }
         ],
        ...
       }
     }
   }

This is what the same configuration file looks like in YAML.

.. code-block:: yaml

   # Example
   problem: !SequentialCoupling
     description: Steady flow + transport with source
     mesh:
       mesh_file: ./input/test16.msh
     primary_equation: !SteadyMH
       input_fields:
         - r_set: BOUNDARY
           bc_type: dirichlet
           bc_pressure: !FieldFormula y
         - r_set: BULK
           cross_section: 1
           conductivity: 1
       ...

There are a few key differences:

   - Indentation

      In YAML, brackets are replaced by indentation. Although any number or spaces or tabs may be used
      for indentation (if used consistently across the whole file), it is recommended to use 2 spaces
      for indentation. When you use the :kbd:`Tab` key in the Text Editor to indent, it automatically
      uses 2 spaces for indentation.

   - Specifying AbstractRecord type

      Use ``!SelectedType`` tag to specify the type of the AbstractRecord.

   - Strings do not need to be delimited by ``"``

   - Key-Value pairs use ``:`` as a separator

   - Array items are delimited by ``-``

   - Everything behind a ``#`` character until the end of line is a comment

For more information about YAML syntax and features, please refer to the
`YAML 1.2 specification <http://yaml.org/spec/1.2/spec.html>`_.

.. code-block:: yaml
   problem = {
       TYPE = "SequentialCoupling",
       ...
   }

    problem: !SequentialCoupling
       ...





Transformation
---------------------

Information about the transformation module can be found in the
`developer documentation <http://geomop.github.io/GeoMop/aut/ModelEditor/data.yaml.html#module-data.yaml.transformator>`_.
