from __future__ import annotations
# Allows forward references in type hints (like, Optional[InputEvent])
# without needing to quote them as strings
from collections import deque
from dataclasses import dataclass
#auto generates rubbish like init
from typing import Deque, Optional

import pygame

from pypboy.input.actions import Action


@dataclass
class InputEvent:
    action: Action


class InputManager:
    
    #Collects input from keyboard (always) and GPIO (optional) into a single queue of actions
    
    def __init__(self):
        self._queue: Deque[InputEvent] = deque()

        # GPIO iniitialisation
        self._gpio_ready = False #disable for now
        self._encoder = None
        self._button = None

    def push(self, action: Action) -> None:
        #add new action to queue
        self._queue.append(InputEvent(action))

    def pop(self) -> Optional[InputEvent]:
        #pull next action from queue
        return self._queue.popleft() if self._queue else None

    
    def process_pygame_event(self, event: pygame.event.Event) -> None:
        #convert pygame event into higher level actions, basiically translates keydown
        if event.type == pygame.QUIT:
            self.push(Action.QUIT)
            return #this is to exit

        if event.type != pygame.KEYDOWN:
            return #ignore

        k = event.key
        #map key to action
        if k == pygame.K_ESCAPE:
            self.push(Action.QUIT)
        elif k == pygame.K_1:
            self.push(Action.TAB_1)
        elif k == pygame.K_2:
            self.push(Action.TAB_2)
        elif k == pygame.K_3:
            self.push(Action.TAB_3)
        elif k == pygame.K_4:
            self.push(Action.TAB_4)
        elif k == pygame.K_5:
            self.push(Action.TAB_5)
        elif k == pygame.K_UP:
            self.push(Action.UP)
        elif k == pygame.K_DOWN:
            self.push(Action.DOWN)
        elif k == pygame.K_LEFT:
            self.push(Action.LEFT)
        elif k == pygame.K_RIGHT:
            self.push(Action.RIGHT)
        elif k == pygame.K_RETURN:
            self.push(Action.SELECT)
        elif k == pygame.K_BACKSPACE:
            self.push(Action.BACK)
        elif k == pygame.K_RETURN:
            self.push(Action.SELECT)
        elif k == pygame.K_BACKSPACE:
            self.push(Action.BACK)
        

    # GPIO INTEGRATION FOR PI ONLY
    def enable_gpio_rotary(self, *, pin_a: int, pin_b: int, pin_sw: int) -> None:
        """
        Call this ONLY on  Pi.
        Uses gpiozero devices. Safe to call on Windows but will fail, learned hard way.
        """
        try:
            #gpiozero abstratcs calls into devices
            from gpiozero import RotaryEncoder, Button  # type: ignore
        except Exception:
            # Running on Windows or gpiozero not installed
            return
        #creates rotary encoder device
        # RotaryEncoder emits steps via .when_rotated_clockwise / anticlockwise
        encoder = RotaryEncoder(a=pin_a, b=pin_b, max_steps=0)  # max_steps=0 = unlimited rotate track
        
        #create button device
        button = Button(pin_sw, pull_up=True, bounce_time=0.03, hold_time=0.6)
        # so this uses internal pull up resistor, debounce, and counts how long a contact is held to count

        #define callback behaviour
        #auto triggered by gpiozero
        def cw():
            self.push(Action.DOWN)   # clockwise = scroll down
        def ccw():
            self.push(Action.UP)#scroll up duh

        def pressed():
            self.push(Action.SELECT) #select

        def held():
            self.push(Action.BACK)

        encoder.when_rotated_clockwise = cw
        encoder.when_rotated_counter_clockwise = ccw
        button.when_pressed = pressed
        button.when_held = held


        #store stuff
        self._encoder = encoder
        self._button = button
        self._gpio_ready = True
