import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font

from PIL import Image
from PIL import ImageTk

import random
import threading

from menu_process import *

cap = cv2.VideoCapture(2)
debug = 1
foto_toggle = 0
image_toggle = 1
take_photo = 0


def toggle_debug():
    global debug
    debug = not debug


def foto_shooter():
    global foto_toggle, image_toggle, take_photo

    btnFoto.config(state="disabled")

    dir_list = ["Up", "Down", "Left", "Right", "Forward"]
    random.shuffle(dir_list)

    image_toggle, photo_name = 0, "Foto"

    while len(dir_list) >= 0:
        img = video(cap, debug)[0]
        direction = video(cap, debug)[1]

        if take_photo != 1:
            try:
                if dir_list[0] != direction:
                    text_list = dir_list[0]
                    print(text_list)
                    lblText.configure(text=text_list)
                else:
                    lblText.configure(text="Tomando foto . . .")
                    photo_name = dir_list[0]
                    waiter.run()
                    dir_list.pop(0)
            except:
                break
        else:
            toggle_debug()
            cv2.imwrite(photo_name + ".png", img)
            lblText.configure(text="Foto tomada")
            print("Foto tomada")
            toggle_debug()
            take_photo = 0

        put_video()
        root.update()

    lblText.configure(text="Toma de fotos finalizada")
    image_toggle = 1
    foto_toggle = 1


def wait_seconds():
    global waiter
    global take_photo

    put_video()
    root.update()

    waiter = threading.Timer(2.0, wait_seconds)
    take_photo = 1


def put_video():
    frame = video(cap, debug)[0]
    im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    img = ImageTk.PhotoImage(image=im)

    lblVideo.configure(image=img)
    lblVideo.image = img


waiter = threading.Timer(2.0, wait_seconds)

root = tk.Tk()
style = ttk.Style()

button_font = font.Font(family='Modern', weight='bold')
btnIniciar = tk.Button(root, text="Debug", width=30, command=toggle_debug, font=button_font)
btnIniciar.grid(column=0, row=0, padx=5, pady=5)
btnFoto = tk.Button(root, text="Fotografiar", width=30, command=foto_shooter, font=button_font)
btnFoto.grid(column=1, row=0, padx=5, pady=5)
btnFinalizar = tk.Button(root, text="Finalizar", width=30, command=lambda: [root.destroy(), cap.release()], font=button_font)
btnFinalizar.grid(column=2, row=0, padx=5, pady=5)

lblText = tk.Label(root)
lblText.grid(column=0, row=2, columnspan=3)
lblVideo = tk.Label(root)
lblVideo.grid(column=0, row=1, columnspan=3)

lblText.configure(text="CLICK EN 'FOTOGRAFIAR' ", font=('Modern', 26, 'bold'))

while cap.isOpened():

    if image_toggle == 1:
        put_video()
    else:
        image = None

    if foto_toggle == 1:
        btnFoto.config(state="active")
        foto_toggle = 0

    root.update()
