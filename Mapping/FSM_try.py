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

game_states = ['waiting']


def change_state(state):
    game_states.pop(0)
    game_states.append(str(state))


def state_thread():
    while game_states[0] == "waiting":
        time.sleep(0.1)
    while game_states[0] == "set_up":
        print("hello")
    while game_states[0] == "start_game":
        do_something = 0
    while game_states[0] == "executing":
        do_something=0
    while game_states[0] == "failed":
        do_something = 0
    while game_states[0] == "won":
        do_something = 0


def cozmo_thread():
    game_state = input("game_state=")
    change_state(game_state)


c_thread = threading.Thread(target=cozmo_thread())
fsm_thread = threading.Thread(target=state_thread())
