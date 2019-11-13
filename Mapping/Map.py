import cozmo
import time
from PIL import Image, ImageColor, ImageTk
from cozmo.util import degrees, Pose, distance_mm, speed_mmps
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes
import matplotlib.pyplot as plt
import matplotlib.image as img
import tkinter as tk

"""
Things to do:
implement some sort of searching strategy so cozmo finds all cubes - included in this is creating 'inital pose' variables
to enable the reset card to be used. 

Also need to change how cubes work so that they .pop values before updating map when cubes are moved, otherwise end up
with them trailing over the map

work out how big the picture is, what is an 

"""
# create a tkinter base window and canvas we can draw our map on.
root = tk.Tk()
canvas = tk.Canvas(root, width=500, height=500)
canvas.pack()

# create blank map
game_map = Image.new('RGB', (500, 500), color=(0, 0, 0))

# get cube images for map and resize to approximately the right size
cube_image = Image.open("cube.jpg")
cube_image.thumbnail((20, 20))
cozmo_image = Image.open("cozmo.jpg")
cozmo_image.thumbnail((20, 20))

# define poses for cozmo and two cubes
cozmo_pose = []
cube_poses = []


# the array holding the commands the player has given
commands = []


# define the max time
max_time = 1


# add event listeners for each custom object, when event happens the listener calls the method to add it to the array
def event_listeners( evt, **kw):
    if isinstance(evt.obj, CustomObject):
        obj = str(evt.obj.object_type)
        print(obj)
        obj_substring = obj[-2:]
        print(obj_substring)
        object_number = int(obj_substring)
        if object_number == 0:
            add_command_to_array(0)
            print("Seen: 0")
        elif object_number == 1:
            add_command_to_array(1)
            print("Seen: 1")
        elif object_number == 2:
            add_command_to_array(2)
            print("Seen: 2")
        elif object_number == 3:
            add_command_to_array(3)
            print("Seen: 1")
        elif object_number == 4:
            add_command_to_array(4)
            print("Seen: 1")
        elif object_number == 5:
            add_command_to_array(5)
            print("Seen: 1")
        elif object_number == 6:
            add_command_to_array(6)
            print("Seen: 1")
        elif object_number == 7:
            add_command_to_array(7)
            print("Seen: 1")
        elif object_number == 8:
            add_command_to_array(8)
            print("Seen: 1")


# define command cards
def make_command_cards(robot):
    forward_card = robot.world.define_custom_cube(CustomObjectTypes.CustomType00, CustomObjectMarkers.Diamonds2, 44, 10,
                                                  10, True)
    turn_left = robot.world.define_custom_cube(CustomObjectTypes.CustomType01, CustomObjectMarkers.Triangles4, 44, 10,
                                               10, True)
    turn_right = robot.world.define_custom_cube(CustomObjectTypes.CustomType02, CustomObjectMarkers.Hexagons5, 44, 10,
                                                10, True)
    reverse = robot.world.define_custom_cube(CustomObjectTypes.CustomType03, CustomObjectMarkers.Hexagons2, 44, 10,
                                             10, True)
    pick_up = robot.world.define_custom_cube(CustomObjectTypes.CustomType04, CustomObjectMarkers.Diamonds3, 44, 10,
                                             10, True)
    put_down = robot.world.define_custom_cube(CustomObjectTypes.CustomType05, CustomObjectMarkers.Hexagons4, 44, 10,
                                              10, True)
    undo = robot.world.define_custom_cube(CustomObjectTypes.CustomType06, CustomObjectMarkers.Circles3, 44, 10,
                                          10, True)
    reset = robot.world.define_custom_cube(CustomObjectTypes.CustomType07, CustomObjectMarkers.Circles4, 44, 10,
                                           10, True)
    execution_card = robot.world.define_custom_cube(CustomObjectTypes.CustomType08, CustomObjectMarkers.Triangles3, 44,
                                                    10, 10, True)
    return forward_card, turn_right, turn_left, reverse, pick_up, put_down, undo, reset, execution_card


# variable to track current state of game should be Building Map, Receiving Instructions, Resetting Map, Lost, Won
game_state = ['horray']


