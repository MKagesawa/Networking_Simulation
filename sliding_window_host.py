import sys
from packet import *
from timeout_calculator import *

class UnackedPacket:
  """
  Structure to store information associated with an unacked packet
  so that we can maintain a list of such UnackedPacket objects.

  This structure is different from the packet structure that is used
  by the simulator. Be careful to not mix Packet and UnackedPacket
  
  The network does not understand an UnackedPacket. It is only used by
  sliding window host for bookkeeping.
  """
  def __init__(self, seq_num):
    self.seq_num      = seq_num # sequence number of unacked packet
    self.num_retx     = 0       # how many times it's been retransmitted so far
    self.timeout_duration = 0   # what is the duration of its timeout
    self.timeout_tick     = 0   # at what tick does this packet timeout?
  def __str__(self):            # string representation of unacked packet for debugging
    return str(self.seq_num)

class SlidingWindowHost:
  """
  This host follows the SlidingWindow protocol. It maintains a window size and the
  list of unacked packets. The algorithm itself is documented with the send method
  """
  def __init__(self, window_size):
    self.unacked = []           # list of unacked packets
    self.window = window_size   # window size
    self.max_seq = -1           # maximum sequence number sent so far
    self.in_order_rx_seq = -1   # maximum sequence number received so far in order
    self.timeout_calculator = TimeoutCalculator()  # object for computing timeouts

  def send(self, tick):
    """
    Method to send packets on to the network. Host must first check if there are any
    unacked packets, it yes, it should retransmist those first. If the window is still
    empty, the host can send more new packets on to the network.

    Args:
        
        **tick**: Current simulated time

    Returns:
        A list of packets that need to be transmitted. Even in case of a single packet,
        it should be returned as part of a list (i.e. [packet])
    """
    # Create an empty list of packets that the host will send
    packets = []

    # First, process retransmissions
    for i in range(0, len(self.unacked)):
      unacked_pkt = self.unacked[i]
      if tick >= self.unacked[i].timeout_tick:
        # Retransmit any packet that has timed out
        # by doing the following in order
        # (1) creating a new packet,
        packet = Packet(tick, unacked_pkt.seq_num)
        # (2) setting its retx attribute to True (just for debugging)
        packet.retx = True
        # (3) Append the packet to the list of packets created earlier
        packets.append(packet)
        # (4) Backing off the timer
        self.timeout_calculator.exp_backoff()
        # (5) Updating timeout_tick and timeout_duration appropriately after backing off the timer
        unacked_pkt.timeout_duration = self.timeout_calculator.timeout
        unacked_pkt.timeout_tick = tick + unacked_pkt.timeout_duration
        # (6) Updating num_retx
        unacked_pkt.num_retx += 1
      self.unacked[i] = unacked_pkt

    assert(len(self.unacked) <= self.window)

    # Now fill up the window with new packets
    while (len(self.unacked) < self.window):
      # Create new packets, set their retransmission timeout, and add them to the list
      packet = Packet(tick, self.max_seq+1)
      unacked_packet = UnackedPacket(packet.seq_num)
      unacked_packet.timeout_duration = self.timeout_calculator.timeout
      unacked_packet.timeout_tick = self.timeout_calculator.timeout + tick
      packets.append(packet)
      # Remember to update self.max_seq and add then just sent packet to self.unacked
      self.max_seq += 1
      self.unacked.append(unacked_packet)
      print("send packet @", tick, "with sequence number ", self.max_seq)
    # window must be filled up at this point
    assert(len(self.unacked) == self.window)

    # return the list of packets that need to be transmitted on to the network
    return packets

  def recv(self, pkt, tick):
    """
    Function to get a packet from the network.

    Args:
        
        **pkt**: Packet received from the network

        **tick**: Simulated time
    """

    assert(tick > pkt.sent_ts)
    #  Compute RTT sample
    RTT = tick - pkt.sent_ts

    #  Update timeout
    self.timeout_calculator.update_timeout(RTT)

    #  Remove received packet from self.unacked
    # for p in self.unacked:
    #   if p.seq_num == pkt.seq_num:
    #     self.unacked.remove(p)
    for i in range(len(self.unacked)):
      if self.unacked[i].seq_num == pkt.seq_num:
        del self.unacked[i]
        break

    #  Update in_order_rx_seq to reflect the largest sequence number that you have received in order so far
    # if not self.unacked:
    #     self.in_order_rx_seq = self.max_seq
    # else:
    #     self.in_order_rx_seq = self.unacked[0].seq_num - 1

    self.in_order_rx_seq = max(self.in_order_rx_seq, pkt.seq_num)
    # self.in_order_rx_seq = max(self.in_order_rx_seq, pkt.seq_num)

    assert(len(self.unacked) <= self.window)
