import cozmo
import time
import datetime
from PIL import Image, ImageTk, ImageDraw
from cozmo.util import degrees, Pose, distance_mm, speed_mmps
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes, LightCube1Id, LightCube2Id, LightCube3Id
from cozmo.faces import Face

import tkinter as tk
import asyncio
import threading

"""
The code contains three classes. 
The cozmo methods class contains all of the required methods to make cozmo run. It enables cozmo to read, store and 
execute actions. The FSM contains the finite state machine and its 6 possible states. The CommandCardAcknowledge was
added to enable Cozmo's backpacks lights to flash.

"""

# global variable to signal when the game ends
game_running = True
# variables for cozmo's voice pitch and speed of speech.
voice_pitch = -1.0
duration_scalar = 0.5
# variables for setting up the tkinter map
size_of_map = 1000
anchor_for_canvas = size_of_map / 2
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
# define the max time (in seconds)
max_time = 250
# variable holding the player's face_ID and pose
player_face_id = []
player_face_pose = []
# variable to track current state of game should be Building Map, Receiving Instructions, Resetting Map, Lost, Won
game_state = ['set_up']
image_number = 0
# Ensures FSM only looks at the player once in listening state
look_at = 0


class CozmoMethods(threading.Thread):
    def __init__(self, robot):
        threading.Thread.__init__(self)
        self.robot = robot

    def run(self):
        self.change_state("set_up")

    # colour light cubes and return those cubes to the main function for further use.
    def colour_light_cubes(self, robot):
        cube1 = robot.world.get_light_cube(LightCube1Id)
        cube1.set_lights(cozmo.lights.red_light)
        cube2 = robot.world.get_light_cube(LightCube2Id)
        cube2.set_lights(cozmo.lights.blue_light)
        self.write_to_log("Light cubes turn on")
        return cube1, cube2

    # get current time for log entries
    def get_time(self):
        time_now = datetime.datetime.now().time()
        return time_now

    # write events to log (list) to be read and written to log file at the end of the program
    def write_to_log(self, event):
        this_time = self.get_time()
        string = '%s at : %s.\n' % (event, this_time)
        log.append(string)

    # Add event listeners for each custom object, when object is seen, the listener calls the method to add it to the
    # command array.
    def object_event_listeners(self, evt, **kw):
        if isinstance(evt.obj, CustomObject):
            obj = str(evt.obj.object_type)
            obj_substring = obj[-2:]
            object_number = int(obj_substring)
            if object_number == 0:
                self.add_command_to_array(0)
                self.write_to_log("Saw forward card")
                print("card: forward seen")
            elif object_number == 1:
                self.add_command_to_array(1)
                self.write_to_log("Saw turn left card")
                print("card: turn left seen")
            elif object_number == 2:
                self.add_command_to_array(2)
                self.write_to_log("Saw turn right card")
                print("card: turn right seen")
            elif object_number == 3:
                self.add_command_to_array(3)
                self.write_to_log("Saw reverse card")
                print("card: reverse seen")
            elif object_number == 4:
                self.add_command_to_array(4)
                self.write_to_log("Saw pick up card")
                print("card: pick up seen")
            elif object_number == 5:
                self.add_command_to_array(5)
                self.write_to_log("Saw put down card")
                print("card: put down seen")
            elif object_number == 6:
                self.add_command_to_array(6)
                self.write_to_log("Saw undo card")
                print("card: undo seen")
            elif object_number == 7:
                self.add_command_to_array(7)
                self.write_to_log("Saw reset card")
                print("card: reset seen")
            elif object_number == 8:
                self.add_command_to_array(8)
                self.write_to_log("Saw execution card")
                print("card: execution seen")
            elif object_number == 9:
                self.add_command_to_array(9)
                self.write_to_log("Saw turn left 45 card")
                print("card turn left 45 seen")
            elif object_number == 10:
                self.add_command_to_array(10)
                self.write_to_log("Saw turn right 45 card")
                print("card turn right 45 seen")

    # This creates each of the custom objects using the factory objects.
    def make_command_cards(self, robot):
        forward_card = robot.world.define_custom_cube(CustomObjectTypes.CustomType00, CustomObjectMarkers.Diamonds2, 44,
                                                      10, 10, True)
        turn_left = robot.world.define_custom_cube(CustomObjectTypes.CustomType01, CustomObjectMarkers.Triangles4, 44,
                                                   10, 10, True)
        turn_right = robot.world.define_custom_cube(CustomObjectTypes.CustomType02, CustomObjectMarkers.Hexagons5, 44,
                                                    10, 10, True)
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
        execution_card = robot.world.define_custom_cube(CustomObjectTypes.CustomType08, CustomObjectMarkers.Triangles3,
                                                        44, 10, 10, True)
        turn_left_45 = robot.world.define_custom_cube(CustomObjectTypes.CustomType09, CustomObjectMarkers.Circles5, 44,
                                                      10, 10, True)
        turn_right_45 = robot.world.define_custom_cube(CustomObjectTypes.CustomType10, CustomObjectMarkers.Triangles2,
                                                       44, 10, 10, True)
        return forward_card, turn_right, turn_left, reverse, pick_up, put_down, undo, reset, execution_card, \
               turn_left_45, turn_right_45

    # Adds commands to command array in the form of numbers which are then read out by carry_out_commands below.
    # Some of the commands are implemented here, such as reset and undo.
    def add_command_to_array(self, command_card):
        if command_card == 8:
            self.change_state("executing")
        elif command_card == 7:
            if len(commands) > 0:
                for x in range(0, len(commands)):
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
        elif command_card == 9:
            commands.append(7)
        elif command_card == 10:
            commands.append(8)

    # reads each command value from the commands list and executes the correct action
    def carry_out_commands(self, robot):
        print("Carrying out commands")
        print(str(commands))
        for val in commands:
            if val == 1:
                self.drive_forward(robot)
            elif val == 2:
                self.turn(90, robot)
                self.write_to_log("Turned left 90")
            elif val == 3:
                self.turn(-90, robot)
                self.write_to_log("Turned right 90")
            elif val == 4:
                self.drive_backwards(robot)
            elif val == 5:
                # This should be 'pick_up_cube,' however this is automatically called by light_cube_visible if the player
                # has correctly guided cozmo to the cube.
                self.light_cube_visible(robot)
                self.write_to_log("Attempted cube pick up")
            elif val == 6:
                self.put_down_cube(robot)
                self.write_to_log("Put cube down")
            elif val == 7:
                self.turn(45, robot)
                self.write_to_log("Turned left 45")
            elif val == 8:
                self.turn(-45, robot)
                self.write_to_log("Turned right 45")

        for x in range(0, len(commands)):
            commands.pop()
        self.check_for_success()

    def check_for_success(self):
        self.write_to_log("Checking for success")
        cube1x = 0
        cube1y = 0
        cube2x = 0
        cube2y = 0
        for val in cube_one_pose:
            cube1x = val[0]
            cube1y = val[1]
        for val in cube_two_pose:
            cube2x = val[0]
            cube2y = val[1]
        print(str(cube1x))
        print(str(cube2x))
        print(str(cube1y))
        print(str(cube2y))
        # the +/- 15 mm tolerance is to account for the cubes not being perfectly stacked on top of one and other.
        # Any more than 15mm and the top cube will fall off
        if (abs(cube2x)-15) <= abs(cube1x) <= (abs(cube2x)+15) and (abs(cube2y)-15) <= abs(cube1y) <= (abs(cube2y)+15):
            self.write_to_log("Success")
            self.change_state("success")
        else:
            self.write_to_log("Failed")
            self.change_state("failed")

    def lost(self, robot):
        self.write_to_log("Player lost entirely")
        print("You lost")
        robot.say_text("you lost! goodbye", voice_pitch=voice_pitch, duration_scalar=duration_scalar)\
            .wait_for_completed()
        self.change_state("game_over")

    def victory(self, robot):
        self.write_to_log("PLayer won")
        print("You won")
        robot.say_text("you won! goodbye", voice_pitch=voice_pitch, duration_scalar=duration_scalar,
                       play_excited_animation=True).wait_for_completed()
        self.change_state("game_over")

    # method to be called when card reading move forward is shown
    def drive_forward(self, robot):
        robot.drive_straight(distance_mm(50), speed_mmps(50)).wait_for_completed()
        self.update_map(robot)
        self.write_to_log('moved forward')

    # method to be called when card reading move backward is shown
    def drive_backwards(self, robot):
        robot.drive_straight(distance_mm(-50), speed_mmps(50)).wait_for_completed()
        self.update_map(robot)
        self.write_to_log('moved backwards')

    # method to be called when card reading turn left OR right is shown, when called must include angle = 90, -90
    def turn(self, angle, robot):
        robot.turn_in_place(degrees(angle)).wait_for_completed()
        self.update_map(robot)

    # method to discover if the player has positioned cozmo where it can see a cube - it will then pick it up or
    # change the game state to FAILED
    def light_cube_visible(self, robot):
        try:
            cube = robot.world.wait_for_observed_light_cube(5)
            self.pick_up_cube(robot, cube)
            print("visible")
        except asyncio.TimeoutError:
            event = "didn't find a cube game failed!"
            self.write_to_log(event)
            self.change_state("failed")

    # cozmo will pick up the cube seen in light_cube_visible
    def pick_up_cube(self, robot, cube):
        robot.stop_all_motors()
        current_action = robot.pickup_object(cube, num_retries=3, in_parallel=True)
        current_action.wait_for_completed()
        if current_action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Pickup Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))
            return

    # cozmo will put a cube down
    def put_down_cube(self, robot):
        robot.move_lift(-1)
        self.drive_backwards(robot)
        self.update_map(robot)

    # update the displayed map
    def update_map(self, robot):
        global image_number
        print("Updated map")
        # ensures all pictures pasted on the map are in the correct current poses
        self.get_world_positions(robot)
        # this paints the canvas white, if not done the previous positions of objects would leave afterprints
        for x in range(0, size_of_map):
            for y in range(0, size_of_map):
                game_map.putpixel((x, y), (255, 255, 255))
        for val in cube_one_pose:
            game_map.paste(cube_image, (500 + int(val[0]), (500 + int(val[1]))))
        for val in cube_two_pose:
            game_map.paste(cube_image, (500 + int(val[0]), (500 + int(val[1]))))
        for val in cozmo_pose:
            game_map.paste(cozmo_image, (500 + int(val[0]), (500 + int(val[1]))))
        for val in player_face_pose:
            game_map.paste(player_image, (500 + int(val[0]), (500 + int(val[1]))))
        update_canvas(game_map)

    # Take in a string as given by str(.pose.position) and then determine x, y coordinates for map making.
    def get_xy_coordinates(self, position_string):
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
    def get_world_positions(self, robot):
        if len(cozmo_pose) > 0:
            for val in cozmo_pose:
                x = val[0]
                y = val[1]
                event = 'cozmo was at (%s, %s)' % (x, y)
                self.write_to_log(event)
            cozmo_pose.pop()
        if len(cube_one_pose) > 0:
            for val in cube_one_pose:
                x = val[0]
                y = val[1]
                event = 'cube one was at (%s, %s)\n' % (x, y)
                self.write_to_log(event)
            cube_one_pose.pop()
        if len(cube_two_pose) > 0:
            for val in cube_two_pose:
                x = val[0]
                y = val[1]
                event = 'cube two was at (%s, %s)\n' % (x, y)
                self.write_to_log(event)
            cube_two_pose.pop()
        cozmo_current_pose = str(robot.pose.position)
        cube_one_current_pose = str(robot.world.get_light_cube(LightCube1Id).pose.position)
        cube_two_current_pose = str(robot.world.get_light_cube(LightCube2Id).pose.position)
        cozmo_xy = self.get_xy_coordinates(cozmo_current_pose)
        cube_one_xy = self.get_xy_coordinates(cube_one_current_pose)
        cube_two_xy = self.get_xy_coordinates(cube_two_current_pose)
        cozmo_pose.append(cozmo_xy)
        cube_one_pose.append(cube_one_xy)
        cube_two_pose.append(cube_two_xy)

    # currently unused, triggered whenever a face is in view
    def face_observed_listeners(self, evt, **kw):
        self.get_player_position()

    # this initial method looks for the game player. Cozmo will look for a face and assume the one it sees is the player
    def find_player(self, robot):
        print("finding players")
        robot.say_text("I'm looking for the player, please look at me.", voice_pitch=voice_pitch,
                       duration_scalar=duration_scalar).wait_for_completed()
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
                xy_position = self.get_xy_coordinates(position)
                if len(player_face_pose) > 0:
                    for _ in player_face_pose:
                        player_face_pose.pop()
                player_face_pose.append(xy_position)
                event = "Cozmo found a face at: %s", position
                self.write_to_log(event)
                return player_face
            # returns the player's face for use later in the program
            if not (player_face and player_face.is_visible):
                try:
                    robot.turn_in_place(degrees(90)).wait_for_completed()
                    player_face = robot.world.wait_for_observed_face(timeout=1)
                except asyncio.TimeoutError:
                    event = "didn't find a face looking elsewhere!"
                    self.write_to_log(event)
            if turn_action:
                turn_action.wait_for_completed()

    # does nothing currently but will be updated to update the player position
    def get_player_position(self):
        for val in player_face_pose:
            abd = 1

    # should only ever be called once to get initial game board (in case reset is needed), set up listeners, make the
    # command cards, set the cube colours
    def make_game_ready(self, robot):
        print("Setting up")
        self.write_to_log("Setting up game board")
        robot.add_event_handler(cozmo.world.faces.EvtFaceObserved, self.face_observed_listeners)
        robot.add_event_handler(cozmo.objects.EvtObjectAppeared, self.object_event_listeners)
        self.make_command_cards(robot)
        cube1, cube2 = self.colour_light_cubes(robot)
        cozmo_current_pose = str(robot.pose.position)
        cozmo_xy = self.get_xy_coordinates(cozmo_current_pose)
        cozmo_pose.append(cozmo_xy)
        for val in cozmo_pose:
            cozmo_initial_pose.append(val)
        self.find_cubes(robot)
        for val in cube_one_pose:
            cube_one_initial_pose.append(val)
        for val in cube_two_pose:
            cube_two_initial_pose.append(val)
        print("game_ready")
        self.change_state("listening_for_commands")

    def find_cubes(self, robot):
        look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        cubes = robot.world.wait_until_observe_num_objects(num=2, object_type=cozmo.objects.LightCube, timeout=60)
        look_around.stop()
        self.update_map(robot)

    # checks if cubes/cozmo are out of position and repositions them correctly
    def reset_game_board(self, robot):
        global look_at
        look_at = 0
        robot.move_lift(-5)
        print("Resetting")
        # check if cubes are out of position (there's some leeway in the if statement here to account for cozmo slipping
        # on the table surface and thinking they've moved a few mm when they haven't. If they're pretty much in the same
        # position then cozmo leaves them be.
        cube = robot.world.get_light_cube(LightCube1Id)
        x_initial = 0
        y_initial = 0
        x_current = 0
        y_current = 0
        for val in cube_one_initial_pose:
            x_initial = val[0]
            y_initial = val[1]
        for val in cube_one_pose:
            x_current = val[0]
            y_current = val[1]
        # create a square search space 20 mm by 20 mm (for cozmo readout error)
        x_current_small = x_current - 20
        x_current_big = x_current + 20
        y_current_small = y_current - 20
        y_current_big = y_current + 20
        if x_current_small <= x_initial <= x_current_big and y_current_small <= y_initial <= y_current_big:
            robot.stop_all_motors()
            current_action = robot.pickup_object(cube, num_retries=3, in_parallel=True)
            current_action.wait_for_completed()
            robot.go_to_pose(Pose(x_initial, y_initial, 0, angle_z=degrees(0))).wait_for_completed()
            self.put_down_cube(robot)

        cube = robot.world.get_light_cube(LightCube2Id)
        x_initial = 0
        y_initial = 0
        x_current = 0
        y_current = 0
        for val in cube_two_initial_pose:
            x_initial = val[0]
            y_initial = val[1]
        for val in cube_two_pose:
            x_current = val[0]
            y_current = val[1]
        # create a square search space 10 mm by 10 mm (for cozmo readout error)
        x_current_small = x_current - 10
        x_current_big = x_current + 10
        y_current_small = y_current - 10
        y_current_big = y_current + 10
        if x_current_small <= x_initial <= x_current_big and y_current_small <= y_initial <= y_current_big:
            robot.stop_all_motors()
            current_action = robot.pickup_object(cube, num_retries=3, in_parallel=True)
            current_action.wait_for_completed()
            robot.go_to_pose(Pose(x_initial, y_initial, 0, angle_z=degrees(0))).wait_for_completed()
            self.put_down_cube(robot)

        x = 0
        y = 0
        for val in cozmo_initial_pose:
            x = val[0]
            y = val[1]
        robot.go_to_pose(Pose(x, y, 0, angle_z=degrees(0))).wait_for_completed()
        self.change_state("listening_for_commands")

    # how to change states
    def change_state(self, state):
        game_state.insert(0, str(state))
        self.write_to_log("Changed to state: %s" % state)

    # cozmo will turn and look at where it last saw the player
    def look_at_player(self, robot, player_face):
        robot.stop_all_motors()
        print(str(player_face))
        print("Looking at players")
        robot.stop_all_motors()
        current_action = robot.turn_towards_face(face=player_face)
        current_action.wait_for_completed()
        if current_action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("look at failed: code=%s reason='%s' result=%s" % (code, reason, result))
            return


