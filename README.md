# Networking_Simulation
Sliding window protocol, congestion collapse, EWMA, AIMD, stop and wait protocol

## Dependency
- Python3
- Matplotlib

### Stop and Wait Protocol
python3 simulator.py --seed 1 --host_type StopAndWait --ticks 50 --rtt_min 10

### Sliding Window Protocol
python3 simulator.py --seed 1 --host_type SlidingWindow --ticks 50 --window_size 5 --rtt_min 2

### Congestion Collapse
python3 simulator.py --seed 1 --host_type SlidingWindow --ticks 10000 --rtt_min 10 --window_size 10

### AIMD
python3 simulator.py --seed 1 --host_type Aimd --ticks 10000 --rtt_min 10 --queue_limit 5

### Plotting
To plot the results, use plotter.py file