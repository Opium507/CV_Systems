import cv2
import sys
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ================================================================
# BLOCK 1: Video source (command line argument OR dialog)
# ================================================================
source = None

if len(sys.argv) > 1:
    arg = sys.argv[1]
    try:
        source = int(arg)
    except ValueError:
        source = arg
else:
    def select_camera():
        global source
        source = int(camera_var.get())
        dialog.destroy()

    def select_file():
        global source
        path = filedialog.askopenfilename(
            title="Select video file",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"),
                       ("All files", "*.*")]
        )
        if path:
            source = path
            dialog.destroy()

    dialog = ctk.CTk()
    dialog.title("Select video source")
    dialog.geometry("320x200")
    dialog.resizable(False, False)

    ctk.CTkLabel(dialog, text="Select video source",
                 font=("Arial", 14)).pack(pady=15)
    camera_var = ctk.StringVar(value="0")
    ctk.CTkLabel(dialog, text="Camera number:").pack()
    ctk.CTkEntry(dialog, textvariable=camera_var, width=60).pack(pady=5)
    ctk.CTkButton(dialog, text="Use camera",
                  command=select_camera).pack(pady=5)
    ctk.CTkLabel(dialog, text="-- or --").pack()
    ctk.CTkButton(dialog, text="Select video file...",
                  command=select_file,
                  fg_color="gray",
                  hover_color="#555555").pack(pady=5)
    dialog.mainloop()

    if source is None:
        sys.exit()

# ================================================================
# BLOCK 2: Main window, buttons, video area
# ================================================================
root = ctk.CTk()
root.title("CV Homework")

def quit_app():
    root.quit()

btn_quit = ctk.CTkButton(root, text="Exit",
                         fg_color="red", hover_color="#cc0000",
                         command=quit_app)
btn_quit.pack(pady=10)

btn_clear = ctk.CTkButton(root, text="Clear points (C)",
                          fg_color="gray", hover_color="#555555",
                          command=lambda: click_points.clear())
btn_clear.pack(pady=5)

video_label = ctk.CTkLabel(root, text="")
video_label.pack(padx=10, pady=10)

# ================================================================
# BLOCK 3: Click points - storage and handling
# ================================================================
click_points = []

def on_click(event):
    click_points.append((event.x, event.y))

video_label.bind('<Button-1>', on_click)

# ================================================================
# BLOCK 4: Video capture via OpenCV
# ================================================================
cap = cv2.VideoCapture(source)
if not cap.isOpened():
    print("Error: could not open source:", source)
    sys.exit()

# ================================================================
# BLOCK 5: Keyboard handling - Q and C
# ================================================================
def on_key(event):
    if event.char.lower() == 'q':
        root.quit()
    elif event.char.lower() == 'c':
        click_points.clear()

root.bind('<Key>', on_key)

# ================================================================
# BLOCK 6: Main frame update loop
# ================================================================
def update_frame():
    ret, frame = cap.read()
    if not ret:
        root.quit()
        return

    # Draw rectangles at click points
    for (x, y) in click_points:
        cv2.rectangle(frame,
                      (x - 20, y - 20),
                      (x + 20, y + 20),
                      (0, 255, 0), 2)

    # Convert OpenCV frame -> CustomTkinter
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.configure(image=imgtk)
    video_label.image = imgtk  # keep reference to prevent GC

    root.after(30, update_frame)

# ================================================================
# BLOCK 7: Launch
# ================================================================
update_frame()
root.mainloop()
cap.release()
