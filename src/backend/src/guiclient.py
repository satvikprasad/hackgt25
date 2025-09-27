import pyautogui
import time
from enum import Enum

class Actions(Enum):
    WAIT = 0
    REQUEST_MOVE= 1
    MOUSE_DOWN = 2
    MOUSE_UP = 3
    TYPE = 4
    KEY_DOWN = 5
    KEY_UP = 6
    SCROLL_UP = 7
    SCROLL_DOWN = 8
    REASSESS = 9
    COMPLETE = 10
    STOP = 11

class GUIClient:

    def __init__(self, commands : list[tuple[Actions, any]]):
        self.commands = commands

        for i in range(len(self.commands)):
            if not self.verify(i):
                raise ValueError(f"Invalid command at index {i}: {self.commands[i]}")

        self.index = 0

    def verify(self, index : int):
        if index < 0 or index >= len(self.commands):
            raise IndexError("Index out of range")

        action, value = self.commands[index]        

        if action in (Actions.MOUSE_DOWN): #value = [(LEFT or RIGHT), (time)]
            if not (isinstance(value, str)):
                return False
        elif action in (Actions.MOUSE_UP):
            if value is not None:
                return False
        elif action == Actions.TYPE:
            if not isinstance(value, str):
                return False
        elif action in (Actions.KEY_DOWN, Actions.KEY_UP):
            if not isinstance(value, str):
                return False
        elif action in (Actions.SCROLL_UP, Actions.SCROLL_DOWN):
            if not isinstance(value, int):
                return False
        elif action in (Actions.STOP):
            if value is not None:
                return False
        elif action in (Action.COMPLETE):
            if value is not None:
                return False
        elif action in (Actions.REQUEST_MOVE):
            if not (isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], str)):
                return False
        elif action in (Actions.REASSESS):
            if value is not None:
                return False
        elif action == Actions.WAIT:
            if not (isinstance(value, (int, float)) and value >= 0):
                return False
        
        return True

    def step(self) -> int:
        if self.index >= len(self.commands):
            raise IndexError("No more commands to execute") 
        
        action, value = self.commands[self.index]

        if action == Actions.MOUSE_MOVE:
            pyautogui.moveTo(value[0], value[1], 0.3)
        elif action == Actions.MOUSE_DOWN:
            if value.lower() == "left":
                pyautogui.mouseDown(button='left')
            elif value.lower() == "right":
                pyautogui.mouseDown(button='right')
        elif action == Actions.MOUSE_UP:
            if value.lower() == "left":
                pyautogui.mouseUp(button='left')
            elif value.lower() == "right":
                pyautogui.mouseUp(button='right')
        elif action == Actions.TYPE:
            pyautogui.typewrite(value, 0.1)
        elif action == Actions.KEY_DOWN:
            pyautogui.keyDown(value)
        elif action == Actions.KEY_UP:
            pyautogui.keyUp(value)
        elif action == Actions.SCROLL_UP:
            pyautogui.scroll(value)
        elif action == Actions.SCROLL_DOWN:
            pyautogui.scroll(-value)
        elif action == Actions.WAIT:
            pyautogui.sleep(value)
        elif action == Actions.REQUEST:
            pass # Placeholder for future implementation
        elif action == Actions.STOP:
            return -1
        elif action == Actions.COMPLETE:
            return 1
        
        self.index += 1
        return 0



time.sleep(2)
commands = [
    (Actions.MOUSE_MOVE, (916, 967)),   # Move mouse to x=500, y=300
    (Actions.MOUSE_DOWN, "left"),       # Hold left mouse button
    (Actions.MOUSE_UP, "left"),         # Release left mouse button
    (Actions.TYPE, "hello world"),      # Type "hello world"
    (Actions.WAIT, 2),                  # Wait for 2 seconds
    (Actions.SCROLL_DOWN, 10),          # Scroll down
    (Actions.STOP, None)                # Stop execution
]

client = GUIClient(commands)

while not client.step() == 0:
    pass




