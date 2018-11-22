class Router:
  def __init__(self, router_id):
    # List holding references to all neighbor router objects
    # This is required to send advertisements to the neighbor router objects
    self.neighbors = []

    # Dictionary mapping a neighbor's ID to the link cost to/from that neighbor.
    # (We'll assume network is undirected. So, link costs are identical in both directions.)
    self.links = dict()

    # ID of this router
    self.router_id = router_id

    # Forwarding table at each router, which maintains next hop for each destination,
    # by mapping from destination to next hop's router ID
    # This is the common output of both LS and DV.
    # It is used by simulator.py to print out shortest paths.
    self.fwd_table = dict()

  # Populate self.neighbors
  def add_neighbors(self, neighbors):
    self.neighbors = neighbors

  # Populate self.links
  def add_links(self, links):
    self.links = links
