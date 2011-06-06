#!/bin/bash
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
sudo easy_install cython
python setup.py install
# Prerequisites installed
cd /home/sgeadmin/
# $1 is nodeName, $2 is numCores
nodeName=$(echo $1|cut -f1 -d:)
numCores=$(echo $1|cut -f2 -d:)
for coreNum in $(eval echo {1..$numCores}); do
  nohup python worker.py $nodeName:$coreNum  > $nodeName:$coreNum.log 2>&1 &
done

exit