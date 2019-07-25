
from . import config
from . import entity
from . import relationship
from . import attribute
from . import path

class Drawing:
    def __init__(self, canvas, cfg=None):
        if cfg is None:
            cfg = config.Configuration()
        self.cfg = cfg
        self.canvas = canvas
        self.nameToEntity = {}
        self.nameToRelationship = {}
        self.namesToAttributeAndPath = {}
        self.nameRoleToPath = {}
    def addEntity(self, name, x, y):
        theEntity = entity.Entity(name, self.canvas, x, y, cfg=self.cfg)
        self.nameToEntity[name] = theEntity
    def addRelationship(self, name, x, y):
        theRelationship = relationship.Relationship(name, self.canvas, x, y, cfg=self.cfg)
        self.nameToRelationship[name] = theRelationship
    def participate(self, entityName, relationshipName, roleName, minimum, maximum):
        theEntity = self.nameToEntity[entityName]
        theRelationship = self.nameToRelationship[relationshipName]
        #origins = theEntity.destinationMap()
        #destinations = theRelationship.destinationMap()
        #barriers = self.allBarriers(origins, destinations)
        #(start, end, points) = path.getPath(origins, destinations, barriers, self.cfg.delta)
        #thePath = path.CardinalPath(start, points, end, minimum, maximum, self.canvas, origins, destinations)
        thePath = None
        self.nameRoleToPath[ (relationshipName, roleName, entityName) ] = (thePath, minimum, maximum)
    def addAttribute(self, name, entityName, x, y, iskey=False):
        theAttribute = attribute.Attribute(name, self.canvas, x,y, cfg=self.cfg, underline=iskey)
        theEntity = self.nameToEntity.get(entityName)
        if theEntity is None:
            theEntity = self.nameToRelationship.get(entityName)
        #origins = theAttribute.destinationMap()
        #destinations = theEntity.destinationMap()
        #barriers = self.allBarriers(origins, destinations)
        #(start, end, points) = path.getPath(origins, destinations, barriers, self.cfg.delta)
        #thePath = path.CardinalPath(start, points, end, None, None, self.canvas, origins, destinations)
        thePath = None
        self.namesToAttributeAndPath[(name, entityName)] = (theAttribute, thePath)
    def prepare(self):
        "assign all paths, avoiding obstacles"
        participations = list(self.nameRoleToPath.keys())
        participations.sort()
        for p in participations:
            (rname, rolename, ename) = p
            (thePath, minimum, maximum) = self.nameRoleToPath[p]
            theEntity = self.nameToEntity[ename]
            theRelationship = self.nameToRelationship[rname]
            origins = theEntity.destinationMap()
            destinations = theRelationship.destinationMap()
            barriers = self.allBarriers(origins, destinations)
            (start, end, points) = path.getPath(origins, destinations, barriers, self.cfg.delta)
            thePath = path.CardinalPath(start, points, end, minimum, maximum, self.canvas, origins, destinations)
            self.nameRoleToPath[ (rname, rolename, ename) ] = (thePath, minimum, maximum)
        attributePairs = list(self.namesToAttributeAndPath.keys())
        attributePairs.sort()
        for p in attributePairs:
            (name, entityName) = p
            (theAttribute, thePath) = self.namesToAttributeAndPath[p]
            theEntity = self.nameToEntity.get(entityName)
            if theEntity is None:
                theEntity = self.nameToRelationship.get(entityName)
            origins = theAttribute.destinationMap()
            destinations = theEntity.destinationMap()
            barriers = self.allBarriers(origins, destinations)
            (start, end, points) = path.getPath(origins, destinations, barriers, self.cfg.delta)
            thePath = path.CardinalPath(start, points, end, None, None, self.canvas, origins, destinations)
            self.namesToAttributeAndPath[(name, entityName)] = (theAttribute, thePath)
    def draw(self):
        for e in list(self.nameToEntity.values()):
            e.draw()
        for r in list(self.nameToRelationship.values()):
            r.draw()
        for (a, p) in list(self.namesToAttributeAndPath.values()):
            a.draw()
        for (p,minimum,maximum) in list(self.nameRoleToPath.values()):
            p.draw()
        for (a, p) in list(self.namesToAttributeAndPath.values()):
            p.draw()
    def allBarriers(self, origins, destinations):
        barriers = {}
        for e in list(self.nameToEntity.values()):
            barriers.update(e.barriers())
        for r in list(self.nameToRelationship.values()):
            barriers.update(r.barriers())
        for (a, p) in list(self.namesToAttributeAndPath.values()):
            barriers.update(a.barriers())
        for p in list(origins.keys())+list(destinations.keys()):
            if p in barriers:
                del barriers[p]
        for (a, p) in list(self.namesToAttributeAndPath.values()):
            if p is not None:
                barriers.update(p.barriers())
        for (p, minimum, maximum) in list(self.nameRoleToPath.values()):
            if p is not None:
                barriers.update(p.barriers())
        return barriers
    
