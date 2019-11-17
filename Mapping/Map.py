import cozmo
import time
import datetime
from PIL import Image, ImageColor, ImageTk
from cozmo.util import degrees, Pose, distance_mm, speed_mmps
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes, LightCube1Id, LightCube2Id, LightCube3Id
from cozmo.faces import Face
import matplotlib.pyplot as plt
import matplotlib.image as img
import tkinter as tk
import asyncio

"""
Things to do:
implement some sort of searching strategy so cozmo finds all cubes - included in this is creating 'inital pose' variables
to enable the reset card to be used. 

Also need to change how cubes work so that they .pop values before updating map when cubes are moved, otherwise end up
with them trailing over the map

work out how big the picture is, what is an 

"""

size_of_map = 1000

# create a tkinter base window and canvas we can draw our map on.
root = tk.Tk()
canvas = tk.Canvas(root, width=size_of_map, height=size_of_map)
canvas.pack()

# create blank map
game_map = Image.new('RGB', (size_of_map, size_of_map), color=(0, 0, 0))

# get cube images for map and resize to approximately the right size
cube_image = Image.open("cube.jpg")
cube_image.thumbnail((100, 50))
cozmo_image = Image.open("cozmo.jpg")
cozmo_image.thumbnail((50, 50))
player_image = Image.open("player.png")
player_image.thumbnail((50, 50))

# define poses for cozmo and two cubes
cozmo_pose = []
cube_one_pose = []
cube_two_pose = []

# create an empty log where we will write to during the program
log = []

# the array holding the commands the player has given
commands = []

# define the max time
max_time = 5

# variable holding the player's face_ID and pose
player_face_id = []
player_face_pose = []

# variable to track current state of game should be Building Map, Receiving Instructions, Resetting Map, Lost, Won
game_state = ['horray']


# colour light cubes
def colour_light_cubes(robot):
    cube1 = robot.world.get_light_cube(LightCube1Id)
    cube1.set_lights(cozmo.lights.red_light)
    cube2 = robot.world.get_light_cube(LightCube2Id)
    cube2.set_lights(cozmo.lights.blue_light)


# get current time
def get_time():
    time = datetime.datetime.now().time()
    return time


# write to log
def write_to_log(event):
    this_time = get_time()
    if 'cube one' in event:
        this_string = str(event)
        log.append(this_string)
    elif 'cube two' in event:
        this_string = str(event)
        log.append(this_string)
    else:
        string = 'Cozmo %s at : %s.\n' % (event, this_time)
        log.append(string)


# add event listeners for each custom object, when event happens the listener calls the method to add it to the array
def object_event_listeners(evt, **kw):
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
        elif object_number == 9:
            print(str())
            print("seen player")


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
    player_card = robot.world.define_custom_cube(CustomObjectTypes.CustomType09, CustomObjectMarkers.Hexagons3, 44, 10,
                                                 10, True)
    return forward_card, turn_right, turn_left, reverse, pick_up, put_down, undo, reset, execution_card, player_card


# Adds commands to command array in the form of numbers which are then read out below
def add_command_to_array(command_card):
    if command_card == 8:
        DONOTHING = 0  # right now this statement has no effect. When we implement the FSM it will have to change the
        # state to going
    elif command_card == 7:
        for val in commands:
            commands.pop()
    elif command_card == 6:
        if len(commands) > 0:
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
    update_map(robot)
    write_to_log('moved forward')


# method to be called when card reading @move forward is shown
def drive_backwards(robot):
    robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
    update_map(robot)
    write_to_log('moved backwards')


# method to be called when card reading turn left OR right is shown, when called must include angle = 90, -90
def turn(angle, robot):
    robot.turn_in_place(degrees(angle)).wait_for_completed()
    update_map(robot)
    if angle == 90:
        write_to_log('turned right')
    if angle == -90:
        write_to_log('turned left')


# cozmo will look for a cube in front of him, if there's not one game state = Lost
def pick_up_cube(robot):
    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cubes = robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=60)
    look_around.stop()
    for cube in cubes:
        robot.dock_with_cube(cubes, approach_angle=cozmo.util.degrees(0), num_retries=2).wait_for_completed()
    update_map(robot)
    write_to_log('picked up cube')


# cozmo will put a cube down
def put_down_cube(robot):
    robot.move_lift(-5)
    update_map(robot)
    write_to_log('put down cube')


# update the displayed map
def update_map(robot):
    """This paints the map white and then pastes the positions of cozmo and the cubes in their updated positions."""
    get_world_positions(robot)
    for x in range(0, size_of_map):
        for y in range(0, size_of_map):
            game_map.putpixel((x, y), (255, 255, 255))
    for val in cube_one_pose:
        draw_cubes_on_map(game_map, val[0], val[1])
        print(str(val[0]) + ',' + str(val[1]))
    for val in cube_two_pose:
        draw_cubes_on_map(game_map, val[0], val[1])
    for val in cozmo_pose:
        draw_cozmo_on_map(val[0], val[1])
    for val in player_face_pose:
        draw_player_on_map(val[0], val[1])
    this_map = ImageTk.PhotoImage(game_map)
    canvas.delete(tk.ALL)
    canvas.create_image(0, 0, image=this_map)
    root.update()


