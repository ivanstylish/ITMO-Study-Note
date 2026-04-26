package org.coordinate.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.junit.jupiter.api.Assertions.*;

/**
 * JUnit 5 тесты для AreaCheck.checkHit(x, y, r)
 *
 * Область состоит из трёх частей:
 *   1. Прямоугольник  : x ∈ [-R, 0], y ∈ [0, R]          (II квадрант, верхний)
 *   2. Треугольник    : x ∈ [-R, 0], y ∈ [-R/2, 0]        (II квадрант, нижний)
 *      граница: y = -0.5*x - R/2
 *   3. Четверть круга : x ∈ [0, R/2], y ∈ [-R/2, 0]       (IV квадрант)
 *      радиус R/2
 */
@DisplayName("AreaCheck — тесты попадания точки в область")
public class AreaCheckTest {

    private AreaCheck areaCheck;
    private static final double R = 2.0;

    @BeforeEach
    void setUp() {
        areaCheck = new AreaCheck();
    }

    // ----------------------------------------------------------------
    // Прямоугольник (II кв., верхний): x ∈ [-R, 0], y ∈ [0, R]
    // ----------------------------------------------------------------

    @Test
    @DisplayName("Центр прямоугольника — попадание")
    void testRectangleCenter() {
        assertTrue(areaCheck.checkHit(-1.0, 1.0, R));
    }

    @Test
    @DisplayName("Угол прямоугольника (-R, R) — попадание")
    void testRectangleTopLeftCorner() {
        assertTrue(areaCheck.checkHit(-R, R, R));
    }

    @Test
    @DisplayName("Угол прямоугольника (0, 0) — попадание (начало координат)")
    void testRectangleOrigin() {
        assertTrue(areaCheck.checkHit(0.0, 0.0, R));
    }

    @Test
    @DisplayName("Точка вне прямоугольника (сверху) — промах")
    void testAboveRectangle() {
        assertFalse(areaCheck.checkHit(-1.0, R + 0.1, R));
    }

    @Test
    @DisplayName("Точка вне прямоугольника (правее) — промах")
    void testRightOfRectangle() {
        assertFalse(areaCheck.checkHit(0.1, 1.0, R));
    }

    // ----------------------------------------------------------------
    // Треугольник (II кв., нижний): x ∈ [-R, 0], y ∈ [-R/2, 0]
    //   граница: y >= -0.5*x - R/2
    // ----------------------------------------------------------------

    @Test
    @DisplayName("Вершина треугольника (-R, 0) — попадание")
    void testTriangleTopLeftVertex() {
        assertTrue(areaCheck.checkHit(-R, 0.0, R));
    }

    @Test
    @DisplayName("Вершина треугольника (0, -R/2) — попадание")
    void testTriangleBottomRightVertex() {
        // y = -0.5 * 0 - R/2 = -R/2  => y >= -R/2, граничная точка
        assertTrue(areaCheck.checkHit(0.0, -R / 2, R));
    }

    @Test
    @DisplayName("Точка внутри треугольника (-1, -0.1) — попадание")
    void testInsideTriangle() {
        // y = -0.5*(-1) - R/2 = 0.5 - 1 = -0.5
        // y=-0.1 >= -0.5 => попадание
        assertTrue(areaCheck.checkHit(-1.0, -0.1, R));
    }

    @Test
    @DisplayName("Точка ниже гипотенузы треугольника — промах")
    void testBelowTriangleHypotenuse() {
        // y = -0.5*(-1) - 1 = -0.5  => y=-0.9 < -0.5 => промах
        assertFalse(areaCheck.checkHit(-1.0, -0.9, R));
    }

    @Test
    @DisplayName("Точка ниже -R/2 в треугольнике — промах")
    void testBelowTriangle() {
        assertFalse(areaCheck.checkHit(-1.0, -R / 2 - 0.1, R));
    }

