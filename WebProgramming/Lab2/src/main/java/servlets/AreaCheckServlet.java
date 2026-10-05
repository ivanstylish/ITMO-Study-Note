package servlets;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class AreaCheckServlet extends HttpServlet {
    private boolean isHit(double x, double y, double r) {
        if (x <= r / 2.0 && y <= r && x >= 0 && y >= 0) {
            return true;
        }
        if (x <= 0 && x >= -r / 2.0 && y >= 0 && y <= r) {
            if (y <= 2*x + r) {
                return true;
            }
        }
        if (x >= 0 && x <= r / 2.0 && y <= 0 && y >= -r / 2.0) {
            double rad = r / 2.0;
            if (x * x + y * y <= rad * rad) {
                return true;
            }
        }
        return false;
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        req.setCharacterEncoding("UTF-8");
        long startTime = System.nanoTime();

        String[] xArray = req.getParameterValues("x");
        String xs = (xArray != null && xArray.length > 0) ? xArray[0] : null;
        String ys = req.getParameter("y");
        String rs = req.getParameter("r");

        if (xs == null || ys == null || rs == null) {
            req.setAttribute("error", "Lack of necessary params");
            req.getRequestDispatcher("/jsp/result.jsp").forward(req, resp);
            return;
        }

        double x, y, r;

        try {
            x = Double.parseDouble(xs);
            y = Double.parseDouble(ys);
            r = Double.parseDouble(rs);
        } catch (Exception e) {
            req.setAttribute("error", "Invalid number params");
            req.getRequestDispatcher("/jsp/result.jsp").forward(req, resp);
            return;
        }

        double[] validX = {-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2};
        boolean validXValue = false;
        for (double vx : validX) {
            if (Math.abs(x - vx) < 0.001) {
                validXValue = true;
                break;
            }
        }
        if (!validXValue) {
            req.setAttribute("error", "X must be one of: -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2");
            req.getRequestDispatcher("/jsp/result.jsp").forward(req, resp);
            return;
        }

        if (y <= -5 || y >= 5) {
            req.setAttribute("error", "Y must be in [-5, 5] area");
            req.getRequestDispatcher("/jsp/result.jsp").forward(req, resp);
            return;
        }

        double[] validR = {1, 1.5, 2, 2.5, 3};
        boolean validRValue = false;
        for (double vr : validR) {
            if (Math.abs(r - vr) < 0.001) {
                validRValue = true;
                break;
            }
        }

        if (!validRValue) {
            req.setAttribute("error", "R must be 1, 1.5, 2, 2.5 or 3");
            req.getRequestDispatcher("/jsp/result.jsp").forward(req, resp);
            return;
        }

        boolean hit = isHit(x, y, r);
        long duration = (System.nanoTime() - startTime) / 1_000_000;
        HitResult hr = new HitResult(x, y, r, hit, duration);

        Object obj = getServletContext().getAttribute("results");
        if (obj instanceof List) {
            @SuppressWarnings("unchecked")
            List<HitResult> list = (List<HitResult>) obj;
            synchronized (list) {
                list.add(0, hr);
                if (list.size() > 100) {
                    list.remove(list.size() - 1);
                }
            }
        }

        List<HitResult> currentResults = new ArrayList<>();
        currentResults.add(hr);
        req.setAttribute("results", currentResults);

        req.getRequestDispatcher("/jsp/result.jsp").forward(req, resp);
    }
}