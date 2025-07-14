import React, { useState, useEffect, useCallback } from 'react';
import Portfolio from './pages/Portfolio';
import PortfolioChart from './components/PortfolioChart';
import TransactionHistory from './components/TransactionHistory';
import DailyProfitLoss from './components/DailyProfitLoss';
import LiveStats from './components/LiveStats';
import AddTransaction from './components/AddTransaction';
import { fetchPortfolio, fetchLiveProfitLoss, fetchDailyProfitLoss, fetchTransactions, fetchPortfolioHistory } from './api';
import { FaBitcoin, FaEthereum, FaSun, FaMoon, FaSync } from 'react-icons/fa';
import './App.css';

function App() {
  const [portfolioData, setPortfolioData] = useState(null);
  const [liveStatsData, setLiveStatsData] = useState(null);
  const [dailyProfitData, setDailyProfitData] = useState(null);
  const [transactionsData, setTransactionsData] = useState(null);
  const [portfolioHistoryData, setPortfolioHistoryData] = useState(null);
  const [currentPrices, setCurrentPrices] = useState({ btc: 0, eth: 0 });
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : false;
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Toggle dark mode
  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem('darkMode', JSON.stringify(newMode));
    document.documentElement.setAttribute('data-theme', newMode ? 'dark' : 'light');
  };

  // Set theme on mount
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  // Extract current prices from portfolio data
  useEffect(() => {
    if (portfolioData) {
      const btcPrice = portfolioData.btc_held > 0 ? portfolioData.btc_value / portfolioData.btc_held : 0;
      const ethPrice = portfolioData.eth_held > 0 ? portfolioData.eth_value / portfolioData.eth_held : 0;
      setCurrentPrices({ btc: btcPrice, eth: ethPrice });
    }
  }, [portfolioData]);

  // Global refresh function that updates all data
  const refreshAllData = useCallback(async () => {
    setIsRefreshing(true);
    setLoading(true);
    try {
      const [portfolio, liveStats, dailyProfit, transactions, portfolioHistory] = await Promise.all([
        fetchPortfolio(),
        fetchLiveProfitLoss(),
        fetchDailyProfitLoss(),
        fetchTransactions(),
        fetchPortfolioHistory()
      ]);
      
      setPortfolioData(portfolio);
      setLiveStatsData(liveStats);
      setDailyProfitData(dailyProfit);
      setTransactionsData(transactions);
      setPortfolioHistoryData(portfolioHistory);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // Load all data when app first mounts
  useEffect(() => {
    refreshAllData();
    
    // Set up automatic refresh every 5 minutes for more real-time data
    const interval = setInterval(() => {
      refreshAllData();
    }, 300000); // 5 minutes

    return () => clearInterval(interval);
  }, [refreshAllData]);

  if (loading && !portfolioData) return <div className="spinner"></div>;

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">Crypto Investment Tracker</h1>
          
          <div className="header-controls">
            {/* Current Prices */}
            <div className="current-prices">
              <div className="price-item">
                <FaBitcoin className="price-icon" style={{ color: '#f7931a' }} />
                <span className="price-value">${currentPrices.btc.toLocaleString()}</span>
              </div>
              <div className="price-item">
                <FaEthereum className="price-icon" style={{ color: '#627eea' }} />
                <span className="price-value">${currentPrices.eth.toLocaleString()}</span>
              </div>
            </div>

            {/* Global Refresh Button */}
            <button 
              onClick={refreshAllData} 
              className={`btn btn-primary global-refresh ${isRefreshing ? 'pulse' : ''}`}
              disabled={isRefreshing}
            >
              <FaSync className={isRefreshing ? 'fa-spin' : ''} />
              {isRefreshing ? 'Refreshing...' : 'Refresh All Data'}
            </button>

            {/* Theme Toggle */}
            <button 
              onClick={toggleDarkMode}
              className="theme-toggle"
              title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {darkMode ? <FaSun /> : <FaMoon />}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Live Stats Section */}
        <section className="section fade-in">
          <LiveStats data={liveStatsData} onRefresh={refreshAllData} />
        </section>

        {/* Daily Profit/Loss Section */}
        <section className="section fade-in">
          <DailyProfitLoss data={dailyProfitData} onRefresh={refreshAllData} />
        </section>

        {/* Portfolio Section */}
        <section className="section fade-in">
          <Portfolio data={portfolioData} onRefresh={refreshAllData} />
        </section>

        {/* Charts Section */}
        <section className="section fade-in">
          <div className="section-header">
            <h2 className="section-title">Portfolio Analytics</h2>
            <button 
              onClick={refreshAllData} 
              className="btn btn-success btn-sm"
              disabled={isRefreshing}
            >
              <FaSync className={isRefreshing ? 'fa-spin' : ''} />
              Refresh Charts
            </button>
          </div>
          <div className="charts-container">
            <div className="chart-section">
              <h3 className="chart-title">Portfolio Value Over Time</h3>
              <PortfolioChart data={portfolioHistoryData} onRefresh={refreshAllData} />
            </div>
            <div className="chart-section">
              <h3 className="chart-title">Profit/Loss Trend</h3>
              <PortfolioChart data={portfolioHistoryData} onRefresh={refreshAllData} />
            </div>
          </div>
        </section>

        {/* Manual Transaction Section */}
        <section className="section fade-in">
          <div className="section-header">
            <h2 className="section-title">Manual Transactions</h2>
            <p className="section-description">
              Add buy/sell transactions to track your manual trades with real-time profit/loss calculations
            </p>
          </div>
          <AddTransaction onRefresh={refreshAllData} />
        </section>

        {/* Transaction History Section */}
        <section className="section fade-in">
          <div className="section-header">
            <h2 className="section-title">Transaction History</h2>
            <button 
              onClick={refreshAllData} 
              className="btn btn-success btn-sm"
              disabled={isRefreshing}
            >
              <FaSync className={isRefreshing ? 'fa-spin' : ''} />
              Refresh History
            </button>
          </div>
          <div className="table-container">
            <TransactionHistory data={transactionsData} onRefresh={refreshAllData} />
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
