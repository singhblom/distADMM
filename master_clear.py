import sys
import zmq
import time

context = zmq.Context()

# Socket to send messages on
sender = context.socket(zmq.PUB)
sender.bind("tcp://*:5551")

# Socket to receive messages on
receiver = context.socket(zmq.SUB)
receiver.bind("tcp://*:5558")
receiver.setsockopt(zmq.SUBSCRIBE, '')

start = time.time()
while time.time()-start < 10:
    sender.send('CLEAR')
    s = receiver.recv()