class FSM(CozmoMethods, threading.Thread):
    def __init__(self, robot):
        threading.Thread.__init__(self)
        CozmoMethods.__init__(self, robot)
        self.robot = robot

    # all the states that can exist
    def run(self):
        robot = self.robot
        global game_running
        global look_at
        set_up = 0
        tries = 0
        current_time = 0
        player_face = self.find_player(robot)
        while game_running:
            while game_state[0] == "set_up":
                # ensure the make_game_ready method is only called at the beginning of the game.
                if set_up == 0:
                    set_up = set_up + 1
                    robot.say_text(
                        "I'm going to set up and build my world map. While I do that - you have a quick look over the "
                        "command cards. Your goal is to use them to give me instructions that will have me pick up one "
                        "cube and stack it on top of the other.", voice_pitch=voice_pitch,
                        duration_scalar=duration_scalar).wait_for_completed()
                    robot.say_text(
                        "I'll tell you when I'm ready to be shown the cards. You'll have two minutes to show me the "
                        "card sequence. If you're ready before that, show me the execute card and I'll get started. "
                        "You'll know when I see a card because my backpack light will flash. ", voice_pitch=voice_pitch,
                        duration_scalar=duration_scalar).wait_for_completed()
                    robot.say_text(
                        "You have 3 tries. good luck", voice_pitch=voice_pitch, duration_scalar=duration_scalar)\
                        .wait_for_completed()

                    self.make_game_ready(robot)
            while game_state[0] == "listening_for_commands":
                if look_at == 0:
                    self.look_at_player(robot, player_face)
                    robot.say_text("ok, show me the cards", voice_pitch=voice_pitch, duration_scalar=duration_scalar)\
                        .wait_for_completed()
                    look_at = look_at + 1
                if current_time <= max_time:
                    time.sleep(0.1)
                    current_time = current_time + 1
                else:
                    look_at = 0
                    current_time = 0
                    self.change_state("executing")
                    time.sleep(0.1)
            while game_state[0] == "executing":
                look_at = 0
                current_time = 0
                robot.say_text("Ok, I'm getting started", voice_pitch=voice_pitch, duration_scalar=duration_scalar)\
                    .wait_for_completed()
                robot.set_head_angle(degrees(0)).wait_for_completed()
                self.carry_out_commands(robot)
                time.sleep(0.1)
            while game_state[0] == "failed":
                robot.say_text("That didn't work!", voice_pitch=voice_pitch, duration_scalar=duration_scalar)\
                    .wait_for_completed()
                tries = tries + 1
                left = 3 - tries
                robot.say_text("You have " + str(left) + " tries left", voice_pitch=voice_pitch,
                               duration_scalar=duration_scalar).wait_for_completed()
                if tries == 3:
                    self.lost(robot)
                else:
                    robot.say_text("I'm just going to get everything back in position", voice_pitch=voice_pitch,
                                   duration_scalar=duration_scalar).wait_for_completed()
                    self.reset_game_board(robot)
            while game_state[0] == "success":
                self.victory(robot)
            if game_state[0] == "game_over":
                game_running = False
                name = input("Please enter a filename for the log file (don't add a file extension thx): ")
                file_name_with_extension = name + ".txt"
                logfile = open(file_name_with_extension, "w+")
                for val in log:
                    logfile.write(val)
                logfile.close()


