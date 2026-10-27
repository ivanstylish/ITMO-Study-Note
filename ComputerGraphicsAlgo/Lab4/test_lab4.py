"""Focused physical, persistence and real Tk event-loop checks."""
import json
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np
from PIL import Image
from lab4_spectrum.reconstruction import reconstruct
from lab4_spectrum.experiment import run, white_scene
from lab4_spectrum.output import save
from lab4_spectrum.core.color_conversion import spectrum_to_rgb
from lab4_spectrum.core.spectral import load_tables, normalize_spd


class Lab4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = run(replace(white_scene(), width_px=200))

    def test_textbook_basis_color_and_scale(self):
        tables = load_tables()
        original = normalize_spd(tables.d65)
        rgb = spectrum_to_rgb(original)
        recovered = reconstruct(rgb)
        self.assertTrue(np.all(recovered >= 0))
        np.testing.assert_allclose(spectrum_to_rgb(recovered), rgb, atol=1e-12)
        self.assertAlmostEqual(recovered @ tables.weights, .6295556600023777, places=10)
        # The prescribed linear method must retain input scale, not impose unit energy.
        np.testing.assert_allclose(reconstruct(2*rgb), 2*recovered, atol=1e-12)
        known = tables.cmf @ np.array([.001, .002, .003])
        np.testing.assert_allclose(reconstruct(spectrum_to_rgb(known)), known, atol=1e-12)
        self.assertGreater(np.linalg.norm(original-recovered), .001)

    def test_invalid_inputs(self):
        for rgb in ([np.nan, 0, 0], [np.inf, 0, 0], [1, 2], [-10, -10, -10], [0, 0, 0]):
            with self.assertRaises(ValueError):
                reconstruct(rgb)
        narrow = np.zeros(41)
        narrow[17] = 1
        # A valid physical color can lie outside the nonnegative cone of this fixed basis.
        with self.assertRaises(ValueError):
            reconstruct(spectrum_to_rgb(narrow))
        for scene in (replace(white_scene(), width_px=199),
                      replace(white_scene(), reflectance=(.5,)*41),
                      replace(white_scene(), width_mm=100)):
            with self.assertRaises(ValueError):
                run(scene)

    def test_physics_and_absolute_image(self):
        r = self.data['result']
        self.assertEqual(r['spectral'].shape, (200, 200, 41))
        np.testing.assert_allclose(r['spectral'] @ load_tables().weights, r['radiance'], atol=1e-11)
        np.testing.assert_allclose(683*r['xyz'][..., 1], r['luminance1'], atol=1e-9)
        for image in self.data['images'][1:]:
            np.testing.assert_array_equal(image, self.data['images'][0])
        self.assertEqual(len(r['control_points']), 3)
        self.assertTrue(all(p['visible'] for p in r['control_points']))
        # Independent on-axis geometry at the front pole, without the renderer helper.
        p = r['parameters']; point = p.center()+[0, 0, p.radius_mm]
        expected = 0
        for light in p.lights:
            delta = light.position()-point
            distance = np.linalg.norm(delta)
            direction = delta/distance
            axis = np.array(light.axis)/np.linalg.norm(light.axis)
            expected += light.intensity_w_sr*max(-axis@direction, 0)*max(direction[2], 0)/(np.pi*(distance/1000)**2)
        integral = self.data['spectrum_metrics'][0]['integral']
        self.assertAlmostEqual(r['control_points'][0]['radiance_w_m2_sr'], expected*integral, places=9)
        # Independent XYZ->photometry check at the pole proves the raw SPD was not normalized.
        from lab4_spectrum.core.color_conversion import CIE_RGB_TO_XYZ
        target_y = (CIE_RGB_TO_XYZ @ self.data['input_rgb'][0])[1]
        self.assertAlmostEqual(r['control_points'][0]['luminance_cd_m2'], 683*expected*target_y, places=8)

    def test_saved_files(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            save(self.data, directory)
            root = Path(directory)
            metadata = json.loads((root/'results.json').read_text(encoding='utf-8'))
            self.assertEqual(len(metadata['control_points']), 3)
            with np.load(root/'absolute_data.npz') as arrays:
                np.testing.assert_array_equal(arrays['spectral_A'], self.data['result']['spectral'])
            np.testing.assert_array_equal(np.array(Image.open(root/'image_A.png')), self.data['images'][0])
            self.assertEqual(len((root/'spectra_comparison.csv').read_text(encoding='utf-8-sig').splitlines()), 42)

    def test_gui_event_loop(self):
        import tkinter as tk
        from unittest.mock import patch
        from lab4_spectrum.gui import App
        root = tk.Tk()
        root.geometry('1320x850')
        app = App(root)
        try:
            root.update()
            app.add_light()
            self.assertEqual(len(app.lights), 3)
            app.delete_light()
            self.assertEqual(len(app.lights), 2)
            app.fields['width_px'].set('200')
            with patch('lab4_spectrum.gui.messagebox.showerror') as errors:
                app.compute()
                deadline = time.monotonic()+60
                while app.busy and time.monotonic()<deadline:
                    root.update()
                    time.sleep(.02)
                self.assertFalse(app.busy)
                self.assertIsNotNone(app.data)
                errors.assert_not_called()
            self.assertEqual(len(app.table.get_children()), 41)
            for tab in app.tabs.tabs():
                app.tabs.select(tab)
                root.update()
            with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory, patch('lab4_spectrum.gui.filedialog.askdirectory', return_value=directory):
                app.export()
                self.assertTrue((Path(directory)/'image_A.png').is_file())
        finally:
            app.after_cancel(app.poll_id)
            root.destroy()


if __name__ == '__main__':
    unittest.main(verbosity=2)
