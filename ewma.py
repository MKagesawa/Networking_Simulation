import sys
import matplotlib.pyplot as plt

if __name__ == '__main__':

    # number of rtt samples
    NUM_SAMPLES = 100

    # initialize all of them to zero
    rtt_samples = [0.0] * NUM_SAMPLES

    # rtt after being smoothed by EWMA
    smooth_rtt = [0.0] * NUM_SAMPLES

    # Create a pattern where the first half of the samples are 0
    for i in range(0, int(NUM_SAMPLES / 2)):
      rtt_samples[i] = 0

    # And the next half are 1
    for i in range(int(NUM_SAMPLES / 2), NUM_SAMPLES):
      rtt_samples[i] = 1

    # initialize mean rtt to zero
    mean_rtt = 0

    # get alpha from the command line
    alpha = float(sys.argv[1])

    # Iterate over all samples
    for i in range(0, NUM_SAMPLES):
        # Update mean rtt using EWMA equation
        # mu <--- mu * (1 - alpha) + alpha * RTT
        mean_rtt = mean_rtt * (1 - alpha) + alpha * rtt_samples[i]
        # Write it into the ith location of smooth_rtt
        smooth_rtt[i] = mean_rtt

    plt.plot(smooth_rtt)
    plt.show()