    // ----------------------------------------------------------------
    // Четверть круга (IV кв.): x ∈ [0, R/2], y ∈ [-R/2, 0], r=R/2
    // ----------------------------------------------------------------

    @Test
    @DisplayName("Центр координат (0,0) — попадание (границ круга)")
    void testQuarterCircleOrigin() {
        assertTrue(areaCheck.checkHit(0.0, 0.0, R));
    }

    @Test
    @DisplayName("Точка на границе круга (R/2, 0) — промах (x>0, y=0 => x²+y²=(R/2)²)")
    void testQuarterCircleBoundary() {
        // x=R/2, y=0 => x²+y² = (R/2)² => на границе => попадание
        assertTrue(areaCheck.checkHit(R / 2, 0.0, R));
    }

    @Test
    @DisplayName("Точка внутри четверти круга (0.5, -0.5) при R=2 — попадание")
    void testInsideQuarterCircle() {
        // x²+y² = 0.25+0.25 = 0.5 <= (R/2)² = 1 => попадание
        assertTrue(areaCheck.checkHit(0.5, -0.5, R));
    }

    @Test
    @DisplayName("Точка вне четверти круга (1.0, -0.5) при R=2 — промах")
    void testOutsideQuarterCircle() {
        // x²+y² = 1.0+0.25 = 1.25 > (R/2)² = 1.0 => промах
        assertFalse(areaCheck.checkHit(1.0, -0.5, R));
    }

    @Test
    @DisplayName("Точка в I квадранте (1, 1) — всегда промах")
    void testFirstQuadrant() {
        assertFalse(areaCheck.checkHit(1.0, 1.0, R));
    }

    @Test
    @DisplayName("Точка в III квадранте (-1, -1) — промах")
    void testThirdQuadrant() {
        assertFalse(areaCheck.checkHit(-1.0, -1.5, R));
    }

    // ----------------------------------------------------------------
    // Параметризованные тесты
    // ----------------------------------------------------------------

    @ParameterizedTest(name = "checkHit({0}, {1}, {2}) = {3}")
    @CsvSource({
        // x,    y,    r,   expected
        "-1.0,  1.0,  2.0, true",   // прямоугольник
        "-2.0,  2.0,  2.0, true",   // угол прямоугольника
        " 0.0,  0.0,  2.0, true",   // начало координат
        "-1.0, -0.1,  2.0, true",   // треугольник
        " 0.5, -0.5,  2.0, true",   // четверть круга
        " 1.0,  1.0,  2.0, false",  // I квадрант
        "-1.0, -0.9,  2.0, false",  // ниже гипотенузы
        " 3.0,  0.0,  2.0, false",  // далеко справа
        " 0.0, -1.5,  2.0, false",  // ниже круга
        "-2.0, -1.5,  2.0, false"   // III квадрант
    })
    @DisplayName("Параметризованный тест checkHit")
    void testCheckHitParameterized(double x, double y, double r, boolean expected) {
        assertEquals(expected, areaCheck.checkHit(x, y, r),
                String.format("checkHit(%.1f, %.1f, %.1f)", x, y, r));
    }

    // ----------------------------------------------------------------
    // Тесты с разными значениями R
    // ----------------------------------------------------------------

    @Test
    @DisplayName("R=1: точка (-0.5, 0.5) — попадание в прямоугольник")
    void testDifferentR_rectangle() {
        assertTrue(areaCheck.checkHit(-0.5, 0.5, 1.0));
    }

    @Test
    @DisplayName("R=3: точка (-2.5, 2.5) — попадание в прямоугольник")
    void testDifferentR_largeR() {
        assertTrue(areaCheck.checkHit(-2.5, 2.5, 3.0));
    }

    @Test
    @DisplayName("R=4: точка вне области — промах")
    void testDifferentR_miss() {
        assertFalse(areaCheck.checkHit(3.0, 3.0, 4.0));
    }
}