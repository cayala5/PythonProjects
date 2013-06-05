#
# christian ayala
#
# date: 12.14.12
#

from visual import *
import random

# brief instructions
"""
-Your goal is to sink all the yellow balls in the black balls.
-Click anywhere to send the NegCue in that direction. I recommend rotating
the scene until you have a top view before you click. Pressing "v" will
toggle the hanging lamp's visibility. Pressing "r" will reset the NegCue
to its starting position
-A black ball can only sink one ball. Once it has sunk a ball, it can itself
be sunk by another black ball.
-Play will only end once all yellow balls are sunk or all blackballs have sunk
or been sunk. Note that if you don't have enough black balls to sink the
remaining yellow balls, you cannot win even if gameplay is still going
"""

#program constants
MOVETHRESHOLD = 0.2
FRICTION = .02
RATE = 100
MAXHIT = 30
BALLSIZE = 20

#whole-program functions
        
def collideB(x,y):
    """returns True if the two objects are colliding"""
    if x.main.pos.y != BALLSIZE or y.main.pos.y != BALLSIZE:
        return False
    distance = mag(x.main.pos - y.main.pos)
    if distance <= 2 * BALLSIZE:
        return True
    else:
        return False

def collideW(xBall):
    """ pass ball object.main to this
        returns True if the given object is colliding with walls
    """
    if abs(xBall.pos.x) >= 250 - BALLSIZE:
        return True
    elif abs(xBall.pos.z) >= 250 - BALLSIZE:
        return True
    else:
        return False

def colPlaneProj(vect):
    """projects any vector onto the xz+BALLSIZE plane"""
    xProj = proj(vect,vector(1,0,0))
    zProj = proj(vect,vector(0,0,1))
    return xProj + zProj + (0,BALLSIZE,0)

# method generators - methods that all three ball classes will need
def GENmoving(ballObj):
    """returns the .moving method for the input ballObject"""
    if ballObj.velocity == vector(0,0,0):
        return False
    else:
        return True

def GENfricStop(ballObj):
    """returns the .fricStop method for ballObject"""
    if mag(ballObj.velocity) <= MOVETHRESHOLD:
        ballObj.velocity = vector(0,0,0)

def GENfriction(ballObj):
    """returns the .friction method for ballObject"""
    fricVector = (norm(ballObj.velocity) * -1) * FRICTION
    ballObj.velocity += fricVector

def GENhitIt(ballObj):
    """returns the .hitIt method for ballObject"""
    ballObj.main.pos += ballObj.velocity

def GENwallCollision(ballObj):
    """ returns the .wallCollision method for ballObject """
    axis = vector(0,1,0)
    if abs(ballObj.main.pos.x) >=250-BALLSIZE and \
       abs(ballObj.main.pos.z) >=250-BALLSIZE:
        ballObj.velocity = -1 * ballObj.velocity
        if ballObj.main.pos.x > 0:
            ballObj.main.pos.x = 250-BALLSIZE
        else:
            ballObj.main.pos.x = -1 * (250-BALLSIZE)
        if ballObj.main.pos.z > 0:
            ballObj.main.pos.z = 250 - BALLSIZE
        else:
            ballObj.main.pos.z = -1 * (250 - BALLSIZE)
    elif abs(ballObj.main.pos.x) >= 250-BALLSIZE:
        ballObj.velocity.x *= -1
        if ballObj.main.pos.x > 0:
            ballObj.main.pos.x = 250-BALLSIZE
        else:
            ballObj.main.pos.x = -1 * (250-BALLSIZE)  
    elif abs(ballObj.main.pos.z) >= 250-BALLSIZE:
        ballObj.velocity.z *= -1
        if ballObj.main.pos.z > 0:
            ballObj.main.pos.z = 250 - BALLSIZE
        else:
            ballObj.main.pos.z = -1 * (250 - BALLSIZE)

