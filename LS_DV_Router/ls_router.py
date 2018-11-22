# Base router class
from router import *
import math

# This is long enough so that broadcasts complete even on large topologies
BROADCAST_INTERVAL = 1000

# Class representing link state routers
class LSRouter(Router):
  def __init__(self, router_id):
    # Common initialization routines
    Router.__init__(self, router_id)

    # Is the broadcast complete? => Can we run Dijkstra's algorithm?
    # For now, we'll use a simple heuristic for this:
    # If BROADCAST_INTERVAL since the first link state advertisement (LSA) at time 0,
    # we'll declare the broadcast complete
    self.broadcast_complete = False

    # Have you run Dijkstra's algorithm? This is to ensure you don't repeatedly run it.
    self.routes_computed = False

    # LSA dictionary mapping from a router ID to the links for that router.
    # We'll initialize lsa_dict to this router's own links.
    self.lsa_dict = dict()

    # For each LSA received from a distinct router,
    # maintain if it has been broadcasted or not.
    # This is to avoid repeated broadcasts of the same LSA
    # We'll initialize self.broadcasted to reflect the fact that this router's own links
    # have not yet been broadcasted as of time 0.
    self.broadcasted = {self.router_id : False}

  # Initialize link state to this router's own links alone
  def initialize_algorithm(self):
    self.lsa_dict = {self.router_id :self.links}

  def tick(self, tick):
    if (tick >= BROADCAST_INTERVAL and (self.routes_computed == False)):
      # If broadcast phase is over, compute routes and return
      self.broadcast_complete = True
      self.dijkstras_algorithm()
      self.routes_computed = True
      return
    elif (tick < BROADCAST_INTERVAL):
      # TODO: Go through the LSAs received so far.
      # broadcast each LSA to this router's neighbors if the LSA has not been broadcasted yet
      for adv_router in self.lsa_dict:
        lsa        = self.lsa_dict[adv_router]
        if (adv_router in self.broadcasted and self.broadcasted[adv_router]):
          continue # move on to the next router
        else:
          # broadcast to all your neighbors, who will broadcast it to theirs and so on
          for neighbor in self.neighbors:
            self.send(neighbor, lsa, adv_router)
            self.broadcasted[adv_router] = True
    else:
      return

  # Note that adv_router is the router that generated this advertisment,
  # which may be different from "self",
  # the router that is broadcasting this advertisement by sending it to a neighbor of self.
  def send(self, neighbor, ls_adv, adv_router):
    neighbor.lsa_dict[adv_router] = ls_adv
    # It's OK to reinitialize this even if adv_router even if adv_router is in lsa_dict

  def dijkstras_algorithm(self):
    # TODO:
    # (1) Implement Dijkstra's single-source shortest path algorithm
    # to find the shortest paths from this router to all other destinations in the network.
    # Feel free to use a different shortest path algo. if you're more comfortable with it.
    # (2) Remember to populate self.fwd_table with the next hop for every destination
    # because simulator.py uses this to check your LS implementation.
    # (3) If it helps, you can use the helper function next_hop below to compute paths once you
    # have populated the prev dictionary which maps a destination to the penultimate hop
    # on the shortest path to this destination from this router.
    nodes = []
    distance = {}
    prev = {}
    # initialization
    distance[self.router_id] = 0  # Distance to the same router is 0
    prev[self.router_id] = -1     # There is no previous for a router connecting to itself
    prioq = [self.router_id]      # Poor man's priority queue for Dijkstra's algorithm 
    for router in self.lsa_dict:
      if (router != self.router_id):
        distance[router] = INFINITY
        prev[router] = -1
        prioq += [router]         # Add all routers that we have seen in the LSAs to prioq

    # the main priority queue based routine
    while (len(prioq) > 0):
      # Find and remove router with minimum distance. This is a very inefficient way to do it.
      min_router = min(prioq, key = lambda element: distance[element])
      prioq = [x for x in prioq if x != min_router]

      # For each neighbor of min_router
      for neighbor in self.lsa_dict[min_router]:
        # Find alternate distance through min_router
        alt_dist = distance[min_router] + self.lsa_dict[min_router][neighbor]

        # Change path if min_router has a better path
        if (alt_dist < distance[neighbor]):
          distance[neighbor] = alt_dist
          prev[neighbor] = min_router

    # Use the distance and prev dictionaries to compute next hops for fwd_table
    self.fwd_table[self.router_id] = self.router_id # initialize fwd_table for this router
    for router in self.lsa_dict: # For all other routers
      if (router != self.router_id):
        self.fwd_table[router] = self.next_hop(router, prev)    
    # print(self.router_id, self.fwd_table)

  def next_hop(self, dst, prev):
    assert (prev[dst] != -1)  # Can't find next_hop if dst is disconnected from self.router_id
    assert (self.router_id != dst)  # Nor if dst and self.router_id are the same
    if (prev[dst] == self.router_id):
      return dst  # base case, src and dst are directly connected
    else:
      return self.next_hop(prev[dst], prev)
