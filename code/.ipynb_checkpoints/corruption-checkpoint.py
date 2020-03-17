import networkx as nx
import numpy as np

class Agent(object):
    ''' This class creates an agent, with an init method that requires:
    role     :: In this model, agents can be 'private', 'public', or
                'criminal'
    corrupt  :: The proportion of agents that start as corrupt
    riskav   :: Risk aversion of the agent. It is a random variable that
                draws from a uniform distribution if "u"; from a beta(2, 5)
                if "l" (low); from a beta(5, 2) if "h" (high); and from
                a beta(2,2) if "m" (medium).
    
    Also, this class is initialized with a random choice of one out of
    three existing political parties,the total payoff from corrupt
    transactions, whether the agent is under investigation, and a 
    factor by which its risk aversion increases every time the agents 
    get under investigation '''
    def __init__(self, role, corrupt, riskav):
        self.__role = role
        if self.__role == 'criminal':
            self.__corrupt = 1
        else:
            self.__corrupt = np.random.choice([1, 0], p=[corrupt, (1 - corrupt)])
        self.__transize = np.random.randint(100, 1000)
        self.__party = np.random.choice(['A', 'B', 'C'])
        self.__payoff = 0
        self.__investigation = 0
        self.__ifactor = np.random.randint(3, 15) / 100
        if riskav == 'u':
            self.__riskav = np.random.random()
        elif riskav == 'l':
            self.__riskav = np.random.beta(2, 5)
        elif riskav == 'h':
            self.__riskav = np.random.beta(5, 2)
        elif riskav == 'm':
            self.__riskav = np.random.beta(2, 2)
        else:
            raise ValueError("Not a valid argument!")

    # The following are getter methods.
    def getRole(self):
        return self.__role

    def getCorrupt(self):
        return self.__corrupt

    def getTransize(self):
        return self.__transize

    def getParty(self):
        return self.__party

    def getPayoff(self):
        return self.__payoff

    def getInvestigation(self):
        return self.__investigation

    def getRiskav(self):
        return self.__riskav

    def getIfactor(self):
        return self.__ifactor

    # And here are the setters.
    def setCorrupt(self, newval):
        self.__corrupt = newval

    def setPayoff(self, newval2):
        self.__payoff += newval2

    def setRiskav(self, newval3):
        self.__riskav += newval3

    def setInv(self, newval4):
        self.__investigation = newval4

        