def GENballCollision(ballObj, collObj):
    """return the .ballCollision method for ballObj """
    ballObj.main.pos -= ballObj.velocity
    collObj.main.pos -= collObj.velocity
    collVelocity = ballObj.velocity - collObj.velocity
    connectNorm = norm(ballObj.main.pos - collObj.main.pos)
    collDir = rotate(vector=connectNorm, angle=math.pi/2, axis=(0,1,0))
    ballObj.velocity = proj(collVelocity, collDir)
    collObj.velocity = proj(collVelocity, connectNorm)
    

#scene set-up
scene.visible = False
scene.width = 800
scene.height = 600
scene.lights[0].color = (0.65,0.65,0.5)
scene.background = (0,0,0)#(0,.807,.819)#(1,1,1)

#hanging light
HANGCOLOR = color.gray(0.1)
HANGMATERIAL = materials.diffuse
HANGHEIGHT = 700
HANGLENGTH = 300
hangLight = frame(pos=(0,HANGHEIGHT,0), axis=(0,0,1))
hangLamp = local_light(frame=hangLight, pos=(0,-1 * HANGLENGTH,0),
                       color=(1,1,0.5))
hangBulb = sphere(frame=hangLight, pos=(0,-1 * HANGLENGTH,0), color=(1,1,0),
                  material=materials.emissive, radius=32.5)
hangFixt = cone(frame=hangLight, pos=(0,-12.5 - HANGLENGTH,0), color=HANGCOLOR,
                material=HANGMATERIAL, axis=(0,75,0), radius=62.5)
hangWire = cylinder(frame=hangLight, pos=(0,0,0), axis=(0,-1 * HANGLENGTH,0),
                    radius=3.5, color=HANGCOLOR, material=HANGMATERIAL)
hangLight.visible = True

#playing field
field = frame()
fieldFloor = box(frame=field, pos=(0,-0.5,0), material=materials.rough,
                 color=(0,0.25,0), length=500, width=500, height=1)
WALLMATERIAL = material=materials.wood
WALLCOLOR = (0.545,.270,.075)
fieldNWall = box(frame=field, pos=(62.5,4.5,-312.5), color=WALLCOLOR,
                 material=WALLMATERIAL, length=625, width=125, height=11)
fieldEWall = box(frame=field, pos=(312.5,4.5,62.5), color=WALLCOLOR,
                 material=WALLMATERIAL, length=125, width=625, height=11)
fieldSWall = box(frame=field, pos=(-62.5,4.5,312.5), color=WALLCOLOR,
                 material=WALLMATERIAL, length=625, width=125, height=11)
fieldWWall = box(frame=field, pos=(-312.5,4.5,-62.5), color=WALLCOLOR,
                 material=WALLMATERIAL, length=125, width=625, height=11)

scene.visible = True

class negCue:
    """the cue ball that hits negaBalls"""

    def __init__(self):
        """creates the negCue"""
        self.main = frame()
        cue = sphere(pos=(0,0,0), frame=self.main, radius=BALLSIZE,
                     color=(.51,0,.51), material=materials.marble)
        self.indicator = arrow(pos=(0,BALLSIZE + 50,0), frame=self.main,
                          shaftwidth = 15, color=(1,1,0), axis=(0,-47,0))
        self.cue = cue
        self.main.pos = (0,BALLSIZE,0)
        self.velocity = vector(0,0,0)
        self.state = "It's just more convenient that negCue have this attrib."

    def moving(self):
        """returns True if the cue has speed in any direction"""
        return GENmoving(self)

    def fricStop(self):
        """stops the cue if its speed falls below the MOVETHRESHOLD"""
        return GENfricStop(self)

    def friction(self):
        """adjusts the cues velocity by FRICTION"""
        return GENfriction(self)

    def hitIt(self):
        """moves cue according to its velocity"""
        return GENhitIt(self)

    def wallCollision(self):
        """ modifies cue velocity if it collides with something """
        return GENwallCollision(self)

    def ballCollision(self, collObj):
        """ modifies cue velocity if it collides with negaBalls """
        if collObj.__class__.__name__ == "regBall":
            return
        else:
            return GENballCollision(self, collObj)

    def isFlying(self):
        """corrects this weird error where the ball gets up"""
        return GENisFlying(self)
        
            
    
