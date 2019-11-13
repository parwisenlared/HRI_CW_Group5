import cozmo
from PIL import Image, ImageColor
from cozmo.util import degrees, Pose, distance_mm, speed_mmps

"""
Things to do:
implement some sort of searching strategy so cozmo finds all cubes - included in this is creating 'inital pose' variables
to enable the reset card to be used. 

Also need to change how cubes work so that they .pop values before updating map when cubes are moved, otherwise end up
with them trailing over the map

work out how big the picture is, what is an 

"""
# create blank map
game_map = Image.new('L', (1000, 1000))

# get cube images for map and resize to approximately the right size
cube_image = Image.open("cube.jpg")
cube_image.thumbnail((45, 45))
cozmo_image = Image.open("cozmo.jpg")
cozmo_image.thumbnail((50, 50))

# define poses for cozmo and two cubes
cozmo_pose = []
cube_poses = []

# the array holding the commands the player has given
commands = []

# define command cards (THIS HAS TO CHANGE TO CUSTOM OBJECTS)
forward_card = 'forward'
turn_left = 'left'
turn_right = 'right'
reverse = 'reverse'
pick_up = 'pick_up'
put_down = 'put_down'
undo = 'undo'
reset = 'reset'
execution_card = 'execute'


# variable to track current state of game should be Building Map, Receiving Instructions, Resetting Map, Lost, Won
game_state = ['horray']


# Adds commands to command array in the form of numbers which are then read out below
def add_command_to_array(command_card, robot):
    if command_card == execution_card:
        carry_out_commands(robot)
    elif command_card == reset:
        for val in commands:
            commands.pop()
    elif command_card == undo:
        commands.pop()
    elif command_card == forward_card:
        commands.append(1)
    elif command_card == turn_left:
        commands.append(2)
    elif command_card == turn_right:
        commands.append(3)
    elif command_card == reverse:
        commands.append(4)
    elif command_card == pick_up:
        commands.append(5)
    elif command_card == put_down:
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
    robot.drive_straight(distance_mm(50), speed_mmps(50)).wait_for_completed()
    get_cozmo_position(robot)
    update_map()


# method to be called when card reading @move forward is shown
def drive_backwards(robot):
    robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
    get_cozmo_position(robot)
    update_map()


# method to be called when card reading turn left OR right is shown, when called must include angle = 90, -90
def turn(angle, robot):
    cozmo.robot.Robot.turn_in_place(degrees(angle)).wait_for_completed()
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
    for x in range(0, 1000):
        for y in range(0, 1000):
            game_map.putpixel((x, y), 255)
    for val in cube_poses:
        draw_cubes_on_map(val[0], val[1])
    for val in cozmo_pose:
        draw_cozmo_on_map(val[0], val[1])
    game_map.show()


def draw_cubes_on_map(x, y):
    """ Take in an x and y value, normalise it to our map so that the origin is always the center and then draw an image
    of a cube there."""
    x = int(x) + 500
    y = int(y) + 500
    game_map.paste(cube_image, (x, y))


def draw_cozmo_on_map(x, y):
    """Same as above, except draw a cozmo"""
    x = int(x) + 500
    y = int(y) + 500
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
    game_map.show()
    add_command_to_array(forward_card, robot)
    add_command_to_array(pick_up, robot)
    add_command_to_array(put_down, robot)
    add_command_to_array(reverse, robot)
    add_command_to_array(execution_card, robot)


cozmo.run_program(cozmo_program)
