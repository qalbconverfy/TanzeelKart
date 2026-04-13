import axios from 'axios'
import Cookies from 'js-cookie'

const API_URL = process.env.NEXT_PUBLIC_API_URL

// Axios Instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request Interceptor — Token add karo
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response Interceptor — Token refresh karo
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config

    if (
      error.response?.status === 401 &&
      !original._retry
    ) {
      original._retry = true

      try {
        const refresh = Cookies.get('refresh_token')
        if (!refresh) {
          clearTokens()
          window.location.href = '/login'
          return Promise.reject(error)
        }

        const res = await axios.post(
          `${API_URL}/api/v1/auth/refresh-token`,
          { refresh_token: refresh }
        )

        const { access_token, refresh_token } = res.data
        setTokens(access_token, refresh_token)
        original.headers.Authorization = `Bearer ${access_token}`
        return api(original)

      } catch (e) {
        clearTokens()
        window.location.href = '/login'
        return Promise.reject(e)
      }
    }

    return Promise.reject(error)
  }
)

// Token Helpers
export const setTokens = (access, refresh) => {
  Cookies.set('access_token', access, {
    expires: 1,
    secure: true,
    sameSite: 'strict'
  })
  Cookies.set('refresh_token', refresh, {
    expires: 7,
    secure: true,
    sameSite: 'strict'
  })
}

export const clearTokens = () => {
  Cookies.remove('access_token')
  Cookies.remove('refresh_token')
}

export const getToken = () => Cookies.get('access_token')

// ─────────────────────────────────────────
// Auth APIs
// ─────────────────────────────────────────

export const authAPI = {
  sendOTP: (phone) =>
    api.post('/api/v1/auth/send-otp', { phone }),

  verifyOTP: (phone, otp) =>
    api.post('/api/v1/auth/verify-otp', { phone, otp }),

  selectAccountType: (user_id, account_type) =>
    api.post('/api/v1/auth/select-account-type', {
      user_id,
      account_type
    }),

  shopVerifyLayer1: (user_id, data) =>
    api.post(
      `/api/v1/auth/shop-verify/layer-1?user_id=${user_id}`,
      data
    ),

  shopVerifyLayer2: (user_id, data) =>
    api.post(
      `/api/v1/auth/shop-verify/layer-2?user_id=${user_id}`,
      data
    ),

  adminLogin: (username, password) =>
    api.post('/api/v1/auth/admin/login', {
      username,
      password
    }),

  adminVerifyOTP: (username, otp) =>
    api.post('/api/v1/auth/admin/verify-otp', {
      username,
      otp
    }),

  emailRegister: (data) =>
    api.post('/api/v1/auth/email/register', data),

  emailLogin: (data) =>
    api.post('/api/v1/auth/email/login', data),

  guestLogin: () =>
    api.post('/api/v1/auth/guest/login'),

  logout: (refresh_token) =>
    api.post('/api/v1/auth/logout', { refresh_token }),
}

// ─────────────────────────────────────────
// User APIs
// ─────────────────────────────────────────

export const userAPI = {
  getProfile: () =>
    api.get('/api/v1/users/me'),

  updateProfile: (data) =>
    api.put('/api/v1/users/me', data),

  getFinance: () =>
    api.get('/api/v1/users/me/finance'),

  updateFCMToken: (fcm_token) =>
    api.put('/api/v1/users/me/fcm-token', { fcm_token }),
}

// ─────────────────────────────────────────
// Shop APIs
// ─────────────────────────────────────────

export const shopAPI = {
  createShop: (data) =>
    api.post('/api/v1/shops/', data),

  getMyShop: () =>
    api.get('/api/v1/shops/my-shop'),

  updateShop: (data) =>
    api.put('/api/v1/shops/my-shop', data),

  getNearbyShops: (data) =>
    api.post('/api/v1/shops/nearby', data),

  searchShops: (query, category) =>
    api.get('/api/v1/shops/search', {
      params: { query, category }
    }),

  getShopByTKCode: (tk_code) =>
    api.get(`/api/v1/shops/tk/${tk_code}`),

  getShopById: (id) =>
    api.get(`/api/v1/shops/${id}`),
}


// ─────────────────────────────────────────
// Product APIs
// ─────────────────────────────────────────

export const productAPI = {
  createProduct: (data) =>
    api.post('/api/v1/products/', data),

  getMyProducts: (page = 1) =>
    api.get('/api/v1/products/my-products', {
      params: { page }
    }),

  getShopProducts: (shop_id, page = 1) =>
    api.get(`/api/v1/products/shop/${shop_id}`, {
      params: { page }
    }),

  searchProducts: (query, page = 1) =>
    api.get('/api/v1/products/search', {
      params: { query, page }
    }),

  updateProduct: (id, data) =>
    api.put(`/api/v1/products/${id}`, data),

  updateStock: (id, stock) =>
    api.patch(`/api/v1/products/${id}/stock`, null, {
      params: { stock }
    }),

  deleteProduct: (id) =>
    api.delete(`/api/v1/products/${id}`),
}

// ─────────────────────────────────────────
// Order APIs
// ─────────────────────────────────────────

