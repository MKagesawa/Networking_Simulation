MIN_TIMEOUT = 100    # minimum possible timeout
MAX_TIMEOUT = 10000  # maximum possible timeout

class TimeoutCalculator:
  """
  Timeout Calculator maintains the mean RTT and RTT variance. Data members of this class
  include alpha, beta and K (which have the same meaning as discussed in the lectures)
  """
  def __init__(self):
    self.mean_rtt      = 0.0
    self.rtt_var       = 0.0
    self.alpha         = 0.125       # alpha value for mean_rtt's EWMA
    self.beta          = 0.25        # beta value for rtt_var's EWMA
    self.k             = 4.0         # what multiple of RTT variation to use in the timeout
    #  Initialize the variable self.timeout to the minimum possible value
    self.timeout       = MIN_TIMEOUT
    self.ewma_init     = False       # EWMA is not initialized until the first sample is seen

  def update_timeout(self, rtt_sample):
    """
    This function is used to update the mean and variance RTTs
    """
    if (not self.ewma_init): # If you have seen no rtts yet or exponentially backed off before
      # Initialize mean_rtt to current sample
      self.mean_rtt = rtt_sample
      # Initialize rtt_var to half of current sample
      self.rtt_var  = rtt_sample/2
      # Set timeout using mean_rtt and rtt_var
      self.timeout  = self.mean_rtt + self.k * self.rtt_var
      # Remember to update self.ewma_init correctly so that the else branch is taken on subsequent packets.
      self.ewma_init = True

    else:
      # Update rtt var based on rtt_sample and old mean rtt
      # sigma < --- sigma * (1 - beta) + beta * | RTT - mu |
      self.rtt_var = self.rtt_var * (1 - self.beta) + self.beta * abs(rtt_sample - self.mean_rtt)
      # Update mean rtt based on rtt_sample
      self.mean_rtt = self.mean_rtt * (1 - self.alpha) + self.alpha * rtt_sample
      # Update timeout based on mean rtt and rtt var
      self.timeout = self.mean_rtt + 4 * self.rtt_var
      if self.timeout > MAX_TIMEOUT:
        self.timeout = MAX_TIMEOUT
      elif self.timeout < MIN_TIMEOUT:
        self.timeout = MIN_TIMEOUT
    return self.timeout
    
  def exp_backoff(self):
    """
    This function is used to double the timeout representing an exponential backoff
    """
    # Exponentially back off by doubling the timeout
    self.timeout *= 2
    # Re-initialize the EWMA
    self.ewma_init = False
    print ("exponential backoff here, re-initializing EWMA")
    if self.timeout > MAX_TIMEOUT:
      self.timeout = MAX_TIMEOUT
    elif self.timeout < MIN_TIMEOUT:
      self.timeout = MIN_TIMEOUT
    return self.timeout
