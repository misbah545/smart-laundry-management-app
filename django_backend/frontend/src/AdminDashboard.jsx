import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  LocalShipping as ShippingIcon,
  AttachMoney as MoneyIcon,
  ShoppingCart as OrdersIcon,
  Inventory as InventoryIcon,
  ReportProblem as ComplaintIcon,
  QrCodeScanner as QRIcon,
  Assessment as AnalyticsIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingIcon,
} from '@mui/icons-material';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Axios interceptor for auth token
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [qrDialogOpen, setQrDialogOpen] = useState(false);
  const [qrCode, setQrCode] = useState('');
  const [qrResult, setQrResult] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/dashboard/`);
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleQRScan = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/admin/verify-qr/`, {
        qr_code: qrCode,
      });
      setQrResult(response.data);
    } catch (err) {
      setQrResult({ verified: false, error: 'Invalid QR Code' });
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3, backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold" color="primary">
          Smart Laundry Admin Panel
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Complete management dashboard for your laundry business
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Navigation Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<DashboardIcon />} label="Dashboard" />
          <Tab icon={<OrdersIcon />} label="Orders" />
          <Tab icon={<QRIcon />} label="QR Scanner" />
          <Tab icon={<InventoryIcon />} label="Inventory" />
          <Tab icon={<ComplaintIcon />} label="Complaints" />
          <Tab icon={<PeopleIcon />} label="Customers" />
          <Tab icon={<ShippingIcon />} label="Drivers" />
          <Tab icon={<AnalyticsIcon />} label="Analytics" />
        </Tabs>
      </Paper>

      {/* Dashboard Overview Tab */}
      {activeTab === 0 && dashboardData && (
        <DashboardOverview data={dashboardData} onRefresh={fetchDashboardData} />
      )}

      {/* Orders Tab */}
      {activeTab === 1 && <OrdersManagement />}

      {/* QR Scanner Tab */}
      {activeTab === 2 && <QRScanner />}

      {/* Inventory Tab */}
      {activeTab === 3 && <InventoryManagement />}

      {/* Complaints Tab */}
      {activeTab === 4 && <ComplaintsManagement />}

      {/* Customers Tab */}
      {activeTab === 5 && <CustomersManagement />}

      {/* Drivers Tab */}
      {activeTab === 6 && <DriversManagement />}

      {/* Analytics Tab */}
      {activeTab === 7 && <AnalyticsReports />}
    </Box>
  );
};

