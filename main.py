import cozmo
import time

acceleration = cozmo.util.Vector3(0,0,0)
def calculateSpeed(acceleration, time):
    max = 400
    speed = (acceleration.x ** 2 + acceleration.y ** 2 + acceleration.z ** 2) **(1./2) * time
    if speed > max:
        speed = max
    return speed
def handle_object_moving_started(evt, **kw):
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
          (evt.obj.object_id, evt.move_duration, acceleration))


def cozmo_program(robot: cozmo.robot.Robot):
    robot.say_text("Hello World").wait_for_completed()
    robot.add_event_handler(cozmo.objects.EvtObjectMovingStarted, handle_object_moving_started)
    robot.add_event_handler(cozmo.objects.EvtObjectMoving, handle_object_moving)
    robot.add_event_handler(cozmo.objects.EvtObjectMovingStopped, handle_object_moving_stopped)

    while True:
        time.sleep(1.0)

cozmo.run_program(cozmo_program)
