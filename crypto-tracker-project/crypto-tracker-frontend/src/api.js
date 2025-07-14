const API_URL = import.meta.env.VITE_API_URL;

// Helper function to add cache-busting timestamp
const addCacheBuster = (url) => {
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}_t=${Date.now()}`;
};

export async function fetchPortfolio() {
  const res = await fetch(addCacheBuster(`${API_URL}/portfolio`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  return await res.json();
}

export async function addTransaction(transaction) {
  const res = await fetch(`${API_URL}/add_transaction`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(transaction),
  });
  return await res.json();
}

export async function fetchTransactions() {
  const res = await fetch(addCacheBuster(`${API_URL}/transactions`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  return await res.json();
}

export async function fetchDailyProfitLoss() {
  const res = await fetch(addCacheBuster(`${API_URL}/daily_profit_loss`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  return await res.json();
}

export async function fetchLiveProfitLoss() {
  const res = await fetch(addCacheBuster(`${API_URL}/live_profit_loss`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  if (!res.ok) throw new Error('Failed to fetch live profit/loss data');
  return await res.json();
}

export async function fetchPortfolioHistory() {
  const res = await fetch(addCacheBuster(`${API_URL}/portfolio_history?frequency=daily`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  return await res.json();
}

export async function fetchCurrentPrices() {
  const res = await fetch(addCacheBuster(`${API_URL}/current_prices`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  if (!res.ok) throw new Error('Failed to fetch current prices');
  return await res.json();
}

export async function fetchTransactionAnalysis() {
  const res = await fetch(addCacheBuster(`${API_URL}/transaction_analysis`), {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  if (!res.ok) throw new Error('Failed to fetch transaction analysis');
  return await res.json();
}
