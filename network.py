# Required for dropping packets at random
import random
import queue

class PropDelayBox:
  """
  A class to delay packets by the propagation delay
  In our case, we'll use it to delay packets by the two-way propagation delay,
  i.e., RTT_min
  """
  def __init__(self, prop_delay):
    self.prop_delay_queue = []   # queue of packets being delayed
    self.prop_delay = prop_delay # how much to delay them by
  def recv(self, pkt, tick):     # enqueue packet after timestamping it
    pkt.pdbox_time = tick
    self.prop_delay_queue += [pkt]
  def tick(self, tick, host):    # execute this on every tick
    to_deliver = []              # packets that are delivered this tick
    for pkt in self.prop_delay_queue:
      if (pkt.pdbox_time + self.prop_delay <= tick): # if propagation delay has been exceeded
        assert(pkt.pdbox_time + self.prop_delay == tick)
        to_deliver += [pkt]
        host.recv(pkt, tick)     # deliver to the host
    self.prop_delay_queue = [x for x in self.prop_delay_queue if x not in to_deliver]

class Link:
  """
  A class to represent a link with a finite capacity of 1 packet per tick
  We can generalize this to other capacities, but we're keeping the assignment simple

  """
  def __init__(self, loss_ratio, queue_limit):
    self.link_queue = queue.Queue()# queue of packets at the link
    self.loss_ratio = loss_ratio # probability of dropping packets when link dequeues them
    self.queue_limit= queue_limit# Max size of queue in packets
  def recv(self, pkt):
    """
    Function to receive a packet from a device connected at either
    ends of the link. Device here can represent an end host or any other
    network device.

    The device connected to the link needs to call the recv function to put
    packet on to the link. If link's queue is full, it starts dropping packets
    and does not receive any more packets.
    """
    if (self.link_queue.qsize() < self.queue_limit):
      self.link_queue.put(pkt)   # append to the queue
    # else:
      print ("Link dropped packet because queue_limit was exceeded")
  def tick(self, tick, pdbox):   # Execute on every tick
    """
    This function simulates what a link would do at each time instant (tick).
    It dequeue packets and sends it to the propogation delay box
    """
    if (self.link_queue.qsize() != 0): # Dequeue from link queue if queue is not empty
      head = self.link_queue.get()
      if (random.uniform(0.0, 1) < (1 - self.loss_ratio)):
        pdbox.recv(head, tick)   # dequeue and send to prop delay box
      # else:
        print ("@ tick ", tick, " link dropped a packet ")
