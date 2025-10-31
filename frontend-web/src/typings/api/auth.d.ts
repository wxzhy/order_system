declare namespace Api {
  /**
   * namespace Auth
   *
   * backend api module: "auth"
   */
  namespace Auth {
    interface LoginToken {
      access_token: string;
      refresh_token: string;
      token_type: string;
    }

    interface UserInfo {
      id: number;
      username: string;
      email: string;
      phone?: string;
      user_type: 'customer' | 'vendor' | 'admin';
      create_time: string;
    }
  }
}
