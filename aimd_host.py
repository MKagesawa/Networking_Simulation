import sys
from packet import *
from timeout_calculator  import *
import matplotlib.pyplot as plt1000
window_size = []
tick_number = []

class UnackedPacket:
  """
  Structure to store information associated with an unacked packet
  so that we can maintain a list of such UnackedPacket objects
  
  Data members of this class include:
  seq_num:  Sequence number of the unacked packet
  num_retx: Number of times this packet has been retransmitted so far
  timeout_duration: Timeout duration for this packet
  timeout_tick: The time (in ticks) at which the packet timeout
  """

  def __init__(self, seq_num):
    self.seq_num      = seq_num # sequence number of unacked packet
    self.num_retx     = 0       # how many times it's been retransmitted so far
    self.timeout_duration = 0   # what is the duration of its timeout
    self.timeout_tick     = 0   # at what tick does this packet timeout?

  def __str__(self):
    return str(self.seq_num)

class AimdHost:

  def __init__(self):
    self.unacked = []           # list of unacked packets
    self.window = 1             # We'll initialize window to 1
    self.max_seq = -1           # maximum sequence number sent so far
    self.in_order_rx_seq = -1   # maximum sequence number received so far in order
    self.slow_start = True      # Are we in slow start?
    self.next_decrease = -1     # When to next decrease your window; adds some hystersis
    self.timeout_calculator = TimeoutCalculator() # object for computing timeouts

  def send(self, tick):
    print ("@ tick " + str(tick) + " window is " + str(self.window))
    tick_number.append(tick)
    window_size.append(self.window)

    # Create an empty list of packets that the host will send
    packets = []
    # First, process retransmissions
    for i in range(0, len(self.unacked)):
      unacked_pkt = self.unacked[i]
      if (tick >= unacked_pkt.timeout_tick):
        # Retransmit any packet that has timed out by doing the following in order
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

        # Multiplicative decrease, if it's time for the next decrease
        # Cut window by half, but don't let it go below 1
        half = self.window / 2
        if half < 1:
          self.window = 1
        elif (half >= 1 and self.next_decrease <= tick):
          self.window = half

        # Make sure the next multiplicative decrease doesn't happen until an RTT later
        self.next_decrease = tick + self.timeout_calculator.mean_rtt

        # Exit slow start, whether you were in it or not
        self.slow_start = False

      self.unacked[i] = unacked_pkt

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

    # Return the list of packets that need to be sent on to the network
    return packets

  def recv(self, pkt, tick):
    assert(tick > pkt.sent_ts)
    # Compute RTT sample
    RTT = tick - pkt.sent_ts
    # Update timeout
    self.timeout_calculator.update_timeout(RTT)

    # Remove received packet from self.unacked
    for p in self.unacked:
      if p.seq_num == pkt.seq_num:
        self.unacked.remove(p)

    # Update in_order_rx_seq to reflect the largest sequence number that you have received in order so far
    self.in_order_rx_seq += 1

    # Increase your window given that you just received an ACK. Remember that:
    # 1. The window increase rule is different for slow start and congestion avoidance.
    # 2. The recv() function is called on every ACK (not every RTT), so you should adjust your window accordingly.
    if (self.slow_start):
      self.window += 1
    else:
      self.window += 1/self.window
