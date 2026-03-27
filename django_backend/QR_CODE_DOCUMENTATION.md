// QR CODE VERIFICATION SYSTEM - ADMIN ONLY FEATURE
// ================================================
//
// WHAT IS THIS?
// This is an ADMIN feature to verify orders using QR codes.
// NOT for customer orders - this is for internal verification.
//
// HOW IT WORKS:
// 1. Admin scans QR code from pickup/delivery proof documents
// 2. System verifies order authenticity
// 3. Admin can see order details, clothes list, and verify proof
// 4. Used for fraud prevention and order tracking verification
//
// CUSTOMER FLOW:
// Customers DO NOT use QR scanning. They:
// - View orders in their mobile app
// - Track delivery status
// - Upload delivery photos (automatic QR attached by system)
// - Get push notifications
//
// ADMIN DASHBOARD FLOW:
// - Navigate to "Verify Orders" from drawer
// - Enter QR code manually (from documents/photos)
// - See order details with 100% clarity
// - Confirm order authenticity
// - Flag suspicious orders if needed
//
// DATABASE RELATION:
// - QR Code stored in Order.qr_code field
// - Customer uploads image with automatic QR generation
// - Admin scans/reads QR to get Order ID
// - API endpoint: /api/admin/verify-qr/ returns order + clothes
//
// API RESPONSE STRUCTURE:
// {
//   "verified": true,
//   "order": {
//     "id": 123,
//     "status": "IN_PROCESS",
//     "total_amount": 950.50,
//     "customer": {
//       "username": "john_doe",
//       "phone": "9876543210",
//       "email": "john@example.com"
//     },
//     "clothes": [
//       {
//         "id": 456,
//         "cloth_type": "Shirt",
//         "fabric": "Cotton",
//         "status": "IN_WASH",
//         "qr_code": "QR_456"
//       }
//     ]
//   }
// }
//
// SECURITY:
// - Only authenticated ADMIN users can access
// - Token required in Authorization header
// - QR codes are unique per order
// - Prevents order duplication/fraud
//
// ================================================