def test(fontdir=".", outfile="/tmp/out.png"):
    from skimpyGimpy import canvas
    from .entity import Entity
    c = canvas.Canvas()
    #c.addFont("propell", fontdir+"/5x7.bdf")
    c.addFont("propell", fontdir+"/propell.bdf")
    d = Drawing(c)
    d.addEntity("EMPLOYEE", 0, 0)
    d.addEntity("DEPT", 0, 200)
    d.addEntity("PROJECT", -200, 0)
    d.addRelationship(("WORKS", "FOR"), 0, 100)
    d.addRelationship(("MANAGES"), -100, 0)
    d.addRelationship("WORKS-ON", -200,100)
    d.addRelationship("OWNS", 200, 100)
    d.participate("DEPT", "OWNS", "dept", 1, "many")
    d.participate("PROJECT", "OWNS", "p", 1, "many")
    d.participate("EMPLOYEE", ("WORKS", "FOR"), "EMP", 1, 1)
    d.participate("DEPT", ("WORKS", "FOR"), "dept", 0, "many")
    d.participate("EMPLOYEE", "MANAGES", "EMP", 0, 1)
    d.participate("DEPT", "MANAGES", "dept", 1, 1)
    d.participate("EMPLOYEE", "WORKS-ON", "emp", 0, "many")
    d.participate("PROJECT", "WORKS-ON", "proj", 0, "many")
    d.addAttribute("ssn", "EMPLOYEE", 300, -100, iskey=True)
    d.addAttribute("enum", "EMPLOYEE", 0, -100)
    d.addAttribute("first", "EMPLOYEE", 100, -100)
    d.addAttribute("last", "EMPLOYEE", 200, -100)
    d.addAttribute("dnum", "DEPT", -100, 200)
    d.prepare()
    d.draw()
    c.dumpToPNG(outfile)
    print("test output to", outfile)
   
def test2(fontdir=".", outfile="/tmp/out2.png"):
    from skimpyGimpy import canvas
    from .entity import Entity
    c = canvas.Canvas()
    #c.addFont("propell", fontdir+"/5x7.bdf")
    c.addFont("propell", fontdir+"/propell.bdf")
    d = Drawing(c)
    d.addEntity("EMPLOYEE", 0, 0)
    d.addEntity("DEPT", 0, 100)
    d.addEntity("PROJECT", 0, 200)
    d.addRelationship(("WORKS", "FOR"), -100, 0)
    d.addRelationship(("MANAGES"), -100, 100)
    d.addRelationship("WORKS-ON", -100, 200)
    d.addRelationship("OWNS", -100, 300)
    d.participate("DEPT", "OWNS", "dept", 1, "many")
    d.participate("PROJECT", "OWNS", "p", 1, "many")
    d.participate("EMPLOYEE", ("WORKS", "FOR"), "EMP", 1, 1)
    d.participate("DEPT", ("WORKS", "FOR"), "dept", 0, "many")
    d.participate("EMPLOYEE", "MANAGES", "EMP", 0, 1)
    d.participate("DEPT", "MANAGES", "dept", 1, 1)
    d.participate("EMPLOYEE", "WORKS-ON", "emp", 0, "many")
    d.participate("PROJECT", "WORKS-ON", "proj", 0, "many")
    d.addAttribute("ssn", "EMPLOYEE", 100, 300, iskey=True)
    d.addAttribute("enum", "EMPLOYEE", 100,150)
    d.addAttribute("first", "EMPLOYEE", 100, 50)
    d.addAttribute("last", "EMPLOYEE", 100, 200)
    d.addAttribute("dnum", "DEPT", 100, 0, iskey=True)
    d.addAttribute("title", ("WORKS", "FOR"), 100, -50)
    d.addAttribute("since", "OWNS", 100, -100)
    d.prepare()
    d.draw()
    c.dumpToPNG(outfile)
    print("test output to", outfile)
    
def test3(fontdir=".", outfile="/tmp/out3.png"):
    from skimpyGimpy import canvas
    from .entity import Entity
    c = canvas.Canvas()
    c.addFont("propell", fontdir+"/propell.bdf")
    d = Drawing(c)
    d.addEntity("EMPLOYEE", 0, 0)
    d.addEntity("DEPT", 200, 0)
    d.addEntity("PROJECT", 400, 0)
    d.addRelationship(("WORKS", "FOR"), 100, 100)
    d.addRelationship(("MANAGES"), 100, -50)
    d.addRelationship("WORKS-ON", 300, -100)
    d.addRelationship("OWNS", 300, 0)
    d.addAttribute("ssn", "EMPLOYEE", 0, -50, iskey=True)
    d.participate("DEPT", "OWNS", "dept", 1, "many")
    d.participate("PROJECT", "OWNS", "p", 1, "many")
    d.participate("EMPLOYEE", ("WORKS", "FOR"), "EMP", 1, 1)
    d.participate("DEPT", ("WORKS", "FOR"), "dept", 0, "many")
    d.participate("EMPLOYEE", "MANAGES", "EMP", 0, 1)
    d.participate("DEPT", "MANAGES", "dept", 1, 1)
    d.participate("EMPLOYEE", "WORKS-ON", "emp", 0, "many")
    d.participate("PROJECT", "WORKS-ON", "proj", 0, "many")
    d.addAttribute("enum", "EMPLOYEE", 0,-100)
    d.addAttribute("first", "EMPLOYEE", 0,50)
    d.addAttribute("last", "EMPLOYEE", 0,100)
    d.addAttribute("dnum", "DEPT", 200, -50, iskey=True)
    d.addAttribute("title", ("WORKS", "FOR"), 100, 150)
    d.addAttribute("since", "OWNS", 300, 60)
    d.prepare()
    d.draw()
    c.dumpToPNG(outfile)
    print("test output to", outfile)

if __name__=="__main__":
    test3()
    
