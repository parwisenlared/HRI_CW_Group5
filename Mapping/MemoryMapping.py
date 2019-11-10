
import cozmo
from cozmo.util import degrees, Pose


def make_map():
    maps = cozmo.nav_memory_map.NavMemoryMapGrid((0, 0), 1, 1, 0, 0)

def handle_memory_map(evt, **kw):
    print("Map Received.")
    make_map()


def cozmo_program(robot: cozmo.robot.Robot):
    cozmo.world.World.request_nav_memory_map(robot, 1.0)
    robot.add_event_handler(cozmo.nav_memory_map.EvtNewNavMemoryMap, handle_memory_map)
    robot.say_text("1").wait_for_completed()
    fixed_object = robot.world.create_custom_fixed_object(Pose(25, 0, 0, angle_z=degrees(0)),
                                                          10, 100, 100, relative_to_robot=True)
    if fixed_object:
        print("fixed_object created successfully")
    robot.say_text("2").wait_for_completed()
    maps = cozmo.nav_memory_map.NavMemoryMapGrid(robot, 100, 100, 0, 0)
    for x in range(0, 10):
        for y in range(0, 10):
            thisNode = maps.get_node(x, y)
            print(thisNode.content)
    print(maps.center)
    print(maps.size)
    robot.say_text("3").wait_for_completed()

cozmo.run_program(cozmo_program)