/**
 * 验证场景
 */
export type VerificationScene = 'login' | 'register' | 'reset-password'

/**
 * 后端原始的 Token 响应
 */
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

/**
 * 存储在前端的 Token 信息
 */
export interface TokenInfo {
  accessToken: string
  refreshToken: string
  tokenType: string
  accessExpiresAt: number
  refreshExpiresAt: number
}

/**
 * 登录请求体
 */
export interface LoginPayload {
  username: string
  password: string
}

/**
 * 邮箱验证码登录请求体
 */
export interface EmailLoginPayload {
  email: string
  verification_code: string
}

/**
 * 注册请求体
 */
export interface RegisterPayload {
  username: string
  email: string
  password: string
  verification_code: string
  phone?: string
}

/**
 * 重置密码请求体
 */
export interface ResetPasswordPayload {
  email: string
  verification_code: string
  new_password: string
}

/**
 * 邮件验证码请求体
 */
export interface EmailCodeRequest {
  email: string
  scene: VerificationScene
}

/**
 * 当前登录用户信息
 */
export interface IUserInfoRes {
  id: number
  username: string
  email: string
  phone?: string | null
  user_type: 'customer' | 'vendor' | 'admin'
  create_time: string
  avatar?: string | null
}

/**
 * 更新用户信息
 */
export interface UpdateInfoPayload {
  username?: string
  email?: string
  phone?: string
}

/**
 * 修改密码请求体
 */
export interface UpdatePasswordPayload {
  old_password: string
  new_password: string
}

/**
 * 上传成功回调信息
 */
export interface IUploadSuccessInfo {
  fileId: number
  originalName: string
  fileName: string
  storagePath: string
  fileHash: string
  fileType: string
  fileBusinessType: string
  fileSize: number
}
