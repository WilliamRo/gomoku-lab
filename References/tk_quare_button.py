import tkinter as tk
import numpy as np

from PIL import Image, ImageTk


form = tk.Tk()

arr = np.ones(shape=[11, 11]) * 255
arr[5] = 0
img = Image.fromarray(arr)
imgTk = ImageTk.PhotoImage(img)
# imgTk =tk.PhotoImage()
# imgTk = tk.PhotoImage(file='black_stone.png')

button = tk.Button(form, image=imgTk, height=50, width=50).pack()
form.mainloop()