class CommandCardAcknowledge(threading.Thread):
    def __init__(self, robot):
        threading.Thread.__init__(self)
        self.robot = robot

    def run(self):
        robot = self.robot
        current_command_length = len(commands)
        while game_running:
            if len(commands) != current_command_length:
                robot.set_all_backpack_lights(cozmo.lights.green_light)
                print("Lights Changed")
                time.sleep(0.1)
                robot.set_all_backpack_lights(cozmo.lights.off_light)
                current_command_length = len(commands)


# this method creates and starts running each of the threads and waits for them to finish before exiting
def cozmo_program(robot: cozmo.robot.Robot):
    c_thread = CozmoMethods(robot)
    fsm_thread = FSM(robot)
    ack_thread = CommandCardAcknowledge(robot)
    ack_thread.start()
    fsm_thread.start()
    c_thread.start()
    root.mainloop()
    c_thread.join()
    fsm_thread.join()
    ack_thread.join()


def update_canvas(this_map):
    global image_number
    this_maps = ImageTk.PhotoImage(this_map)
    canvas.create_image(anchor_for_canvas, anchor_for_canvas, image=this_maps)
    image_number = image_number + 1
    filename = "mapNumber" + str(image_number) + ".png"
    this_map.save(filename)


# this starts the program
cozmo.run_program(cozmo_program)
