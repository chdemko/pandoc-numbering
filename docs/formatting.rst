Formatting
----------

Basically:

-  the text displayed for a new numbering is
   ``**Category number** *(Title)*`` or ``**Category number**``;
-  the link displayed for an automatic reference is ``Category number``
   using the cite shortcut notation;
-  the entry in the table of contents is ``Category number``
   (``Category`` for LaTeX document) or ``Title``.

These behaviors can be changed by adding metadata for a given category.

-  ``format-text-classic`` is for the text displayed (you can use
   special characters ``%D``, ``%d``, ``%s``, ``%g``, ``%n``, ``#``,
   ``%c``)
-  ``format-text-title`` is for the text displayed when a title is
   present (you can use special characters ``%D``, ``%d``, ``%T``,
   ``%t``, ``%s``, ``%g``, ``%n``, ``#``, ``%c``)
-  ``format-link-classic``\ is for the link displayed using the cite
   shortcut notation (you can use special characters ``%D``, ``%d``,
   ``%s``, ``%g``, ``%n``, ``#``, ``%c``, ``%p``)
-  ``format-link-title``\ is for the link displayed when a title is
   present using the cite shortcut notation (you can use special
   characters ``%D``, ``%d``, ``%T``, ``%t``, ``%s``, ``%g``, ``%n``,
   ``#``, ``%c``, ``%p``)
-  ``format-caption-classic`` is for the text displayed in the captions
   (you can use special characters ``%D``, ``%d``, ``%s``,
   ``%g``, ``%n``, ``#`` and ``%p`` for LaTeX)
-  ``format-caption-title`` is for the text displayed in the captions
   when a title is present (you can use special characters
   ``%D``, ``%d``, ``%T``, ``%t``, ``%s``, ``%g``, ``%n``, ``#`` and ``%p``
   for LaTeX)
-  ``format-entry-classic`` is for the entry displayed in the table of
   contents (you can use special characters ``%D``, ``%d``, ``%s``,
   ``%g``, ``%n``, ``#``)
-  ``format-entry-title`` is for the entry displayed in the table of
   contents when a title is present (you can use special characters
   ``%D``, ``%d``, ``%T``, ``%t``, ``%s``, ``%g``, ``%n``, ``#``)

By default these values are equal to

.. code-block:: md

   ---
   pandoc-numbering:
     exercise:
       standard:
         format-text-classic: '**%D %n**'
         format-text-title: '**%D %n** *(%T)*'
         format-link-classic: '%D %n'
         format-link-title: '%D %n (%T)'
         format-caption-classic: '%D %n'
         format-caption-title': '%D %n (%T)'
         format-entry-title': '%T'
         format-entry-classic': '%D %g'
       latex:
         format-text-classic: '**%D %n**'
         format-text-title: '**%D %n** *(%T)*'
         format-link-classic: '%D %n'
         format-link-title: '%D %n (%T)'
         format-caption-classic: '%D %n'
         format-caption-title: '%D %n (%T)'
         format-entry-title': '%T'
         format-entry-classic': '%D'
   ---

