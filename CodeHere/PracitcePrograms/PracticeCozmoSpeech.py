import cozmo
from cozmo.util import degrees


def cozmo_program(robot: cozmo.robot.Robot):
    voice_pitch = -1.0
    duration_scalar = 0.5
    robot.say_text("I'm going to set up and build my world map. While I do that - you have a quick look over the "
                   "command cards. Your goal is to use them to give me instructions that will have me pick up one cube"
                   "and stack it on top of the other.", voice_pitch=voice_pitch, duration_scalar=duration_scalar)\
        .wait_for_completed()
    robot.say_text("I'll tell you when I'm ready to be shown the cards. You'll have two minutes to show me the card "
                   "sequence. If you're ready before that, show me the execute card and I'll get started. You'll know "
                   "when I see a card because my backpack light will flash. ", voice_pitch=voice_pitch,
                   duration_scalar=duration_scalar).wait_for_completed()
    robot.say_text("You have 3 tries. good luck", voice_pitch=voice_pitch, duration_scalar=duration_scalar)\
        .wait_for_completed()


cozmo.run_program(cozmo_program)
