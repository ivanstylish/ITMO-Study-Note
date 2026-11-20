"""Tkinter viewer for the Lab 5 lighting comparison."""
import json
from copy import deepcopy
from pathlib import Path
from queue import Empty, SimpleQueue
from tempfile import mkdtemp
from threading import Event, Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from PIL import Image, ImageTk

from experiment import RESULTS_DIR, SCENE_FILE, Settings, load_scene, make_images, run, save
from scene import build_scene


class RenderCancelled(Exception):
    # 进度回调在批次结束时检查取消请求，计划内中止走单独的消息分支。
    pass


class Preview(tk.Canvas):
    def __init__(self, parent, on_pixel):
        super().__init__(parent, width=1, height=1, background="#161d28", highlightthickness=0)
        self.on_pixel = on_pixel
        self.image = None
        self.bounds = None
        self.redraw = None
        self.pixel = None
        self.image_item = self.create_image(0, 0, anchor="nw")
        self.marker = self.create_oval(0, 0, 0, 0, outline="#ffe384", width=2, state="hidden")
        self.bind("<Configure>", self.schedule_draw)
        self.bind("<Motion>", self.pick)
        self.bind("<Leave>", lambda event: self.on_pixel(None))

    def show(self, image):
        self.image = image
        self.bounds = None
        self.schedule_draw()

    def schedule_draw(self, event=None):
        if self.redraw is not None:
            self.after_cancel(self.redraw)
        self.redraw = self.after_idle(self.draw)

    def draw(self):
        self.redraw = None
        if self.image is None:
            return
        width, height = self.winfo_width(), self.winfo_height()
        native_width, native_height = self.image.size
        # 预览等比缩小，记录图像实际边界供取点和双图标记使用。
        scale = min(width / native_width, height / native_height, 1)
        w, h = max(1, round(native_width * scale)), max(1, round(native_height * scale))
        left, top = (width - w) // 2, (height - h) // 2
        self.bounds = left, top, w, h
        resized = self.image.resize((w, h), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized, master=self)
        self.coords(self.image_item, left, top)
        self.itemconfigure(self.image_item, image=self.photo)
        self.highlight(self.pixel)

    def pick(self, event):
        if self.bounds is None:
            return
        left, top, width, height = self.bounds
        x, y = event.x - left, event.y - top
        # 从画布反算原图的整数列和行，图像外的留边没有对应像素。
        pixel = (x * self.image.width // width, y * self.image.height // height)
        self.on_pixel(pixel if 0 <= x < width and 0 <= y < height else None)

    def highlight(self, pixel):
        self.pixel = pixel
        if pixel is None or self.bounds is None:
            self.itemconfigure(self.marker, state="hidden")
            return
        left, top, width, height = self.bounds
        x = left + (pixel[0] + 0.5) * width / self.image.width
        y = top + (pixel[1] + 0.5) * height / self.image.height
        self.coords(self.marker, x - 6, y - 6, x + 6, y + 6)
        self.itemconfigure(self.marker, state="normal")


class App(ttk.Frame):
    def __init__(self, root, scene_path, config, settings):
        super().__init__(root, padding=18)
        self.pack(fill="both", expand=True)
        self.config_data = config
        self.light_index = None
        self.data = self.summary = None
        self.exporting = False
        self.messages = SimpleQueue()
        self.cancel_requested = Event()
        self.selected_scene = tk.StringVar()
        self.metadata = tk.StringVar(value="Изображения появятся после расчёта")
        self.pixel_value = tk.StringVar()
        self.status = tk.StringVar()
        self.progress = tk.IntVar(value=0)
        self.render_fields = {}
        self.light_fields = {}

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        header = ttk.Frame(self)
        header.grid(row=0, columnspan=2, sticky="ew", pady=(0, 14))
        ttk.Label(header, text="Трассировка путей", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Результат отчёта", command=self.show_report).pack(side="right")

        controls = ttk.Frame(self)
        controls.grid(row=1, column=0, sticky="nsw", padx=(0, 16))
        self.build_controls(controls, settings)

        comparison = ttk.Frame(self)
        comparison.grid(row=1, column=1, sticky="nsew")
        comparison.columnconfigure((0, 1), weight=1, uniform="image")
        comparison.rowconfigure(2, weight=1)
        ttk.Label(comparison, textvariable=self.metadata).grid(row=0, columnspan=2, sticky="w", pady=(0, 12))
        self.previews = []
        for column, title in enumerate(("Прямое освещение", "Прямое и вторичное освещение")):
            gap = (0, 5) if column == 0 else (5, 0)
            ttk.Label(comparison, text=title, style="Heading.TLabel").grid(
                row=1, column=column, sticky="w", padx=gap, pady=(0, 6))
            preview = Preview(comparison, self.inspect_pixel)
            preview.grid(row=2, column=column, sticky="nsew", padx=gap)
            self.previews.append(preview)
        ttk.Label(comparison, textvariable=self.pixel_value).grid(
            row=3, columnspan=2, sticky="w", pady=(8, 0))

        footer = ttk.Frame(self)
        footer.grid(row=2, columnspan=2, sticky="ew", pady=(15, 0))
        ttk.Progressbar(footer, maximum=100, variable=self.progress, length=145).pack(side="left")
        ttk.Label(footer, textvariable=self.status).pack(side="left", padx=10)

        self.set_scene(scene_path, config)
        self.inspect_pixel(None)
        self.show_report()
        self.after(65, self.poll)
        root.protocol("WM_DELETE_WINDOW", self.close)

    def build_controls(self, parent, settings):
        scene_panel = ttk.LabelFrame(parent, text="Сцена", padding=8)
        scene_panel.pack(fill="x", pady=(0, 8))
        ttk.Label(scene_panel, textvariable=self.selected_scene, width=30).pack(anchor="w")
        scene_actions = ttk.Frame(scene_panel)
        scene_actions.pack(fill="x", pady=(6, 0))
        ttk.Button(scene_actions, text="Открыть JSON…", command=self.open_scene).pack(side="left", padx=(0, 4))
        ttk.Button(scene_actions, text="Сбросить", command=self.reset_scene).pack(side="left")

        light_panel = ttk.LabelFrame(parent, text="Источники света", padding=8)
        light_panel.pack(fill="x", pady=(0, 8))
        self.light_choice = ttk.Combobox(light_panel, state="readonly", width=20)
        self.light_choice.grid(row=0, columnspan=4, sticky="ew", pady=(0, 5))
        self.light_choice.bind("<<ComboboxSelected>>", self.choose_light)
        self.light_entries = []
        for row, (key, label, fields) in enumerate((
            ("position", "Положение, м", "XYZ"), ("intensity", "Сила, Вт/ср", "RGB")
        )):
            ttk.Label(light_panel, text=label).grid(row=1 + row * 2, column=0, rowspan=2, sticky="w", padx=(0, 6))
            variables = []
            for column, channel in enumerate(fields, start=1):
                ttk.Label(light_panel, text=channel).grid(row=1 + row * 2, column=column)
                variable = tk.StringVar()
                entry = ttk.Entry(light_panel, textvariable=variable, width=6, justify="center")
                entry.grid(row=2 + row * 2, column=column, padx=2)
                variables.append(variable)
                self.light_entries.append(entry)
            self.light_fields[key] = variables

        form = ttk.LabelFrame(parent, text="Расчёт", padding=8)
        form.pack(fill="x", pady=(0, 8))
        form.columnconfigure(1, weight=1)
        for row, (key, label) in enumerate((
            ("size", "Размер кадра, пикс."), ("samples", "Путей на пиксель"),
            ("depth", "Глубина"), ("white", "Уровень белого"),
        )):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=2)
            variable = tk.StringVar(value=str(getattr(settings, key)))
            ttk.Entry(form, textvariable=variable, width=8).grid(row=row, column=1, sticky="e")
            self.render_fields[key] = variable
        self.seed = settings.seed
        ttk.Button(form, text="Быстрый режим · 1 путь", command=self.fast_mode).grid(
            row=4, columnspan=2, sticky="ew", pady=(6, 0))

        self.run_button = ttk.Button(parent, text="Рассчитать", style="Primary.TButton", command=self.start_render)
        self.run_button.pack(fill="x", pady=(0, 4))
        actions = ttk.Frame(parent)
        actions.pack(fill="x")
        self.cancel_button = ttk.Button(actions, text="Отменить", state="disabled", command=self.cancel)
        self.cancel_button.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.save_button = ttk.Button(actions, text="Сохранить…", state="disabled", command=self.export)
        self.save_button.pack(side="left", fill="x", expand=True)

    def set_scene(self, path, config):
        self.config_data = config
        self.selected_scene.set(path.name)
        names = [f"Источник {i + 1}" for i in range(len(config["lights"]))]
        self.light_choice.configure(values=names, state="readonly" if names else "disabled")
        self.light_index = None
        if names:
            self.light_choice.current(0)
            self.choose_light()
        else:
            self.light_choice.set("Нет источников")
            for variables in self.light_fields.values():
                for variable in variables:
                    variable.set("")
        for entry in self.light_entries:
            entry.configure(state="normal" if names else "disabled")

    def read_light(self):
        edited = {}
        for key, variables in self.light_fields.items():
            try:
                components = [float(variable.get().replace(",", ".")) for variable in variables]
            except ValueError:
                raise ValueError("Координаты и интенсивности источника должны быть числами.") from None
            if not np.isfinite(components).all() or (key == "intensity" and min(components) < 0):
                raise ValueError("Координаты должны быть конечными, интенсивности — конечными и неотрицательными.")
            edited[key] = components
        return edited

    def choose_light(self, event=None):
        index = self.light_choice.current()
        if self.light_index is not None:
            try:
                self.config_data["lights"][self.light_index].update(self.read_light())
            except ValueError as error:
                self.light_choice.current(self.light_index)
                self.error(error)
                return
        self.light_index = index
        light = self.config_data["lights"][index]
        for key, variables in self.light_fields.items():
            for variable, value in zip(variables, light[key]):
                variable.set(str(value))

    def open_scene(self):
        filename = filedialog.askopenfilename(parent=self, filetypes=[("Сцена JSON", "*.json")])
        if filename:
            self.change_scene(Path(filename))

    def reset_scene(self):
        self.change_scene(SCENE_FILE)

    def change_scene(self, path):
        try:
            config, _ = load_scene(path)
            self.set_scene(path, config)
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
            self.error(error)

    def fast_mode(self):
        # 快速模式只填写待计算参数，当前两张图继续使用自己的结果参数。
        for key, value in (("size", 500), ("samples", 1), ("depth", 2)):
            self.render_fields[key].set(str(value))

    def show_report(self):
        # 从报告的线性数据和元信息生成对照图，参数来自该次计算的 results.json。
        try:
            summary = json.loads((RESULTS_DIR / "results.json").read_text(encoding="utf-8"))
            with np.load(RESULTS_DIR / "radiance.npz") as archive:
                data = {key: archive[key] for key in ("direct", "indirect", "full")}
            width, height = summary["size_px"]
            if any(image.shape != (height, width, 3) for image in data.values()):
                raise ValueError("Размеры массивов отчёта не совпадают.")
            self.show(data, summary, "Результат отчёта")
            self.status.set("Загружены изображения отчёта")
        except (OSError, ValueError, KeyError) as error:
            self.status.set(f"Результат отчёта недоступен · {error}")

    def show(self, data, summary, label):
        images = make_images(data, summary)
        self.data, self.summary = data, summary
        for preview, image in zip(self.previews, images):
            preview.show(image)
        self.inspect_pixel(None)
        width, height = summary["size_px"]
        samples, depth, white = summary["samples"], summary["depth"], summary["white"]
        self.metadata.set(f"{label}   ·   {width} × {height}   ·   путей/пикс. {samples}   ·   глубина {depth}   ·   белый {white:g}")
        if not self.exporting:
            self.save_button.configure(state="normal")

    def inspect_pixel(self, pixel):
        for preview in self.previews:
            preview.highlight(pixel)
        if pixel is None:
            self.pixel_value.set("Наведите указатель на изображение, чтобы сравнить значения RGB.\n ")
            return
        x, y = pixel
        # 读取同一原图像素 [行, 列] 的绝对值，用于复核报告 §6 的直接、间接与总贡献。
        values = [" / ".join(f"{channel:.4g}" for channel in self.data[key][y, x])
                  for key in ("direct", "indirect", "full")]
        self.pixel_value.set(f"x {x}, y {y}   ·   RGB, Вт/(м²·ср)\n"
                             f"Прямой  {values[0]}    Вторичный  {values[1]}    Сумма  {values[2]}")

    def error(self, error):
        messagebox.showerror("Лабораторная работа № 5", str(error), parent=self)

    def start_render(self):
        try:
            fields = {key: value.get() for key, value in self.render_fields.items()}
            try:
                numeric = {key: int(fields[key]) for key in ("size", "samples", "depth")}
                white = float(fields["white"].replace(",", "."))
            except ValueError:
                raise ValueError("Введите целые размер, число путей и глубину, а также числовой уровень белого.") from None
            settings = Settings(**numeric, seed=self.seed, white=white)
            # 对场景取快照，渲染线程使用启动时的参数，后续界面输入留给下一次计算。
            config = deepcopy(self.config_data)
            if self.light_index is not None:
                config["lights"][self.light_index].update(self.read_light())
            scene = build_scene(config)
        except (ValueError, KeyError, TypeError) as error:
            self.error(error)
            return

        self.cancel_requested.clear()
        self.progress.set(0)
        self.status.set("Трассировка путей…")
        self.run_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")

        def work():
            previous = -1

            def progress(fraction):
                nonlocal previous
                if self.cancel_requested.is_set():
                    raise RenderCancelled
                percent = int(fraction * 100)
                if percent != previous:
                    self.messages.put(("progress", percent))
                    previous = percent

            try:
                self.messages.put(("rendered", run(config, scene, settings, progress)))
            except RenderCancelled:
                self.messages.put(("cancelled", None))
            except Exception as error:
                self.messages.put(("render_error", error))

        Thread(target=work, daemon=True).start()

    def cancel(self):
        self.cancel_requested.set()
        self.cancel_button.configure(state="disabled")
        self.status.set("Остановка расчёта…")

    def export(self):
        destination = filedialog.askdirectory(parent=self, title="Выберите папку для экспорта")
        if not destination:
            return
        data, summary = self.data, self.summary
        self.exporting = True
        self.save_button.configure(state="disabled")
        self.status.set("Сохранение результатов…")

        def work():
            try:
                folder = Path(mkdtemp(prefix="lab5-", dir=destination))
                save(folder, data, summary)
                self.messages.put(("saved", folder))
            except Exception as error:
                self.messages.put(("save_error", error))

        Thread(target=work, daemon=True).start()

    def poll(self):
        # Tk 主线程消费后台线程的消息，负责更新进度、预览和错误状态。
        while True:
            try:
                event, payload = self.messages.get_nowait()
            except Empty:
                break
            if event == "progress":
                self.progress.set(payload)
                continue
            if event in ("saved", "save_error"):
                self.exporting = False
                self.save_button.configure(state="normal")
                if event == "saved":
                    self.status.set(f"Сохранено · {payload}")
                else:
                    self.status.set("Ошибка сохранения")
                    self.error(payload)
                continue
            self.run_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            if event == "rendered" and not self.cancel_requested.is_set():
                self.show(*payload, "Новый расчёт")
                self.status.set("Расчёт завершён")
            elif event == "render_error":
                self.status.set("Ошибка расчёта")
                self.error(payload)
            else:
                self.progress.set(0)
                self.status.set("Расчёт отменён")
        self.after(65, self.poll)

    def close(self):
        self.cancel_requested.set()
        self.winfo_toplevel().destroy()


def launch(scene_path=SCENE_FILE, config=None, settings=None):
    if config is None:
        config, _ = load_scene(scene_path)
    root = tk.Tk()
    root.title("ЛР № 5 · Алгоритмы компьютерной графики")
    root.geometry("1150x690")
    root.minsize(940, 670)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"), foreground="#182943")
    style.configure("Heading.TLabel", font=("Segoe UI", 11, "bold"))
    style.configure("Primary.TButton", padding=8, foreground="white", background="#245d9f")
    style.map("Primary.TButton", background=[("disabled", "#65758a"), ("active", "#194d88")])
    App(root, scene_path, config, settings or Settings())
    root.mainloop()


if __name__ == "__main__":
    launch()
