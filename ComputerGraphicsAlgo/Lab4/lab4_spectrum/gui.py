"""The Lab 3 form/results layout, limited to Lab 4 inputs and outputs."""
import queue
import threading
import tkinter as tk
from dataclasses import replace
from tkinter import filedialog, messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .core.color_conversion import scene_rgb
from .experiment import run, white_scene
from .output import save, spectral_figure, summary


class App(ttk.Frame):
    def __init__(self, root):
        super().__init__(root, padding=10)
        self.pack(fill="both", expand=True)
        self.data = None
        self.busy = False
        self.completed = queue.SimpleQueue()
        self.scene = white_scene()
        self.lights = list(self.scene.lights)
        self.colors = list(scene_rgb(self.scene)[1])
        self.fields, self.light_fields = {}, {}
        self.selected = None
        self.status = tk.StringVar(value="Задайте параметры и нажмите «Рассчитать».")
        panes = ttk.Panedwindow(self, orient="horizontal")
        panes.pack(fill="both", expand=True)
        left, right = ttk.Frame(panes, width=370), ttk.Frame(panes)
        panes.add(left, weight=0)
        panes.add(right, weight=1)
        action_row = ttk.Frame(left, padding=4)
        action_row.pack(side="bottom", fill="x")
        canvas = tk.Canvas(left, width=365, highlightthickness=0)
        bar = ttk.Scrollbar(left, command=canvas.yview)
        canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        form = ttk.Frame(canvas, padding=4)
        window = canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window, width=e.width))
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        for title, fields in (
            ("Экран и сфера, мм", (("width_mm", "W"), ("height_mm", "H"), ("width_px", "Wres (Hres по W/H)"),
             ("center_x_mm", "xC"), ("center_y_mm", "yC"), ("center_z_mm", "zC"), ("radius_mm", "Радиус"))),
            ("Наблюдатель и экран", (("observer_z_mm", "zO, мм"), ("screen_z_mm", "z экрана, мм"),
             ("screen_distance_mm", "f, мм (необязательно)"),
             ("direction_x", "Направление dx"), ("direction_y", "dy"), ("direction_z", "dz")))):
            group = ttk.LabelFrame(form, text=title, padding=6)
            group.pack(fill="x", pady=4)
            for key, label in fields:
                value = self.scene.direction["xyz".index(key[-1])] if key.startswith("direction_") else getattr(self.scene, key)
                self.field(group, self.fields, key, label, "" if value is None else value)
        group = ttk.LabelFrame(form, text="Источники: абсолютный CIE RGB", padding=6)
        group.pack(fill="x", pady=4)
        self.source = ttk.Combobox(group, state="readonly")
        self.source.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.source.bind("<<ComboboxSelected>>", self.select_light)
        for key, label in (("x_mm", "xL, мм"), ("y_mm", "yL, мм"), ("z_mm", "zL, мм"),
            ("intensity_w_sr", "I₀ исходный, Вт/ср"), ("axis_x", "Ось ax"), ("axis_y", "ay"), ("axis_z", "az"),
            ("R", "R"), ("G", "G"), ("B", "B")):
            self.field(group, self.light_fields, key, label, 0)
        actions = ttk.Frame(group)
        actions.grid(row=11, column=0, columnspan=2)
        for label, action in (("Применить", self.commit_light), ("Добавить", self.add_light), ("Удалить", self.delete_light)):
            ttk.Button(actions, text=label, command=lambda f=action: self.guard(f)).pack(side="left")
        ttk.Label(form, text="Белая сфера: kd(λ)=1.\nСетка 380–780 нм, шаг 10 нм.", padding=5).pack(fill="x")
        self.compute_button = ttk.Button(action_row, text="Рассчитать", command=lambda: self.guard(self.compute))
        self.compute_button.pack(fill="x", pady=5)
        self.save_button = ttk.Button(action_row, text="Сохранить результаты…", command=lambda: self.guard(self.export))
        self.save_button.pack(fill="x")
        self.tabs = ttk.Notebook(right)
        self.tabs.pack(fill="both", expand=True)
        self.image_tab, self.spectra_tab, numbers = (ttk.Frame(self.tabs) for _ in range(3))
        for frame, name in ((self.image_tab, "Изображения A / 1 / 2"), (self.spectra_tab, "Спектрограммы и таблица"), (numbers, "Абсолютная яркость")):
            self.tabs.add(frame, text=name)
        self.numbers = tk.Text(numbers, wrap="word", font=("Consolas", 11), state="disabled")
        self.numbers.pack(fill="both", expand=True)
        self.table = ttk.Treeview(self.spectra_tab, columns=("nm", "original", "recovered", "error"), show="headings", height=7)
        for key, label in zip(self.table["columns"], ("λ, нм", "L1 исходный, 1/нм", "L1 восстановленный", "Разность")):
            self.table.heading(key, text=label)
            self.table.column(key, width=120)
        self.table.pack(side="bottom", fill="x")
        ttk.Label(self, textvariable=self.status, wraplength=1100, padding=4).pack(fill="x")
        self.plot_canvases = []
        self.refresh_sources(0)
        self.poll_id = self.after(80, self.poll)

    @staticmethod
    def field(parent, store, key, label, value):
        row = parent.grid_size()[1]
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        store[key] = tk.StringVar(value=str(value))
        ttk.Entry(parent, textvariable=store[key], width=19).grid(row=row, column=1, sticky="ew", pady=2)
        parent.columnconfigure(1, weight=1)

    def guard(self, action):
        try:
            action()
        except (ValueError, OSError, TypeError) as error:
            messagebox.showerror("Ошибка", str(error), parent=self)

    def refresh_sources(self, index):
        self.source.configure(values=[f"Источник {i+1}" for i in range(len(self.lights))])
        self.source.current(index)
        self.selected = None
        self.select_light()

    def select_light(self, event=None):
        index = self.source.current()
        if self.selected is not None:
            try:
                self.commit_light()
            except ValueError as error:
                self.source.current(self.selected)
                messagebox.showerror("Ошибка", str(error), parent=self)
                return
        self.selected = index
        light = self.lights[index]
        values = {k: getattr(light, k) for k in ("x_mm", "y_mm", "z_mm", "intensity_w_sr")}
        values.update(zip(("axis_x", "axis_y", "axis_z"), light.axis))
        values.update(zip("RGB", self.colors[index]))
        for key, value in values.items():
            self.light_fields[key].set(str(value))

    def commit_light(self):
        values = {k: float(v.get()) for k, v in self.light_fields.items()}
        if not np.all(np.isfinite(list(values.values()))):
            raise ValueError("Требуются конечные значения источника")
        self.lights[self.selected] = replace(self.lights[self.selected],
            **{k: values[k] for k in ("x_mm", "y_mm", "z_mm", "intensity_w_sr")},
            axis=tuple(values["axis_"+c] for c in "xyz"))
        self.colors[self.selected] = np.array([values[c] for c in "RGB"])

    def add_light(self):
        self.commit_light()
        self.lights.append(self.scene.lights[0])
        self.colors.append(scene_rgb(self.scene)[1][0].copy())
        self.refresh_sources(len(self.lights)-1)

    def delete_light(self):
        if len(self.lights) == 1:
            raise ValueError("Требуется хотя бы один источник")
        del self.lights[self.selected]
        del self.colors[self.selected]
        self.refresh_sources(0)

    def read_scene(self):
        self.commit_light()
        values = {k: float(v.get()) for k, v in self.fields.items()
                  if not k.startswith("direction_") and k != "screen_distance_mm"}
        distance = self.fields["screen_distance_mm"].get().strip()
        values["screen_distance_mm"] = float(distance) if distance else None
        values["width_px"] = int(self.fields["width_px"].get())
        return replace(self.scene, **values, lights=tuple(self.lights),
                       direction=tuple(float(self.fields["direction_"+c].get()) for c in "xyz"))

    def compute(self):
        if self.busy:
            return
        scene, colors = self.read_scene(), np.array(self.colors)
        self.busy = True
        self.compute_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        self.status.set("Вычисление…")
        def worker():
            try:
                self.completed.put((run(scene, colors), None))
            except Exception as error:
                self.completed.put((None, error))
        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        try:
            data, error = self.completed.get_nowait()
        except queue.Empty:
            pass
        else:
            self.busy = False
            self.compute_button.configure(state="normal")
            self.save_button.configure(state="normal")
            if error:
                self.status.set(str(error))
                messagebox.showerror("Ошибка расчёта", str(error), parent=self)
            else:
                self.data = data
                self.show_results()
                self.status.set("Готово. На экране — рассчитанная сцена. Экспорт сохраняет именно этот результат.")
        self.poll_id = self.after(80, self.poll)

    def show_results(self):
        for canvas in self.plot_canvases:
            canvas.get_tk_widget().destroy()
        figure = Figure(figsize=(10, 5), layout="constrained")
        for ax, image, name in zip(figure.subplots(1, 3), self.data["images"], ("image_A", "image_1 (recomputed)", "image_2 (recomputed)")):
            ax.imshow(image)
            ax.set_title(name, fontsize=10)
            ax.set_axis_off()
        self.plot_canvases = []
        for parent, fig in ((self.image_tab, figure), (self.spectra_tab, spectral_figure(self.data))):
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()
            self.plot_canvases.append(canvas)
        self.table.delete(*self.table.get_children())
        for w, original, recovered in zip(range(380, 781, 10), self.data["original_spd"][0], self.data["recovered"][0]):
            self.table.insert("", "end", values=(w, f"{original:.8g}", f"{recovered:.8g}", f"{recovered-original:.5g}"))
        self.numbers.configure(state="normal")
        self.numbers.delete("1.0", "end")
        self.numbers.insert("1.0", summary(self.data))
        self.numbers.configure(state="disabled")

    def export(self):
        if self.data is None or self.busy:
            raise ValueError("Сначала выполните расчёт")
        directory = filedialog.askdirectory(parent=self)
        if directory:
            save(self.data, directory)
            self.status.set("Результаты сохранены: " + directory)


def launch():
    root = tk.Tk()
    root.title("Лабораторная работа 4 — RGB → спектр")
    root.geometry("1320x850")
    root.minsize(1000, 650)
    App(root)
    root.mainloop()
