import tkinter as tk


form = tk.Tk()
frame1 = tk.Frame(form)
frame2 = tk.Frame(form)
frame1.pack(side=tk.TOP)
frame2.pack(side=tk.TOP)
btn1 = tk.Button(frame1, text='Button1')
btn2 = tk.Button(frame1, text='Button2')
btn3 = tk.Button(frame2, text='Button3')
btn4 = tk.Button(frame2, text='Button4')
btn1.pack(side=tk.LEFT)
btn2.pack(side=tk.LEFT)
btn3.pack(side=tk.LEFT)
btn4.pack(side=tk.LEFT)

form.mainloop()