#!/bin/bash
# This code assumes you have ell1.pyx, setyp.py and all the other files in the /home/sgeadmin directory.
# Also, a file nodelist with one line per worker of the format nodeNUM N where nodeNUM is the address
# to the worker node, and N is the number of cores for the node, is needed in /home/sgeadmin 

# First start compile ell1.pyx
cp * /home/sgeadmin
cd /home/sgeadmin
chmod +x *.sh
sudo easy_install cython
sudo python setup.py build_ext --inplace

# Then start all workers
cat nodelist |   # Supply input from a file.
while read line   # As long as there is another line to read ...
do
  nodeName=$(echo $line|cut -f1 -d:)
  numCores=$(echo $line|cut -f2 -d:)
  echo "Starting $numCores workers on node $nodeName"
  ssh $nodeName "/home/sgeadmin/startnode.sh $line > $line.log 2>&1 &"
done

# Then get needed libraries on the master
cd /root
git clone git://github.com/zeromq/zeromq2-1
git clone git://github.com/zeromq/pyzmq
yes yes | sudo apt-get install automake autoconf libtool uuid-dev
cd zeromq2-1/
./autogen.sh
./configure
make
sudo make install
cd ..
cd pyzmq
sudo python setup.py configure --zmq=/usr/local
python setup.py install

# Then start master.py
cd /home/sgeadmin
python master.py 100
