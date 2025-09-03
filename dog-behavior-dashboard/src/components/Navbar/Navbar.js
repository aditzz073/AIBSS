import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          <img src="/dog.png" alt="DogCare" className="nav-logo-img" />
        </Link>
        
        <div className={`nav-menu ${isMenuOpen ? 'active' : ''}`}>
          <Link 
            to="/" 
            className={`nav-link ${isActive('/')}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Home
          </Link>
          <Link 
            to="/analysis" 
            className={`nav-link ${isActive('/analysis')}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Upload Image
          </Link>
          <Link 
            to="/video-analysis" 
            className={`nav-link ${isActive('/video-analysis')}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Upload Video
          </Link>
          <Link 
            to="/live" 
            className={`nav-link ${isActive('/live')}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Live Feed
          </Link>
          <Link 
            to="/dashboard" 
            className={`nav-link ${isActive('/dashboard')}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Dashboard
          </Link>
          <Link 
            to="/about" 
            className={`nav-link ${isActive('/about')}`}
            onClick={() => setIsMenuOpen(false)}
          >
            About
          </Link>
        </div>
        
        <Link to="/analysis" className="nav-cta-button">
          Try Now
        </Link>
        
        <div className="nav-toggle" onClick={toggleMenu}>
          <span className="bar"></span>
          <span className="bar"></span>
          <span className="bar"></span>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
