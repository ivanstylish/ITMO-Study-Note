<%@ page import="servlets.HitResult" %>
<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%
    java.util.List results = (java.util.List)application.getAttribute("results");
%>

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Area Check</title>
    <link rel="stylesheet" href="
<%=request.getContextPath()%>/style/style.css">
    <script src="<%=request.getContextPath()%>/script/form.js" defer>
    </script>
</head>
<body>
<header class="page-header">
    <div class="title">Лабораторная работа #2</div>
    <div class="subtitle">ФИО: Чжун Цзяцзюнь &nbsp; Группа: P3210 &nbsp; Вариант: 1891</div>
</header>

<main class="main-center">
    <section class="card form-card">
        <h3>Param input</h3>
        <form id="mainForm" onsubmit="return false;">
            <div class="field">
                <label>X Coordinate:</label>
                <div class="x-grid">
                    <label><input type="checkbox" name="x" value="-2"> -2</label>
                    <label><input type="checkbox" name="x" value="-1.5"> -1.5</label>
                    <label><input type="checkbox" name="x" value="-1"> -1</label>
                    <label><input type="checkbox" name="x" value="-0.5"> -0.5</label>
                    <label><input type="checkbox" name="x" value="0"> 0</label>
                    <label><input type="checkbox" name="x" value="0.5"> 0.5</label>
                    <label><input type="checkbox" name="x" value="1"> 1</label>
                    <label><input type="checkbox" name="x" value="1.5"> 1.5</label>
                    <label><input type="checkbox" name="x" value="2"> 2</label>
                </div>
            </div>

            <div class="field">
                <label>Y Coordinate:</label>
                <input id="y" name="y" type="text" placeholder="-5 .. 5">
            </div>

            <div class="field">
                <label>R radius:</label>
                <div class="r-buttons">
                    <button type="button" class="r-btn" data-r="1">1</button>
                    <button type="button" class="r-btn" data-r="1.5">1.5</button>
                    <button type="button" class="r-btn" data-r="2">2</button>
                    <button type="button" class="r-btn" data-r="2.5">2.5</button>
                    <button type="button" class="r-btn" data-r="3">3</button>
                </div>
                <div class="selected">Selected R: <span id="rValue">-</span></div>
            </div>

            <div class="actions">
                <button id="checkBtn" class="action-primary">Check point</button>
                <button id="clearBtn" class="action-secondary">Clear result</button>
            </div>
        </form>
    </section>

    <section class="card svg-card">
        <h3>Coordinate area</h3>
        <div class="svg-wrap">
            <svg xmlns="http://www.w3.org/2000/svg" id="svg" width="300" height="300" viewBox="0 0 300 300">
                <!--坐标轴-->
                <line x1="0" y1="150" x2="300" y2="150" stroke="#000720"></line>
                <line x1="150" y1="0" x2="150" y2="300" stroke="#000720"></line>
                <!--箭头-->
                <polygon points="300,150 295,145 295,155" fill="#000720"></polygon>
                <polygon points="150,0 145,5 155,5" fill="#000720"></polygon>

                <g id="axisMarks"></g>

                <g id="shapes"></g>
            </svg>
        </div>
    </section>
</main>

    <section class="card result-card" id="resultCard">
        <h3>History Result</h3>
        <div class="table-wrap">
        <table class="results" id="resultsTable">
            <thead>
            <tr>
                <th>Time</th>
                <th>X</th>
                <th>Y</th>
                <th>R</th>
                <th>Hit</th>
            </tr>
            </thead>
            <tbody>
            <% if (results != null) {
                for (Object o : results) {
                    HitResult hr = (HitResult) o;
            %>
                <tr>
                    <td><%= hr.getTime()%></td>
                    <td><%= hr.getX() %></td>
                    <td><%= hr.getY() %></td>
                    <td><%= hr.getR() %></td>
                    <td><%= hr.isHit() ? "YES":"NO" %></td>
                </tr>
            <%    }
                } %>
            </tbody>
        </table>
    </div>
    </section>

    <input type="hidden" id="savedPointsJson" value='<%
      if (results != null && !results.isEmpty()) {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        boolean first = true;
        for (Object o : results) {
          HitResult hr=(HitResult) o;
          if (!first) sb.append(",");
          sb.append("{\"x\":").append(hr.getX()).append(",\"y\":").append(hr.getY()).append(",\"r\":").append(hr.getR()).append(",\"hit\":").append(hr.isHit()).append("}");
          first=false;
        }
        sb.append("]");
        out.print(sb.toString());
      } else out.print("[]");
  %>' />
</body>
</html>