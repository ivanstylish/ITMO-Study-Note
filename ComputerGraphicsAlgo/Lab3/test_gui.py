"""Integration checks for the real Tk/Matplotlib interface, using 200 px scenes.

Run on a machine with Tk display support: python test_gui.py
The numerical renderer is executed rather than replaced with a fake.
"""
from dataclasses import asdict, replace
from pathlib import Path
import csv
import io
import json
import threading
import time
import tempfile
import unittest
import tkinter as tk
from tkinter import ttk
from unittest.mock import patch

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image

from lab3_color_sphere import gui
from lab3_color_sphere.spectral import default_parameters, spectra_csv

BASE = Path(__file__).resolve().parent


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calls, cls.dialog_errors, cls.callback_errors = [], [], []
        cls.original_calculate = gui.calculate
        cls.main_thread = threading.get_ident()

        def counted(scene):
            cls.calls.append((scene, threading.get_ident()))
            return cls.original_calculate(scene)

        cls.patches = [
            patch.object(gui, 'calculate', counted),
            patch.object(gui.messagebox, 'showerror', lambda title, body: cls.dialog_errors.append(str(body))),
            patch.object(gui.messagebox, 'showinfo', lambda *args, **kwargs: None),
        ]
        for item in cls.patches:
            item.start()
        cls.root = tk.Tk()
        cls.root.geometry('1280x900')
        cls.root.withdraw()
        cls.root.report_callback_exception = lambda *args: cls.callback_errors.append(str(args))
        cls.app = gui.SphereApp(cls.root, replace(default_parameters('white'), width_px=200))
        cls.root.update()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        for item in reversed(cls.patches):
            item.stop()

    def setUp(self):
        self.app.set_scene(replace(default_parameters('white'), width_px=200))
        self.dialog_errors.clear()
        self.root.update()

    def events(self, seconds=.12):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.root.update()
            time.sleep(.005)

    def compute(self, case=None):
        if case is not None:
            self.app.set_scene(replace(default_parameters(case), width_px=200))
        began = len(self.calls)
        self.app.compute()
        deadline = time.monotonic() + 30
        while self.app.busy and time.monotonic() < deadline:
            self.root.update()
            time.sleep(.005)
        self.events(.05)
        self.assertFalse(self.app.busy, 'Calculation failed to finish')
        self.assertFalse(self.dialog_errors, self.dialog_errors)
        self.assertFalse(self.callback_errors, self.callback_errors)
        self.assertEqual(len(self.calls) - began, 1)
        self.assertTrue(all(thread_id != self.main_thread for _, thread_id in self.calls[began:]))

    def test_01_grouped_forms_and_matplotlib_canvas(self):
        """Scene fields and result canvases exist as normal Tk controls."""
        labels = [w.cget('text') for w in descendants(self.app) if isinstance(w, ttk.LabelFrame)]
        self.assertEqual(len(labels), 4)
        self.assertNotIn('Условия освещения', labels)
        self.assertFalse(hasattr(self.app, 'mode_combo'))
        self.assertFalse(hasattr(self.app, 'set_mode'))
        self.assertGreaterEqual(len(self.app.variables), 13)
        self.assertIsInstance(self.app.result_tabs, ttk.Notebook)
        for canvas in (self.app.rgb_canvas, self.app.gray_canvas, self.app.spectra_canvas):
            self.assertIsInstance(canvas, FigureCanvasTkAgg)

    def test_02_typing_and_spectrum_selection_do_not_render(self):
        """Keystrokes and spectrum selection do not execute spectral integration."""
        began = len(self.calls)
        self.app.variables['width_mm'].set('1400')
        self.app.variables['height_mm'].set('1400')
        self.app.light_spectrum.set('Красный')
        self.events()
        self.assertEqual(len(self.calls), began)

    def test_13_single_condition_exports_images_without_nested_case_folder(self):
        """Both single-condition saves contain usable RGB and grayscale images."""
        for case in ('white', 'colored'):
            with self.subTest(case=case):
                self.compute(case)
                began = len(self.calls)
                with tempfile.TemporaryDirectory(prefix='gui-single-', dir=BASE) as directory:
                    self.app.export_results(directory)
                    folder = Path(directory)
                    self.assertFalse((folder/case).exists())
                    self.assertEqual(len(list(folder.iterdir())), 7)
                    for index in (1, 2):
                        with Image.open(folder/f'image_{index}.png') as image:
                            self.assertEqual(image.size, (200, 200))
                            self.assertEqual(image.mode, 'RGB')
                        with Image.open(folder/f'image_{index}_gray.png') as image:
                            self.assertEqual(image.size, (200, 200))
                            self.assertEqual(image.mode, 'L')
                self.assertEqual(len(self.calls), began)

    def test_03_white_calculates_two_independent_images(self):
        """D65 two-path equivalence is preserved through the GUI calculation."""
        self.compute('white')
        result = self.app.results['white']
        self.assertEqual(result['spectral'].shape, (200, 200, 41))
        self.assertIsNot(result['rgb1'], result['rgb2'])
        np.testing.assert_allclose(result['rgb1'], result['rgb2'], rtol=3e-13, atol=2e-14)
        np.testing.assert_array_equal(result['images'][0], result['images'][1])
        self.assertEqual(sum(len(ax.images) for ax in self.app.rgb_figure.axes), 2)

    def test_04_colored_paths_keep_their_measurable_difference(self):
        """Colored output contains the real difference between the two paths."""
        self.compute('colored')
        result = self.app.results['colored']
        self.assertGreater(result['comparison']['monitor_mae_8bit'], .1)
        self.assertGreater(np.max(np.abs(result['rgb1'] - result['rgb2'])), .1)
        self.assertEqual(sum(len(ax.images) for ax in self.app.rgb_figure.axes), 2)

    def test_05_custom_spectra_are_calculated_without_preset_replacement(self):
        """Compute uses exactly the user's material, lights and geometry."""
        source = default_parameters('colored')
        scene = replace(source, width_px=200, radius_mm=300,
                        reflectance=tuple(np.linspace(.1, .8, 41)),
                        lights=(replace(source.lights[0], x_mm=-500,
                                        spectrum=tuple(np.linspace(.2, 1.1, 41))),))
        self.app.set_scene(scene)
        self.compute()
        self.assertEqual(len(self.app.results), 1)
        result = next(iter(self.app.results.values()))
        self.assertEqual(asdict(result['parameters']), asdict(scene))
        self.assertEqual(sum(len(ax.images) for ax in self.app.rgb_figure.axes), 2)
        self.assertEqual(sum(len(ax.images) for ax in self.app.gray_figure.axes), 2)

    def test_06_result_views_refresh_cached_data_without_calculation(self):
        """RGB, gray, curves and sample values are views of one cached result."""
        self.compute('colored')
        began = len(self.calls)
        for tab in self.app.result_tabs.tabs():
            self.app.result_tabs.select(tab)
            self.events(.03)
        self.app.refresh_results()
        self.events(.03)
        self.assertEqual(len(self.calls), began)
        self.assertTrue(any(ax.lines for ax in self.app.spectra_figure.axes))
        self.assertEqual(sum(len(ax.images) for ax in self.app.gray_figure.axes), 2)

    def test_07_three_sample_points_have_absolute_numeric_values(self):
        """The numeric view shows all three directly calculated control points."""
        self.compute('colored')
        rows = [self.app.points_tree.item(item, 'values') for item in self.app.points_tree.get_children()]
        self.assertEqual(len(rows), 3)
        flattened = ' '.join(' '.join(map(str, row)) for row in rows)
        for point in self.app.results['colored']['control_points']:
            self.assertIn(point['name'], flattened)
            self.assertGreater(point['radiance_w_m2_sr'], 0)
            expected = point['radiance_w_m2_sr']
            numeric = []
            for row in rows:
                if point['name'] in row:
                    for value in row:
                        try:
                            numeric.append(float(str(value).replace(',', '.')))
                        except ValueError:
                            pass
            self.assertTrue(any(abs(value - expected) < 1e-4 for value in numeric), (expected, rows))

    def test_08_invalid_input_is_reported_before_expensive_calculation(self):
        """Invalid form input triggers validation without starting the renderer."""
        began = len(self.calls)
        self.app.variables['radius_mm'].set('-1')
        self.app.compute()
        self.events()
        self.assertFalse(self.app.busy)
        self.assertEqual(len(self.calls), began)
        self.assertTrue(self.dialog_errors)

    def test_09_json_roundtrip_keeps_custom_spectra_and_geometry(self):
        """JSON saving and loading preserve arbitrary user material and sources."""
        source = default_parameters('colored')
        p = replace(source, width_px=200, reflectance=tuple(np.linspace(.1, .9, 41)),
                    lights=(replace(source.lights[0], x_mm=-500,
                                    spectrum=tuple(np.linspace(.2, 1.1, 41))),))
        self.app.set_scene(p)
        with tempfile.TemporaryDirectory(prefix='gui-json-', dir=BASE) as directory:
            path = Path(directory)/'scene.json'
            self.app.save_json(path)
            saved = json.loads(path.read_text(encoding='utf-8-sig'))
            self.app.set_scene(replace(default_parameters('white'), width_px=200))
            self.app.load_json(path)
            restored = self.app.read_scene()
        self.assertEqual(json.loads(json.dumps(asdict(restored))), saved)
        np.testing.assert_array_equal(restored.reflectance, p.reflectance)
        np.testing.assert_array_equal(restored.lights[0].spectrum, p.lights[0].spectrum)

    def test_10_advanced_json_and_csv_editors_update_normal_forms(self):
        """Advanced text inputs still feed the same validated scene model."""
        p = replace(default_parameters('colored'), width_px=200, radius_mm=300)
        self.app.json_text.delete('1.0', 'end')
        self.app.json_text.insert('1.0', json.dumps(asdict(p)))
        self.app.apply_json()
        self.assertEqual(float(self.app.variables['radius_mm'].get()), 300)
        rows = list(csv.DictReader(io.StringIO(spectra_csv(p))))
        for row in rows:
            row['reflectance'] = '.25'
        text = io.StringIO()
        writer = csv.DictWriter(text, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
        self.app.apply_spectra(text.getvalue())
        np.testing.assert_array_equal(self.app.read_scene().reflectance, [.25]*41)

    def test_11_export_preserves_absolute_arrays(self):
        """Both spectra settings export the calculated full physical arrays."""
        for case in ('white', 'colored'):
            with self.subTest(case=case):
                self.compute(case)
                began = len(self.calls)
                with tempfile.TemporaryDirectory(prefix='gui-export-', dir=BASE) as directory:
                    self.app.export_results(directory)
                    folder = Path(directory)
                    self.assertEqual(len(list(folder.iterdir())), 7)
                    with np.load(folder/'radiance_data.npz', allow_pickle=False) as saved:
                        self.assertEqual(saved['spectral_radiance'].shape, (200, 200, 41))
                        np.testing.assert_array_equal(saved['rgb1'], self.app.results[case]['rgb1'])
                        np.testing.assert_array_equal(saved['rgb2'], self.app.results[case]['rgb2'])
                    data = json.loads((folder/'results.json').read_text(encoding='utf-8'))
                    self.assertEqual(len(data['control_points']), 3)
                self.assertEqual(len(self.calls), began, 'Export must not recompute')

    def test_12_light_add_delete_and_negative_z_edits_are_committed(self):
        """The selected light can be edited, added and removed without rendering."""
        began = len(self.calls)
        initial_count = len(self.app.lights)
        self.app.add_light()
        self.assertEqual(len(self.app.lights), initial_count + 1)
        self.assertEqual(self.app.selected_light, initial_count)
        self.app.light_variables['z_mm'].set('-1700.25')
        self.app.light_variables['axis_z'].set('1')
        self.app.light_variables['intensity_w_sr'].set('3.125')
        scene = self.app.read_scene()
        self.assertEqual(scene.lights[-1].z_mm, -1700.25)
        self.assertEqual(scene.lights[-1].intensity_w_sr, 3.125)
        self.assertEqual(scene.lights[-1].axis[2], 1)
        self.app.lights_tree.selection_set('0')
        self.app._select_light()
        self.assertEqual(self.app.selected_light, 0)
        self.assertEqual(self.app.lights[-1].z_mm, -1700.25)
        while len(self.app.lights) > 1:
            self.app.delete_light()
        with self.assertRaises(ValueError):
            self.app.delete_light()
        self.events()
        self.assertEqual(len(self.calls), began)


if __name__ == '__main__':
    started = time.perf_counter()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GuiTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    record = dict(tests_run=result.testsRun, successful=result.wasSuccessful(),
                  failures=[str(test) + '\n' + trace for test, trace in result.failures],
                  errors=[str(test) + '\n' + trace for test, trace in result.errors],
                  elapsed_seconds=round(time.perf_counter()-started, 3),
                  scope='Real hidden Tk event loop and FigureCanvasTkAgg, actual 200 px spectral calculations')
    (BASE/'gui_validation.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
