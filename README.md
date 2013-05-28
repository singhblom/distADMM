distADMM
========

Implements Boyd et al. Alternating Direction Method of Multiplyers
in a distributed setting. It is currently set up to run on Amazon's EC2,
put should be trivial to change for whatever cluster you want.

How to run
----------

To run on EC2, tar all of these, get them to the cloud with ftp,
untar, set permissions to runnable, and run ./initialize.sh on master.