class negaBall:
    """these balls are only moved by the negaCue and swallow regBalls"""
    
    def __init__(self,pos):
        """creates the negaBall"""
        self.main = frame()
        ball = sphere(frame=self.main, radius=BALLSIZE, pos=(0,0,0),
                      color=color.gray(0.065), material=materials.emissive)
        self.ball = ball
        self.main.pos = vector(pos)
        self.velocity = vector(0,0,0)
        self.state = "EMPTY"

    def moving(self):
        """returns True if the cue has speed in any direction"""
        return GENmoving(self)

    def fricStop(self):
        """stops the cue if its speed falls below the MOVETHRESHOLD"""
        return GENfricStop(self)

    def friction(self):
        """adjusts the cues velocity by FRICTION"""
        return GENfriction(self)

    def hitIt(self):
        """moves cue according to its velocity"""
        return GENhitIt(self)

    def wallCollision(self):
        """ modifies cue velocity if it collides with something """
        return GENwallCollision(self)

    def isFlying(self):
        """corrects this weird error where the ball gets up"""
        return GENisFlying(self)

    def ballCollision(self, collObj):
        """ modifies cue velocity if it collides with negaBalls """
        if self.state == "EMPTY":
            if collObj.__class__.__name__ == "regBall" or \
               (collObj.__class__.__name__ == "negaBall" and \
                collObj.state == "FULL"):
                self.swallow(collObj)
            else:
                return GENballCollision(self, collObj)
        elif self.state == "FULL" and \
             collObj.__class__.__name__ == "negaBall" and \
             collObj.state == 'EMPTY':
            collObj.swallow(self)
        else:
            return GENballCollision(self, collObj)

    def swallow(self, swalObj):
        """ turns this ball red and deletes the ball it swallows """
        self.ball.color = (0.65, 0, 0)
        self.ball.material == materials.emissive
        self.state = "FULL"
        swalObj.main.visible = False
        swalObj.state = "DEAD"
        swalObj.main.pos.y = 4 * BALLSIZE
        
        
    

class regBall:
    """These are the play balls"""

    def __init__(self,pos):
        """creates a conventional yellow billiard ball"""
        self.main = frame()
        ball = sphere(frame=self.main, radius=BALLSIZE, pos=(0,0,0),
                      color=(1,1,0), material=materials.plastic)
        self.ball = ball
        self.main.pos = vector(pos)
        self.velocity = vector(0,0,0)
        self.state = "LIVE"

    def moving(self):
        """returns True if the cue has speed in any direction"""
        return GENmoving(self)

    def fricStop(self):
        """stops the cue if its speed falls below the MOVETHRESHOLD"""
        return GENfricStop(self)

    def friction(self):
        """adjusts the cues velocity by FRICTION"""
        return GENfriction(self)

    def hitIt(self):
        """moves cue according to its velocity"""
        return GENhitIt(self)

    def wallCollision(self):
        """ modifies cue velocity if it collides with something """
        return GENwallCollision(self)

    def ballCollision(self, collObj):
        """ modifies cue velocity if it collides with negaBalls """
        if collObj.__class__.__name__ == "negCue":
            return
        else:
            return GENballCollision(self, collObj)



#populate playing field
neg = negCue()
PYRVEC = ((2 * BALLSIZE) * vector(1,0,0)) + vector(1,0,1)
PYRTHETA = 5 * math.pi/4
regB1 = regBall((100,BALLSIZE,100))
regB2 = regBall(regB1.main.pos + rotate(PYRVEC, angle= -1 * (math.pi/12),
                                         axis=(0,1,0)))
regB3 = regBall(regB1.main.pos + rotate(PYRVEC, angle= -5 * (math.pi/12),
                                         axis=(0,1,0)))

