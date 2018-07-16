import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps, Pose
import time
from ticTacToeLogic import Board, CPUOpponent, Tile

root_pose = cozmo.util.Vector2(0,0) #cube is used to sync cozmo to edge of board
cozmo_pose = cozmo.util.Vector2(0,0)
cozmo_rotation = 0 #o to 360, should be facing center of board, on start place
cube = None #cube to use for ticTacToe
board = Board()
cpuOppo = CPUOpponent(board=board)
cozmoTile = Tile.X


acceleration = cozmo.util.Vector3(0,0,0)

tile_width = 85

def moveCozmo(robot, x, y, rotation=0, look_for_cube=False):
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
    robot.set_lift_height(.6).wait_for_completed() #after dropping lift, so it doesn't drag on the ground and affect position over time

    #move cozmo
    robot.set_head_angle(degrees(0), num_retries=10).wait_for_completed()

    if look_for_cube:
        action = robot.go_to_pose(Pose(root_pose.position.x + tile_width * x,root_pose.position.y + tile_width * y, 0, angle_z=degrees(rotation)))
        lookForCube(robot, action)
    else:
        action = robot.go_to_pose(Pose(root_pose.position.x + tile_width * x,root_pose.position.y + tile_width * y, 0, angle_z=degrees(rotation)))
        action.wait_for_completed()

def moveCube(robot, x, y):
    global cube
    robot.set_head_angle(degrees(0), num_retries=10).wait_for_completed() #so field of view is correctly parallel to ground
    robot.pickup_object(cube, num_retries=10).wait_for_completed()
    moveCozmo(robot, x, y)
    robot.place_object_on_ground_here(cube, num_retries=10).wait_for_completed()
    robot.set_lift_height(.6).wait_for_completed() #after dropping lift, so it doesn't drag on the ground and affect position over time

def cozmoTicTacToeMove(robot):
    # print("cozmo pls move")
    global board
    if not board.isDone:
        cube.set_lights(cozmo.lights.red_light.flash())
        x, y = cpuOppo.nextMove()
        status = board.currentPlayer.value
        status = status + " is turn"
        robot.say_text(status).wait_for_completed()
        cube.set_lights(cozmo.lights.red_light)
        robot.say_text("Playing on {} {}".format(x, y)).wait_for_completed()
        board.play(x, y)
        moveCube(robot, x, y)
        moveCozmo(robot, -1.5, 1,)
        status = board.currentPlayer.value
        status = status + " is turn"
        robot.say_text(status).wait_for_completed()
        cube.set_lights(cozmo.lights.green_light)
    else:
        print("cozmo done!")
    print(board)



def lookForCube(robot, action):
    global cube
    while not cube.is_visible and not action.is_completed:
        time.sleep(.05)
        print(cube.is_visible)
        print(action.is_completed)
    if cube.is_visible and not action.is_completed:
        action.abort()

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
    print(cube.is_visible)


    # robot.say_text(note, voice_pitch=voice_pitch, duration_scalar=0.3).wait_for_completed()

def handle_object_moving(evt, **kw):
    # This will be called whenever an EvtObjectMoving event is dispatched -
    # whenever we detect a cube is still moving a (via an accelerometer in the cube)
    print("Object %s is moving: acceleration=%s, duration=%.1f seconds, speed=%.2f" %
          (evt.obj.object_id, evt.acceleration, evt.move_duration, calculateSpeed(evt.acceleration, evt.move_duration)))
    # robot.say_text(note, voice_pitch=, duration_scalar=0.3).wait_for_completed()
    print(cube.is_visible)

def handle_object_tapped(evt, **kw):
    global cube
    global board
    if (evt.obj.object_id == cube.object_id) and board.currentPlayer != cozmoTile:
        print(evt)
    print(cube.is_visible)


def handle_object_moving_stopped(evt, **kw):
    # This will be called whenever an EvtObjectMovingStopped event is dispatched -
    # whenever we detect a cube stopped moving (via an accelerometer in the cube)
    global root_pose

    print("Object %s stopped moving: duration=%.1f seconds, speed=%s" %
          (evt.obj.object_id, evt.move_duration, calculateSpeed(acceleration, evt.move_duration)))
    if evt.obj.object_id == cube.object_id:
        x, y = cube.pose.position.x, cube.pose.position.y
        print((x - root_pose.position.x) / tile_width, (y - root_pose.position.y) / tile_width)

