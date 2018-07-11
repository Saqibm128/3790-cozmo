import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps, Pose
import time
from ticTacToeLogic import Board, CPUGame, Tile

root_pose = cozmo.util.Vector2(0,0) #cube is used to sync cozmo to edge of board
cozmo_pose = cozmo.util.Vector2(0,0)
cozmo_rotation = 0 #o to 360, should be facing center of board, on start place
cube = None #cube to use for ticTacToe
board = Board()
game = CPUGame(board=board)


acceleration = cozmo.util.Vector3(0,0,0)

def moveCozmo(robot, x, y, rotation=0):
    '''
    Move cozmo to (x,y) with rotation degrees
    '''
    global cozmo_pose
    global cozmo_rotation
    global root_pose

    rotation = rotation % 360

    #align cozmo
    # robot.turn_in_place(degrees(0 - cozmo_rotation)).wait_for_completed() not implemented
    print("Moving Cozmo to: ({}, {})".format(x,y))
    # robot.move_lift(-5)

    #move y
    robot.go_to_pose(Pose(root_pose.position.x + 100 * x,root_pose.position.y + 100 * y, 0, angle_z=degrees(0))).wait_for_completed()

def moveCube(robot, x, y):
    global cube
    robot.pickup_object(cube, num_retries=3).wait_for_completed()
    moveCozmo(robot, x, y)
    robot.place_object_on_ground_here(cube, num_retries=3).wait_for_completed()

def cozmoMove(robot):
    x, y = game.nextMove()
    if not board.isDone:
        status = board.currentPlayer.value
        status = status + " is turn"
        robot.say_text(status).wait_for_completed()
        robot.say_text("Playing on {} {}".format(x, y)).wait_for_completed()
        board.play(x, y)
        moveCube(robot, x, y)
    else:
        robot.say_text("I am finished").wait_for_completed()
        if board.winner() == Tile.NO_WIN:
            robot.say_text("catscratch").wait_for_completed()
        else:
            winner = board.winner().value
            robot.say_text(winner + " has won").wait_for_completed()






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


def cozmo_program(robot: cozmo.robot.Robot):
    global root_pose
    global cube

    board = Board()
    robot.say_text("Tic Tac Toe").wait_for_completed()

    # robot.say_text("Let's Play TicTacToe").wait_for_completed()
    root_pose = robot.pose
    moveCozmo(robot, 0, 0)

    cube = robot.world.wait_for_observed_light_cube()
    print("Cube found:", cube.pose, cube.object_id)
    print(root_pose)

    while not board.isDone:
        cozmoMove(robot)
    # robot.add_event_handler(cozmo.objects.EvtObjectMovingStarted, handle_object_moving_started)
    # robot.add_event_handler(cozmo.objects.EvtObjectMoving, handle_object_moving)
    # robot.add_event_handler(cozmo.objects.EvtObjectMovingStopped, handle_object_moving_stopped)
    #
    # while True:
    #     time.sleep(1.0)

cozmo.run_program(cozmo_program)
