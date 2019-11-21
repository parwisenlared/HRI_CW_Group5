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
import threading

"""
-------------YO YO YO, MAKE SURE IN THE FSM make_game_ready is only called ONCE-----------------------------------------
create definition to find initial poses and start map

"""


# variables for setting up the tkinter map
size_of_map = 1000
anchor_for_canvas = size_of_map/2

# create a tkinter base window and canvas we can draw our map on.
root = tk.Tk()
canvas = tk.Canvas(root, width=size_of_map, height=size_of_map)
canvas.pack()

# create blank map
game_map = Image.new('RGB', (size_of_map, size_of_map), color=(0, 0, 0))

# get images for map and resize to approximately the right size
cube_image = Image.open("cube.jpg")
cube_image.thumbnail((50, 50))
cozmo_image = Image.open("cozmo.jpg")
cozmo_image.thumbnail((50, 50))
player_image = Image.open("player.png")
player_image.thumbnail((50, 50))

# define poses for cozmo and two cubes
cube_one_initial_pose = []
cube_two_initial_pose = []
cozmo_initial_pose = []
cozmo_pose = []
cube_one_pose = []
cube_two_pose = []

# create an empty log where we will write to during the program
log = []

# the array holding the commands the player has given
commands = []

# define the max time
max_time = 50

# variable holding the player's face_ID and pose
player_face_id = []
player_face_pose = []

# variable to track current state of game should be Building Map, Receiving Instructions, Resetting Map, Lost, Won
game_state = ['waiting']


# how to change states
def change_state(state):
    game_state.insert(0, str(state))


# all the states that can exist
def state_thread(robot):
    set_up = 0
    tries = 0
    current_time = 0
    game_running = True
    player_face = find_player(robot)
    while game_running:
        while game_state[0] == "waiting":
            print("hello")
            time.sleep(0.1)
        while game_state[0] == "set_up":
            # ensure the make_game_ready method is only called at the beginning of the game.
            if set_up == 0:
                set_up = set_up + 1
                make_game_ready(robot)
        while game_state[0] == "listening_for_commands":
            look_at = 0
            if look_at == 0:
                look_at_player(robot, player_face)
                look_at = 1
            time.sleep(0.1)
            if current_time <= max_time:
                time.sleep(0.5)
                current_time = current_time + 1
            else:
                current_time = 0
                change_state("executing")
                time.sleep(0.1)
        while game_state[0] == "executing":
            carry_out_commands(robot)
            time.sleep(0.1)
        while game_state[0] == "failed":
            tries = tries + 1
            if tries == 3:
                lost(robot)
            else:
                reset_game_board(robot)
        while game_state[0] == "success":
            victory(robot)
        while game_state[0] == "game_over":
            game_running = False


# colour light cubes and return those cubes to the main function for further use.
def colour_light_cubes(robot):
    cube1 = robot.world.get_light_cube(LightCube1Id)
    cube1.set_lights(cozmo.lights.red_light)
    cube2 = robot.world.get_light_cube(LightCube2Id)
    cube2.set_lights(cozmo.lights.blue_light)
    return cube1, cube2


# get current time for log entries
def get_time():
    time_now = datetime.datetime.now().time()
    return time_now


# write events to log (list) to be read and written to log file at the end of the program
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


# Add event listeners for each custom object, when object is seen, the listener calls the method to add it to the
# command array.
def object_event_listeners(evt, **kw):
    if isinstance(evt.obj, CustomObject):
        obj = str(evt.obj.object_type)
        obj_substring = obj[-2:]
        object_number = int(obj_substring)
        if object_number == 0:
            add_command_to_array(0)
        elif object_number == 1:
            add_command_to_array(1)
        elif object_number == 2:
            add_command_to_array(2)
        elif object_number == 3:
            add_command_to_array(3)
        elif object_number == 4:
            add_command_to_array(4)
        elif object_number == 5:
            add_command_to_array(5)
        elif object_number == 6:
            add_command_to_array(6)
        elif object_number == 7:
            add_command_to_array(7)
        elif object_number == 8:
            add_command_to_array(8)


# This creates each of the custom objects using the factory objects.
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


# Adds commands to command array in the form of numbers which are then read out by carry_out_commands below. Some of the
# commands are implemented here, such as reset and undo.
def add_command_to_array(command_card):
    if command_card == 8:
        change_state("executing")
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

    # Lorenzo and Odhran suggest you sould use a switch case instead of all the elif :o


