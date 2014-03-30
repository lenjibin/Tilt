from graphics3d import *
import Leap

makeGraphicsWindow(1280, 800,True)             

BALL_RADIUS = 1.5
FLOOR_WIDTH = 40
BUFFER = 0.05

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
        self.r = Vector(0,0,0)
        self.ax = 0
        self.ay = 0
        self.az = 0
        self.vel_y = 0
        self.y_dis = 0

    def set_pos(self,x,y,z):
        self.r.x = x
        self.r.y = y
        self.r.z = z

    def move(self,norm_vec):
        self.y_dis += self.vel_y
        if self.y_dis > 0:
            self.vel_y -= .04
        else:
            self.vel_y = 0
            self.y_dis = 0
        dx = norm_vec.x
        dy = norm_vec.y
        dz = norm_vec.z
        self.az += math.degrees(-dx/BALL_RADIUS)
        self.ay += math.degrees(dz/BALL_RADIUS)*math.sin(-dx/BALL_RADIUS)
        self.ax += math.degrees(dz/BALL_RADIUS)*math.cos(-dx/BALL_RADIUS)
        self.set_pos(self.r.x+dx,
                       (BALL_RADIUS - dx*(self.r.x+dx) - dz*(self.r.z+dz))/dy + self.y_dis,
                       self.r.z+dz)

        if self.r.x > FLOOR_WIDTH/2 - BALL_RADIUS or self.r.x < -FLOOR_WIDTH/2 + BALL_RADIUS:
            self.set_pos(self.r.x-dx,
                         self.r.y,
                         self.r.z)
        if self.r.z > FLOOR_WIDTH/2 - BALL_RADIUS or self.r.z < -FLOOR_WIDTH/2 + BALL_RADIUS:
            self.set_pos(self.r.x,
                         self.r.y,
                         self.r.z-dz)

    def jump(self):
        self.vel_y = 1

def sw(world):

    setCameraPosition(0,20,50)
    setCameraRotation(-15,0,0)

    world.leap_controller = Leap.Controller()
    world.frames = [0]*10
    
    world.textCanvas = Canvas2D(500, 100,1)
    
    world.ball = Ball(Sphere3D(BALL_RADIUS, 12, texture='textures/moonmap2k.jpg'))
    world.ball.set_pos(0,BALL_RADIUS,0)
    world.floor = Floor(Rect3D(FLOOR_WIDTH, FLOOR_WIDTH, texture = "Textures/floor tile.jpg"))

    world.recentlyFired = getElapsedTime()
    
    return world

def uw(world):

    world.frames = [world.leap_controller.frame()] + world.frames[:-1]
    currentFrame = world.frames[0]

    if currentFrame.is_valid:
        if not currentFrame.hands.is_empty:
            hand = currentFrame.hands[0]
            normal = hand.palm_normal
            (world.floor.rot_x, world.floor.rot_y, world.floor.rot_z) = (-normal.z*Leap.RAD_TO_DEG, normal.x*Leap.RAD_TO_DEG, 0)#direction.yaw*Leap.RAD_TO_DEG)
            norm_vec = -normal
            world.ball.move(Vector(norm_vec.x, norm_vec.y, norm_vec.z))
            
    if world.frames[0] is not 0 and world.frames[1] is not 0:
        if not world.frames[0].hands.is_empty and not world.frames[1].hands.is_empty:
            hand1 = world.frames[0].hands[0]
            hand2 = world.frames[1].hands[0]
            if not hand1.fingers.is_empty and not hand2.fingers.is_empty:
                finger1 = hand1.fingers[0]
                finger2 = hand2.fingers[0]
                if finger1.tip_position.y - finger2.tip_position.y >  20 and getElapsedTime() - world.recentlyFired > 1500:
                    world.ball.jump()
                    world.recentlyFired = getElapsedTime()

    if keyPressedNow(pygame.K_r):
        world.ball.r.x = 0
        world.ball.r.y = 0
        world.ball.r.z = 0
            
    return world

def dw(world):
    draw3D(world.ball.sphere3d, world.ball.r.x, world.ball.r.y + BUFFER, world.ball.r.z, world.ball.ax, world.ball.ay, world.ball.az)
    draw3D(world.floor.rect3d, 0, 0, 0,world.floor.rot_x+90,world.floor.rot_y,world.floor.rot_z)
    #clearCanvas2D(world.textCanvas)
    #drawString2D(world.textCanvas, world.string, 0,0, color="white")
    #draw2D(world.textCanvas, 0,0)

runGraphics(sw,uw,dw,frameRate=60)

