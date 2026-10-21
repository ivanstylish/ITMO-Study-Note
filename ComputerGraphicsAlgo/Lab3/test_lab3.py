"""Independent numeric and file round-trip checks for Lab 3.

Run with ``python test_lab3.py``. Only NumPy, Pillow and the standard library
are needed. The JSON record names the source hash actually tested.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import tempfile
import time
import unittest
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
from PIL import Image

from types import SimpleNamespace
from lab3_color_sphere import geometry, spectral, color_conversion, rendering

# 仅测试端组合接口，生产包保持清晰的模块边界。
app = SimpleNamespace(**{name: value for module in
    (geometry, spectral, color_conversion, rendering)
    for name, value in vars(module).items() if not name.startswith('_')})


BASE = Path(__file__).resolve().parent


def front_points(p):
    """Three specified points, independent of raster sampling."""
    normals = np.array([[0, 0, 1], [-.6, 0, .8], [.6, 0, .8]])
    return p.center() + p.radius_mm * normals


def scalar_spectral_reference(point, p, wavelengths):
    """Scalar, per-source, per-wavelength reference from the task diagram.

    It intentionally does not call the renderer's geometry, quadrature,
    normalization or color-conversion helpers.
    """
    point = np.asarray(point, dtype=float)
    normal = (point - p.center()) / p.radius_mm
    output = []
    for j in range(len(wavelengths)):
        total = 0.0
        for light in p.lights:
            vector = light.position() - point
            distance_mm = math.sqrt(sum(float(x) ** 2 for x in vector))
            incident = vector / distance_mm
            axis = np.asarray(light.axis, float)
            axis /= math.sqrt(sum(float(x) ** 2 for x in axis))
            emission = max(0.0, float(np.dot(-incident, axis)))
            receiving = max(0.0, float(np.dot(normal, incident)))
            # Integral of a linearly interpolated source table in nm.
            area = sum((float(light.spectrum[k]) + float(light.spectrum[k + 1]))
                       * (float(wavelengths[k + 1]) - float(wavelengths[k])) / 2
                       for k in range(len(wavelengths) - 1))
            exponent = 2 if p.model == "reference_diagram" else 1
            total += (light.intensity_w_sr * emission * receiving ** exponent
                      * float(light.spectrum[j]) / area
                      * float(p.reflectance[j])
                      / (math.pi * (distance_mm / 1000.0) ** 2))
        output.append(total)
    return np.array(output)


class Lab3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = app.load_tables()
        cls.white_p = replace(app.default_parameters("white"), width_px=200)
        cls.colored_p = replace(app.default_parameters("colored"), width_px=200)
        cls.white = app.calculate(cls.white_p)
        cls.colored = app.calculate(cls.colored_p)

    def test_01_tables_and_official_d65_provenance(self):
        """41 exact wavelength rows and known samples of the CIE D65 source."""
        expected_waves = np.arange(380, 781, 10)
        assert_array_equal(self.tables.wavelengths, expected_waves)
        self.assertEqual(self.tables.cmf.shape, (41, 3))
        assert_allclose(self.tables.d65[[0, 5, 10, 15, 18, 40]],
                        [49.9755, 86.6823, 115.923, 107.689, 100, 63.3828], rtol=0, atol=1e-10)
        self.assertEqual(sorted(p.name for p in (spectral.BASE / 'data').glob('*.csv')),
                         ['cie_xyz_1931.csv', 'light_spectra.csv', 'reflectance.csv'])

    def test_02_quadrature_has_absolute_nanometre_scale(self):
        """A constant spectrum integrates to 400 nm, not 41 samples or one."""
        tables = app.ColorTables(np.arange(380, 781, 10),
                                 np.tile([1.0, 2.0, 3.0], (41, 1)),
                                 np.ones(41), self.tables.weights)
        assert_allclose(app.spectrum_to_xyz(np.ones(41), tables), [400, 800, 1200], rtol=0, atol=1e-12)
        assert_allclose(app.normalize_spd(np.ones(41), tables), np.full(41, 1 / 400), rtol=0, atol=1e-15)

    def test_03_signed_cie_rgb_matrix_round_trip(self):
        """CIE RGB is signed and the chosen matrix convention is reversible."""
        xyz = np.array([[1.0, 0, 0], [.2, .7, .1], [0, 0, 1.0]])
        rgb = xyz @ app.XYZ_TO_CIE_RGB.T
        self.assertLess(rgb[0, 1], 0)
        assert_allclose(rgb[0], [2.36461, -.51517, .00520], rtol=0, atol=1e-12)
        assert_allclose(rgb @ app.CIE_RGB_TO_XYZ.T, xyz, rtol=0, atol=1e-14)

    def test_04_white_d65_paths_agree_before_and_after_display(self):
        """The D65 calibration makes the two white-light paths identical."""
        result = self.white
        assert_allclose(result["rgb1"], result["rgb2"], rtol=2e-13, atol=2e-14)
        assert_array_equal(result["images"][0], result["images"][1])
        self.assertEqual(result["comparison"]["monitor_different_pixels"], 0)

    def test_05_colored_paths_expose_the_rgb_approximation(self):
        """Colored spectra give a measurable difference on this colored sphere."""
        self.assertGreater(self.colored["comparison"]["rgb_absolute_max_difference"], 1e-4)
        self.assertGreater(self.colored["comparison"]["monitor_different_pixels"], 100)
        self.assertGreater(self.colored["comparison"]["monitor_mae_8bit"], .1)

    def test_06_constant_reflectance_paths_agree_for_colored_sources(self):
        """A neutral material is an exact, independently justified RGB case."""
        p = replace(self.colored_p, reflectance=(.37,) * 41)
        values = app.radiance_at(front_points(p), p)
        assert_allclose(values["rgb1"], values["rgb2"], rtol=2e-13, atol=2e-14)

    def test_07_independent_scalar_reference_at_three_points(self):
        """Vectorized radiance matches a scalar derivation of the reference figure."""
        for p in (self.white_p, self.colored_p, replace(self.colored_p, model="lambert")):
            points = front_points(p)
            actual = app.radiance_at(points, p)["spectral"]
            expected = np.stack([scalar_spectral_reference(point, p, self.tables.wavelengths)
                                 for point in points])
            assert_allclose(actual, expected, rtol=3e-13, atol=1e-15)

    def test_08_multiple_sources_add_linearly(self):
        """Adding sources adds their absolute spectral and tristimulus results."""
        p = self.colored_p
        points = front_points(p)
        together = app.radiance_at(points, p)
        separate = [app.radiance_at(points, replace(p, lights=(light,))) for light in p.lights]
        for key in ("spectral", "xyz", "rgb1", "rgb2", "radiance_w_m2_sr", "luminance_cd_m2"):
            assert_allclose(together[key], sum(part[key] for part in separate), rtol=2e-13, atol=2e-13)

    def test_09_intensity_doubles_but_spd_amplitude_is_relative(self):
        """I0 controls total intensity while relative SPD amplitude cancels."""
        p = self.colored_p
        points = front_points(p)
        original = app.radiance_at(points, p)["spectral"]
        doubled = replace(p, lights=tuple(replace(light, intensity_w_sr=2 * light.intensity_w_sr)
                                          for light in p.lights))
        scaled = replace(p, lights=tuple(replace(light, spectrum=tuple(7 * np.array(light.spectrum)))
                                         for light in p.lights))
        assert_allclose(app.radiance_at(points, doubled)["spectral"], 2 * original, rtol=1e-13, atol=1e-15)
        assert_allclose(app.radiance_at(points, scaled)["spectral"], original, rtol=1e-13, atol=1e-15)

    def test_10_analytic_units_and_inverse_square(self):
        """A normal-incidence point at 1 m gives I0*kd/pi W/(m2 sr)."""
        point = np.array([0.0, 0.0, 950.0])
        light = app.Light(0, 0, 1950, 100, spectrum=(1.0,) * 41)
        p = replace(self.white_p, reflectance=(.4,) * 41, lights=(light,))
        near = app.radiance_at(point, p)["radiance_w_m2_sr"]
        far = app.radiance_at(point, replace(p, lights=(replace(light, z_mm=2950),)))["radiance_w_m2_sr"]
        self.assertAlmostEqual(float(near), 40 / math.pi, places=11)
        self.assertAlmostEqual(float(far), 10 / math.pi, places=11)

    def test_11_reference_figure_really_has_the_second_cosine(self):
        """At 60 degree incidence the diagram yields half the standard Lambert value."""
        point = np.array([0.0, 0.0, 950.0])
        light = app.Light(math.sqrt(3) * 500, 0, 1450, 100,
                          axis=(-math.sqrt(3) / 2, 0, -.5), spectrum=(1.0,) * 41)
        p = replace(self.white_p, reflectance=(.4,) * 41, lights=(light,))
        diagram = float(app.radiance_at(point, p)["radiance_w_m2_sr"])
        standard = float(app.radiance_at(point, replace(p, model="lambert"))["radiance_w_m2_sr"])
        self.assertAlmostEqual(diagram, 10 / math.pi, places=11)
        self.assertAlmostEqual(standard, 20 / math.pi, places=11)

    def test_12_source_orientation_back_lighting_and_view_independence(self):
        """A source cannot shine backwards and hidden lit surface radiance remains physical."""
        point = np.array([0.0, 0.0, 950.0])
        p = replace(self.white_p, lights=(app.Light(0, 0, 1950, 100, axis=(0, 0, 1)),))
        assert_array_equal(app.radiance_at(point, p)["spectral"], np.zeros(41))
        # South pole is invisible from the default camera but emits toward its outer hemisphere.
        south = np.array([0.0, 0.0, 250.0])
        p = replace(p, lights=(app.Light(0, 0, -750, 100, axis=(0, 0, 1)),))
        self.assertGreater(float(app.radiance_at(south, p)["radiance_w_m2_sr"]), 0)
        assert_array_equal(app.radiance_at(point, p)["spectral"], np.zeros(41))

    def test_13_black_scene_is_valid_and_has_finite_zero_images(self):
        """Zero reflectance needs no division by zero or fabricated maximum."""
        p = replace(self.white_p, reflectance=(0.0,) * 41)
        result = app.calculate(p)
        for key in ("spectral", "xyz", "rgb1", "rgb2", "radiance", "luminance1", "luminance2"):
            self.assertTrue(np.isfinite(result[key]).all())
            self.assertEqual(np.count_nonzero(result[key]), 0)
        for array in result["images"] + result["grays"]:
            self.assertEqual(np.count_nonzero(array), 0)
        self.assertEqual(result["exposure"]["shared_gain"], 0)

    def test_14_exact_square_pixels_and_valid_rectangular_screen(self):
        """Integer rounding must not silently create nonsquare physical pixels."""
        p = replace(self.white_p, width_mm=1500, height_mm=1200, width_px=250)
        app.validate(p)
        self.assertEqual(p.height_px, 200)
        self.assertAlmostEqual(p.width_mm / p.width_px, p.height_mm / p.height_px)
        with self.assertRaises(ValueError):
            app.validate(replace(self.white_p, width_px=601, height_mm=1000))

    def test_15_below_view_negative_light_z_and_sphere_center_z_zero(self):
        """The new source and sphere coordinate ranges work on the opposite side."""
        p = replace(self.colored_p, width_mm=2000, height_mm=2000,
                    observer_z_mm=-2500, direction=(0, 0, 1), screen_z_mm=2000,
                    center_z_mm=0, lights=tuple(replace(light, z_mm=-light.z_mm, axis=(0, 0, 1))
                                              for light in self.colored_p.lights))
        app.validate(p)
        mask, point = app.trace(p, np.array(0.0), np.array(0.0))
        self.assertTrue(bool(mask))
        assert_allclose(point, [0, 0, -350], rtol=0, atol=1e-10)
        for record in app.control_points(p):
            self.assertTrue(record["visible"])
        self.assertGreater(float(app.radiance_at(point, p)["radiance_w_m2_sr"]), 0)

    def test_16_full_cubes_at_both_resolution_limits(self):
        """Actually calculate 200 and 800 square images with all 41 spectral channels."""
        self.assertEqual(self.white["spectral"].shape, (200, 200, 41))
        large = app.calculate(replace(self.white_p, width_px=800))
        self.assertEqual(large["spectral"].shape, (800, 800, 41))
        self.assertEqual(large["images"][0].shape, (800, 800, 3))
        self.assertGreater(large["statistics"]["visible_pixel_count"], 100000)
        self.assertTrue(np.isfinite(large["spectral"]).all())
        assert_allclose(large["rgb1"][large["mask"]], large["rgb2"][large["mask"]], rtol=2e-13, atol=2e-14)

    def test_17_control_points_are_distinct_visible_surface_points(self):
        """Control values are exact coordinate evaluations rather than nearby pixels."""
        p = self.colored_p
        rows = self.colored["control_points"]
        points = np.array([[row["x_mm"], row["y_mm"], row["z_mm"]] for row in rows])
        self.assertEqual(len({tuple(point) for point in points}), 3)
        assert_allclose(np.linalg.norm(points - p.center(), axis=1), p.radius_mm, atol=1e-10)
        for point, row in zip(points, rows):
            self.assertTrue(row["visible"])
            self.assertGreater(np.dot(point - p.center(), p.observer() - point), 0)
            expected = scalar_spectral_reference(point, p, self.tables.wavelengths)
            integrated = sum((expected[j] + expected[j + 1]) * 5 for j in range(40))
            self.assertAlmostEqual(row["radiance_w_m2_sr"], float(integrated), places=11)

    def test_18_camera_geometry_center_ray_miss_and_oblique_view(self):
        """Ray intersections and an off-axis camera follow the actual scene geometry."""
        p = self.white_p
        mask, points = app.trace(p, np.array([0, 600.0]), np.array([0, 600.0]))
        assert_array_equal(mask, [True, False])
        assert_allclose(points[0], [0, 0, 950], atol=1e-10)
        p = replace(p, center_x_mm=200, center_y_mm=100, direction=(200, 100, -1900),
                    width_mm=1600, height_mm=1600)
        app.validate(p)
        hit, point = app.trace(p, np.array(0.0), np.array(0.0))
        self.assertTrue(bool(hit))
        self.assertAlmostEqual(np.linalg.norm(point - p.center()), p.radius_mm, places=9)
        self.assertTrue(all(row["visible"] for row in app.control_points(p)))

    def test_19_invalid_numeric_spectral_and_geometry_inputs(self):
        """NaN, bad spectra, zero axes, clipping, and invalid placements fail validation."""
        p = self.white_p
        invalid = {
            "NaN geometry": replace(p, radius_mm=float("nan")),
            "NaN intensity": replace(p, lights=(replace(p.lights[0], intensity_w_sr=float("nan")),)),
            "wrong spectrum length": replace(p, reflectance=(.4,) * 40),
            "negative reflectance": replace(p, reflectance=(-.1,) * 41),
            "reflectance above one": replace(p, reflectance=(1.1,) * 41),
            "NaN spectrum": replace(p, reflectance=(float("nan"),) * 41),
            "negative source spectrum": replace(p, lights=(replace(p.lights[0], spectrum=(-1.0,) * 41),)),
            "zero source spectrum": replace(p, lights=(replace(p.lights[0], spectrum=(0.0,) * 41),)),
            "zero source axis": replace(p, lights=(replace(p.lights[0], axis=(0, 0, 0)),)),
            "zero camera direction": replace(p, direction=(0, 0, 0)),
            "wrong direction length": replace(p, direction=(0, -1)),
            "camera inside sphere": replace(p, observer_z_mm=600),
            "source inside sphere": replace(p, lights=(replace(p.lights[0], x_mm=0, y_mm=0, z_mm=600),)),
            "cropped sphere": replace(p, width_mm=500, height_mm=500),
            "screen in front of sphere": replace(p, screen_z_mm=800),
            "resolution too low": replace(p, width_px=199),
            "resolution too high": replace(p, width_px=801),
            "boolean numeric": replace(p, width_px=True),
            "no source": replace(p, lights=()),
        }
        for label, scene in invalid.items():
            with self.subTest(label=label), self.assertRaises(ValueError):
                app.validate(scene)

    def test_20_spectral_table_roundtrip_and_bad_wavelength_rows(self):
        """The editable table preserves spectra and enforces the 10 nm grid."""
        p = self.colored_p
        text = app.spectra_csv(p)
        restored = app.apply_spectra_csv(p, text)
        assert_array_equal(restored.reflectance, p.reflectance)
        for a, b in zip(restored.lights, p.lights):
            assert_array_equal(a.spectrum, b.spectrum)
        with self.assertRaises(ValueError):
            app.apply_spectra_csv(p, text.replace("380,", "381,", 1))
        with self.assertRaises(ValueError):
            app.apply_spectra_csv(p, "\n".join(text.splitlines()[:-1]))

    def test_21_saved_arrays_images_json_and_grays_roundtrip(self):
        """Reopen actual exported files and reconstruct gray from the saved RGB bytes."""
        result = self.colored
        with tempfile.TemporaryDirectory(prefix="lab3-files-", dir=BASE) as temporary:
            directory = Path(temporary)
            # Check the eventual recursive cleanup target before creating files.
            self.assertTrue(directory.resolve().is_relative_to(BASE.resolve()))
            app.save_results(result, directory)
            arrays = {"spectral_radiance": "spectral", "xyz1": "xyz", "rgb1": "rgb1", "rgb2": "rgb2",
                      "radiance_w_m2_sr": "radiance", "luminance1_cd_m2": "luminance1",
                      "luminance2_cd_m2": "luminance2", "mask": "mask"}
            with np.load(directory / "radiance_data.npz", allow_pickle=False) as saved:
                for stored, key in arrays.items():
                    assert_array_equal(saved[stored], result[key])
                self.assertEqual(saved["spectral_radiance"].dtype, np.dtype("float64"))
            metadata = json.loads((directory / "results.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["incidence_power"], 2)
            self.assertEqual(len(metadata["control_points"]), 3)
            restored_p = app.load_parameters(directory / "results.json")
            self.assertEqual(json.loads(json.dumps(asdict(restored_p))),
                             json.loads(json.dumps(asdict(result["parameters"]))))
            for i in range(2):
                with Image.open(directory / f"image_{i + 1}.png") as image:
                    self.assertEqual(image.mode, "RGB")
                    rgb_bytes = np.array(image)
                with Image.open(directory / f"image_{i + 1}_gray.png") as image:
                    self.assertEqual(image.mode, "L")
                    gray_bytes = np.array(image)
                assert_array_equal(rgb_bytes, result["images"][i])
                encoded = rgb_bytes.astype(float) / 255
                linear = np.where(encoded <= .04045, encoded / 12.92, ((encoded + .055) / 1.055) ** 2.4)
                # Independent standard weights, allowing one code step for the rounded display matrix.
                luminance = linear @ np.array([.2126, .7152, .0722])
                expected = np.where(luminance <= .0031308, 12.92 * luminance,
                                    1.055 * luminance ** (1 / 2.4) - .055)
                self.assertLessEqual(int(np.max(np.abs(gray_bytes.astype(int) - np.rint(255 * expected).astype(int)))), 1)
            with (directory / "three_points.csv").open(encoding="utf-8-sig", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 3)

    def test_22_memory_cube_mask_surface_and_physical_statistics(self):
        """Absolute physical arrays remain distinct from black background and display bytes."""
        result = self.colored
        mask = result["mask"]
        self.assertEqual(result["spectral"].dtype, np.dtype("float64"))
        self.assertEqual(result["images"][0].dtype, np.dtype("uint8"))
        self.assertEqual(np.count_nonzero(result["spectral"][~mask]), 0)
        assert_allclose(result["spectral"] @ self.tables.weights, result["radiance"], rtol=2e-13, atol=1e-14)
        assert_allclose(683 * result["xyz"][..., 1], result["luminance1"], rtol=0, atol=1e-12)
        assert_allclose(np.linalg.norm(result["points"][mask] - self.colored_p.center(), axis=-1),
                        self.colored_p.radius_mm, rtol=0, atol=1e-8)
        self.assertAlmostEqual(result["statistics"]["radiance_w_m2_sr"]["maximum"],
                               float(result["radiance"][mask].max()), places=12)
        self.assertIn("sphere_sampled_radiance_w_m2_sr", result["statistics"])
        self.assertEqual(max(image.max() for image in result["images"]), 255)

    def test_23_extended_coordinate_boundaries_and_signed_material_conversion(self):
        """New coordinate limits and signed CIE material channels are supported."""
        p = replace(self.white_p, center_z_mm=0, screen_z_mm=-1000,
                    lights=(replace(self.white_p.lights[0], x_mm=-10000, y_mm=10000, z_mm=-10000),
                            replace(self.white_p.lights[1], x_mm=10000, y_mm=-10000, z_mm=10000)))
        app.validate(p)
        kd = np.exp(-.5 * ((self.tables.wavelengths - 530) / 10) ** 2)
        p = replace(self.white_p, reflectance=tuple(kd))
        kd_rgb, _ = app.scene_rgb(p)
        self.assertTrue(np.any(kd_rgb < 0), "CIE RGB material coefficients must remain signed")

    def test_24_horizontal_direction_uses_explicit_screen_distance(self):
        """A direction with zero Z component works when its screen distance is explicit."""
        p = replace(self.white_p, direction=(1, 0, 0), screen_distance_mm=3500,
                    center_x_mm=2000, center_y_mm=0, center_z_mm=2500,
                    width_mm=2000, height_mm=2000,
                    lights=(app.Light(1200, 500, 3000, 100, axis=(1, 0, 0),
                                      spectrum=tuple(self.tables.d65)),))
        app.validate(p)
        hit, point = app.trace(p, np.array(0.0), np.array(0.0))
        self.assertTrue(bool(hit))
        assert_allclose(point, [1650, 0, 2500], rtol=0, atol=1e-10)
        self.assertGreater(float(app.radiance_at(point, p)["radiance_w_m2_sr"]), 0)
        for invalid_distance in (0, -1, float("nan"), float("inf")):
            with self.subTest(distance=invalid_distance), self.assertRaises(ValueError):
                app.validate(replace(p, screen_distance_mm=invalid_distance))


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self._started = {}
        self._status = {}

    def startTest(self, test):
        self._started[test.id()] = time.perf_counter()
        self._status[test.id()] = "passed"
        super().startTest(test)

    def addFailure(self, test, error):
        self._status[test.id()] = "failed"
        super().addFailure(test, error)

    def addError(self, test, error):
        self._status[test.id()] = "error"
        super().addError(test, error)

    def addSubTest(self, test, subtest, error):
        if error is not None:
            self._status[test.id()] = "failed"
        super().addSubTest(test, subtest, error)

    def stopTest(self, test):
        self.records.append(dict(test=test.id(), description=test.shortDescription(),
                                 status=self._status[test.id()],
                                 elapsed_seconds=round(time.perf_counter() - self._started[test.id()], 6)))
        super().stopTest(test)


def main():
    began = time.perf_counter()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Lab3Tests)
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordedResult).run(suite)
    record = dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
                  command="python test_lab3.py", python=sys.version,
                  source_sha256={path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in sorted((BASE / 'lab3_color_sphere').glob('*.py'))},
                  tests_run=result.testsRun, successful=result.wasSuccessful(),
                  failure_count=len(result.failures), error_count=len(result.errors),
                  skipped_count=len(result.skipped),
                  elapsed_seconds=round(time.perf_counter() - began, 6), tests=result.records,
                  failures=[dict(test=str(test), traceback=trace) for test, trace in result.failures + result.errors],
                  scope="Local numeric, full 200/800 spectral calculation, validation, and export round-trip. GUI is not exercised by this suite.")
    (BASE / "validation_results.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
