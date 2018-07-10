import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps
import time
from ticTacToeLogic import Board

cozmo_position = cozmo.util.Vector2(0,0)
cozmo_rotation = 0 #o to 360, should be facing center of board, on start place


acceleration = cozmo.util.Vector3(0,0,0)

def moveCozmo(robot, x, y, rotation=0):
    '''
    Move cozmo to (x,y) with rotation degrees
    '''
    global cozmo_position
    global cozmo_rotation

    rotation = rotation % 360

    #align cozmo
    # robot.turn_in_place(degrees(0 - cozmo_rotation)).wait_for_completed() not implemented
    print("Moving Cozmo to: ({}, {})".format(x,y))
    #move y
    robot.drive_straight(distance_mm(50) * (y - cozmo_position.y), speed_mmps(50)).wait_for_completed()

    #move x
    robot.turn_in_place(degrees(90)).wait_for_completed()
    robot.drive_straight(distance_mm(50) * (x -  cozmo_position.x), speed_mmps(50)).wait_for_completed()
    robot.turn_in_place(degrees(rotation-90)).wait_for_completed()
    cozmo_position = cozmo.util.Vector2(x, y)
    cozmo_rotation = rotation






def calculateSpeed(acceleration, time):
    max = 400
    speed = (acceleration.x ** 2 + acceleration.y ** 2 + acceleration.z ** 2) **(1./2) * time
    if speed > max:
        speed = max
    return speed
def handle_object_moving_started(evt, **kw):
    global acceleration
    # This will be called whenever an EvtObjectMovingStarted event is dispatched -
    # whenever we detect a cube starts moving (via an accelerometer in the cube)
    print("Object %s started moving: acceleration=%s" %
          (evt.obj.object_id, evt.acceleration))
    acceleration = evt.acceleration

    # robot.say_text(note, voice_pitch=voice_pitch, duration_scalar=0.3).wait_for_completed()

def handle_object_moving(evt, **kw):
    # This will be called whenever an EvtObjectMoving event is dispatched -
    # whenever we detect a cube is still moving a (via an accelerometer in the cube)
    print("Object %s is moving: acceleration=%s, duration=%.1f seconds, speed=%.2f" %
          (evt.obj.object_id, evt.acceleration, evt.move_duration, calculateSpeed(evt.acceleration, evt.move_duration)))
    # robot.say_text(note, voice_pitch=, duration_scalar=0.3).wait_for_completed()

def handle_object_moving_stopped(evt, **kw):
    # This will be called whenever an EvtObjectMovingStopped event is dispatched -
    # whenever we detect a cube stopped moving (via an accelerometer in the cube)
    print("Object %s stopped moving: duration=%.1f seconds, speed=%s" %
          (evt.obj.object_id, evt.move_duration, calculateSpeed(acceleration, evt.move_duration)))

    print("Object Found:")


def cozmo_program(robot: cozmo.robot.Robot):
    board = Board()
    robot.say_text("Let's Play TicTacToe").wait_for_completed()
    moveCozmo(robot, 3, 3)
    moveCozmo(robot, 3, 1)
    moveCozmo(robot, 4, 2)
    # robot.add_event_handler(cozmo.objects.EvtObjectMovingStarted, handle_object_moving_started)
    # robot.add_event_handler(cozmo.objects.EvtObjectMoving, handle_object_moving)
    # robot.add_event_handler(cozmo.objects.EvtObjectMovingStopped, handle_object_moving_stopped)

    while True:
        time.sleep(1.0)

cozmo.run_program(cozmo_program)
