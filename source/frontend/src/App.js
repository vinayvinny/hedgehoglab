import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

  // Fetch items on component mount
  useEffect(() => {
    fetchItems();
  }, []);

  // Get all items from the API
  const fetchItems = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/items`);
      setItems(response.data);
      setError(null);
    } catch (err) {
      setError('Error fetching items. Please try again later.');
      console.error('Error fetching items:', err);
    } finally {
      setLoading(false);
    }
  };

  // Add a new item
  const addItem = async (e) => {
    e.preventDefault();
    if (!newItem.trim()) return;

    try {
      const response = await axios.post(`${API_URL}/items`, { name: newItem });
      setItems([...items, response.data]);
      setNewItem('');
      setError(null);
    } catch (err) {
      setError('Error adding item. Please try again.');
      console.error('Error adding item:', err);
    }
  };

  // Delete an item
  const deleteItem = async (id) => {
    try {
      await axios.delete(`${API_URL}/items/${id}`);
      setItems(items.filter(item => item.id !== id));
      setError(null);
    } catch (err) {
      setError('Error deleting item. Please try again.');
      console.error('Error deleting item:', err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Three-Tier Application Demo</h1>
        <p>React Frontend + Flask API + PostgreSQL Database</p>
      </header>

      <main>
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={addItem} className="item-form">
          <input
            type="text"
            value={newItem}
            onChange={(e) => setNewItem(e.target.value)}
            placeholder="Add a new item"
            className="item-input"
          />
          <button type="submit" className="add-button">Add Item</button>
        </form>

        <div className="items-container">
          <h2>Items List</h2>
          {loading ? (
            <p>Loading items...</p>
          ) : items.length === 0 ? (
            <p>No items found. Add some items above!</p>
          ) : (
            <ul className="items-list">
              {items.map((item) => (
                <li key={item.id} className="item">
                  <span>{item.name}</span>
                  <button 
                    onClick={() => deleteItem(item.id)}
                    className="delete-button"
                  >
                    Delete
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;