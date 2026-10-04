"""Independent geometry, physical scaling, validation and export checks."""
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np
from PIL import Image
from lab2_sphere import (Parameters, Light, calculate, radiance_at,
                         trace, validate, save_results, control_points)


class Lab2Tests(unittest.TestCase):
    def setUp(self):
        self.p = Parameters(width_px=200, height_px=200)

    def test_axial_closed_form(self):
        p = replace(self.p, lights=(Light(0, 0, 1700, 100),))
        point = p.center() + np.array([0, 0, p.radius_mm])
        value, diffuse, specular = radiance_at(point, p)
        expected = 100 / 0.75**2
        self.assertAlmostEqual(value, expected*(p.kd+p.ks), places=10)
        self.assertAlmostEqual(diffuse, expected*p.kd, places=10)
        self.assertAlmostEqual(specular, expected*p.ks, places=10)

    def test_nearest_ray_intersection(self):
        hit, point = trace(self.p, np.array(0.0), np.array(0.0))
        self.assertTrue(hit)
        np.testing.assert_allclose(point, [0, 0, 950], atol=1e-10)
        hit, _ = trace(self.p, np.array(600.0), np.array(600.0))
        self.assertFalse(hit)

    def test_intensity_linearity_and_normalization(self):
        first = calculate(self.p)
        twice = calculate(replace(self.p, lights=tuple(
            replace(l, intensity_w_sr=2*l.intensity_w_sr) for l in self.p.lights)))
        np.testing.assert_allclose(twice['total'], 2*first['total'], rtol=1e-12)
        np.testing.assert_array_equal(twice['image'], first['image'])

    def test_two_lights_are_additive(self):
        pts = np.array([[0, 0, 950], [-210, 0, 880], [210, 0, 880]])
        combined = radiance_at(pts, self.p)[0]
        separate = sum(radiance_at(pts, replace(self.p, lights=(light,)))[0]
                       for light in self.p.lights)
        np.testing.assert_allclose(combined, separate, rtol=1e-12)

    def test_black_scene_and_back_facing_surface(self):
        result = calculate(replace(self.p, kd=0, ks=0))
        self.assertFalse(np.any(result['image']))
        self.assertTrue(np.isfinite(result['total']).all())
        self.assertEqual(float(radiance_at(np.array([0, 0, 250]), self.p)[0]), 0)
        self.assertEqual(float(radiance_at(np.array([0, 0, 950]),
            replace(self.p, lights=(Light(0, 0, 100, 100),)))[0]), 0)

    def test_control_points_lie_on_sphere(self):
        for record in control_points(self.p):
            point = np.array([record[k] for k in ('x_mm', 'y_mm', 'z_mm')])
            self.assertAlmostEqual(np.linalg.norm(point-self.p.center()), self.p.radius_mm)
            self.assertTrue(record['visible'])

    def test_reject_bad_geometry_and_nonfinite_parameters(self):
        for change in ({'width_mm': 1300}, {'width_px': 199},
                       {'direction': (0, 0, 0)}, {'radius_mm': 1000},
                       {'center_x_mm': 600}, {'kd': float('nan')},
                       {'lights': (Light(0, 0, 600, 100),)}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate(replace(self.p, **change))
        validate(replace(self.p, direction=(0.05, 0, -1)))

    def test_pixel_surface_and_png_export(self):
        result = calculate(self.p)
        np.testing.assert_allclose(np.linalg.norm(result['points'][result['mask']]
                                  - self.p.center(), axis=-1), self.p.radius_mm, atol=1e-8)
        self.assertEqual(result['image'].max(), 255)
        self.assertFalse(np.any(result['image'][~result['mask']]))
        self.assertGreater(result['y'][0], result['y'][-1])
        with tempfile.TemporaryDirectory() as directory:
            save_results(result, directory)
            png = Image.open(Path(directory)/'sphere_normalized.png')
            self.assertEqual(png.mode, 'L')
            self.assertEqual(png.size, (200, 200))
            np.testing.assert_array_equal(np.asarray(png), result['image'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
