import tkinter as tk
import cv2
from .slime import DesktopPet
from .handpose import HandPose
class GlobalSetting():
    def __init__(self, root: tk.Tk):
        self.slime = DesktopPet(root)
        self.handpose = HandPose()