export const orderAPI = {
  createOrder: (data) =>
    api.post('/api/v1/orders/', data),

  getMyOrders: (page = 1) =>
    api.get('/api/v1/orders/my-orders', {
      params: { page }
    }),

  getShopOrders: (status, page = 1) =>
    api.get('/api/v1/orders/shop-orders', {
      params: { status, page }
    }),

  updateOrderStatus: (order_id, status) =>
    api.patch(`/api/v1/orders/${order_id}/status`, {
      status
    }),

  cancelOrder: (order_id, reason) =>
    api.post(`/api/v1/orders/${order_id}/cancel`, {
      reason
    }),

  getOrderDetail: (order_id) =>
    api.get(`/api/v1/orders/${order_id}`),
}

// ─────────────────────────────────────────
// Delivery APIs
// ─────────────────────────────────────────

export const deliveryAPI = {
  getPendingDeliveries: () =>
    api.get('/api/v1/delivery/pending'),

  assignDelivery: (order_id) =>
    api.post('/api/v1/delivery/assign', { order_id }),

  updateStatus: (delivery_id, data) =>
    api.patch(
      `/api/v1/delivery/${delivery_id}/status`,
      data
    ),

  updateLocation: (delivery_id, lat, lon) =>
    api.patch(
      `/api/v1/delivery/${delivery_id}/location`,
      { latitude: lat, longitude: lon }
    ),

  getMyDeliveries: (status, page = 1) =>
    api.get('/api/v1/delivery/my-deliveries', {
      params: { status, page }
    }),

  getSundayList: () =>
    api.get('/api/v1/delivery/sunday-collection-list'),

  sundayCollect: (data) =>
    api.post('/api/v1/delivery/sunday-collection', data),
}

// ─────────────────────────────────────────
// Udhaar APIs
// ─────────────────────────────────────────

export const udhaarAPI = {
  addUdhaar: (data) =>
    api.post('/api/v1/udhaar/add', data),

  payUdhaar: (data) =>
    api.post('/api/v1/udhaar/pay', data),

  getMyUdhaar: () =>
    api.get('/api/v1/udhaar/my-udhaar'),

  getDeliveryCharges: () =>
    api.get('/api/v1/udhaar/delivery-charges'),

  payDeliveryCharge: (data) =>
    api.post('/api/v1/udhaar/pay-delivery-charge', data),

  getShopUdhaarList: () =>
    api.get('/api/v1/udhaar/shop-list'),
}

// ─────────────────────────────────────────
// Notification APIs
// ─────────────────────────────────────────

export const notificationAPI = {
  getNotifications: (page = 1) =>
    api.get('/api/v1/notifications/', {
      params: { page }
    }),

  markRead: (ids) =>
    api.patch('/api/v1/notifications/mark-read', {
      notification_ids: ids
    }),

  markAllRead: () =>
    api.patch('/api/v1/notifications/mark-all-read'),

  deleteNotification: (id) =>
    api.delete(`/api/v1/notifications/${id}`),
}

// ─────────────────────────────────────────
// Weather APIs
// ─────────────────────────────────────────

export const weatherAPI = {
  getLatest: (node_id = 'reoti_main') =>
    api.get('/api/v1/weather/latest', {
      params: { node_id }
    }),

  getForecast: (node_id = 'reoti_main') =>
    api.get('/api/v1/weather/forecast', {
      params: { node_id }
    }),

  getNodes: () =>
    api.get('/api/v1/weather/nodes'),
}

// ─────────────────────────────────────────
// Video APIs
// ─────────────────────────────────────────

export const videoAPI = {
  getCategories: () =>
    api.get('/api/v1/videos/categories'),

  getTrending: () =>
    api.get('/api/v1/videos/trending'),

  getByCategory: (name, max = 10) =>
    api.get(`/api/v1/videos/category/${name}`, {
      params: { max_results: max }
    }),

  search: (query, max = 10) =>
    api.post('/api/v1/videos/search', {
      query,
      max_results: max
    }),
}

// ─────────────────────────────────────────
// Map APIs
// ─────────────────────────────────────────

export const mapAPI = {
  getMapData: (lat, lon, radius = 2) =>
    api.get('/api/v1/map/data', {
      params: { latitude: lat, longitude: lon, radius_km: radius }
    }),

  getShopsOnMap: (category) =>
    api.get('/api/v1/map/shops', {
      params: { category }
    }),

  getLandmarks: () =>
    api.get('/api/v1/map/landmarks'),
}

// ─────────────────────────────────────────
// Admin APIs
// ─────────────────────────────────────────

export const adminAPI = {
  getStats: () =>
    api.get('/api/v1/admin/stats'),

  getPendingVerifications: () =>
    api.get('/api/v1/admin/pending-verifications'),

  verifyShop: (data) =>
    api.post('/api/v1/admin/verify-shop', data),

  verifyMedical: (data) =>
    api.post('/api/v1/admin/verify-medical', data),

  getUsers: (page = 1) =>
    api.get('/api/v1/admin/users', {
      params: { page }
    }),

  addAdmin: (data) =>
    api.post('/api/v1/admin/add-admin', data),
}

export default api
