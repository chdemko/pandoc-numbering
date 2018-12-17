List of things
--------------

If you want a listing of a particular category at the top of your
document, you can add a ``listing-title`` entry in the metadata:

.. code-block:: md

   ---
   pandoc-numbering:
     exercise:
       general:
         listing-title: List of exercises
   ---
   Exercise (The first exercise) #

   Exercise (The second exercise) #

will be rendered as:

.. code-block:: md

   List of exercises {#list-of-exercises .pandoc-numbering-listing .exercise .unnumbered .unlisted}
   =================

   -   [[The first exercise]{.pandoc-numbering-entry
       .exercise}](#exercise:1)
   -   [[The second exercise]{.pandoc-numbering-entry
       .exercise}](#exercise:2)

   [**Exercise 1** *(The first exercise)*]{#exercise:1
   .pandoc-numbering-text .exercise}

   [**Exercise 2** *(The second exercise)*]{#exercise:2
   .pandoc-numbering-text .exercise}

By default, an identifier is added to the listing title. It’s possible
to change the identifier using a ``listing-identifier`` entry in the
metadata:

.. code-block:: md

   ---
   pandoc-numbering:
     exercise:
       general:
         listing-title: List of exercises
         listing-identifier: myident
   ---
   Exercise (The first exercise) #

   Exercise (The second exercise) #

will be rendered as:

.. code-block:: md

   List of exercises {#myident .pandoc-numbering-listing .exercise .unnumbered .unlisted}
   =================

   -   [[The first exercise]{.pandoc-numbering-entry
       .exercise}](#exercise:1)
   -   [[The second exercise]{.pandoc-numbering-entry
       .exercise}](#exercise:2)

   [**Exercise 1** *(The first exercise)*]{#exercise:1
   .pandoc-numbering-text .exercise}

   [**Exercise 2** *(The second exercise)*]{#exercise:2
   .pandoc-numbering-text .exercise}

It’s also possible not to have an identifier using the ``False`` value:

.. code-block:: md

   ---
   pandoc-numbering:
     exercise:
       general:
         listing-title: List of exercises
         listing-identifier: False
   ---
   Exercise (The first exercise) #

   Exercise (The second exercise) #

For controlling the format used in the pdf output, you can precise two
things: \* the tab before each entry (expressed in ``em`` LaTeX size) \*
the space used by the numbering part (expressed in ``em`` LaTeX size)

.. code-block:: md

   ---
   pandoc-numbering:
     exercise:
       general:
         listing-title: List of exercises
       latex:
         entry-space: 3
         entry-tab: 2
   ---
   Exercise (The first exercise) #

   Exercise (The second exercise) #

