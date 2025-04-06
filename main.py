import tkinter as tk
from src.init import GlobalSetting

if __name__ == "__main__":
    root = tk.Tk()
    pet = GlobalSetting(root)
    root.mainloop()