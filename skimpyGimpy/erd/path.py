
DOSMOOTH = True
import math
import heapq
from . import config
from . import entity
from . import card

class pathMaker:
    def __init__(self, origins, destinations, barriers, delta, stepLimit=1000000):
        (self.origins, self.destinations, self.barriers, self.delta, self.stepLimit) = (
            origins, destinations, barriers, delta, stepLimit)
        self.gdestinations = griddict(destinations, delta)
        self.gbarriers = griddict(barriers, delta)
        self.gorigins = griddict(origins, delta)
        self.pointCost = {}
        self.pointPrevious = {}
        self.visited = {}
        specials = self.gorigins.copy()
        specials.update(self.gdestinations)
        specials.update(self.gbarriers)
        self.specials = specials
        # (cost, gridpoint) for current points
        #heap = [ (0, origin) for origin in self.gorigins.keys() ]
        heap = []
        for origin in list(self.gorigins.keys()):
            if origin not in self.gbarriers:
                heap.append( (0, origin) )
        heapq.heapify(heap)
        self.heap = heap
        self.final_destination = None
    def addEstimate(self, point, previous, cost):
        # increase cost by one penalty point for each special within two ticks
        if point in self.gbarriers:
            #pr "barrier", point
            return # don't enter barrier
        (x,y) = point
        specials = self.specials
        for xx in range(x-2,x+3):
            for yy in range(y-2,y+3):
                if (xx,yy) in specials:
                    cost += 0.2
        oldcost = self.pointCost.get(point)
        if oldcost is None or cost<oldcost:
            heapq.heappush(self.heap, (cost, point) )
            self.pointCost[point] = cost
            self.pointPrevious[point] = previous
            #pr "added", point, cost, previous
    def process(self, point, baseCost):
        visited = self.visited
        if point in visited:
            # already processed at same or lesser cost: skip
            return
        visited[point] = True
        (x,y) = point
        newcost = baseCost+2
        for (dx, dy) in ((0,1), (0,-1), (1,0), (-1,0)):
            xx = x+dx
            yy = y+dy
            self.addEstimate((xx,yy), point, newcost)
        newcost = baseCost+3
        for (dx, dy) in ((1,1), (1,-1), (-1,1), (-1,-1)):
            xx = x+dx
            yy = y+dy
            self.addEstimate((xx,yy), point, newcost)
        # extra penalty for double jump (allows jump across barrier lines
        newcost = baseCost+10
        gdests = self.gdestinations
        gorig = self.gorigins
        for (dx, dy) in ((0,2), (0,-2), (2,0), (-2,0), (2,2), (2,-2), (-2,2), (-2,-2)):
            xx = x+dx
            yy = y+dy
            pp = (xx,yy)
            if pp not in gdests or pp in gorig:
                self.addEstimate(pp, point, newcost)
    def search(self):
        done = False
        count = 0
        stepLimit = self.stepLimit
        gdestinations = self.gdestinations
        while not done:
            count += 1
            if count>stepLimit:
                raise ValueError("step limit exceeded")
            (cost, nextp) = heapq.heappop(self.heap)
            if nextp in gdestinations:
                self.final_destination = nextp
                done = True
                self.path_cost = cost
                return
            else:
                self.process(nextp, cost)
    def extract(self):
        delta = self.delta
        final_destination = self.final_destination
        if final_destination is None:
            raise ValueError("no final destination found")
        gridpoints = []
        lastpoint = final_destination
        gorigins = self.gorigins
        visited = {}
        #cost = 0
        while lastpoint not in gorigins and lastpoint not in visited:
            gridpoints.append(lastpoint)
            visited[lastpoint] = True
            nextpoint = self.pointPrevious[lastpoint]
            #pr "lastpoint, cost", lastpoint, cost
            lastpoint = nextpoint
            #cost = self.pointCost[lastpoint]
        if lastpoint not in gorigins:
            raise ValueError("apparent loop in path at "+lastpoint)
        gridpoints.reverse()
        #pr "gridpoints", gridpoints
        start = gorigins[lastpoint]
        end = self.gdestinations[final_destination]
        midpoints = [(delta*gx, delta*gy) for (gx, gy) in gridpoints[1:-1]]
        path = [start]+midpoints+[end]
        #pr "path", path
        return (start, end, path)
    
