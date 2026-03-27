import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Container,
  Paper,
} from '@mui/material';
import { LockOutlined as LockIcon } from '@mui/icons-material';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const AdminLogin = ({ onLoginSuccess }) => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/login/`, credentials);
      
      if (response.data.user_type !== 'ADMIN') {
        setError('Access denied. Admin credentials required.');
        return;
      }

      // Store token and user info
      localStorage.setItem('admin_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('admin_user', JSON.stringify(response.data));

      onLoginSuccess(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Paper elevation={10} sx={{ borderRadius: 3 }}>
          <Card>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ textAlign: 'center', mb: 3 }}>
                <Box
                  sx={{
                    backgroundColor: 'primary.main',
                    width: 60,
                    height: 60,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto',
                    mb: 2,
                  }}
                >
                  <LockIcon sx={{ color: 'white', fontSize: 30 }} />
                </Box>
                <Typography variant="h4" fontWeight="bold" color="primary" gutterBottom>
                  Smart Laundry
                </Typography>
                <Typography variant="h6" color="textSecondary">
                  Admin Panel Login
                </Typography>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <form onSubmit={handleLogin}>
                <TextField
                  fullWidth
                  label="Username"
                  variant="outlined"
                  margin="normal"
                  value={credentials.username}
                  onChange={(e) =>
                    setCredentials({ ...credentials, username: e.target.value })
                  }
                  required
                />
                <TextField
                  fullWidth
                  label="Password"
                  type="password"
                  variant="outlined"
                  margin="normal"
                  value={credentials.password}
                  onChange={(e) =>
                    setCredentials({ ...credentials, password: e.target.value })
                  }
                  required
                />
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  sx={{ mt: 3, py: 1.5 }}
                  disabled={loading}
                >
                  {loading ? 'Logging in...' : 'Login'}
                </Button>
              </form>

              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Typography variant="body2" color="textSecondary">
                  Smart Laundry Management System v2.0
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Paper>
      </Container>
    </Box>
  );
};

export default AdminLogin;
