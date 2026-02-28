import cv2
import sys
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ================================================================
# БЛОК 1: Источник видео
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
            title="Выбери видеофайл",
            filetypes=[("Видео файлы", "*.mp4 *.avi *.mov *.mkv"),
                       ("Все файлы", "*.*")]
        )
        if path:
            source = path
            dialog.destroy()

    dialog = ctk.CTk()
    dialog.title("Выбор источника видео")
    dialog.geometry("320x250")
    dialog.resizable(False, False)

    ctk.CTkLabel(dialog, text="Выберите источник видео",
                 font=("Arial", 14)).pack(pady=15)
    camera_var = ctk.StringVar(value="0")
    ctk.CTkLabel(dialog, text="Номер камеры:").pack()
    ctk.CTkEntry(dialog, textvariable=camera_var, width=60).pack(pady=5)
    ctk.CTkButton(dialog, text="Использовать камеру", command=select_camera).pack(pady=5)
    ctk.CTkLabel(dialog, text="— или —").pack()
    ctk.CTkButton(dialog, text="Выбрать видеофайл...",
                  command=select_file,
                  fg_color="gray",
                  hover_color="#555555").pack(pady=5)
    dialog.mainloop()

    if source is None:
        sys.exit()

# ================================================================
# БЛОК 2: Главное окно, кнопки, видео-область
# ================================================================
root = ctk.CTk()
root.title("CV Homework")

def quit_app():
    root.quit()

btn_quit = ctk.CTkButton(root, text="Выход",
                         fg_color="red", hover_color="#cc0000",
                         command=quit_app)
btn_quit.pack(pady=10)

btn_clear = ctk.CTkButton(root, text="Сбросить точки (C)",
                          fg_color="gray", hover_color="#555555",
                          command=lambda: click_points.clear())
btn_clear.pack(pady=5)

video_label = ctk.CTkLabel(root, text="")
video_label.pack(padx=10, pady=10)

# ================================================================
# БЛОК 3: Точки кликов — хранение и обработка (ТЗ п.2 и п.3)
# ================================================================
click_points = []

def on_click(event):
    click_points.append((event.x, event.y))

video_label.bind('<Button-1>', on_click)

# ================================================================
# БЛОК 4: Захват видео через OpenCV
# ================================================================
cap = cv2.VideoCapture(source)

# ================================================================
# БЛОК 5: Обработка клавиатуры Q и C (ТЗ п.3 и п.4)
# ================================================================
def on_key(event):
    if event.char.lower() == 'q':
        root.quit()
    elif event.char.lower() == 'c':
        click_points.clear()

root.bind('<Key>', on_key)

# ================================================================
# БЛОК 6: Главный цикл обновления кадров
# ================================================================
def update_frame():
    ret, frame = cap.read()
    if not ret:
        root.quit()
        return

    # Рисование прямоугольников по точкам кликов
    for (x, y) in click_points:
        cv2.rectangle(frame,
                      (x - 20, y - 20),
                      (x + 20, y + 20),
                      (0, 255, 0), 2)

    # Конвертация OpenCV → CustomTkinter
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.configure(image=imgtk)
    video_label.image = imgtk

    root.after(30, update_frame)

# ================================================================
# БЛОК 7: Запуск
# ================================================================
update_frame()
root.mainloop()
cap.release()