def draw_cubes_on_map(game_maps, x, y):
    """ Take in an x and y value, normalise it to our map so that the origin is always the center and then draw an image
    of a cube there."""
    x = int(x) + 500
    y = int(y) + 500
    print(x, y)
    game_maps.paste(cube_image, (x, y))


def draw_cozmo_on_map(x, y):
    """Same as above, except draw a cozmo"""
    x = int(x) + 500
    y = int(y) + 500
    game_map.paste(cozmo_image, (x, y))


def draw_player_on_map(x, y):
    """Same as above, except draw a cozmo"""
    x = int(x) + 500
    y = int(y) + 500
    game_map.paste(player_image, (x, y))


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


def get_world_positions(robot):
    if len(cozmo_pose) > 0:
        for val in cozmo_pose:
            x = val[0]
            y = val[1]
            event = 'was at (%s, %s)' % (x, y)
            write_to_log(event)
        cozmo_pose.pop()
    if len(cube_one_pose) > 0:
        for val in cube_one_pose:
            x = val[0]
            y = val[1]
            event = 'cube one was at (%s, %s)\n' % (x, y)
            write_to_log(event)
        cube_one_pose.pop()
    if len(cube_two_pose) > 0:
        for val in cube_two_pose:
            x = val[0]
            y = val[1]
            event = 'cube two was at (%s, %s)\n' % (x, y)
            write_to_log(event)
        cube_two_pose.pop()
    cozmo_current_pose = str(robot.pose.position)
    cube_one_current_pose = str(robot.world.get_light_cube(LightCube1Id).pose.position)
    cube_two_current_pose = str(robot.world.get_light_cube(LightCube2Id).pose.position)
    cozmo_xy = get_xy_coordinates(cozmo_current_pose)
    cube_one_xy = get_xy_coordinates(cube_one_current_pose)
    cube_two_xy = get_xy_coordinates(cube_two_current_pose)
    cozmo_pose.append(cozmo_xy)
    cube_one_pose.append(cube_one_xy)
    cube_two_pose.append(cube_two_xy)


def face_observed_listeners(evt, **kw):
    get_player_position()


def find_player(robot):
#    robot.say_text("If you are not playing please cover your face while I look for the player.").wait_for_completed()
    robot.move_lift(-3)
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
    player_face = None
    while True:
        turn_action = None
        if player_face:
            face_id = cozmo.world.faces.Face.face_id.fget(player_face)
            player_face_id.append(face_id)
            position = str(cozmo.world.faces.Face.pose.fget(player_face))
            xy_position = get_xy_coordinates(position)
            if len(player_face_pose) > 0:
                for _ in player_face_pose:
                    player_face_pose.pop()
            player_face_pose.append(xy_position)
            event = "Cozmo found a face at: %s", position
            write_to_log(event)
            return player_face
        if not (player_face and player_face.is_visible):
            try:
                robot.turn_in_place(degrees(360)).wait_for_completed()
                player_face = robot.world.wait_for_observed_face(timeout=1)
            except asyncio.TimeoutError:
                event = "didn't find a face looking elsewhere!"
                write_to_log(event)
        if turn_action:
            turn_action.wait_for_completed()


def look_at_player(robot, player_face):
    robot.turn_towards_face(player_face).wait_for_completed()


def get_player_position():
    for val in player_face_pose:
        print(val)


def cozmo_program(robot: cozmo.robot.Robot):
    # robot.add_event_handler(cozmo.world.faces.EvtFaceAppeared, face_appeared_listeners)
    # player_face = find_player(robot)
    # turn(90, robot)
    # drive_backwards(robot)
    # look_at_player(robot, player_face)
    # robot.add_event_handler(cozmo.world.faces.EvtFaceObserved, face_observed_listeners)
    # this creates a custom name for each log fike
    # name = input("Please enter a filename for the log file (don't add a file extension thx): ")
    # file_name_with_extension = name + ".txt"
    # logfile = open(file_name_with_extension, "w+")

    # get the inital map of the game, where is cozmo
    update_map(robot)

    # create event handlers for seeing custom objects
    robot.add_event_handler(cozmo.objects.EvtObjectAppeared, object_event_listeners)
    # set up customer makers for commands
    make_command_cards(robot)

    # set up lightcubes for use
    colour_light_cubes(robot)

    # fsm will be initialised here - once it's made
    game_state[0] = 'Building Map'

    # this is mostly just insanity checking atm
    update_map(robot)
    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cubes = robot.world.wait_until_observe_num_objects(num=2, object_type=cozmo.objects.LightCube, timeout=60)
    look_around.stop()
    update_map(robot)
    print(commands)
    update_map(robot)
    for a in range(0, max_time):
        time.sleep(1)
    carry_out_commands(robot)
    drive_forward(robot)
    drive_backwards(robot)
    for a in range(0, max_time):
        time.sleep(1)
    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cubes = robot.world.wait_until_observe_num_objects(num=2, object_type=cozmo.objects.LightCube, timeout=60)
    look_around.stop()
    update_map(robot)
    for a in range(0, max_time):
        time.sleep(1)
    root.mainloop()
    #for val in log:
    #    logfile.write(val)
    #logfile.close()


cozmo.run_program(cozmo_program)