regB4 = regBall(regB2.main.pos + rotate(PYRVEC, angle= -5 * (math.pi/12),
                                         axis=(0,1,0))) 

negB1 = negaBall((-150,BALLSIZE,-150))
negB2 = negaBall(negB1.main.pos + rotate(PYRVEC, angle= -1 * (math.pi/12),
                                         axis=(0,1,0)))
negB3 = negaBall(negB1.main.pos + rotate(PYRVEC, angle= -5 * (math.pi/12),
                                         axis=(0,1,0)))
negB4 = negaBall(negB2.main.pos + rotate(PYRVEC, angle= -5 * (math.pi/12),
                                         axis=(0,1,0)))
negB5 = negaBall(negB1.main.pos + rotate(PYRVEC, angle=PYRTHETA, axis=(0,1,0)))
negB6 = negaBall(negB1.main.pos + rotate(PYRVEC, angle=PYRTHETA + math.pi,
                                         axis=(0,1,0)))

negBs = [negB1, negB2, negB3, negB4, negB5, negB6]
regBs = [regB1, regB2, regB3, regB4]
ballObjects = [neg] + negBs + regBs

t = 0
while True:
    rate(RATE)
    dt = 1/RATE
    
    #hangLight
    lampDT = 0.03
    angle = 0.001 * cos(t)
    hangLight.rotate(axis=(0,0,1), angle=angle)
    t += lampDT

    # cue-hitting mechanism
    hitVector = vector(0,0,0)
    if scene.mouse.events:
        m1 = scene.mouse.getevent()
        clickPos = colPlaneProj(m1.pos)
        if m1.press == "left":
            #find hitVector
            rawHitVector = (clickPos - neg.main.pos) * (1.0/30)
        elif m1.release == "left":
            if abs(mag(rawHitVector)) >= MAXHIT:
                hitVector = norm(rawHitVector) * MAXHIT
            else:
                hitVector = rawHitVector
                if not max([ball.moving() for ball in ballObjects]):
                    neg.velocity = hitVector

    #keyboard commands
    if scene.kb.keys:
        s = scene.kb.getkey()
        if s == "r": # a reset button for when things go wrong
            neg.main.pos = vector(0,BALLSIZE,0)
            neg.velocity = vector(0,0,0)
        elif s == "v": # toggle the lamp (there's still light)
            hangLight.visible = bool(int(hangLight.visible) - 1)
    

    # animation routine
    for i in range(len(ballObjects)):
        if ballObjects[i].state == "DEAD":
            ballObjects[i].velocity = vector(0,0,0)
        elif ballObjects[i] == neg or ballObjects[i].state != "DEAD":
            if collideW(ballObjects[i].main):
                ballObjects[i].wallCollision()
            ballObjects[i].hitIt()
            ballObjects[i].friction()
            ballObjects[i].fricStop()
            ballObjects[i].friction()
            for j in range(i+1,len(ballObjects)):
                if collideB(ballObjects[i], ballObjects[j]) == True:
                    ballObjects[i].ballCollision(ballObjects[j])

    if max([ball.moving() for ball in ballObjects]):
        neg.indicator.visible = False
    else:
        neg.indicator.visible = True


    # win/lose conditions
    if min([reg.state == "DEAD" for reg in regBs]):
        scene.forward = vector(0,0,-1)
        for ball in ballObjects:
            ball.main.pos.y = random.choice(range(BALLSIZE,HANGHEIGHT))
        winState = text(text='Way to go!', align='center', pos=(0,300,0),
                        color=color.green, height=100, depth=25)
        break
    elif min([nega.state != "EMPTY" for nega in negBs]):
        scene.forward = vector(0,0,-1)
        for ball in ballObjects:
            ball.main.pos.y = random.choice(range(BALLSIZE,HANGHEIGHT))
        loseState = text(text="Awww, you lost...", pos=(0,300,0),
                         align='center', color=color.red, height=100,
                         depth=25)
                         
        break
      

    
    
    



    
    
    
        



        

    
    
    


