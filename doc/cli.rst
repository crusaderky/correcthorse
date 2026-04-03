Command Line Interface
======================

``chbs``
~~~~~~~~

Generate one or more random passphrases.

Usage:

.. code-block:: bash

   chbs [--sep SEP] [n_words] [count]

- ``n_words``: Number of words per passphrase (default: 4)
- ``count``: Number of passphrases to generate (default: 1)
- ``--sep SEP``: Separator between words (default: space)

Examples:

.. code-block:: bash

   $ chbs
   reckla poachard peristerophily abstractor

   $ chbs 6
   uncarnate plainstanes statutably drabler unemotive irrespectively

   $ chbs 3 5
   aeroyacht trumpets costrel
   thymelaeales adiate desilicified
   henries minesweeper stillery
   interjectional predazzite untediously
   nabataean phonetist speisses

``chbssum``
~~~~~~~~~~~

Generate or check file hashes. It has the same interface as ``sha256sum``.

Usage:

.. code-block:: bash

   chbssum [-b | -t] [-n N] [--sep SEP] [-c [--ignore-missing] [--quiet] [--status]] [file ...]

If no files are given, or when ``-`` is specified, reads from standard input.
The filename is separated from the hash words by two whitespaces.

Options:

- ``-b``, ``--binary``: read in binary mode
- ``-t``, ``--text``: read in text mode (default)
- ``-n N``: number of words in the hash (default: 4)
- ``--sep SEP``: separator between words (default: space)
- ``-c``, ``--check``: read checksums from the FILEs and check them

The following options are useful only when verifying checksums:

- ``--ignore-missing``: don't fail or report status for missing files
- ``--quiet``: don't print OK for each successfully verified file
- ``--status``: don't output anything, status code shows success

When checking, the number of words is inferred from each line in the checksums file.

Examples:

.. code-block:: bash

   $ chbssum myfile.txt
   wob demonstrations rhinoderma behaviorist  myfile.txt

   $ echo -n "hello world" | chbssum
   wob demonstrations rhinoderma behaviorist  -

   $ chbssum file1.txt file2.txt
   repulsor hellenophile soloing desired  file1.txt
   wob demonstrations rhinoderma behaviorist  file2.txt

   $ chbssum file1.txt file2.txt > checksums.txt
   $ chbssum -c checksums.txt
   file1.txt: OK
   file2.txt: OK