# Adds commands to command array in the form of numbers which are then read out below
def add_command_to_array(command_card):
    if command_card == 8:
        DONOTHING = 0 # right now this statement has no effect. When we implement the FSM it will have to change the
        # state to going
    elif command_card == 7:
        for val in commands:
            commands.pop()
    elif command_card == 6:
        commands.pop()
    elif command_card == 0:
        commands.append(1)
    elif command_card == 1:
        commands.append(2)
    elif command_card == 2:
        commands.append(3)
    elif command_card == 3:
        commands.append(4)
    elif command_card == 4:
        commands.append(5)
    elif command_card == 5:
        commands.append(6)


# reads each command value from commands and executes the correct action
def carry_out_commands(robot):
    for val in commands:
        if val == 1:
            drive_forward(robot)
        elif val == 2:
            turn(-90, robot)
        elif val == 3:
            turn(90, robot)
        elif val == 4:
            drive_backwards(robot)
        elif val == 5:
            pick_up_cube(robot)
        elif val == 6:
            put_down_cube(robot)


# method to be called when card reading @move forward is shown
def drive_forward(robot):
    robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
    get_cozmo_position(robot)
    update_map()


# method to be called when card reading @move forward is shown
def drive_backwards(robot):
    robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
    get_cozmo_position(robot)
    update_map()


# method to be called when card reading turn left OR right is shown, when called must include angle = 90, -90
def turn(angle, robot):
    robot.turn_in_place(degrees(angle)).wait_for_completed()
    get_cozmo_position(robot)
    update_map()


# cozmo will look for a cube in front of him, if there's not one game state = Lost
def pick_up_cube(robot):
    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cubes = robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=60)
    look_around.stop()
    robot.dock_with_cube(cubes, approach_angle=cozmo.util.degrees(0), num_retries=2)
    get_cozmo_position(robot)
    update_map()


# cozmo will put a cube down
def put_down_cube(robot):
    robot.move_lift(-5)
    get_cozmo_position(robot)
    update_map()


# update the displayed map
def update_map():
    """This paints the map white and then pastes the positions of cozmo and the cubes in their updated positions."""
    for x in range(0, 500):
        for y in range(0, 500):
            game_map.putpixel((x, y), (255, 255, 255))
    for val in cube_poses:
        draw_cubes_on_map(val[0], val[1])
    for val in cozmo_pose:
        draw_cozmo_on_map(val[0], val[1])
    this_map = ImageTk.PhotoImage(game_map)
    canvas.create_image(20, 20, image=this_map)
    root.update()


def draw_cubes_on_map(x, y):
    """ Take in an x and y value, normalise it to our map so that the origin is always the center and then draw an image
    of a cube there."""
    x = int(x) + 250
    y = int(y) + 250
    game_map.paste(cube_image, (x, y))


def draw_cozmo_on_map(x, y):
    """Same as above, except draw a cozmo"""
    x = int(x) + 250
    y = int(y) + 250
    game_map.paste(cozmo_image, (x, y))


def get_xy_coordinates(position_string):
    """Take in a string as given by str(.pose.position) and then determine x, y coordinates for map making."""
    # find the start indexes for each coordinate
    x_start = position_string.find("x")
    y_start = position_string.find("y")
    z_start = position_string.find("z")

    # get x and y coordinates from substring
    x_substring = position_string[(x_start + 2):y_start:]
    x_coordinate = float(x_substring)
    y_substring = position_string[(y_start + 2):z_start:]
    y_coordinate = float(y_substring)
    return x_coordinate, y_coordinate


def get_cozmo_position(robot):
    if len(cozmo_pose) > 0:
        cozmo_pose.pop(0)
    current_pose = str(robot.pose.position)
    print(current_pose)
    xy = get_xy_coordinates(current_pose)
    cozmo_pose.append(xy)


def cozmo_program(robot: cozmo.robot.Robot):
    update_map()
    robot.add_event_handler(cozmo.objects.EvtObjectAppeared, event_listeners)
    make_command_cards(robot)
    game_state[0] = 'Building Map'
    get_cozmo_position(robot)
    update_map()
    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cubes = robot.world.wait_until_observe_num_objects(num=2, object_type=cozmo.objects.LightCube, timeout=60)
    look_around.stop()
    for cube in cubes:
        this_cube = get_xy_coordinates(str(cube.pose.position))
        cube_poses.append(this_cube)
    print(cube_poses)
    update_map()
    print(commands)
    update_map()
    for a in range(0, max_time):
        time.sleep(1)
    carry_out_commands(robot)
    drive_forward(robot)
    for a in range(0, max_time):
        time.sleep(1)
    root.mainloop()

cozmo.run_program(cozmo_program)