def cozmo_program(robot: cozmo.robot.Robot):
    global root_pose
    global cube
    global board

    print("Bot Voltage:", robot.battery_voltage)
    if robot.battery_voltage < 3.7:
        print("Low bot voltage!")


    robot.say_text("Tic Tac Toe").wait_for_completed()
    robot.set_head_angle(degrees(0), num_retries=10).wait_for_completed()
    # print(robot.MIN_HEAD_ANGLE, robot.MAX_HEAD_ANGLE)
    # raise BaseException("")

    # robot.say_text("Let's Play TicTacToe").wait_for_completed()

    # while True:
    #     time.sleep(.5)
    #     print(robot.battery_voltage)

    lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cube = robot.world.wait_for_observed_light_cube()
    lookaround.stop()

    # cube.visibility_timeout = 1
    # cube.set_lights(cozmo.lights.red_light)
    # # robot.say_text("Found Cube").wait_for_completed()
    #
    root_pose = robot.pose
    # # moveCozmo(robot, 0, 0)
    # print("Cube found:", cube.pose, cube.object_id)
    # print(root_pose)
    #
    #
    #
    robot.add_event_handler(cozmo.objects.EvtObjectMovingStarted, handle_object_moving_started)
    robot.add_event_handler(cozmo.objects.EvtObjectMoving, handle_object_moving)
    robot.add_event_handler(cozmo.objects.EvtObjectMovingStopped, handle_object_moving_stopped)
    robot.add_event_handler(cozmo.objects.EvtObjectTapped, handle_object_tapped)
    robot.enable_stop_on_cliff(True)
    # ## DEBUG: commented code for yolo cozmo
    # while not board.isDone:
    #         cozmoTicTacToeMove(robot)

    while not board.isDone:
        if board.currentPlayer == cozmoTile:
            cozmoTicTacToeMove(robot)
        else:
            #reset if we need to loop back after in correct move
            moveCozmo(robot, -1.5, 1) #get back to good vantage point in case we moved away
            cube.set_lights(cozmo.lights.green_light)


        if board.isDone:
            break;
        cube.wait_for_tap()
        cube.set_lights(cozmo.lights.green_light.flash())
        if not cube.is_visible:
            # action = robot.go_to_object(cube, distance_mm(100.0)) #after the tap, go closer to object so that pose info is correct
            # lookForCube(robot, action)
            if not cube.is_visible:
                moveCozmo(robot, 1, 1, 0, look_for_cube=True)
                lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
                robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=60)
                lookaround.stop()
        # robot.go_to_object(cube, distance_mm(100.0)).wait_for_completed() #after the tap, go closer to object so that pose info is correct


        x, y = cube.pose.position.x, cube.pose.position.y
        print((x - root_pose.position.x) / tile_width, (y - root_pose.position.y) / tile_width)
        x, y = round((x - root_pose.position.x) / tile_width - .5), round((y - root_pose.position.y) / tile_width) # x has a fudge factor to help
        # fudge factors
        if x >= -2 and x < 0:
            x = 0
        if y >= -2 and y < 0:
            y = 0

        if x >= 2 and x < 4:
            x = 2
        if y >= 2 and y < 4:
            y = 2

        if (x >= 0) and (x < 3) and (y >= 0) and (y < 3):
            print(x, y)
            oldPlayer = board.currentPlayer
            if board.play(x, y) == Tile.EMPTY: #Valid move
                status = oldPlayer.value #if move succeeds, we use old player, since new player is out of date
                robot.say_text(status + " move to {} {}".format(x, y)).wait_for_completed()
            else:
                robot.say_text("That spot is already filled").wait_for_completed()
            print(board)
        else:
            robot.say_text("That is outside the board").wait_for_completed()

    #done
    robot.say_text("Game finished").wait_for_completed()
    if board.winner() == Tile.NO_WIN:
        robot.say_text("catscratch").wait_for_completed()
    else:
        if board.winner() != cozmoTile:
            cube.set_lights(cozmo.lights.green_light.flash())
        else:
            cube.set_lights(cozmo.lights.red_light.flash())
            robot.say_text("I Have Won").wait_for_completed()
        winner = board.winner().value
        robot.say_text(winner + " has won").wait_for_completed()

    while True:
        time.sleep(1.0)
        # print(cube.pose)

cozmo.run_program(cozmo_program)
