package servlets;

import jakarta.servlet.ServletContext;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class ControllerServlet extends HttpServlet{
    @Override
    public void init() {
        ServletContext ctx = getServletContext();
        synchronized (ctx) {
            if (ctx.getAttribute("results") == null) {
                ctx.setAttribute("results", new ArrayList<HitResult>());
            }
        }
    }

    protected void process(HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException {

        req.setCharacterEncoding("UTF-8");

        if ("true".equals(req.getParameter("clear"))) {
            ServletContext ctx = getServletContext();
            synchronized (ctx) {
                ctx.setAttribute("results", new ArrayList<HitResult>());
            }
            req.getRequestDispatcher("/jsp/form.jsp").forward(req, res);
            return;
        }

        String[] x = req.getParameterValues("x");
        String y = req.getParameter("y");
        String r = req.getParameter("r");

        if (x != null && x.length > 0 && y != null && r != null
                && !y.isEmpty() && !r.isEmpty()) {
            if (x.length == 1) {
                req.getRequestDispatcher("/area").forward(req, res);
                return;
            } else {
                try {
                    double yVal = Double.parseDouble(y);
                    double rVal = Double.parseDouble(r);

                    List<HitResult> currentResults = new ArrayList<>();

                    for (String xStr : x) {
                        double xVal = Double.parseDouble(xStr);
                        HitResult hr = processPoint(xVal, yVal, rVal);
                        currentResults.add(hr);
                    }
                    req.setAttribute("results", currentResults);
                    req.getRequestDispatcher("/jsp/result.jsp").forward(req, res);
                    return;
                } catch (NumberFormatException e) {
                    req.setAttribute("error", "Invalid number format");
                    req.getRequestDispatcher("/jsp/form.jsp").forward(req, res);
                    return;
                }
            }
        }
        req.getRequestDispatcher("/jsp/form.jsp").forward(req, res);
    }

    private HitResult processPoint(double x, double y, double r) {
        long startTime = System.nanoTime();
        boolean hit = isHit(x, y, r);
        long duration = (System.nanoTime() - startTime) / 1_000_000;

        HitResult hr = new HitResult(x, y, r, hit, duration);

        ServletContext ctx = getServletContext();
        Object obj = ctx.getAttribute("results");
        if (obj instanceof java.util.List) {
            @SuppressWarnings("unchecked")
            java.util.List<HitResult> list = (java.util.List<HitResult>) obj;
            synchronized (list) {
                list.add(0, hr);
                if (list.size() > 100) {
                    list.remove(list.size() - 1);
                }
            }
        }

        return hr;
    }

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
            return x * x + y * y <= rad * rad;
        }
        return false;
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        process(req, resp);
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        process(req, resp);
    }
}