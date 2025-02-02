import tkinter as tk
from tkinter import colorchooser

class StickyNote:
    def __init__(self, root):
        self.root = root
        self.root.title("Sticky Note")
        self.root.geometry("300x250")
        self.root.configure(bg="yellow")
        self.root.attributes("-alpha", 0)  # Start with full transparency
        self.gradient_enabled = False  # Track if gradient is active
        self.bg_color = "yellow"  # Default background color

        # Make the window draggable
        self.root.overrideredirect(True)  
        self.root.bind("<B1-Motion>", self.move_window)
        self.root.bind("<Button-3>", self.close_window)

        # Frame for title bar
        self.title_bar = tk.Frame(root, bg="orange", relief="raised", bd=2, height=25)
        self.title_bar.pack(fill="x")

        # Buttons
        self.color_button = tk.Button(self.title_bar, text="🎨", command=self.choose_color, bg="orange", fg="black")
        self.color_button.pack(side="left", padx=5)

        self.gradient_button = tk.Button(self.title_bar, text="🌈", command=self.toggle_gradient, bg="orange", fg="black")
        self.gradient_button.pack(side="left", padx=5)

        self.minimize_button = tk.Button(self.title_bar, text="_", command=self.minimize, bg="orange", fg="black")
        self.minimize_button.pack(side="right", padx=5)

        self.close_button = tk.Button(self.title_bar, text="X", command=self.save_and_close, bg="orange", fg="black")
        self.close_button.pack(side="right", padx=5)

        # Gradient Background Canvas
        self.canvas = tk.Canvas(root, width=300, height=250, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Text Area (placed above the canvas)
        self.text_area = tk.Text(root, font=("Arial", 12), wrap="word", bg=self.bg_color)
        self.text_area.place(relx=0.5, rely=0.55, anchor="center", width=280, height=180)

        # Load saved notes
        self.load_note()

        # Save note on close
        self.root.protocol("WM_DELETE_WINDOW", self.save_and_close)

        # Bind the Map event (when window is restored)
        self.root.bind("<Map>", self.restore_window)

        # Apply fade-in effect
        self.fade_in(0)

    def move_window(self, event):
        self.root.geometry(f"+{event.x_root}+{event.y_root}")

    def close_window(self, event=None):
        self.root.destroy()

    def save_and_close(self):
        with open("note.txt", "w") as file:
            file.write(self.text_area.get("1.0", tk.END))
        self.root.destroy()

    def load_note(self):
        try:
            with open("note.txt", "r") as file:
                self.text_area.insert("1.0", file.read())
        except FileNotFoundError:
            pass

    def choose_color(self):
        """ Open color picker and set the chosen color as background. """
        color = colorchooser.askcolor()[1]
        if color:
            self.bg_color = color
            self.text_area.config(bg=color)
            self.root.configure(bg=color)
            self.gradient_enabled = False  # Disable gradient when a solid color is chosen
            self.canvas.delete("gradient")

    def toggle_gradient(self):
        """ Toggle gradient mode on or off. """
        if self.gradient_enabled:
            # Disable gradient and revert to solid color
            self.gradient_enabled = False
            self.text_area.config(bg=self.bg_color)
            self.root.configure(bg=self.bg_color)
            self.canvas.delete("gradient")
        else:
            # Enable gradient and let the user pick colors
            color1 = colorchooser.askcolor(title="Choose Start Color")[1]
            color2 = colorchooser.askcolor(title="Choose End Color")[1]
            if color1 and color2:
                self.gradient_enabled = True
                self.apply_gradient(color1, color2)

    def apply_gradient(self, color1, color2):
        """ Apply a gradient background from color1 to color2. """
        self.canvas.delete("gradient")  # Remove old gradient if any
        for i in range(250):  # Gradient from top to bottom
            color = self.interpolate_color(color1, color2, i / 250)
            self.canvas.create_line(0, i, 300, i, fill=color, tags="gradient")

    def interpolate_color(self, start_color, end_color, factor):
        """ Blend two colors based on a factor (0 to 1) """
        start_rgb = self.hex_to_rgb(start_color)
        end_rgb = self.hex_to_rgb(end_color)
        blended_rgb = tuple(int(start_rgb[i] + factor * (end_rgb[i] - start_rgb[i])) for i in range(3))
        return self.rgb_to_hex(blended_rgb)

    def hex_to_rgb(self, hex_color):
        """ Convert hex color (#RRGGBB) to an RGB tuple """
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb_tuple):
        """ Convert an RGB tuple to hex color (#RRGGBB) """
        return f"#{rgb_tuple[0]:02x}{rgb_tuple[1]:02x}{rgb_tuple[2]:02x}"

    def minimize(self):
        self.root.overrideredirect(False)  # Temporarily allow normal behavior
        self.root.iconify()  # Minimize window

    def restore_window(self, event=None):
        if self.root.state() == "normal":  # Only restore when actually reopened
            self.root.overrideredirect(True)  # Reapply override-redirect
            self.root.unbind("<Map>")  # Remove binding after restoring

    def fade_in(self, alpha):
        """ Gradually fade in the sticky note """
        if alpha < 1:
            self.root.attributes("-alpha", alpha)
            self.root.after(10, lambda: self.fade_in(alpha + 0.05))

# Run the Sticky Note
root = tk.Tk()
app = StickyNote(root)
root.mainloop()
