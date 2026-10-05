import React from 'react';

const ResultTable = ({ results }) => {
    return (
        <div className="history-container">
            {results && results.length > 0 ? (
                <table className="result-table">
                    <thead>
                    <tr>
                        <th>X</th>
                        <th>Y</th>
                        <th>R</th>
                        <th>HIT</th>
                        <th>Check Time</th>
                    </tr>
                    </thead>
                    <tbody>
                    {results.map((res, index) => (
                        <tr key={res.id || index} className={index % 2 === 0 ? 'table-row-even' : 'table-row-odd'}>
                            <td>{res.x.toFixed(3)}</td>
                            <td>{res.y.toFixed(3)}</td>
                            <td>{res.r.toFixed(3)}</td>
                            <td className={res.hit ? 'result-hit' : 'result-miss'}>
                                {res.hit ? 'HIT' : 'MISS'}
                            </td>
                            <td>{new Date(res.timestamp).toLocaleTimeString('ru-RU')}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            ) : (
                <p className="empty-message">No results to display.</p>
            )}
        </div>
    );
};

export default ResultTable;