class Model(object):
    '''This creates a new instance of the model, and is initialized with:
    num        :: The total number of agents.
    net0       :: How the initial network is setup. "R" for random,
                  "S" for small world, and "H" for homophily based.
    netup      :: How the network gets updated. "R" for random and 
                  "H" for homophily dynamic. 
    nmin, nmax :: Boundaries for the random variable that controls how many
                  attempts of transaction are going to occur at every time 
                  step.  
    maxpay     :: Maximum payoff that any agent can hold until it is 
                  investigated.
    pc         :: Probability that a corrupt agent gets caught
    corrupt    :: initial proportion of corrupt agents
    riskav     :: distribution for the random variable risk aversion'''
    def __init__(self, num, net0, netup, nmin, nmax, maxpay, pc, corrupt =0.05, riskav='u'): 
        self.__num = num
        self.__net0 = net0
        self.__netup = netup
        self.__nmin = nmin
        self.__nmax = nmax
        self.__maxpay = maxpay
        self.__pc = pc
        self.__corrupt = corrupt
        self.__riskav = riskav
        self.__private = []
        self.__public = []
        self.__criminal = []
        self.__agentset = []
        self.__net = nx.Graph()
        self.__jail = []
        self.__transactions = []

    def Generate(self):
        ''' This method appends agents to the list and then, appends 
            them to their corresponding list, according to their role'''
        for pri in range(round(self.__num * 0.7)):
            self.__agentset.append(Agent('private', self.__corrupt, self.__riskav))

        for pub in range(round(self.__num * 0.19)):
            self.__agentset.append(Agent('public', self.__corrupt, self.__riskav))

        for cri in range(round(self.__num * 0.11)):
            self.__agentset.append(Agent('criminal', self.__corrupt, self.__riskav))

    def Step(self, p, pd, newenter):
        self.NetUpdate(p, pd)
        self.Interact()
        self.CheckCorruption(newenter)
        self.Subset()

    def Subset(self):
        ''' This method takes the list of agents and creates three lists,
        one for each role '''
        self.__private = []
        self.__public = []
        self.__criminal = []
        
        for agent in self.__net.nodes():
            if agent.getRole() == 'private':
                self.__private.append(agent)
            elif agent.getRole() == 'public':
                self.__public.append(agent)
            else:
                self.__criminal.append(agent)

    def NetSetup(self, p=None, pd=None):
        ''' This method creates a network from a set of agents. This is just the 
        initial setup of the network.
        The arguments are:
        p        :: probability of creating a new link. 
        pd       :: probability to delete a link. Only used in "HD"'''
        for agent in self.__agentset:
            self.__net.add_node(agent)

        nodes = list(self.__net.nodes())

        if self.__net0 == 'R':  # Random
            for i in range(len(nodes)):
                for j in range(i+1, len(nodes)):
                    if np.random.random() <= p:
                        self.__net.add_edge(nodes[i], nodes[j])
                    
        elif self.__net0 == 'S':  # Small World
            # First, the ring network
            for i in range(len(nodes) - 2):
                for j in [1, 2]:
                    self.__net.add_edge(nodes[i], nodes[i+j])
            # now for the next to last and last elements of the list (close the ring)
            for i in [-2, -1]:
                for j in [1, 2]:
                    self.__net.add_edge(nodes[i], nodes[i+j])
                
            edges = list(self.__net.edges())
            # Put all the edges "to remove" in one list
            toRemove = []
            for edge in edges:
                if np.random.random() <= p:
                    toRemove.append(edge)

            # Remove the edges
            self.__net.remove_edges_from(toRemove)

            # Loop through the first node of all "removed" edges and connect it with a random node.
            for edge in toRemove:
                i = edge[0]
                j = np.random.choice(nodes)
                # Next two lines are to make sure there are no self loops and number of links is the same as at the beginning
                while self.__net.degree(i) == 0:
                    if i != j:
                        self.__net.add_edge(i,j)
                
        elif self.__net0 == 'H':  # Homophily dynamic
            while nx.density(self.__net) < 0.06:
                # Start with only GA until 6% of the potential links in the network are present
                i = np.random.choice(nodes)
                ga = []
                for node in nodes:
                    if (node.getParty() == i.getParty()) and (i != node):
                        ga.append(node)
                j = np.random.choice(ga)
                if np.random.random() <= p:
                    self.__net.add_edge(i, j)
                    
            # Once the network has sufficient links, let's do the other processes until its density gets close to p
            while (nx.density(self.__net) >= 0.6) and (nx.density(self.__net) < p):
                # Global Attachment
                i = np.random.choice(nodes)
                ga = []
                for node in nodes:
                    if (node.getParty() == i.getParty()) and (i != node):
                        ga.append(node)
                j = np.random.choice(ga)
                if (np.random.random() <= p) and (i != j):
                    self.__net.add_edge(i, j)

                # Local Attachment
                iset = []
                for node in nodes:
                    if self.__net.degree(node) > 0:
                        iset.append(node)
                i = np.random.choice(iset)
                j = np.random.choice(list(self.__net.neighbors(i)))
                if self.__net.degree(j) > 0:
                    h = np.random.choice(list(self.__net.neighbors(j)))
                    if self.__net.has_edge(i, h) is False:
                        self.__net.add_edge(i, h)
            
                # Link deletion
                edges = list(self.__net.edges())
                for edge in edges:
                    if np.random.random() <= pd:
                        self.__net.remove_edge(edge[0], edge[1])

    def NetUpdate(self, p=None, pd=None):
        '''This function takes a network and "rewires" it. In case it is a 
           dynamic random network, the rewiring is random. In case it is a 
           homophily dynamic network, the rewiring happens through the GA,
           LA and LD processes.
           The arguments for the function are:
           p          :: probability of creating a link
           pd         :: probability of link deletion. Only used in "HD"'''

        nodes = list(self.__net.nodes())
        edges = list(self.__net.edges())
    
        if self.__netup == 'R':
            self.__net.remove_edges_from(edges)
            for i in range(len(nodes)):
                for j in range(i+1, len(nodes)):
                    if np.random.random() <= p:
                        self.__net.add_edge(nodes[i], nodes[j])
                    
        if self.__netup == 'H':
            # Global Attachment
            i = np.random.choice(nodes)
            ga = []
            for node in nodes:
                if (node.getParty() == i.getParty()) and (i != node):
                    ga.append(node)
            j = np.random.choice(ga)
            if np.random.random() <= p:
                self.__net.add_edge(i, j)

            # Local Attachment
            iset = []
            for node in nodes:
                if self.__net.degree(node) > 0:
                    iset.append(node)
            i = np.random.choice(iset)
            j = np.random.choice(list(self.__net.neighbors(i)))
            if self.__net.degree(j) > 0:
                h = np.random.choice(list(self.__net.neighbors(j)))
                if self.__net.has_edge(i, h) is False:
                    self.__net.add_edge(i, h)
            
            # Link deletion
            edges = list(self.__net.edges())
            for edge in edges:
                if np.random.random() <= pd:
                    self.__net.remove_edge(edge[0], edge[1])

    def Interact(self): 
        ''' The interaction between agents occurs in the following way:
            for every time step, a randomly chosen number of times we go through
            a loop where first a criminal agent (randomly selected) looks at its
            neighbors and selects a private or public one. If that agent is corrupt,
            a transaction happens and the corrupt agent gets a payoff. If it is not
            corrupt, it can accept the transaction with probability equal to 
            (1 - riskav)
            The same happens for a randomly selected private agent who looks at its 
            public neighbors.'''
        tt = 0

        for t in range(np.random.randint(self.__nmin, self.__nmax)):
            agenti = np.random.choice(self.__net.nodes())
            if (agenti.getCorrupt()) == 1 and (len(list(self.__net.neighbors(agenti))) > 0):
                agentj = np.random.choice(list(self.__net.neighbors(agenti)))
                if agentj.getCorrupt() == 1:
                    agentj.setPayoff(0.1 * agenti.getTransize())
                    tt += 1
                elif np.random.random() < (1 - agentj.getRiskav()):
                    agentj.setCorrupt(1)
                    agentj.setPayoff(0.1 * agenti.getTransize())
                    tt += 1
            
            #crinodes = []
            #for i in self.__net.nodes():
            #    if i.getRole() == 'criminal':
            #        crinodes.append(i)
            #c = np.random.choice(crinodes)
            #cneipri = []
            #cneipub = []
            #for nei in list(self.__net.neighbors(c)):
            #    if nei.getRole() == 'public':
            #        cneipub.append(nei)
            #    elif nei.getRole() == 'private':
            #        cneipri.append(nei)
            
            #if len(cneipri) > 0:
            #    pri = np.random.choice(cneipri)
            #    if pri.getCorrupt() == 1:
            #        pri.setPayoff(0.05 * c.getTransize())
            #        tt += 1
            #    elif np.random.random() < (1 - pri.getRiskav()):
            #        pri.setCorrupt(1)
            #        pri.setPayoff(0.05 * c.getTransize())
            #        tt += 1

            #if len(cneipub) > 0:
            #    pub = np.random.choice(cneipub)
            #    if pub.getCorrupt() == 1:
            #        pub.setPayoff(0.05 * c.getTransize())
            #        tt += 1
            #    elif np.random.random() < (1 - pub.getRiskav()):
            #        pub.setCorrupt(1)
            #        pub.setPayoff(0.05 * c.getTransize())
            #        tt += 1

            #prinodes = []
            #for i in self.__net.nodes():
            #    if (i.getRole() == 'private') and (i.getCorrupt() == 1):
            #        prinodes.append(i)
            #p = np.random.choice(prinodes)
            #pnei = []
            #for nei in list(self.__net.neighbors(p)):
            #    if nei.getRole() == 'public':
            #        pnei.append(nei)

            #if len(pnei) > 0:
            #    pub = np.random.choice(pnei)
            #    if pub.getCorrupt() == 1:
            #        pub.setPayoff(0.05 * c.getTransize())
            #        tt += 1
            #    elif np.random.random() < (1 - pub.getRiskav()):
            #        pub.setCorrupt(1)
            #        pub.setPayoff(0.05 * c.getTransize())
            #        tt += 1


        self.__transactions.append(tt)

    def CheckCorruption(self, newenter):
        ''' This methods should be used at the end of each time step.
        Once all transactions have been made and payoffs have been paid, 
        we check every agent's payoff. If it exceeds some value, an
        investigation occurs and the corruption is discovered with
        probability pc. The node goes to jail (is removed from the 
        network) and all of its neighbors came under investigation. 
        When this happens, the risk aversion for the corrupt neighbors
        increases by a factor ifactor.'''
        catched = []
        nodestodel = []
        for node in self.__net.nodes():
            if (node.getPayoff() >= self.__maxpay) and (np.random.random() <= self.__pc):
                role = node.getRole()
                catched.append(role)
                nodestodel.append(node)
                for nei in list(self.__net.neighbors(node)):
                    if nei.getInvestigation() == 0:
                        nei.setInv(1)
                    nei.setRiskav(nei.getRiskav() * nei.getIfactor())
        
        self.__net.remove_nodes_from(nodestodel)
        for i in nodestodel:
            self.__agentset.remove(i)

        self.__jail.append(catched)

        if newenter is True:
            toreplace = self.__jail[-1]
            for a in ['private', 'public']:
                for b in range(toreplace.count(a)):
                    self.__agentset.append(Agent(a, self.__corrupt, self.__riskav))

    def getJailed(self):
        return self.__jail

    def getNet(self):
        return self.__net

    def getTransactions(self):
        return self.__transactions
    
    def getPrivate(self):
        return self.__criminal
    
    def CorruptCount(self):
        c = 0
        for i in self.__net.nodes():
            if i.getCorrupt() == 1:
                c += 1
        return c
