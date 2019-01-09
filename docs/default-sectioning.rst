Default **sectioning**
----------------------

If the **sectioning** part is empty, it is possible to use a default
**sectioning** part defined in the meta-data block using the
``sectioning-levels`` key:

.. code-block:: md

   ---
   pandoc-numbering:
     ex:
       general:
         sectioning-levels: -.+.
   ---
   Section
   =======

   Subsection
   ----------

   Exercise #ex:

will be rendered as

.. code-block:: md

   Section
   =======

   Subsection
   ----------

   [**Exercise 1.1**]{#ex:1.1.1 .pandoc-numbering-text .ex}

You can also use the ``first-section-level`` and ``last-section-level``
key (first section level to appear, last section level to appear):

.. code-block:: md

   ---
   pandoc-numbering:
     ex:
       general:
         sectioning-levels: -.+.
   ---

is equivalent to

.. code-block:: md

   ---
   pandoc-numbering:
     ex:
       general:
         first-section-level: 2
         last-section-level: 2
   ---

