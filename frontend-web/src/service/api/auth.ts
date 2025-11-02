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
 * Update current user profile
 *
 * @param userData User profile data to update
 */
export function fetchUpdateProfile(userData: {
  username?: string;
  email?: string;
  phone?: string;
}) {
  return alova.Put<Api.Auth.UserInfo>('/auth/me', userData);
}

/**
 * Change current user password
 *
 * @param oldPassword Current password
 * @param newPassword New password
 */
export function fetchChangePassword(oldPassword: string, newPassword: string) {
  return alova.Put<{ message: string }>('/auth/me/password', {
    old_password: oldPassword,
    new_password: newPassword
  });
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
