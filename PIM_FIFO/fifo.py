import random
import sys
import matplotlib.pyplot as plt

class Packet:
  def __init__(self, input_port, output_port, arrival_tick):
    self.input_port  = input_port
    self.output_port = output_port
    self.arrival_tick= arrival_tick

# User-supplied parameters
NUM_PORTS    = int(sys.argv[1])
ARRIVAL_PROB = float(sys.argv[2])
SEED         = int(sys.argv[3])

# Total number of simulation ticks
NUM_TICKS    = 20000

# Seed random number generator
random.seed(SEED)

# variables to compute average delay of packets transmitted out of output ports
delay_count = 0
delay_sum   = 0.0

# One input queue for each input port
# Initialized to empty queue for each input port
input_queues = []
for input_port in range(NUM_PORTS):
  input_queues += [[]]

# For plotting results
time = []
average_delay = []

# Main simulator loop: Loop over ticks
for tick in range(NUM_TICKS):
  # Tick every input port
  for input_port in range(NUM_PORTS):
    # Is there a packet here?
    if (random.random() < ARRIVAL_PROB):
      # If so, pick output port uniformly at random
      output_port = random.randint(0, NUM_PORTS - 1)
      input_queues[input_port] += [Packet(input_port, output_port, tick)]

  # Implement FIFO algorithm:
  # First, look at all the head packets, i.e., packets at the head of each of the input_queues
  # Second, If multiple inputs have head packets destined to the same output port,
  # pick an input port at random, and deq from that. Repeat for each output port.
  head_packets = []
  for q in input_queues:
    if (len(q) > 0):
      head_packets += [q[0]]

  # More detailed instructions for FIFO algorithm:
  # First, populate a dictionary d that maps an output port to the list of all packets destined to that output.
  # Second, for each output port o, pick one of the packets in the list d[o] at random
  # To pick one packet out of a list at random, you can use the random.choice function.
  # Note: To complete the matching for an input port i that was picked and hence matched to an output port,
  # dequeue from that input port's queue (input_queues[i])

  # Update the average delay based on the packets that were just dequeued.
  # Otherwise, your average delay will be 0/0 because no samples would have been accumulated.

  packets_for_each_output = dict()
  for output_port in range(NUM_PORTS):
    packets_for_each_output[output_port] = []
  for packet in head_packets:
    packets_for_each_output[packet.output_port] += [packet]
 
  # Second, for each output port, pick one of the packets in the list at random
  for output_port in range(NUM_PORTS):
    if (len(packets_for_each_output[output_port]) > 0):
      chosen_packet = random.choice(packets_for_each_output[output_port])
      chosen_input  = chosen_packet.input_port
      input_queues[chosen_input] = input_queues[chosen_input][1:]
      delay = tick - chosen_packet.arrival_tick
      delay_sum += delay
      delay_count += 1
  # Average delay printing
  if (tick % 100 == 0):
    print ("Average delay after ", tick, " ticks = ", delay_sum / delay_count, " ticks")
print()

plt.plot(time, average_delay)
plt.ylabel('Average delay since tick 0 (in ticks)')
plt.xlabel('Time (in ticks)')
plt.show()
