import tkinter as tk
from fractalfriend.demo import write_pngs_for_report, do_whole_interpolation


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        master.title("Fractal Friend")

        self.master.minsize(640, 0)
        self.create_widgets()
        self.pack()

    def create_widgets(self):
        

        self.__buttons = []

        label = tk.Label(self.master, text="Press a button to run one of the demo functions.")
        label.pack(side="top")
        
        functions = [("PNGs for Report (This will open a long series of display windows)", write_pngs_for_report)]

        num_divisions = 10
        for h in [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]:
            
            def setup_function():
                # Setting up closure for callback
                param = h
                
                def func():
                    print("Using h=%f" % param)
                    do_whole_interpolation(param, num_divisions)

                functions.append(("Interpolate %d times with h=%f" % (num_divisions, h), func))
                
            setup_function()

        for label, function in functions:

            button = tk.Button(self.master)
            button["text"] = label
            
            
            button["command"] = function
            button.pack(side="top", pady=(0,4), padx=4)
    
            self.__buttons.append(button)

        self.pack()
        


def launch_ui():
    root = tk.Tk()

    app = App(root)
    
    # start the program
    app.mainloop()
    

if __name__ == '__main__':
    launch_ui()