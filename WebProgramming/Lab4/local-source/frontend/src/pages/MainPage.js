import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import GraphComponent from '../components/GraphComponent';
import ResultTable from '../components/ResultTable';
import { fetchResults, checkPoint, setR, clearRemoteResults } from '../slices/pointSlice';
import { logout } from '../slices/authSlice';

const MainPage = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const { list: results, r: currentR } = useSelector(state => state.points);

    const [x, setX] = useState(0);
    const [y, setY] = useState('');
    const [xError, setXError] = useState('');
    const [yError, setYError] = useState('');
    const [rError, setRError] = useState('');
    const [showClearModal, setShowClearModal] = useState(false);

    const xOptions = [-3, -2, -1, 0, 1, 2, 3, 4, 5];
    const rOptions = [-3, -2, -1, 0, 1, 2, 3, 4, 5];

    useEffect(() => {
        dispatch(fetchResults());
    }, [dispatch]);

    const handleFormSubmit = (e) => {
        e.preventDefault();

        setXError('');
        setYError('');
        setRError('');

        const numY = parseFloat(y);

        if (currentR <= 0) {
            setRError('R must be positive');
            return;
        }

        if (y === '' || isNaN(numY)) {
            setYError('Please enter Y value');
            return;
        }

        if (numY < -3 || numY > 3) {
            setYError('Y must be between -3 and 3');
            return;
        }

        dispatch(checkPoint({ x: parseFloat(x), y: numY, r: parseFloat(currentR) }))
            .unwrap()
            .then(() => {
                setY('');
            })
            .catch((error) => {
                setYError(String(error));
            });
    };

    const handleGraphClick = (clickedX, clickedY) => {
        if (currentR > 0) {
            dispatch(checkPoint({x: clickedX, y: clickedY, r: currentR}));
        } else {
            setRError('Please select R > 0');
        }
    };

    const confirmClear = () => {
        dispatch(clearRemoteResults());
        setShowClearModal(false);
    };

    const handleLogout = () => {
        dispatch(logout());
        navigate('/');
    };

    const handleRChange = (val) => {
        dispatch(setR(val));
        setRError('');
        if (val <= 0) {
            setRError('R must be positive');
        }
    };

    return (
        <div className="page-container">
            <div className="header">
                <h1>Web Lab 4 - Point Checker</h1>
                <button className="btn-danger" onClick={handleLogout}>Logout</button>
            </div>

            <div className="main-layout">
                <div className="card input-card">
                    <h2>Parameters</h2>
                    <form onSubmit={handleFormSubmit}>
                        <div className="form-section">
                            <label className="form-section-label"><strong>X Value:</strong></label>
                            <table className="custom-checkbox-table">
                                <tbody>
                                <tr>
                                    {xOptions.map(val => (
                                        <td key={val}>
                                            <label>
                                                <input
                                                    type="checkbox"
                                                    checked={x === val}
                                                    onChange={() => {
                                                        setX(val);
                                                        setXError('');
                                                    }}
                                                />
                                                {val}
                                            </label>
                                        </td>
                                    ))}
                                </tr>
                                </tbody>
                            </table>
                            {xError && <div style={{color: '#d32f2f', fontSize: '14px', marginTop: '5px'}}>{xError}</div>}
                        </div>

                        <div className="form-section">
                            <label className="form-section-label"><strong>Y Value (-3 to 3):</strong></label>
                            <input
                                type="text"
                                value={y}
                                onChange={(e) => {
                                    const val = e.target.value;
                                    if (val === '' || /^-?\d*\.?\d*$/.test(val)) {
                                        setY(val);
                                        setYError('');
                                    }
                                }}
                                placeholder="-3...3"
                                className="y-input"
                            />
                            {yError && <div style={{color: '#d32f2f', fontSize: '14px', marginTop: '5px'}}>{yError}</div>}
                        </div>

                        <div className="form-section">
                            <label className="form-section-label"><strong>Radius R:</strong></label>
                            <table className="custom-checkbox-table">
                                <tbody>
                                <tr>
                                    {rOptions.map(val => (
                                        <td key={val}>
                                            <label>
                                                <input
                                                    type="checkbox"
                                                    checked={currentR === val}
                                                    onChange={() => handleRChange(val)}
                                                />
                                                {val}
                                            </label>
                                        </td>
                                    ))}
                                </tr>
                                </tbody>
                            </table>
                            {rError && <div style={{color: '#d32f2f', fontSize: '14px', marginTop: '5px'}}>{rError}</div>}
                        </div>

                        <div className="button-row">
                            <button type="submit" className="btn-primary btn-flex">
                                Check Point
                            </button>
                            <button
                                type="button"
                                className="btn-danger btn-flex"
                                onClick={() => setShowClearModal(true)}
                            >
                                Clear History
                            </button>
                        </div>
                    </form>
                </div>

                <div className="card graph-card">
                    <h2>Graph (R = {currentR})</h2>
                    <GraphComponent
                        r={currentR}
                        results={results}
                        onMapClick={handleGraphClick}
                    />
                </div>
            </div>

            <div className="card">
                <h2>Results</h2>
                <ResultTable results={results} />
            </div>

            {showClearModal && (
                <div className="modal-overlay" onClick={() => setShowClearModal(false)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <h3>Confirm Action</h3>
                        <p>Are you sure you want to delete all points?</p>
                        <div className="modal-actions">
                            <button className="btn-cancel" onClick={() => setShowClearModal(false)}>
                                Cancel
                            </button>
                            <button className="btn-confirm" onClick={confirmClear}>
                                Yes, Clear All
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MainPage;