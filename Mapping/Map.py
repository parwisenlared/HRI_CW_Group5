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
game_map = Image.new('L', (4200, 2970))

# get cube images for map and resize to approximately the right size
cube_image = Image.open("cube.jpg")
cube_image.thumbnail((45, 45))
cozmo_image = Image.open("cozmo.jpg")
cozmo_image.thumbnail((50, 50))

# define poses for cozmo and two cubes
cozmo_pose = []
cube_poses = []


def update_map():
    """This paints the map white and then pastes the positions of cozmo and the cubes in their updated positions."""
    for x in range(0, 4200):
        for y in range(0, 2970):
            game_map.putpixel((x, y), 255)
    for val in cube_poses:
        draw_cubes_on_map(val[0], val[1])
    for val in cozmo_pose:
        draw_cozmo_on_map(val[0], val[1])


def draw_cubes_on_map(x, y):
    """ Take in an x and y value, normalise it to our map so that the origin is always the center and then draw an image
    of a cube there."""
    x = int(x) + 2100
    y = int(y) + 1475
    game_map.paste(cube_image, (x, y))


def draw_cozmo_on_map(x, y):
    """Same as above, except draw a cozmo"""
    x = int(x) + 2100
    y = int(y) + 1475
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
    xy = get_xy_coordinates(current_pose)
    cozmo_pose.append(xy)


def cozmo_program(robot: cozmo.robot.Robot):
    get_cozmo_position(robot)
    look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cubes = robot.world.wait_until_observe_num_objects(num=2, object_type=cozmo.objects.LightCube, timeout=60)
    look_around.stop()
    for cube in cubes:
        this_cube = get_xy_coordinates(str(cube.pose.position))
        cube_poses.append(this_cube)
    print(cube_poses)
    update_map()
    game_map.show()


cozmo.run_program(cozmo_program)