// Dashboard Overview Component
const DashboardOverview = ({ data, onRefresh }) => {
  const { overview, charts, recent_orders, inventory_alerts } = data;

  const statsCards = [
    {
      title: 'Total Orders',
      value: overview.total_orders,
      today: overview.today_orders,
      icon: <OrdersIcon />,
      color: '#1976d2',
    },
    {
      title: 'Total Revenue',
      value: `₹${overview.total_revenue.toLocaleString()}`,
      today: `₹${overview.today_revenue.toLocaleString()}`,
      icon: <MoneyIcon />,
      color: '#2e7d32',
    },
    {
      title: 'Active Customers',
      value: overview.active_customers,
      today: overview.new_customers_today,
      icon: <PeopleIcon />,
      color: '#ed6c02',
    },
    {
      title: 'Pending Orders',
      value: overview.pending_orders,
      today: overview.in_process_orders,
      icon: <TrendingIcon />,
      color: '#d32f2f',
    },
  ];

  // Chart data
  const ordersPieData = {
    labels: charts.orders_by_status.labels,
    datasets: [
      {
        data: charts.orders_by_status.data,
        backgroundColor: ['#ffc107', '#2196f3', '#4caf50', '#f44336'],
      },
    ],
  };

  const revenueLineData = {
    labels: charts.revenue_last_7_days.map(item => new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
    datasets: [
      {
        label: 'Revenue (₹)',
        data: charts.revenue_last_7_days.map(item => item.revenue),
        borderColor: '#2e7d32',
        backgroundColor: 'rgba(46, 125, 50, 0.1)',
        tension: 0.4,
      },
    ],
  };

  return (
    <Box>
      {/* Refresh Button */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <Button startIcon={<RefreshIcon />} onClick={onRefresh} variant="outlined">
          Refresh Data
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statsCards.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ background: `linear-gradient(135deg, ${stat.color} 0%, ${stat.color}dd 100%)`, color: 'white' }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" fontWeight="bold" sx={{ my: 1 }}>
                      {stat.value}
                    </Typography>
                    <Typography variant="caption">
                      Today: {stat.today}
                    </Typography>
                  </Box>
                  <Box sx={{ fontSize: 48, opacity: 0.3 }}>
                    {stat.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Orders by Status</Typography>
              <Box sx={{ height: 300, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <Pie data={ordersPieData} options={{ maintainAspectRatio: false }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Revenue (Last 7 Days)</Typography>
              <Box sx={{ height: 300 }}>
                <Line data={revenueLineData} options={{ maintainAspectRatio: false, responsive: true }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alerts & Recent Orders */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="error">
                Low Stock Alerts
              </Typography>
              {inventory_alerts.length > 0 ? (
                <Box>
                  {inventory_alerts.map((item, index) => (
                    <Alert severity="warning" key={index} sx={{ mb: 1 }}>
                      <strong>{item.item_name}</strong>: {item.current_quantity} {item.unit} remaining
                    </Alert>
                  ))}
                </Box>
              ) : (
                <Typography color="textSecondary">All items are well stocked!</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Recent Orders</Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Order ID</TableCell>
                      <TableCell>Customer</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Amount</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recent_orders.slice(0, 5).map((order) => (
                      <TableRow key={order.id}>
                        <TableCell>#{order.id}</TableCell>
                        <TableCell>{order.customer}</TableCell>
                        <TableCell>
                          <Chip label={order.status} size="small" color="primary" />
                        </TableCell>
                        <TableCell>₹{order.total_amount}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Additional Metrics */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Drivers</Typography>
              <Typography variant="h3" color="primary">{overview.total_drivers}</Typography>
              <Typography variant="body2" color="textSecondary">
                Active Today: {overview.active_drivers}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Complaints</Typography>
              <Typography variant="h3" color="warning.main">{overview.pending_complaints}</Typography>
              <Typography variant="body2" color="textSecondary">
                Resolved: {overview.resolved_complaints}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Average Rating</Typography>
              <Typography variant="h3" color="success.main">{overview.avg_rating} ⭐</Typography>
              <Typography variant="body2" color="textSecondary">
                AI Predicted Orders: {overview.predicted_orders_today}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

// Orders Management Component
const OrdersManagement = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [statusDialogOpen, setStatusDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState('');

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/orders/`);
      setOrders(response.data.results || response.data);
    } catch (err) {
      console.error('Failed to fetch orders', err);
    } finally {
      setLoading(false);
    }
  };

  const updateOrderStatus = async () => {
    try {
      await axios.put(`${API_BASE_URL}/admin/orders/${selectedOrder.id}/status/`, {
        status: newStatus,
      });
      setStatusDialogOpen(false);
      fetchOrders();
    } catch (err) {
      console.error('Failed to update status', err);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'PENDING': 'warning',
      'ASSIGNED': 'info',
      'PICKED': 'primary',
      'IN_PROCESS': 'secondary',
      'DELIVERED': 'success',
      'CANCELLED': 'error',
    };
    return colors[status] || 'default';
  };

  if (loading) return <CircularProgress />;

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Orders Management</Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Order ID</strong></TableCell>
                <TableCell><strong>Customer</strong></TableCell>
                <TableCell><strong>Driver</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell><strong>Amount</strong></TableCell>
                <TableCell><strong>Date</strong></TableCell>
                <TableCell><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell>#{order.id}</TableCell>
                  <TableCell>{order.customer?.username || order.customer}</TableCell>
                  <TableCell>{order.driver?.username || order.driver || 'Not Assigned'}</TableCell>
                  <TableCell>
                    <Chip label={order.status} color={getStatusColor(order.status)} size="small" />
                  </TableCell>
                  <TableCell>₹{order.total_amount || 0}</TableCell>
                  <TableCell>{new Date(order.order_date).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => {
                        setSelectedOrder(order);
                        setNewStatus(order.status);
                        setStatusDialogOpen(true);
                      }}
                    >
                      Update
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Update Status Dialog */}
        <Dialog open={statusDialogOpen} onClose={() => setStatusDialogOpen(false)}>
          <DialogTitle>Update Order Status</DialogTitle>
          <DialogContent>
            <FormControl fullWidth sx={{ mt: 2 }}>
              <InputLabel>Status</InputLabel>
              <Select value={newStatus} onChange={(e) => setNewStatus(e.target.value)}>
                <MenuItem value="PENDING">Pending</MenuItem>
                <MenuItem value="ASSIGNED">Assigned</MenuItem>
                <MenuItem value="PICKED">Picked</MenuItem>
                <MenuItem value="IN_PROCESS">In Process</MenuItem>
                <MenuItem value="DELIVERED">Delivered</MenuItem>
                <MenuItem value="CANCELLED">Cancelled</MenuItem>
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setStatusDialogOpen(false)}>Cancel</Button>
            <Button onClick={updateOrderStatus} variant="contained">Update</Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
};

// QR Scanner Component
const QRScanner = () => {
  const [qrCode, setQrCode] = useState('');
  const [qrResult, setQrResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleQRScan = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/admin/verify-qr/`, {
        qr_code: qrCode,
      });
      setQrResult(response.data);
    } catch (err) {
      setQrResult({ verified: false, error: 'Invalid QR Code' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>QR Code Scanner</Typography>
        <Box sx={{ mt: 3 }}>
          <TextField
            fullWidth
            label="Enter QR Code"
            value={qrCode}
            onChange={(e) => setQrCode(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button
            variant="contained"
            startIcon={<QRIcon />}
            onClick={handleQRScan}
            disabled={!qrCode || loading}
            fullWidth
          >
            {loading ? 'Scanning...' : 'Verify QR Code'}
          </Button>

          {qrResult && (
            <Box sx={{ mt: 3 }}>
              {qrResult.verified ? (
                <Alert severity="success" sx={{ mb: 2 }}>
                  <Typography variant="h6">Order Verified ✓</Typography>
                </Alert>
              ) : (
                <Alert severity="error" sx={{ mb: 2 }}>
                  <Typography variant="h6">Invalid QR Code</Typography>
                </Alert>
              )}

              {qrResult.order && (
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Order Details</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography><strong>Order ID:</strong> #{qrResult.order.id}</Typography>
                      <Typography><strong>Customer:</strong> {qrResult.order.customer.name}</Typography>
                      <Typography><strong>Phone:</strong> {qrResult.order.customer.phone}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography><strong>Status:</strong> {qrResult.order.status}</Typography>
                      <Typography><strong>Amount:</strong> ₹{qrResult.order.total_amount}</Typography>
                      <Typography><strong>Items:</strong> {qrResult.order.clothes_count}</Typography>
                    </Grid>
                  </Grid>

                  <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Clothes</Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Type</TableCell>
                          <TableCell>Fabric</TableCell>
                          <TableCell>Color</TableCell>
                          <TableCell>Qty</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {qrResult.order.clothes.map((cloth) => (
                          <TableRow key={cloth.id}>
                            <TableCell>{cloth.cloth_type}</TableCell>
                            <TableCell>{cloth.fabric}</TableCell>
                            <TableCell>{cloth.color}</TableCell>
                            <TableCell>{cloth.quantity}</TableCell>
                            <TableCell>
                              <Chip label={cloth.status} size="small" color="primary" />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              )}
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

// Inventory Management Component
const InventoryManagement = () => {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [restockDialog, setRestockDialog] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [restockQty, setRestockQty] = useState('');

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchInventory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/inventory/`);
      setInventory(response.data.inventory);
    } catch (err) {
      console.error('Failed to fetch inventory', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRestock = async () => {
    try {
      await axios.post(`${API_BASE_URL}/admin/inventory/restock/`, {
        item_id: selectedItem.id,
        quantity: parseFloat(restockQty),
      });
      setRestockDialog(false);
      fetchInventory();
    } catch (err) {
      console.error('Failed to restock', err);
    }
  };

  const getStatusColor = (status) => {
    if (status === 'critical') return 'error';
    if (status === 'low') return 'warning';
    return 'success';
  };

  if (loading) return <CircularProgress />;

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Inventory Management</Typography>
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Item Name</strong></TableCell>
                <TableCell><strong>Category</strong></TableCell>
                <TableCell><strong>Current Qty</strong></TableCell>
                <TableCell><strong>Min Threshold</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell><strong>Supplier</strong></TableCell>
                <TableCell><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {inventory.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.item_name}</TableCell>
                  <TableCell>{item.category}</TableCell>
                  <TableCell>{item.current_quantity} {item.unit}</TableCell>
                  <TableCell>{item.minimum_threshold} {item.unit}</TableCell>
                  <TableCell>
                    <Chip 
                      label={item.status.toUpperCase()} 
                      color={getStatusColor(item.status)} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>{item.supplier_name}</TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      variant="contained"
                      onClick={() => {
                        setSelectedItem(item);
                        setRestockDialog(true);
                      }}
                    >
                      Restock
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Restock Dialog */}
        <Dialog open={restockDialog} onClose={() => setRestockDialog(false)}>
          <DialogTitle>Restock Item</DialogTitle>
          <DialogContent>
            <Typography sx={{ mb: 2 }}>
              Restock <strong>{selectedItem?.item_name}</strong>
            </Typography>
            <TextField
              fullWidth
              type="number"
              label={`Quantity (${selectedItem?.unit})`}
              value={restockQty}
              onChange={(e) => setRestockQty(e.target.value)}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setRestockDialog(false)}>Cancel</Button>
            <Button onClick={handleRestock} variant="contained">Restock</Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
};

// Complaints Management Component
const ComplaintsManagement = () => {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resolveDialog, setResolveDialog] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [response, setResponse] = useState('');

  useEffect(() => {
    fetchComplaints();
  }, []);

  const fetchComplaints = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/complaints/`);
      setComplaints(response.data.complaints);
    } catch (err) {
      console.error('Failed to fetch complaints', err);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async () => {
    try {
      await axios.put(`${API_BASE_URL}/admin/complaints/${selectedComplaint.id}/resolve/`, {
        response: response,
      });
      setResolveDialog(false);
      fetchComplaints();
    } catch (err) {
      console.error('Failed to resolve complaint', err);
    }
  };

  if (loading) return <CircularProgress />;

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Complaints Management</Typography>
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>ID</strong></TableCell>
                <TableCell><strong>Customer</strong></TableCell>
                <TableCell><strong>Type</strong></TableCell>
                <TableCell><strong>Subject</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell><strong>Priority</strong></TableCell>
                <TableCell><strong>Date</strong></TableCell>
                <TableCell><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {complaints.map((complaint) => (
                <TableRow key={complaint.id}>
                  <TableCell>#{complaint.id}</TableCell>
                  <TableCell>{complaint.customer}</TableCell>
                  <TableCell>{complaint.complaint_type}</TableCell>
                  <TableCell>{complaint.subject}</TableCell>
                  <TableCell>
                    <Chip 
                      label={complaint.status} 
                      color={complaint.status === 'RESOLVED' ? 'success' : 'warning'} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={complaint.priority} 
                      color={complaint.priority === 'HIGH' ? 'error' : 'default'} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>{new Date(complaint.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    {complaint.status !== 'RESOLVED' && (
                      <Button
                        size="small"
                        variant="contained"
                        onClick={() => {
                          setSelectedComplaint(complaint);
                          setResolveDialog(true);
                        }}
                      >
                        Resolve
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Resolve Dialog */}
        <Dialog open={resolveDialog} onClose={() => setResolveDialog(false)} maxWidth="md" fullWidth>
          <DialogTitle>Resolve Complaint</DialogTitle>
          <DialogContent>
            {selectedComplaint && (
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  <strong>Subject:</strong> {selectedComplaint.subject}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  <strong>Description:</strong> {selectedComplaint.description}
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Your Response"
                  value={response}
                  onChange={(e) => setResponse(e.target.value)}
                  sx={{ mt: 2 }}
                />
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setResolveDialog(false)}>Cancel</Button>
            <Button onClick={handleResolve} variant="contained" color="success">
              Mark as Resolved
            </Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
};

// Customers Management Component
const CustomersManagement = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/customers/`);
      setCustomers(response.data.customers);
    } catch (err) {
      console.error('Failed to fetch customers', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <CircularProgress />;

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Customers Management</Typography>
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>ID</strong></TableCell>
                <TableCell><strong>Name</strong></TableCell>
                <TableCell><strong>Email</strong></TableCell>
                <TableCell><strong>Phone</strong></TableCell>
                <TableCell><strong>Total Orders</strong></TableCell>
                <TableCell><strong>Total Spent</strong></TableCell>
                <TableCell><strong>Loyalty Points</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {customers.map((customer) => (
                <TableRow key={customer.id}>
                  <TableCell>#{customer.id}</TableCell>
                  <TableCell>{customer.name}</TableCell>
                  <TableCell>{customer.email}</TableCell>
                  <TableCell>{customer.phone}</TableCell>
                  <TableCell>{customer.total_orders}</TableCell>
                  <TableCell>₹{customer.total_spent.toLocaleString()}</TableCell>
                  <TableCell>
                    <Chip label={customer.loyalty_points} color="primary" size="small" />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={customer.is_active ? 'Active' : 'Inactive'} 
                      color={customer.is_active ? 'success' : 'default'} 
                      size="small" 
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

// Drivers Management Component
const DriversManagement = () => {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDrivers();
  }, []);

  const fetchDrivers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/drivers/`);
      setDrivers(response.data.drivers);
    } catch (err) {
      console.error('Failed to fetch drivers', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <CircularProgress />;

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Drivers Management</Typography>
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>ID</strong></TableCell>
                <TableCell><strong>Name</strong></TableCell>
                <TableCell><strong>Email</strong></TableCell>
                <TableCell><strong>Phone</strong></TableCell>
                <TableCell><strong>Total Deliveries</strong></TableCell>
                <TableCell><strong>Active Orders</strong></TableCell>
                <TableCell><strong>Avg Rating</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {drivers.map((driver) => (
                <TableRow key={driver.id}>
                  <TableCell>#{driver.id}</TableCell>
                  <TableCell>{driver.name}</TableCell>
                  <TableCell>{driver.email}</TableCell>
                  <TableCell>{driver.phone}</TableCell>
                  <TableCell>{driver.total_deliveries}</TableCell>
                  <TableCell>{driver.active_orders}</TableCell>
                  <TableCell>{driver.avg_rating} ⭐</TableCell>
                  <TableCell>
                    <Chip 
                      label={driver.is_active ? 'Active' : 'Inactive'} 
                      color={driver.is_active ? 'success' : 'default'} 
                      size="small" 
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

// Analytics Reports Component
const AnalyticsReports = () => {
  const [reportType, setReportType] = useState('daily');
  const [analytics, setAnalytics] = useState(null);
  const [workload, setWorkload] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
    fetchWorkloadPrediction();
  }, [reportType]);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/analytics/?type=${reportType}`);
      setAnalytics(response.data);
    } catch (err) {
      console.error('Failed to fetch analytics', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkloadPrediction = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/workload-prediction/`);
      setWorkload(response.data.predictions);
    } catch (err) {
      console.error('Failed to fetch workload prediction', err);
    }
  };

  if (loading) return <CircularProgress />;

  return (
    <Box>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h5">Analytics & Reports</Typography>
            <FormControl>
              <Select value={reportType} onChange={(e) => setReportType(e.target.value)}>
                <MenuItem value="daily">Daily</MenuItem>
                <MenuItem value="weekly">Weekly</MenuItem>
                <MenuItem value="monthly">Monthly</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {analytics && (
            <Grid container spacing={3} sx={{ mt: 2 }}>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">{analytics.summary.total_orders}</Typography>
                  <Typography variant="body2">Total Orders</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    ₹{analytics.summary.total_revenue.toLocaleString()}
                  </Typography>
                  <Typography variant="body2">Total Revenue</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="info.main">
                    ₹{analytics.summary.avg_order_value.toLocaleString()}
                  </Typography>
                  <Typography variant="body2">Avg Order Value</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">{analytics.summary.repeat_customers}</Typography>
                  <Typography variant="body2">Repeat Customers</Typography>
                </Paper>
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>AI Workload Prediction (Next 7 Days)</Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Date</strong></TableCell>
                  <TableCell><strong>Predicted Orders</strong></TableCell>
                  <TableCell><strong>Confidence</strong></TableCell>
                  <TableCell><strong>Recommended Staff</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {workload.map((day, index) => (
                  <TableRow key={index}>
                    <TableCell>{new Date(day.date).toLocaleDateString()}</TableCell>
                    <TableCell>{day.predicted_orders}</TableCell>
                    <TableCell>{(day.confidence * 100).toFixed(0)}%</TableCell>
                    <TableCell>{day.recommended_staff}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AdminDashboard;
