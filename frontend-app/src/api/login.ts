import type {
  EmailCodeRequest,
  EmailLoginPayload,
  LoginPayload,
  RegisterPayload,
  ResetPasswordPayload,
  TokenResponse,
  UpdateInfoPayload,
  UpdatePasswordPayload,
  IUserInfoRes,
} from './types/login'
import { http } from '@/http/http'

/**
 * 用户登录
 */
export function login(payload: LoginPayload) {
  return http.post<TokenResponse>('/auth/login', payload)
}

/**
 * 邮箱验证码登录
  return http.post<TokenResponse>('/auth/login/email', payload)
}

/**
 * 刷新令牌
 */
  return http.post<TokenResponse>('/auth/refresh', { refresh_token: refreshTokenValue })
}

/**
 * 发送邮箱验证码
 */
export function sendEmailCode(payload: EmailCodeRequest) {
  return http.post<{ message: string }>('/auth/send-email-code', payload)
}

/**
 * 普通用户注册
 */
export function register(payload: RegisterPayload) {
  return http.post<IUserInfoRes>('/auth/register', payload)
}

/**
 * 重置密码
 */
export function resetPassword(payload: ResetPasswordPayload) {
  return http.post<{ message: string }>('/auth/reset-password', payload)
}

/**
 * 获取当前登录用户信息
 */
export function getUserInfo() {
  return http.get<IUserInfoRes>('/user/me')
}

/**
 * 更新用户信息
 */
export function updateInfo(data: UpdateInfoPayload) {
  return http.put<IUserInfoRes>('/user/me', data)
}

/**
 * 修改当前用户密码
 */
export function updateUserPassword(data: UpdatePasswordPayload) {
  return http.put('/user/me/password', data)
}
