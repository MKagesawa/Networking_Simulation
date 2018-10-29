import matplotlib.pyplot as plt
from network import *
import sys
import argparse
from stop_and_wait_host  import *
from sliding_window_host import *
from aimd_host import *

window = []
throughput = []
ticks = []
num_original = 0
num_retransmitted = 0

if __name__ == '__main__':
    for w in range(2, 400):
        pdbox = PropDelayBox(10)
        random.seed(1)
        host = SlidingWindowHost(w)
        link = Link(loss_ratio=0, queue_limit=1000000)
            # Run the simulation for the specified number of ticks,
            # by running the host, then the link, then the pdbox
        for tick in range(0, 100000):
            window.append(w)
            packets = host.send(tick)
            if packets is not None:
            # If a single packet is received, convert it to list
                if type(packets) is Packet:
                    packets = [packets]
                # Transmit the packets received from the host
            for packet in packets:
                if packet.retx:
                    num_retransmitted += 1
                else:
                    num_original += 1
                link.recv(packet)

            link.tick(tick, pdbox)
            pdbox.tick(tick, host)
            throughput.append((host.in_order_rx_seq+1)/100000)
            # window.append(host.window)
            # ticks.append(tick)

print('num_original: ', num_original)
print('num_retransmitted: ', num_retransmitted)
# print('window: ', window)
# print('ticks: ', ticks)

# plt.plot(ticks, window)
# plt.show()
