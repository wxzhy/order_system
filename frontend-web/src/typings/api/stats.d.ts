declare namespace Api {
  namespace Stats {
    interface VendorPersonal {
      store_exists: boolean;
      store_state?: 'pending' | 'approved' | 'disabled' | null;
      item_total: number;
      order_total: number;
      order_pending: number;
    }

    interface AdminPersonal {
      pending_store_review: number;
      pending_comment_review: number;
    }

    interface CustomerPersonal {
      order_total: number;
      order_pending: number;
    }

    interface PersonalResponse {
      user_type: 'customer' | 'vendor' | 'admin';
      vendor?: VendorPersonal;
      admin?: AdminPersonal;
      customer?: CustomerPersonal;
    }

    interface SiteResponse {
      user_total: number;
      merchant_total: number;
      order_total: number;
      turnover_total: number;
    }
  }
}