# reads each command value from the commands list and executes the correct action
def carry_out_commands(robot):
    print("Carrying out commands")
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
            # This should be 'pick_up_cube,' however this is automatically called by light_cube_visible if the player
            # has correctly guided cozmo to the cube.
            light_cube_visible(robot)
        elif val == 6:
            put_down_cube(robot)
    check_for_success()


def check_for_success():
    print("Checking for success")
    x1 = 0
    y1 = 0
    x2 = 1
    y2 = 1
    for val in cube_one_pose:
        x1 = val[0]
        y1 = val[1]
    for val in cube_two_pose:
        x2 = val[0]
        y2 = val[1]
    if x1 == x2 and y1 == y2:
        change_state("success")
    else:
        change_state("failed")


def lost(robot):
    print("You lost")
    robot.say_text("you lost! goodbye").wait_for_completed()
    change_state("game_over")


def victory(robot):
    print("You won")
    robot.say_text("you won! goodbye").wait_for_completed()
    change_state("game_over")


# method to be called when card reading move forward is shown
def drive_forward(robot):
    robot.drive_straight(distance_mm(50), speed_mmps(50)).wait_for_completed()
    update_map(robot)
    write_to_log('moved forward')


# method to be called when card reading move backward is shown
def drive_backwards(robot):
    robot.drive_straight(distance_mm(-50), speed_mmps(50)).wait_for_completed()
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


# method to discover if the player has positioned cozmo where it can see a cube - it will then pick it up or change the
# game state to FAILED
def light_cube_visible(robot):
    try:
        cube = robot.world.wait_for_observed_light_cube(5)
        pick_up_cube(robot, cube)
        print("visible")
    except asyncio.TimeoutError:
        event = "didn't find a cube game failed!"
        write_to_log(event)
        change_state("failed")


# cozmo will pick up the cube seen in light_cube_visible
def pick_up_cube(robot, cube):
    robot.pickup_object(cube, num_retries=2).wait_for_completed()
    update_map(robot)
    write_to_log('picked up cube')


# cozmo will put a cube down
def put_down_cube(robot):
    robot.move_lift(-1)
    drive_backwards(robot)
    update_map(robot)
    write_to_log('put down cube')


# update the displayed map
def update_map(robot):
    print("Updated map")
    # ensures all pictures pasted on the map are in the correct current poses
    get_world_positions(robot)
    # this paints the canvas white, if not done the previous positions of objects would leave afterprints
    for x in range(0, size_of_map):
        for y in range(0, size_of_map):
            game_map.putpixel((x, y), (255, 255, 255))
    for val in cube_one_pose:
        game_map.paste(cube_image, (500+int(val[0]), (500+int(val[1]))))
        print(str(val[0]) + ',' + str(val[1]))
    for val in cube_two_pose:
        game_map.paste(cube_image, (500+int(val[0]), (500+int(val[1]))))
    for val in cozmo_pose:
        game_map.paste(cozmo_image, (500+int(val[0]), (500+int(val[1]))))
    for val in player_face_pose:
        game_map.paste(player_image, (500+int(val[0]), (500+int(val[1]))))
    this_map = ImageTk.PhotoImage(game_map)
    canvas.delete(tk.ALL)
    canvas.create_image(anchor_for_canvas, anchor_for_canvas, image=this_map)
    root.update()


# Take in a string as given by str(.pose.position) and then determine x, y coordinates for map making.
def get_xy_coordinates(position_string):
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


# reads in old poses and writes them to log and then updates them ready to be drawn on map
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


# currently unused, triggered whenever a face is in view
def face_observed_listeners(evt, **kw):
    get_player_position()


# this initial method looks for the game player. Cozmo will look for a face and assume the one it sees is the player
def find_player(robot):
    print("finding players")
    # robot.say_text("If you are not playing please cover your face while I look for the player.").wait_for_completed()
    robot.move_lift(-3)
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
    player_face = None
    # keep the method running until a player is found, no point continuing the script if no player
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
            # this places the xy coordinate of the player in the list, currently the player's position is not updated.
            event = "Cozmo found a face at: %s", position
            write_to_log(event)
            return player_face
        # returns the player's face for use later in the program
        if not (player_face and player_face.is_visible):
            try:
                robot.turn_in_place(degrees(90)).wait_for_completed()
                player_face = robot.world.wait_for_observed_face(timeout=1)
            except asyncio.TimeoutError:
                event = "didn't find a face looking elsewhere!"
                write_to_log(event)
        if turn_action:
            turn_action.wait_for_completed()


