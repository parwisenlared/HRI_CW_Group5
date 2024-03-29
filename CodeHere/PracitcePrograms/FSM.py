import Map
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

## ================================================

# STATE
class State(object):
    def __init__(self, FSM):
        self.FSM = FSM

    def Enter(self):
        pass

    def Execute(self):
        pass

    def Exit(self):
        pass


# Define the states

class State1(State):
    def __init__(self,FSM):
        super(State1, self).__init__(FSM)

    def Enter(self):
        print("Preparing State1")
        super(State1,self).Enter()
    
    def Execute(self):
        print("Cozmo looks for person and explains game")
        # Cozmo explains game: make him talk?
        self.FSM.ToTransition("toState2")

        """
        if (trigger transition):
            if not
                self.FSM.ToTransition("toState2")
            else:
                self.FSM.ToTransition("toState2")
        """

    def Exit(self):
        print("Exiting State1")

class State2(State):
    def __init__(self,FSM):
        super(State2, self).__init__(FSM)

    def Enter(self):
        print("Preparing State2")
        super(State2,self).Enter()
    
    def Execute(self):
        print("Player shows a sequence of Control Cards to Cozmo")
        Map.look_at_player
        # look at this for two min. And then say: "You're time is over"
        self.FSM.ToTransition("toState3")

        """
        if (trigger transition):
            if not
                self.FSM.ToTransition("toState3")
            else:
                self.FSM.ToTransition("toState3")
        """
    def Exit(self):
        print("Exiting State2")
        

class State3(State):

    def __init__(self,FSM):
        super(State3, self).__init__(FSM)

    def Enter(self):
        print("Preparing State3")
        super(State3,self).Enter()
    
    def Execute(self):
        print("The player shows the Execution Card")
        # Robot says: show me the execution card (here?)
        """
        if (Map.lo):
            if not
                print("Show me the Execution card again")
                self.FSM.ToTransition("toState3")
            else:
                self.FSM.ToTransition("toState4")
        """
    
    def Exit(self):
        print("Exiting State3")

class State4(State):

    def __init__(self,FSM):
        super(State4, self).__init__(FSM)

    def Enter(self):
        print("Preparing State4")
        super(State4,self).Enter()
    
    def Execute(self):
        print("Cozmo executes the sequence of actions of State2")
        Map.carry_out_commands(robot)
        self.FSM.ToTransition("toState4")
    
    def Exit(self):
        print("Exiting State4")


class State5(State):

    def __init__(self,FSM):
        super(State5, self).__init__(FSM)

    def Enter(self):
        print("Preparing State5")
        super(State5,self).Enter()
    
    def Execute(self):
        print("Cozmo checks if the goal has been achieved")
        """
        if (Map.light_cube_visible(robot) = false):
            if not
                # Cozmo says: "Congratulations Human"
                Map.reset_game_board()
                self.FSM.ToTransition("toSleep")
            else:
                # Cozmo says: "You failed. Start again, looser"
                Map.reset_game_board()
                self.FSM.ToTransition("toState1")
        """
    def Exit(self):
        print("Exiting State5")

class Sleep(State):

    def __init__(self,FSM):
        super(Sleep, self).__init__(FSM)

    def Enter(self):
        print("Preparing State6")
        super(Sleep,self).Enter()
    
    def Execute(self):
        print("End of the game. Winner")
        # Cozmo says: Sleeping now.
        # Terminate Cozmo.
    
    def Exit(self):
        print("Exiting State6")

## ================================================

class Transition(object):
    def __init__(self, toState):
        self.toState = toState
    
    def Execute(self):
        print("Transitioning")

## ================================================

class FSM(object):
    def __init__(self,char):
        self.char = char
        self.states = {}
        self.transitions = {}
        self.curState = None
        self.prevState = None # Used to prevent looping to states
        self.trans = None

    def AddTransition(self, transName, transition):
        self.transitions[transName] = transition

    def AddState(self, stateName, state):
        self.states[stateName] = state

    def SetState(self, stateName):
        self.prevState = self.curState
        self.curState = self.states[stateName]

    def ToTransition(self, toTrans):
        self.trans = self.transitions[toTrans]

    def Execute(self):
        if (self.trans):
            self.curState.Exit()
            self.trans.Execute()
            self.SetState(self.trans.toState)
            self.curState.Enter()
            self.trans = None
        self.curState.Execute()
        
## ================================================

# IMPLEMENTATION

Char = type(("Char"),(object,),{})

class CozmoGame(Char):
    def __init__(self):
        self.FSM = FSM(self)

        # STATES
        self.FSM.AddState("State1", State1(self.FSM))
        self.FSM.AddState("State2", State2(self.FSM))
        self.FSM.AddState("State3", State3(self.FSM))
        self.FSM.AddState("State4", State4(self.FSM))
        self.FSM.AddState("State5", State5(self.FSM))
        self.FSM.AddState("State6", State6(self.FSM))

        # TRANSITIONS
        self.FSM.AddTransition("toState1", Transition("State1"))
        self.FSM.AddTransition("toState2", Transition("State2"))
        self.FSM.AddTransition("toState3", Transition("State3"))
        self.FSM.AddTransition("toState4", Transition("State4"))
        self.FSM.AddTransition("toState5", Transition("State5"))
        self.FSM.AddTransition("toState6", Transition("State6"))
        
        # set default state
        self.FSM.SetState("State1")

        # shall I create a sleep mode (do nothing)?

        def Execute(self):
            self.FSM.Execute()

## ================================================

if __name__ == "__main__":
    
    Map.make_game_ready()
    logfile = Map.make_log_file()

    cozmo.run_program(Map.cozmo_program)
    g = CozmoGame()
    g.Execute()
    




