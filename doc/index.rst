chbshash: XKCD's *Correct Horse Battery Staple* passphrase generator and hasher
===============================================================================

.. image:: _static/password_strength_2x.png
   :alt: XKCD comic #936: Password Strength

`chbshash` is a Python library and command-line tool for generating random
passphrases and hashing buffers and files. It is inspired by the `XKCD #936
<https://xkcd.com/936/?correct=horse&battery=staple>`__ comic.


Quick Start
-----------
`chbshash` offers two command-line tools:

.. code-block:: bash

   $ chbs
   knockoff bodybuilders appraisal hypopodia
   $ echo "hello world" | chbssum
   oxaluria hematodynamics lemmoblastic blinks  -
   $ echo "hello world" > hello.txt
   $ chbssum hello.txt > checksum.txt
   $ cat checksum.txt
   oxaluria hematodynamics lemmoblastic blinks  hello.txt
   $ chbssum -c checksum.txt
   hello.txt: OK

It's also available as a Python library:

>>> from chbshash import random, hash
>>> random()
'practicing elatery unbenight stopwork'
>>> random(3, sep="-")
'muscicide-pycnonotinae-appendance'
>>> hash(b"hello world\n")
'oxaluria hematodynamics lemmoblastic blinks'
>>> hash(b"hello world\n", 3, sep="-")
'oxaluria-hematodynamics-lemmoblastic'


Entropy and Security
--------------------
`chbshash` uses a dictionary of the 370,105 most common English words to generate
passphrases. With the default 4 words per passphrase, there are 370,105\ :sup:`4` ≈ 2\
:sup:`74` ≈ 10\ :sup:`22` possible combinations. That's more than in the XKCD comic!
This makes it much stronger than typical passwords, as explained by the comic.

For hashing, this is lower than the industry standard, SHA-256, which features entropy
of 2\ :sup:`256` ≈ 10\ :sup:`77`. This means it is still statistically impossible to
obtain a collision with `chbshash` hashes by chance, but it is not cryptographically
secure, as a collision may be crafted given enough computing power and time.

.. toctree::

   installing
   api
   cli
   develop
   whats-new


Credits
-------
- `XKCD #936 <https://xkcd.com/936/?correct=horse&battery=staple>`__
- List of English words from `english-words <https://github.com/dwyl/english-words/>`__


Licenses
--------

- This software is available under the open source
  `Apache License <http://www.apache.org/licenses/LICENSE-2.0.html>`__.
- `english-words <https://github.com/dwyl/english-words/>`__ is
  `unlicensed <https://unlicense.org/>`__.
- XKCD comic is licensed under a `Creative Commons Attribution-NonCommercial 2.5 License
  <http://creativecommons.org/licenses/by-nc/2.5/>`__.
