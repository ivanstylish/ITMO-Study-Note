import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { login, register } from "../slices/authSlice";

const Clock = () => {
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const interval = setInterval(() => {
            setTime(new Date());
        }, 10000);
        return () => clearInterval(interval);
    }, []);

    const formatDateTime = (date) => {
        const timePart = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const datePart = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        return { timePart, datePart };
    };

    const { timePart, datePart } = formatDateTime(time);

    return (
        <div className="clock-card card">
            <h2>Time Clock</h2>
            <div className="clock-display">
                {timePart}<br/>
                <span style={{fontSize: '0.5em', fontWeight: 'normal'}}>{datePart}</span>
            </div>
            <p className="clock-note">Updates every 10 seconds.</p>
        </div>
    );
};

const StartPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoginMode, setIsLoginMode] = useState(true);
    const [message, setMessage] = useState('');
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const { isAuthenticated, status, error } = useSelector(state => state.auth);

    useEffect(() => {
        if (isAuthenticated) {
            navigate('/main');
        }
        if (status === 'registered') {
            setMessage('Registration successful! You can now log in.');
            setIsLoginMode(true);
        }
        if (error) {
            setMessage(error);
        }
    }, [isAuthenticated, status, navigate, error]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');

        if (isLoginMode) {
            dispatch(login({ username, password }))
                .unwrap()
                .then(() => {
                    setMessage('Login successful! Redirecting...');
                    setTimeout(() => navigate('/main'), 1000);
                })
                .catch((err) => {
                    setMessage(typeof err === 'string' ? err : 'Login failed: Invalid credentials');
                });
        } else {
            dispatch(register({ username, password }))
                .unwrap()
                .then(() => {
                    setMessage('Registration successful! Please log in.');
                    setIsLoginMode(true);
                })
                .catch((err) => {
                    setMessage(err || 'Registration failed');
                });
        }
    };

    return (
        <div className="page-container">
            <header className="header">
                <h1>Лабораторная работа 4</h1>
                <div>
                    ФИО: Чжун Цзяцзюнь<br/>
                    Группа: P3210<br/>
                    Вариант: 2222
                </div>
            </header>

            <div className="main-content">
                <Clock />

                <div className="card">
                    <h2>{isLoginMode ? 'Login' : 'Register'}</h2>
                    <form onSubmit={handleSubmit}>
                        <div className="form-row">
                            <label className="form-label">Username:</label>
                            <input
                                className="text-input"
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>
                        <div className="form-row">
                            <label className="form-label">Password:</label>
                            <input
                                className="text-input"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        {message && (
                            <div className="messages">
                                <span className={status === 'failed' || error ? 'error-message' : 'message-info'}>
                                    {message}
                                </span>
                            </div>
                        )}

                        <div className="button-group">
                            <button type="submit" className="btn-submit">
                                {isLoginMode ? 'Log In' : 'Register'}
                            </button>
                            <button
                                type="button"
                                className="btn-switch"
                                onClick={() => {
                                    setIsLoginMode(!isLoginMode);
                                    setMessage('');
                                }}
                            >
                                {isLoginMode ? 'Switch to Register' : 'Switch to Login'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            <footer className="footer">Lab4</footer>
        </div>
    );
};

export default StartPage;