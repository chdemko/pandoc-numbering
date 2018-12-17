Classes
-------

The classes added to the elements can be changed using the ``classes``
keyword in the meta.

.. code-block:: md

   ---
   pandoc-numbering:
     exercise:
       general:
         listing-title: List of exercises
         classes: [my-class1, my-class2]
   ---
   Section
   =======

   Exercise (The first exercise) #

   Exercise (The second exercise) #

   See @exercise:1

will be rendered as:

.. code-block:: md

   List of exercises {.pandoc-numbering-listing .my-class1 .my-class2 .unnumbered .unlisted}
   =================

   -   [[The first exercise]{.pandoc-numbering-entry .my-class1
       .my-class2}](#exercise:1)
   -   [[The second exercise]{.pandoc-numbering-entry .my-class1
       .my-class2}](#exercise:2)

   Section
   =======

   [**Exercise 1** *(The first exercise)*]{#exercise:1
   .pandoc-numbering-text .my-class1 .my-class2}

   [**Exercise 2** *(The second exercise)*]{#exercise:2
   .pandoc-numbering-text .my-class1 .my-class2}

   See [[Exercise 1 (The first exercise)]{.pandoc-numbering-link .my-class1
   .my-class2}](#exercise:1 "Exercise 1 (The first exercise)")

