import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import Cookies from 'js-cookie'


// ─────────────────────────────────────────
// Auth Store
// ─────────────────────────────────────────

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => set({
        user,
        isAuthenticated: !!user
      }),

      setLoading: (loading) => set({
        isLoading: loading
      }),

      logout: () => {
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        set({ user: null, isAuthenticated: false })
      },

      updateUser: (data) => set((state) => ({
        user: { ...state.user, ...data }
      })),
    }),
    {
      name: 'tanzeelkart-auth',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated
      }),
    }
  )
)


// ─────────────────────────────────────────
// Cart Store
// ─────────────────────────────────────────

export const useCartStore = create(
  persist(
    (set, get) => ({
      items: [],
      shop_id: null,

      addItem: (product, shop_id) => {
        const { items, shop_id: currentShop } = get()

        // Different shop ka item — cart clear
        if (currentShop && currentShop !== shop_id) {
          set({
            items: [{
              ...product,
              quantity: 1,
              subtotal: product.discount_price || product.price
            }],
            shop_id
          })
          return
        }

        const existing = items.find(
          (i) => i.id === product.id
        )

        if (existing) {
          set({
            items: items.map((i) =>
              i.id === product.id
                ? {
                    ...i,
                    quantity: i.quantity + 1,
                    subtotal: (i.quantity + 1) *
                      (product.discount_price || product.price)
                  }
                : i
            )
          })
        } else {
          set({
            items: [...items, {
              ...product,
              quantity: 1,
              subtotal: product.discount_price || product.price
            }],
            shop_id
          })
        }
      },

      removeItem: (product_id) => {
        const items = get().items.filter(
          (i) => i.id !== product_id
        )
        set({
          items,
          shop_id: items.length === 0 ? null : get().shop_id
        })
      },

      updateQuantity: (product_id, quantity) => {
        if (quantity <= 0) {
          get().removeItem(product_id)
          return
        }
        set({
          items: get().items.map((i) =>
            i.id === product_id
              ? {
                  ...i,
                  quantity,
                  subtotal: quantity *
                    (i.discount_price || i.price)
                }
              : i
          )
        })
      },

      clearCart: () => set({ items: [], shop_id: null }),

      getTotal: () => {
        return get().items.reduce(
          (sum, i) => sum + i.subtotal, 0
        )
      },

      getItemCount: () => {
        return get().items.reduce(
          (sum, i) => sum + i.quantity, 0
        )
      },
    }),
    {
      name: 'tanzeelkart-cart',
    }
  )
)


// ─────────────────────────────────────────
// Notification Store
// ─────────────────────────────────────────

export const useNotificationStore = create((set) => ({
  notifications: [],
  unreadCount: 0,

  setNotifications: (notifications) => set({
    notifications
  }),

  setUnreadCount: (count) => set({
    unreadCount: count
  }),

  markRead: (id) => set((state) => ({
    notifications: state.notifications.map((n) =>
      n.id === id ? { ...n, is_read: true } : n
    ),
    unreadCount: Math.max(0, state.unreadCount - 1)
  })),
}))
