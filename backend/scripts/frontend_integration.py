"""
Frontend Integration Helper Script

This script helps to test the API endpoints and provides examples of how to integrate
the backend with the frontend React application.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL
API_BASE_URL = "https://backend-asn8.onrender.com"

def test_auth_endpoints():
    """Test authentication endpoints and print example code for frontend integration."""
    print("\n=== Authentication Endpoints ===")
    
    # Register example
    print("\n--- Register User Example ---")
    register_data = {
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
        "phone": "1234567890",
        "date_of_birth": "01/01/1990",
        "gender": "Male"
    }
    print("Frontend Integration Code:")
    print("""
// Register User
const registerUser = async (userData) => {
  try {
    const response = await fetch('https://backend-asn8.onrender.com/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    
    if (!response.ok) {
      throw new Error('Registration failed');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error during registration:', error);
    throw error;
  }
};
    """)
    
    # Login example
    print("\n--- Login User Example ---")
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    print("Frontend Integration Code:")
    print("""
// Login User
const loginUser = async (credentials) => {
  try {
    const response = await fetch('https://backend-asn8.onrender.com/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    const data = await response.json();
    
    // Store the token in localStorage
    localStorage.setItem('token', data.access_token);
    
    return data;
  } catch (error) {
    console.error('Error during login:', error);
    throw error;
  }
};
    """)

def test_user_endpoints():
    """Test user endpoints and print example code for frontend integration."""
    print("\n=== User Endpoints ===")
    
    # Get current user example
    print("\n--- Get Current User Example ---")
    print("Frontend Integration Code:")
    print("""
// Get Current User
const getCurrentUser = async () => {
  try {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const response = await fetch('https://backend-asn8.onrender.com/users/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('token');
        throw new Error('Authentication expired. Please login again.');
      }
      throw new Error('Failed to fetch user data');
    }
    
    const userData = await response.json();
    return userData;
  } catch (error) {
    console.error('Error fetching current user:', error);
    throw error;
  }
};
    """)
    
    # Update AuthContext example
    print("\n--- Update AuthContext Example ---")
    print("""
// AuthContext.tsx update example
import React, { createContext, useState, useEffect, useContext } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  user: any | null;
  login: (credentials: { username: string; password: string }) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Check if user is already logged in on component mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      
      if (!token) {
        setLoading(false);
        return;
      }
      
      try {
        const response = await fetch('https://backend-asn8.onrender.com/users/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          // Token is invalid or expired
          localStorage.removeItem('token');
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  const login = async (credentials: { username: string; password: string }) => {
    setLoading(true);
    try {
      const response = await fetch('https://backend-asn8.onrender.com/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });
      
      if (!response.ok) {
        throw new Error('Login failed');
      }
      
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      
      // Fetch user data
      const userResponse = await fetch('https://backend-asn8.onrender.com/users/me', {
        headers: {
          'Authorization': `Bearer ${data.access_token}`,
        },
      });
      
      if (!userResponse.ok) {
        throw new Error('Failed to fetch user data');
      }
      
      const userData = await userResponse.json();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
    """)

def test_profile_endpoints():
    """Test profile endpoints and print example code for frontend integration."""
    print("\n=== Profile Endpoints ===")
    
    # Update UserDataContext example
    print("\n--- Update UserDataContext Example ---")
    print("""
// UserDataContext.tsx update example
import React, { createContext, useState, useEffect, useContext } from 'react';
import { useAuth } from './AuthContext';

interface UserDataContextType {
  profile: any | null;
  addresses: any[];
  bankDetails: any[];
  fetchUserData: () => Promise<void>;
  updateProfile: (profileData: any) => Promise<void>;
  addAddress: (addressData: any) => Promise<void>;
  updateAddress: (addressId: string, addressData: any) => Promise<void>;
  addBankDetail: (bankData: any) => Promise<void>;
  updateBankDetail: (bankId: string, bankData: any) => Promise<void>;
  loading: boolean;
}

const UserDataContext = createContext<UserDataContextType | undefined>(undefined);

export const UserDataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [profile, setProfile] = useState<any | null>(null);
  const [addresses, setAddresses] = useState<any[]>([]);
  const [bankDetails, setBankDetails] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchUserData = async () => {
    if (!isAuthenticated) return;
    
    setLoading(true);
    const token = localStorage.getItem('token');
    
    try {
      // Fetch complete user profile with related data
      const response = await fetch('https://backend-asn8.onrender.com/users/me/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch user data');
      }
      
      const userData = await response.json();
      setProfile(userData.profile);
      setAddresses(userData.addresses || []);
      setBankDetails(userData.bank_details || []);
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchUserData();
    }
  }, [isAuthenticated]);

  const updateProfile = async (profileData: any) => {
    setLoading(true);
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch('https://backend-asn8.onrender.com/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update profile');
      }
      
      const updatedProfile = await response.json();
      setProfile(updatedProfile);
      return updatedProfile;
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const addAddress = async (addressData: any) => {
    setLoading(true);
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch('https://backend-asn8.onrender.com/profile/addresses', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(addressData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to add address');
      }
      
      const newAddress = await response.json();
      setAddresses([...addresses, newAddress]);
      return newAddress;
    } catch (error) {
      console.error('Error adding address:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateAddress = async (addressId: string, addressData: any) => {
    setLoading(true);
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`https://backend-asn8.onrender.com/profile/addresses/${addressId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(addressData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update address');
      }
      
      const updatedAddress = await response.json();
      setAddresses(addresses.map(addr => addr.id === addressId ? updatedAddress : addr));
      return updatedAddress;
    } catch (error) {
      console.error('Error updating address:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const addBankDetail = async (bankData: any) => {
    setLoading(true);
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch('https://backend-asn8.onrender.com/profile/bank-details', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bankData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to add bank detail');
      }
      
      const newBankDetail = await response.json();
      setBankDetails([...bankDetails, newBankDetail]);
      return newBankDetail;
    } catch (error) {
      console.error('Error adding bank detail:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateBankDetail = async (bankId: string, bankData: any) => {
    setLoading(true);
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch(`https://backend-asn8.onrender.com/profile/bank-details/${bankId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bankData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to update bank detail');
      }
      
      const updatedBankDetail = await response.json();
      setBankDetails(bankDetails.map(bank => bank.id === bankId ? updatedBankDetail : bank));
      return updatedBankDetail;
    } catch (error) {
      console.error('Error updating bank detail:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return (
    <UserDataContext.Provider
      value={{
        profile,
        addresses,
        bankDetails,
        fetchUserData,
        updateProfile,
        addAddress,
        updateAddress,
        addBankDetail,
        updateBankDetail,
        loading,
      }}
    >
      {children}
    </UserDataContext.Provider>
  );
};

export const useUserData = () => {
  const context = useContext(UserDataContext);
  if (context === undefined) {
    throw new Error('useUserData must be used within a UserDataProvider');
  }
  return context;
};
    """)

def main():
    print("=== Frontend Integration Helper ===")
    print("This script provides examples of how to integrate the backend with the frontend.")
    
    test_auth_endpoints()
    test_user_endpoints()
    test_profile_endpoints()
    
    print("\n=== API Integration Notes ===")
    print("""
1. Update API Base URL:
   - Create a config file in your frontend to store the API base URL
   - Example: const API_BASE_URL = 'https://backend-asn8.onrender.com';

2. Authentication:
   - Store JWT token in localStorage after login
   - Include token in Authorization header for protected routes
   - Handle token expiration and auto-logout

3. API Request Helper:
   - Create a helper function to handle API requests with authentication
   - Example:
   ```
   const apiRequest = async (endpoint, options = {}) => {
     const token = localStorage.getItem('token');
     
     const headers = {
       'Content-Type': 'application/json',
       ...options.headers,
     };
     
     if (token) {
       headers.Authorization = `Bearer ${token}`;
     }
     
     const config = {
       ...options,
       headers,
     };
     
     const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
     
     if (!response.ok) {
       if (response.status === 401) {
         // Handle unauthorized (token expired)
         localStorage.removeItem('token');
         window.location.href = '/login';
         throw new Error('Session expired. Please login again.');
       }
       
       const errorData = await response.json().catch(() => ({}));
       throw new Error(errorData.detail || 'API request failed');
     }
     
     return response.json();
   };
   ```

4. Update Components:
   - Replace static data with API calls in components
   - Add loading states and error handling
   - Use React Query or SWR for efficient data fetching and caching
    """)

if __name__ == "__main__":
    main()
