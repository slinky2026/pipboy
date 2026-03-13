from enum import Enum, auto

class Action(Enum):
    #High-level input actions used throughout.

    #Instead of responding directly to raw keyboard events
    #(e.g. pygame.KEYDOWN) like i did at first, the program converts physical inputs
    #into Actions. This lets me do:
    #Keyboard input (Windows dev), GPIO / rotary encoder input (Raspberry Pi hardware), Future input devices
    #to all trigger the same internal behaviour.

    #separates:
      #  Input source (keyboard, GPIO, etc.)
       # Application behaviour (screen navigation, selection, etc.), basically better for my development so i
       #dont lose my mind
    
    #THIS IS TOP NAV BAR
    TAB_1 = auto() #eg stats
    TAB_2 = auto()
    TAB_3 = auto()
    TAB_4 = auto()
    TAB_5 = auto()

    #THIS IS NAV WITHIN EACH TAB
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    #interaction controls
    SELECT = auto()
    BACK = auto()
    QUIT = auto()
