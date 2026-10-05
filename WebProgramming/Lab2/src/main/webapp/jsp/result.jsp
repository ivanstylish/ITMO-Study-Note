<%@ page import="servlets.HitResult" %>
<%@ page import="java.util.List" %>
<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%
    List<HitResult> resultsList = (List<HitResult>) request.getAttribute("results");
    String err = (String) request.getAttribute("error");
%>

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Check Result</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'ARLRDBD', Arial, sans-serif;
        }

        body {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .result-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            max-width: 900px;
            width: 100%;
            border: 2px solid #e2e8f0;
        }

        h2 {
            color: #f41c52;
            margin-bottom: 1.5rem;
            font-size: 2rem;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .error-message {
            background: #fed7d7;
            color: #c53030;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border: 2px solid #feb2b2;
            text-align: center;
        }

        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            overflow: hidden;
        }

        .results-table thead {
            background: #f41c52;
            color: white;
        }

        .results-table th {
            padding: 15px;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .results-table td {
            padding: 12px 15px;
            text-align: center;
            border-bottom: 1px solid #eee;
            font-size: 15px;
        }

        .results-table tbody tr:hover {
            background: #f7fafc;
        }

        .results-table tbody tr:nth-child(even) {
            background: #f9f9f9;
        }

        .results-table tbody tr:nth-child(even):hover {
            background: #f0f4ff;
        }

        .hit-yes {
            color: #22c55e;
            font-weight: bold;
        }

        .hit-no {
            color: #ef4444;
            font-weight: bold;
        }

        .summary {
            background: #f0f4ff;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            border-left: 4px solid #f41c52;
        }

        .summary h3 {
            color: #f41c52;
            margin-bottom: 0.5rem;
            font-size: 1.2rem;
        }

        .summary p {
            color: #555;
            font-size: 1rem;
            margin: 0.3rem 0;
        }

        .no-data {
            color: #718096;
            padding: 2rem;
            text-align: center;
            font-size: 1.1rem;
        }

        .button-container {
            text-align: center;
            margin-top: 2rem;
        }

        .return-button {
            padding: 12px 40px;
            background: #f41c52;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(244, 28, 82, 0.4);
            transition: all 0.3s;
        }

        .return-button:hover {
            background: #dc0a41;
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(244, 28, 82, 0.6);
        }

        .return-button:active {
            transform: translateY(0);
        }
    </style>
</head>
<body>
<div class="result-container">
    <h2>Check Result</h2>

    <% if (err != null) { %>
    <div class="error-message">
        <strong>Error：</strong> <%= err %>
    </div>
    <% } else if (resultsList != null && !resultsList.isEmpty()) { %>

    <div class="summary">
        <h3>Submit Abstract</h3>
        <p>A total of <strong><%= resultsList.size() %></strong> points</p>
        <%
            long hitCount = resultsList.stream().filter(HitResult::isHit).count();
            long missCount = resultsList.size() - hitCount;
        %>
        <p>Hit：<span class="hit-yes"><%= hitCount %></span> times| Miss：<span class="hit-no"><%= missCount %></span> times</p>
    </div>

    <table class="results-table">
        <thead>
        <tr>
            <th>Time</th>
            <th>X</th>
            <th>Y</th>
            <th>R</th>
            <th>IsHit</th>
            <th>Duration(ms)</th>
        </tr>
        </thead>
        <tbody>
        <% for (HitResult hr : resultsList) { %>
        <tr>
            <td><%= hr.getTime() %></td>
            <td><%= hr.getX() %></td>
            <td><%= hr.getY() %></td>
            <td><%= hr.getR() %></td>
            <td class="<%= hr.isHit() ? "hit-yes" : "hit-no" %>">
                <%= hr.isHit() ? "YES" : "NO" %>
            </td>
            <td><%= hr.getDuration() %></td>
        </tr>
        <% } %>
        </tbody>
    </table>

    <% } else { %>
    <div class="no-data">
        No data available
    </div>
    <% } %>

    <div class="button-container">
        <form method="GET" action="app" style="display: inline;">
            <button type="submit" class="return-button">
                Return to form
            </button>
        </form>
    </div>
</div>
</body>
</html>