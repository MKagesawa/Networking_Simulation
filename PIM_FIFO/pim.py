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
PIM_ITERS    = int(sys.argv[4]) # Number of PIM iterations

# Total number of simulation ticks
NUM_TICKS    = 20000

# Seed random number generator
random.seed(SEED)

# For plotting results
time = []
average_delay = []

# variables to compute average delay of packets transmitted out of output ports
delay_count = 0
delay_sum   = 0.0

# Virtual output queues at each input
# Initialized to empty queue for each combination of input port and output port
# These queues sit on the input side.
voqs = []
for input_port in range(NUM_PORTS):
  voqs += [[]]
  for output_port in range(NUM_PORTS):
    voqs[input_port] += [[]]

# Main simulator loop: Loop over ticks
for tick in range(NUM_TICKS):
  # Tick every input port
  for input_port in range(NUM_PORTS):
    # Is there a packet here?
    if (random.random() < ARRIVAL_PROB):
      # If so, pick output port uniformly at random
      output_port = random.randint(0, NUM_PORTS - 1)
      voqs[input_port][output_port] += [Packet(input_port, output_port, tick)]

  for iteration in range(PIM_ITERS):
    inputs = {}  # input_port: [output_ports received grants from]
    outputs = {} # output_port: [input_ports received requests from]
    # Request Phase
    # Each input port sends out a request to each of the output ports for which its VOQ is not-empty, i.e., the input has at least one packet for that particular output port.
    for i in range(NUM_PORTS):
      for o in range(NUM_PORTS):
        # print('i', i, 'o', o)
        if len(voqs[i][o]) > 0: # packet found
          if o in outputs:
            outputs[o].append(voqs[i][o][0].input_port)
          else:
            outputs[o] = []
            outputs[o].append(voqs[i][o][0].input_port)

    # Grant Phase
    # If an output port receives requests from multiple input ports, it picks one input port at random and grants it the request.
    for key in outputs :
      if len(outputs[key]) > 0: # if there are packets
        chosen = random.choice(outputs[key])
        if chosen in inputs:
          inputs[chosen].append(key)
        else:
          inputs[chosen] = [key]
    
    # Accept Phase
    # If an input port receives grants from multiple output ports, it picks one output port at random and accepts the output port's grant.
    for key in sorted(inputs):
      chosen = inputs[key][0]
      if len(inputs[key]) > 1: # if received multiple grants
        chosen = random.choice(inputs[key])
      
      # Update average delay
      packet = voqs[key][chosen][0]
      voqs[key][chosen].pop(0)
      delay = tick - packet.arrival_tick
      delay_sum += delay
      delay_count += 1

    # Average delay printing
    if (tick % 100 == 0):
      print ("Average delay after ", tick, " ticks = ", delay_sum / delay_count, " ticks")
      time.append(tick)
      average_delay.append(delay_sum / delay_count)
print()

plt.plot(time, average_delay)
plt.ylabel('Average delay since tick 0 (in ticks)')
plt.xlabel('Time (in ticks)')
plt.show()
