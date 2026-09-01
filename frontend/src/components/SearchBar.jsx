import { useState, useEffect } from "react";
import api from "../services/api";

export default function SearchBar({ onSearch }) {
  const [query, setQuery] = useState("");
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState("");

  useEffect(() => {
    api.get("/categories/active")
      .then((res) => setCategories(res.data.items || []))
      .catch(() => {});
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({ search: query, category });
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Search products..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="search-input"
      />
      <select
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        className="search-select"
      >
        <option value="">All Categories</option>
        {categories.map((cat) => (
          <option key={cat.id} value={cat.name}>{cat.name}</option>
        ))}
      </select>
      <button type="submit" className="btn btn-primary">Search</button>
    </form>
  );
}
