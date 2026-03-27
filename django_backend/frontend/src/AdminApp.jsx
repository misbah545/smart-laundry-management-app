import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AdminLogin from './AdminLogin';
import AdminDashboard from './AdminDashboard';
import { Box, AppBar, Toolbar, Typography, Button, IconButton } from '@mui/material';
import { ExitToApp as LogoutIcon, Menu as MenuIcon } from '@mui/icons-material';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function AdminApp() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [adminUser, setAdminUser] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('admin_token');
    const user = localStorage.getItem('admin_user');
    
    if (token && user) {
      setIsLoggedIn(true);
      setAdminUser(JSON.parse(user));
    }
  }, []);

  const handleLoginSuccess = (userData) => {
    setIsLoggedIn(true);
    setAdminUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('admin_user');
    setIsLoggedIn(false);
    setAdminUser(null);
  };

  if (!isLoggedIn) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AdminLogin onLoginSuccess={handleLoginSuccess} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* Top Navigation Bar */}
        <AppBar position="static" elevation={2}>
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Smart Laundry Admin Panel
            </Typography>
            <Typography variant="body1" sx={{ mr: 2 }}>
              Welcome, {adminUser?.username || 'Admin'}
            </Typography>
            <Button color="inherit" startIcon={<LogoutIcon />} onClick={handleLogout}>
              Logout
            </Button>
          </Toolbar>
        </AppBar>

        {/* Main Dashboard Content */}
        <Box component="main" sx={{ flexGrow: 1 }}>
          <AdminDashboard />
        </Box>

        {/* Footer */}
        <Box
          component="footer"
          sx={{
            py: 2,
            px: 2,
            mt: 'auto',
            backgroundColor: (theme) =>
              theme.palette.mode === 'light'
                ? theme.palette.grey[200]
                : theme.palette.grey[800],
            textAlign: 'center',
          }}
        >
          <Typography variant="body2" color="text.secondary">
            © 2026 Smart Laundry Management System. All rights reserved.
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default AdminApp;
