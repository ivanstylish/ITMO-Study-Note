import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import StartPage from './pages/StartPage';
import MainPage from './pages/MainPage';
import './css/style.css';

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<StartPage />} />
                <Route path="/main" element={<ProtectedRoute><MainPage /></ProtectedRoute>} />
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </Router>
    );
};

const ProtectedRoute = ({ children }) => {
    const isAuthenticated = useSelector(state => state.auth.isAuthenticated);
    return isAuthenticated ? children : <Navigate to="/" replace />;
};

export default App;