# cozmo will turn and look at where it last saw the player
def look_at_player(robot, player_face):
    print("Looking at players")
    robot.turn_towards_face(player_face).wait_for_completed()


# does nothing currently but will be updated to update the player position
def get_player_position():
    for val in player_face_pose:
        abd = 1


# this creates a custom name for each log fike
def make_log_file():
    name = input("Please enter a filename for the log file (don't add a file extension thx): ")
    file_name_with_extension = name + ".txt"
    logfile = open(file_name_with_extension, "w+")
    return logfile


# should only ever be called once to get initial game board (in case reset is needed), set up listeners, make the
# command cards, set the cube colours
def make_game_ready(robot):
    print("Setting up")
    robot.add_event_handler(cozmo.world.faces.EvtFaceObserved, face_observed_listeners)
    robot.add_event_handler(cozmo.objects.EvtObjectAppeared, object_event_listeners)
    make_command_cards(robot)
    cube1, cube2 = colour_light_cubes(robot)
    cozmo_current_pose = str(robot.pose.position)
    cozmo_xy = get_xy_coordinates(cozmo_current_pose)
    cozmo_pose.append(cozmo_xy)
    for val in cozmo_pose:
        cozmo_initial_pose.append(val)
    find_cubes(robot)
    for val in cube_one_pose:
        cube_one_initial_pose.append(val)
    for val in cube_two_pose:
        cube_two_initial_pose.append(val)
    print("game_ready")
    change_state("listening_for_commands")


def find_cubes(robot):
    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cubes = robot.world.wait_until_observe_num_objects(num=2, object_type=cozmo.objects.LightCube, timeout=60)
    look_around.stop()
    update_map(robot)


# checks if cubes/cozmo are out of position and repositions them correctly
def reset_game_board(robot):
    print("Resetting")
    find_cubes(robot)
    x_current = 0
    x_initial = 0
    y_current = 0
    y_initial = 0
    cube = robot.world.get_light_cube(1)
    for val in cube_one_pose:
        x_current = val[0]
        y_current = val[1]
    for val in cube_one_initial_pose:
        x_initial = val[0]
        y_initial = val[1]
    if x_current != x_initial or y_current != y_initial:
        pick_up_cube(robot, cube)
        robot.go_to_pose(Pose((x_initial-50), (y_initial-50), 0, angle_z=degrees(0))).wait_for_completed()
        put_down_cube(robot)
        drive_backwards(robot)
    x_current = 0
    x_initial = 0
    y_current = 0
    x_initial = 0
    cube = robot.world.get_light_cube(2)
    for val in cube_one_pose:
        x_current = val[0]
        y_current = val[1]
    for val in cube_one_initial_pose:
        x_initial = val[0]
        y_initial = val[1]
    if x_current != x_initial or y_current != y_initial:
        pick_up_cube(robot, cube)
        robot.go_to_pose(Pose((x_initial-50), (y_initial-50), 0, angle_z=degrees(0))).wait_for_completed()
        put_down_cube(robot)
        drive_backwards(robot)
    x = 0
    y = 0
    for val in cozmo_initial_pose:
        x = val[0]
        y = val[1]
    robot.go_to_pose(Pose(x, y, 0, angle_z=degrees(0))).wait_for_completed()
    change_state("listening_for_commands")


# this thread contains all of the running of cozmo and the log. Currently just tests and does not implement the game
def cozmo_thread(robot):
    change_state("set_up")


# this thread creates the tkinter mainloop. This is to increase the responsiveness of the window without freezing
# the program
def tkinter_thread():
    root.mainloop()


def log_making():
    logfile = make_log_file()
    for val in log:
        logfile.write(val)
    logfile.close()


# this method creates and starts running each of the threads and waits for them to finish before exiting
def cozmo_program(robot: cozmo.robot.Robot):
    c_thread = threading.Thread(target=cozmo_thread(robot))
    fsm_thread = threading.Thread(target=state_thread(robot))
    tk_thread = threading.Thread(target=tkinter_thread())
    fsm_thread.start()
    tk_thread.start()
    c_thread.start()
    c_thread.join()
    tk_thread.join()
    fsm_thread.join()
    log_thread = threading.Thread(target=log_making())
    log_thread.start()
    log_thread.join()


# this starts the program
cozmo.run_program(cozmo_program)