def getPath(origins, destinations, barriers, delta, stepLimit=1000000):
    pm = pathMaker(origins, destinations, barriers, delta, stepLimit)
    pm.search()
    return pm.extract()

class CardinalPath:
    def __init__(self, start, path, end, minimum, maximum,
                 canvas, origins, destinations, cfg=None):
        if cfg is None:
            cfg = config.Configuration()
        self.cfg = cfg
        self.start = origins[start]
        self.path = path
        self.end = destinations[end]
        self.minimum = minimum
        self.maximum = maximum
        self.canvas = canvas
        self.origins = origins
        self.destinations = destinations
    def barriers(self):
        b = [self.start, self.end] + self.path
        result = {}
        for x in b:
            result[x] = True
        return result
    def draw(self):
        c = self.canvas
        cfg = self.cfg
        path = [self.start] + self.path + [self.end]
        if DOSMOOTH:
            smooth(path)
            smooth(path) # I said smooth, dammit
        c.setColor(*cfg.lineColor)
        c.setWidth(cfg.lineWidth)
        c.addLines(path)
        pent = self.path[-1]
        (up, right) = entity.orthogonals(pent, self.end)
        (upx, upy) = up
        (rightx, righty) = right
        minimum = self.minimum
        maximum = self.maximum
        if minimum is not None and maximum is not None:
            crd = card.Cardinality(minimum, maximum, upx, upy, rightx, righty,
                           cfg.delta, c)
            (x,y) = self.end
            crd.drawAt(x,y)

def smooth(path):
    lpath = len(path)
    for i in range(2, lpath-3):
        path[i] = mix(path[i-2], path[i-1], path[i], path[i+1], path[i+2])

def mix(pmm, pminus, p, pplus, ppp):
    (xmm, ymm) = pmm
    (xm, ym) = pminus
    (x,y) = p
    (xp, yp) = pplus
    (xpp, ypp) = ppp
    xmix = xmm/16.0 + xm/4.0+x*3/8.0+xp/4.0 + xpp/16.0
    ymix = ymm/16.0 + ym/4.0+y*3/8.0+yp/4.0 + ypp/16.0
    return (xmix, ymix)
    
def griddict(D, delta):
    result = {}
    for p in list(D.keys()):
        result[gridpoint(p, delta)] = p
    return result

def gridpoint(p, delta):
    (x,y) = p
    fd = float(delta)
    gx = int(round(x/fd))
    gy = int(round(y/fd))
    return (gx, gy)

def test(fontdir=".", outfile="/tmp/out.png"):
    from skimpyGimpy import canvas
    from .entity import Entity
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/atari-small.bdf")
    l = Entity("test literal", c, 120, 240)
    #l = Entity("t", c, 60, 0)
    l2 = Entity(["another", "test", "literal"], c, -120, -120)
    #l2 = Entity("a", c, -60, 0)
    l3 = Entity("barrier entity", c, 0, 0)
    l4 = Entity(["another", "barrier"], c, -120, 48)
    #l3 = Entity("b", c, 0, 0)
    l.draw()
    l2.draw()
    l3.draw()
    l4.draw()
    origins = l.destinationMap()
    destinations = l2.destinationMap()
    barriers = {}
    for x in [l, l2, l3, l4]:
        barriers.update( x.barriers() )
    barriers.update( l3.destinationMap() )
    barriers.update( l4.destinationMap() )
    (start, end, path) = getPath(origins, destinations, barriers, 12)
    c.setColor(90, 90, 0)
    #c.addLines(path)
    pth = CardinalPath(start, path, end, 0, "many",
                 c, origins, destinations)
    pth.draw()
    c.dumpToPNG(outfile)
    print("test output to", outfile)

if __name__=="__main__":
    test()

