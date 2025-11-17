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
export type EmailCodeScene = 'login' | 'register' | 'reset-password';

export function fetchRegister(userData: {
  username: string;
  email: string;
  password: string;
  verification_code: string;
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

export function fetchSendEmailCode(email: string, scene: EmailCodeScene) {
  return alova.Post<{ message: string }>('/auth/send-email-code', { email, scene });
}

export function fetchEmailCodeLogin(email: string, verification_code: string) {
  return alova.Post<Api.Auth.LoginToken>('/auth/login/email', {
    email,
    verification_code
  });
}

export function fetchResetPassword(payload: {
  email: string;
  verification_code: string;
  new_password: string;
}) {
  return alova.Post<{ message: string }>('/auth/reset-password', payload);
}

export function fetchCustomBackendError(code: string, msg: string) {
  return alova.Get('/auth/error', {
    params: { code, msg }
  });
}

export function sendCaptcha(phone: string) {
  return alova.Post<{ message: string }>('/auth/sendCaptcha', { phone });
}

export function verifyCaptcha(phone: string, code: string) {
  return alova.Post<{ message: string }>('/auth/verifyCaptcha', { phone, code });
}
