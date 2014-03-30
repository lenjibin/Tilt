from graphics3d import *
import Leap

makeGraphicsWindow(1280, 800,True)             

BALL_RADIUS = 1
BUFFER = .1

class Vector:
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z
        
    def dot(self, other):
        return self.x*other.x + self.y*other.y + self.z*other.z

    def norm(self):
        return (self.x**2 + self.y**2 + self.z**2)**.5

    def add(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def sub(self, other):
        return self.add(other.mul(-1.0))
    
    def mul(self, scale):
        return Vector(self.x*scale, self.y*scale, self.z*scale)

    def div(self, scale):
        return self.mul(1.0/scale)

class Floor:
    def __init__(self, rect3d):
        self.rect3d = rect3d
        self.rot_x = 0
        self.rot_y = 0
        self.rot_z = 0

class Ball:
    def __init__(self, sphere3d):
        self.sphere3d = sphere3d
        self.a = Vector(0,0,0)
        self.v = Vector(0,0,0)
        self.r = Vector(0,0,0)

    def set_pos(self,x,y,z):
        self.r.x = x
        self.r.y = y
        self.r.z = z

    def move(self,norm_vec):
        g = Vector(0,-100,0)
        self.a = g.sub(norm_vec.mul(g.dot(norm_vec)))
        self.v = self.v.add(self.a.div(200.0))
        self.v.y = 0
        self.r = self.r.add(self.v.div(200.0))
        #self.r.x += dx
        #self.az += math.degrees(-dx/BALL_RADIUS)
        #we will calculate the y position later
        #self.y += dy
        #self.r.z += dz
        #self.ay += math.degrees(dz/BALL_RADIUS)*math.sin(-dx/BALL_RADIUS)
        #self.ax += math.degrees(dz/BALL_RADIUS)*math.cos(-dx/BALL_RADIUS)

def sw(world):

    setCameraPosition(0,10,30)

    world.leap_controller = Leap.Controller()
    world.frames = []*10
    
    world.textCanvas = Canvas2D(500, 100,1)
    
    world.ball = Ball(Sphere3D(BALL_RADIUS, 12, texture='textures/moonmap2k.jpg'))
    world.ball.set_pos(0,BALL_RADIUS,0)
    world.floor = Floor(Rect3D(20, 20, texture = "Textures/floor tile.jpg"))

    world.string = ""
    
    return world

def uw(world):

    world.frames = [world.leap_controller.frame()] + world.frames[:-1]
    currentFrame = world.frames[0]

    if currentFrame.is_valid:
        if not currentFrame.hands.is_empty:
            hand = currentFrame.hands[0]
            direction = hand.direction
            normal = hand.palm_normal
            (world.floor.rot_x, world.floor.rot_y, world.floor.rot_z) = (direction.pitch*Leap.RAD_TO_DEG, normal.roll*Leap.RAD_TO_DEG, 0)#direction.yaw*Leap.RAD_TO_DEG)
            norm_vec = -normal
            world.ball.move(Vector(norm_vec.x, norm_vec.y, norm_vec.z))
            world.ball.set_pos(world.ball.r.x,
                               (BALL_RADIUS - norm_vec.x*world.ball.r.x - norm_vec.z*world.ball.r.z)/norm_vec.y,
                               world.ball.r.z)
            #world.string = "dx: " + str(norm_vec.x) + ", \ndz: " + str(norm_vec.z)

    if keyPressedNow(pygame.K_r):
        world.ball.r.x = 0
        world.ball.r.y = 0
        world.ball.r.z = 0
            
    return world

def dw(world):
    draw3D(world.ball.sphere3d, world.ball.r.x, world.ball.r.y + BUFFER, world.ball.r.z-20, 0, 0, 0)
    draw3D(world.floor.rect3d, 0, 0, -20,world.floor.rot_x+90,world.floor.rot_y,world.floor.rot_z)
    clearCanvas2D(world.textCanvas)
    drawString2D(world.textCanvas, world.string, 0,0, color="white")
    draw2D(world.textCanvas, 0,0)

runGraphics(sw,uw,dw,frameRate=200)

