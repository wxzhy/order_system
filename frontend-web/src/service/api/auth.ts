import { alova } from '../request';

/**
 * Login
 *
 * @param username Username, email or phone
 * @param password Password
 */
export function fetchLogin(username: string, password: string) {
  return alova.Post<Api.Auth.LoginToken>('/auth/login', { username, password });
}

/**
 * Get current user info
 */
export function fetchGetUserInfo() {
  return alova.Get<Api.Auth.UserInfo>('/auth/me');
}

/**
 * Register new user
 *
 * @param userData User registration data
 */
export function fetchRegister(userData: {
  username: string;
  email: string;
  password: string;
  phone?: string;
  user_type?: 'customer' | 'vendor' | 'admin';
}) {
  return alova.Post('/auth/register', userData);
}

/**
 * Refresh token
 *
 * @param refreshToken Refresh token
 */
export function fetchRefreshToken(refreshToken: string) {
  return alova.Post<Api.Auth.LoginToken>(
    '/auth/refresh',
    { refresh_token: refreshToken },
    {
      meta: {
        authRole: 'refreshToken'
      }
    }
  );
}
