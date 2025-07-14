import React, { useState, useEffect } from 'react';
import { addTransaction, fetchCurrentPrices } from '../api';
import { FaBitcoin, FaEthereum, FaPlus, FaMinus, FaSync, FaDollarSign } from 'react-icons/fa';
import './AddTransaction.css';

const AddTransaction = ({ onTransactionAdded, onRefresh }) => {
  const [formData, setFormData] = useState({
    coin: 'bitcoin',
    type: 'buy',
    amount: '',
    dollarAmount: '',
    price: '',
    date: new Date().toISOString().split('T')[0],
    useCurrentPrice: true,
    inputMode: 'crypto' // 'crypto' or 'dollar'
  });
  
  const [currentPrices, setCurrentPrices] = useState({ bitcoin: 0, ethereum: 0 });
  const [loading, setLoading] = useState(false);
  const [priceLoading, setPriceLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  // Fetch current prices on component mount
  useEffect(() => {
    loadCurrentPrices();
  }, []);

  // Update price when coin changes and useCurrentPrice is true
  useEffect(() => {
    if (formData.useCurrentPrice && currentPrices[formData.coin]) {
      setFormData(prev => ({
        ...prev,
        price: currentPrices[formData.coin].toString()
      }));
    }
  }, [formData.coin, formData.useCurrentPrice, currentPrices]);

  const loadCurrentPrices = async () => {
    setPriceLoading(true);
    try {
      const prices = await fetchCurrentPrices();
      setCurrentPrices(prices);
      
      // Set initial price if useCurrentPrice is true
      if (formData.useCurrentPrice) {
        setFormData(prev => ({
          ...prev,
          price: prices[prev.coin].toString()
        }));
      }
    } catch (error) {
      console.error('Error fetching current prices:', error);
      setMessage('Failed to fetch current prices');
    } finally {
      setPriceLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (name === 'useCurrentPrice') {
      setFormData(prev => ({
        ...prev,
        [name]: checked,
        price: checked ? currentPrices[prev.coin].toString() : ''
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleDollarAmountChange = (e) => {
    const dollarAmount = e.target.value;
    const price = parseFloat(formData.price) || 0;
    
    setFormData(prev => ({
      ...prev,
      dollarAmount: dollarAmount,
      amount: price > 0 ? (parseFloat(dollarAmount) / price).toString() : ''
    }));
  };

  const calculateTransactionValue = () => {
    const amount = parseFloat(formData.amount) || 0;
    const price = parseFloat(formData.price) || 0;
    return amount * price;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      // Validate form data
      if (!formData.amount || !formData.price || !formData.date) {
        throw new Error('Please fill in all required fields');
      }

      if (parseFloat(formData.amount) <= 0) {
        throw new Error('Amount must be greater than 0');
      }

      if (parseFloat(formData.price) <= 0) {
        throw new Error('Price must be greater than 0');
      }

      // Prepare transaction data
      const transactionData = {
        coin: formData.coin,
        type: formData.type,
        amount: parseFloat(formData.amount),
        price: parseFloat(formData.price),
        date: formData.date
      };

      const response = await addTransaction(transactionData);
      
      if (response.error) {
        throw new Error(response.error);
      }

      setMessage(`${formData.type === 'buy' ? 'Purchase' : 'Sale'} transaction added successfully!`);
      
      // Reset form
      setFormData({
        coin: 'bitcoin',
        type: 'buy',
        amount: '',
        dollarAmount: '',
        price: formData.useCurrentPrice ? currentPrices.bitcoin.toString() : '',
        date: new Date().toISOString().split('T')[0],
        useCurrentPrice: formData.useCurrentPrice,
        inputMode: 'crypto'
      });

      // Notify parent components
      if (onTransactionAdded) {
        onTransactionAdded(response.transaction);
      }
      if (onRefresh) {
        onRefresh();
      }

      // Auto-close after successful submission
      setTimeout(() => {
        setIsOpen(false);
        setMessage('');
      }, 2000);

    } catch (error) {
      setMessage(error.message || 'Failed to add transaction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-transaction-container">
      <button 
        className="add-transaction-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        <FaPlus />
        Add Manual Transaction
      </button>

      {isOpen && (
        <div className="add-transaction-modal">
          <div className="add-transaction-content">
            <div className="modal-header">
              <h3>Add Manual Transaction</h3>
              <button 
                className="close-button"
                onClick={() => setIsOpen(false)}
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit} className="transaction-form">
              {/* Transaction Type */}
              <div className="form-group">
                <label>Transaction Type</label>
                <div className="transaction-type-selector">
                  <button
                    type="button"
                    className={`type-button ${formData.type === 'buy' ? 'active buy' : ''}`}
                    onClick={() => setFormData(prev => ({ ...prev, type: 'buy' }))}
                  >
                    <FaPlus /> Buy
                  </button>
                  <button
                    type="button"
                    className={`type-button ${formData.type === 'sell' ? 'active sell' : ''}`}
                    onClick={() => setFormData(prev => ({ ...prev, type: 'sell' }))}
                  >
                    <FaMinus /> Sell
                  </button>
                </div>
              </div>

              {/* Cryptocurrency Selection */}
              <div className="form-group">
                <label>Cryptocurrency</label>
                <div className="coin-selector">
                  <button
                    type="button"
                    className={`coin-button ${formData.coin === 'bitcoin' ? 'active' : ''}`}
                    onClick={() => setFormData(prev => ({ ...prev, coin: 'bitcoin' }))}
                  >
                    <FaBitcoin /> Bitcoin
                  </button>
                  <button
                    type="button"
                    className={`coin-button ${formData.coin === 'ethereum' ? 'active' : ''}`}
                    onClick={() => setFormData(prev => ({ ...prev, coin: 'ethereum' }))}
                  >
                    <FaEthereum /> Ethereum
                  </button>
                </div>
              </div>

              {/* Input Mode Selection */}
              <div className="form-group">
                <label>Input Method</label>
                <div className="coin-selector">
                  <button
                    type="button"
                    className={`coin-button ${formData.inputMode === 'crypto' ? 'active' : ''}`}
                    onClick={() => setFormData(prev => ({ ...prev, inputMode: 'crypto', dollarAmount: '', amount: '' }))}
                  >
                    {formData.coin === 'bitcoin' ? <FaBitcoin /> : <FaEthereum />} 
                    Crypto Amount
                  </button>
                  <button
                    type="button"
                    className={`coin-button ${formData.inputMode === 'dollar' ? 'active' : ''}`}
                    onClick={() => setFormData(prev => ({ ...prev, inputMode: 'dollar', dollarAmount: '', amount: '' }))}
                  >
                    <FaDollarSign /> Dollar Amount
                  </button>
                </div>
              </div>

              {/* Amount Input - Crypto or Dollar */}
              {formData.inputMode === 'crypto' ? (
                <div className="form-group">
                  <label>Amount ({formData.coin === 'bitcoin' ? 'BTC' : 'ETH'})</label>
                  <input
                    type="number"
                    name="amount"
                    value={formData.amount}
                    onChange={handleInputChange}
                    step="0.00000001"
                    min="0"
                    placeholder="0.00000000"
                    required
                  />
                </div>
              ) : (
                <div className="form-group">
                  <label>Dollar Amount (USD)</label>
                  <input
                    type="number"
                    name="dollarAmount"
                    value={formData.dollarAmount}
                    onChange={handleDollarAmountChange}
                    step="0.01"
                    min="0"
                    placeholder="0.00"
                    required
                  />
                  {formData.dollarAmount && formData.price && (
                    <div className="current-price-display">
                      Equivalent: {(parseFloat(formData.dollarAmount) / parseFloat(formData.price)).toFixed(8)} {formData.coin === 'bitcoin' ? 'BTC' : 'ETH'}
                    </div>
                  )}
                </div>
              )}

              {/* Price */}
              <div className="form-group">
                <label>Price per {formData.coin === 'bitcoin' ? 'BTC' : 'ETH'} (USD)</label>
                <div className="price-input-group">
                  <div className="price-controls">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        name="useCurrentPrice"
                        checked={formData.useCurrentPrice}
                        onChange={handleInputChange}
                      />
                      Use current price
                    </label>
                    <button
                      type="button"
                      className="refresh-price-btn"
                      onClick={loadCurrentPrices}
                      disabled={priceLoading}
                    >
                      <FaSync className={priceLoading ? 'fa-spin' : ''} />
                    </button>
                  </div>
                  <input
                    type="number"
                    name="price"
                    value={formData.price}
                    onChange={handleInputChange}
                    step="0.01"
                    min="0"
                    placeholder="0.00"
                    disabled={formData.useCurrentPrice}
                    required
                  />
                </div>
                {currentPrices[formData.coin] > 0 && (
                  <div className="current-price-display">
                    Current {formData.coin === 'bitcoin' ? 'BTC' : 'ETH'} price: ${currentPrices[formData.coin].toLocaleString()}
                  </div>
                )}
              </div>

              {/* Date */}
              <div className="form-group">
                <label>Transaction Date</label>
                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleInputChange}
                  max={new Date().toISOString().split('T')[0]}
                  required
                />
              </div>

              {/* Transaction Value Display */}
              {formData.amount && formData.price && (
                <div className="transaction-summary">
                  <div className="summary-item">
                    <span className="summary-label">Transaction Value:</span>
                    <span className="summary-value">
                      <FaDollarSign />
                      {calculateTransactionValue().toLocaleString()}
                    </span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Type:</span>
                    <span className={`summary-value ${formData.type}`}>
                      {getTransactionIcon(formData.type)}
                      {formData.type.toUpperCase()}
                    </span>
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <div className="form-actions">
                <button
                  type="submit"
                  className={`submit-btn ${formData.type}`}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <FaSync className="fa-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      {getTransactionIcon(formData.type)}
                      {formData.type === 'buy' ? 'Add Purchase' : 'Add Sale'}
                    </>
                  )}
                </button>
              </div>

              {/* Message Display */}
              {message && (
                <div className={`message ${message.includes('successfully') ? 'success' : 'error'}`}>
                  {message}
                </div>
              )}
            </form>
          </div>
        </div>
      )}
    </div>
  );

  function getTransactionIcon(type) {
    return type === 'buy' ? 
      <FaPlus style={{ color: '#28a745' }} /> : 
      <FaMinus style={{ color: '#dc3545' }} />;
  }
};

export default AddTransaction;
