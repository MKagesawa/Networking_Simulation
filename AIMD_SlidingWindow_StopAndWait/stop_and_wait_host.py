from packet import *
from timeout_calculator import *  # Import timeout calculator for StopAndWait

class StopAndWaitHost:
  """
  This host implements the stop and wait protocol. Here the host only
  sends one packet in return of an acknowledgement.
  """
  def __init__(self):
    self.in_order_rx_seq = -1       # maximum sequence number received so far in order
    self.ready_to_send = True      # can we send a packet or are we still waiting for an ACK?
    self.packet_sent_time   = -1   # when was this packet sent out last?
    self.timeout_calculator = TimeoutCalculator() # initialize TimeoutCalculator

  def send(self, tick):
    """
    Function to send a packet with the next sequence number on to the network.
    """

    if (self.ready_to_send):
      # Send next sequence number by creating a packet
      packet = Packet(tick, self.in_order_rx_seq)

      # Remember to update packet_sent_time and ready_to_send appropriately
      self.packet_sent_time = tick
      self.ready_to_send = False

      # Return the packet
      sequence_number = packet.seq_num
      print("sent packet @", tick, "with sequence number ", sequence_number+1)
      return packet

    elif (tick - self.packet_sent_time >= self.timeout_calculator.timeout):
      # Timeout has been exceeded, retransmit packet
      # following the same procedure as above when transmitting a packet for the first time
      packet = Packet(tick, self.in_order_rx_seq + 1)

      # Exponentially back off the timer
      self.timeout_calculator.exp_backoff()

      # Set retx field on packet to detect retransmissions for debugging
      packet.retx = True

      # Return the packet
      print("Retransmission sent packet @ ", tick, " with sequence number ", packet.seq_num)
      return packet

  def recv(self, pkt, tick):
    """
    Function to get a packet from the network.

    Args:
        
        **pkt**: Packet received from the network

        **tick**: Simulated time
    """
    assert(tick > pkt.sent_ts)
    # Compute RTT sample
    RTT = tick - pkt.sent_ts

    # Update timeout based on RTT sample
    self.timeout_calculator.update_timeout(RTT)
    print("@", tick, "timeout computed to be ", self.timeout_calculator.timeout)
    print("rx packet @", tick, "with sequence number ", self.in_order_rx_seq+1)
    # Update self.in_order_rx_seq and self.ready_to_send depending on pkt.seq_num
    if pkt.seq_num == self.in_order_rx_seq:
      self.ready_to_send = True
      self.in_order_rx_seq += 1
    else:
      self.ready_to_send = False

