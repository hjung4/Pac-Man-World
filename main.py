import tkinter, subprocess
import tkinter.font as font
from tkinter import *

root = tkinter.Tk()
root.title("Pac-Man World")

helv72 = font.Font(family="helvetica", size=72, weight="bold")
helv36 = font.Font(family="helvetica", size=36)

Label(text="PAC-MAN WORLD",font=helv72).pack(side="top",padx=10,pady=10)
Label(text="Choose a game: ",font=helv36).pack(side="top",padx=10,pady=10)

def runPacMan():
    subprocess.call(["python","games/Pac-Man.py"])
def runSuperPacMan():
    subprocess.call(["python","games/Super_Pac-Man.py"])
def runProfessorPacMan():
    subprocess.call(["python","games/Professor_Pac-Man.py"])
    
B1 = tkinter.Button(root, text = "Pac-Man", font=helv36, width = 30, command = runPacMan)
B2 = tkinter.Button(root, text = "Super Pac-Man", font=helv36, width = 30, command = runSuperPacMan)
B3 = tkinter.Button(root, text = "Professor Pac-Man", font=helv36, width = 30, command = runProfessorPacMan)

B1.pack(side="top",fill="both",expand=True,padx=4,pady=4)
B2.pack(side="top",fill="both",expand=True,padx=4,pady=4)
B3.pack(side="top",fill="both",expand=True,padx=4,pady=4)

root.geometry("1000x700")

root.mainloop()
