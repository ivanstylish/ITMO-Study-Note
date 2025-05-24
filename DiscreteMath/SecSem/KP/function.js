
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Graph of fuzzy reasoning affiliation function</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/recharts/2.8.0/Recharts.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.5/babel.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .chart-section { margin: 40px 0; }
        .chart-container { height: 400px; margin: 20px 0; }
        h1 { text-align: center; color: #333; }
        h2 { color: #555; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .description { font-size: 14px; color: #666; margin-top: 10px; }
        .example { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-top: 20px; }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } = Recharts;

        const MembershipFunctions = () => {
            // 预算隶属度函数数据
            const budgetData = [];
            for (let x = 0; x <= 1200; x += 20) {
                let lb = 0, mb = 0, hb = 0;
                
                if (x <= 600) {
                    lb = 1 - x/600;
                }
                
                if (x <= 600) {
                    mb = x/600;
                } else if (x <= 1200) {
                    mb = 2 - x/600;
                }
                
                if (x >= 600 && x <= 1200) {
                    hb = x/600 - 1;
                }
                
                budgetData.push({
                    x: x,
                    LB: Math.max(0, lb),
                    MB: Math.max(0, mb),
                    HB: Math.max(0, hb)
                });
            }

            // 性能需求隶属度函数数据
            const performanceData = [];
            for (let y = 0; y <= 1; y += 0.02) {
                let lp = 0, mp = 0, hp = 0;
                
                if (y <= 0.5) {
                    lp = 1 - 2*y;
                }
                
                if (y <= 0.5) {
                    mp = 2*y;
                } else if (y <= 1) {
                    mp = 2 - 2*y;
                }
                
                if (y >= 0.5 && y <= 1) {
                    hp = 2*y - 1;
                }
                
                performanceData.push({
                    x: y,
                    LP: Math.max(0, lp),
                    MP: Math.max(0, mp),
                    HP: Math.max(0, hp)
                });
            }

            // 推荐价格隶属度函数数据
            const priceData = [];
            for (let z = 0; z <= 1200; z += 20) {
                let ec = 0, bu = 0, mi = 0, pr = 0, fl = 0;
                
                if (z <= 300) {
                    ec = 1 - z/300;
                }
                
                if (z <= 300) {
                    bu = z/300;
                } else if (z <= 600) {
                    bu = 2 - z/300;
                }
                
                if (z >= 300 && z <= 600) {
                    mi = z/300 - 1;
                } else if (z >= 600 && z <= 900) {
                    mi = 3 - z/300;
                }
                
                if (z >= 600 && z <= 900) {
                    pr = z/300 - 2;
                } else if (z >= 900 && z <= 1200) {
                    pr = 4 - z/300;
                }
                
                if (z >= 900 && z <= 1200) {
                    fl = z/300 - 3;
                }
                
                priceData.push({
                    x: z,
                    EC: Math.max(0, ec),
                    BU: Math.max(0, bu),
                    MI: Math.max(0, mi),
                    PR: Math.max(0, pr),
                    FL: Math.max(0, fl)
                });
            }

            return (
                <div className="container">
                    <h1>Graph of Fuzzy Reasoning Membership Functions</h1>
                    
                    <div className="chart-section">
                        <h2>1. User Budget Membership Function</h2>
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={budgetData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis 
                                        dataKey="x" 
                                        label={{ value: 'Budget (US$)', position: 'insideBottom', offset: -10 }}
                                    />
                                    <YAxis 
                                        label={{ value: 'Degree of Membership', angle: -90, position: 'insideLeft' }}
                                        domain={[0, 1]}
                                    />
                                    <Tooltip formatter={(value, name) => [value.toFixed(2), name]} />
                                    <Legend />
                                    <Line type="monotone" dataKey="LB" stroke="#FF6B6B" strokeWidth={2} name="Low Budget (LB)" dot={false} />
                                    <Line type="monotone" dataKey="MB" stroke="#4ECDC4" strokeWidth={2} name="Medium Budget (MB)" dot={false} />
                                    <Line type="monotone" dataKey="HB" stroke="#45B7D1" strokeWidth={2} name="High Budget (HB)" dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                        <p className="description">
                            Function definitions: LB: 1-x/600 (0≤x≤600), MB: Triangle (0-1200), HB: x/600-1 (600≤x≤1200)
                        </p>
                    </div>

                    <div className="chart-section">
                        <h2>2. Performance Requirement Membership Function</h2>
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={performanceData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis 
                                        dataKey="x" 
                                        label={{ value: 'Level of Performance Requirements', position: 'insideBottom', offset: -10 }}
                                        tickFormatter={(value) => value.toFixed(1)}
                                    />
                                    <YAxis 
                                        label={{ value: 'Degree of Membership', angle: -90, position: 'insideLeft' }}
                                        domain={[0, 1]}
                                    />
                                    <Tooltip formatter={(value, name) => [value.toFixed(2), name]} />
                                    <Legend />
                                    <Line type="monotone" dataKey="LP" stroke="#FF9F43" strokeWidth={2} name="Low Performance (LP)" dot={false} />
                                    <Line type="monotone" dataKey="MP" stroke="#10AC84" strokeWidth={2} name="Medium Performance (MP)" dot={false} />
                                    <Line type="monotone" dataKey="HP" stroke="#5F27CD" strokeWidth={2} name="High Performance (HP)" dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                        <p className="description">
                            Function definitions: LP: 1-2y (0≤y≤0.5), MP: triangle (0-1), HP: 2y-1 (0.5≤y≤1)
                        </p>
                    </div>

                    <div className="chart-section">
                        <h2>3. Recommended Price Membership Function</h2>
                        <div className="chart-container">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={priceData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis 
                                        dataKey="x" 
                                        label={{ value: 'Recommended Price (USD)', position: 'insideBottom', offset: -10 }}
                                    />
                                    <YAxis 
                                        label={{ value: 'Degree of Membership', angle: -90, position: 'insideLeft' }}
                                        domain={[0, 1]}
                                    />
                                    <Tooltip formatter={(value, name) => [value.toFixed(2), name]} />
                                    <Legend />
                                    <Line type="monotone" dataKey="EC" stroke="#e74c3c" strokeWidth={2} name="Economy (EC)" dot={false} />
                                    <Line type="monotone" dataKey="BU" stroke="#f39c12" strokeWidth={2} name="Budget (BU)" dot={false} />
                                    <Line type="monotone" dataKey="MI" stroke="#2ecc71" strokeWidth={2} name="Mid-range (MI)" dot={false} />
                                    <Line type="monotone" dataKey="PR" stroke="#3498db" strokeWidth={2} name="High-end (PR)" dot={false} />
                                    <Line type="monotone" dataKey="FL" stroke="#9b59b6" strokeWidth={2} name="Flagship (FL)" dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                        <p className="description">
                            EC: Economy (0-300), BU: Budget (0-600), MI: Mid-range (300-900), PR: High-end (600-1200), FL: Flagship (900-1200)
                        </p>
                    </div>

                    <div className="example">
                        <h2>Calculation Example</h2>
                        <p><strong>Input:</strong> User budget $800, performance requirements 0.7</p>
                        <p><strong>Membership calculation:</strong></p>
                        <ul>
                            <li>M<sub>MB</sub>(800) = 0.67, M<sub>HB</sub>(800) = 0.33</li>
                            <li>M<sub>MP</sub>(0.7) = 0.6, M<sub>HP</sub>(0.7) = 0.4</li>
                        </ul>
                        <p><strong>Rule Activation:</strong></p>
                        <ul>
                            <li>Medium Budget & Medium Performance → Mid-range Phone (Strength: 0.6)</li>
                            <li>Medium Budget & High Performance → High-end Phone (Strength: 0.4)</li>
                            <li>High Budget & Medium Performance → High-end Phone (Strength: 0.33)</li>
                            <li>High Budget & High Performance → Flagship Phone (Strength: 0.33)</li>
                        </ul>
                        <p><strong>Result:</strong> Recommended Price <span style={{color: '#2ecc71', fontWeight: 'bold'}}>$600</span></p>
                    </div>
                </div>
            );
        };

        ReactDOM.render(<MembershipFunctions />, document.getElementById('root'));
    </script>
</body>
</html>
