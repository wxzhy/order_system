import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as loginApi, refreshToken as refreshTokenApi } from '@/api/login'
import type { LoginPayload, TokenInfo, TokenResponse } from '@/api/types/login'
import { isDoubleTokenMode } from '@/utils'
import { useUserStore } from './user'

const ACCESS_FALLBACK_MS = 25 * 60 * 1000 // 25 分钟，略短于服务端 30 分钟
const REFRESH_FALLBACK_MS = 7 * 24 * 60 * 60 * 1000 // 7 天

function createInitialTokenInfo(): TokenInfo {
  return {
    accessToken: '',
    refreshToken: '',
    tokenType: 'bearer',
    accessExpiresAt: 0,
    refreshExpiresAt: 0,
  }
}

function base64UrlDecode(segment: string): string {
  const normalized = segment.replace(/-/g, '+').replace(/_/g, '/')
  const padded = normalized.padEnd(normalized.length + (4 - ((normalized.length % 4) || 4)) % 4, '=')

  if (typeof globalThis !== 'undefined' && typeof globalThis.atob === 'function') {
    return globalThis.atob(padded)
  }

  if (typeof uni !== 'undefined' && typeof uni.base64ToArrayBuffer === 'function') {
    const buffer = uni.base64ToArrayBuffer(padded)
    return String.fromCharCode(...new Uint8Array(buffer))
  }

  return ''
}

function decodeJwtExpiry(token: string, fallbackMs: number) {
  try {
    const parts = token.split('.')
    if (parts.length < 2)
      return Date.now() + fallbackMs

    const payloadStr = base64UrlDecode(parts[1])
    if (!payloadStr)
      return Date.now() + fallbackMs

    const payload = JSON.parse(payloadStr) as { exp?: number }
    if (typeof payload.exp === 'number')
      return payload.exp * 1000
  }
  catch (error) {
    console.warn('Failed to decode token expiry', error)
  }
  return Date.now() + fallbackMs
}

function transformToken(response: TokenResponse): TokenInfo {
  return {
    accessToken: response.access_token,
    refreshToken: response.refresh_token,
    tokenType: response.token_type,
    accessExpiresAt: decodeJwtExpiry(response.access_token, ACCESS_FALLBACK_MS),
    refreshExpiresAt: decodeJwtExpiry(response.refresh_token, REFRESH_FALLBACK_MS),
  }
}

export const useTokenStore = defineStore(
  'token',
  () => {
    const tokenInfo = ref<TokenInfo>(createInitialTokenInfo())

    const setTokenInfo = (info: TokenInfo) => {
      tokenInfo.value = info
      uni.setStorageSync('accessTokenExpireTime', info.accessExpiresAt)
      uni.setStorageSync('refreshTokenExpireTime', info.refreshExpiresAt)
    }

    const clearTokenInfo = () => {
      tokenInfo.value = createInitialTokenInfo()
      uni.removeStorageSync('accessTokenExpireTime')
      uni.removeStorageSync('refreshTokenExpireTime')
    }

    const isTokenExpired = computed(() => {
      if (!tokenInfo.value.accessToken)
        return true
      if (!tokenInfo.value.accessExpiresAt)
        return false
      return Date.now() >= tokenInfo.value.accessExpiresAt
    })

    const isRefreshTokenExpired = computed(() => {
      if (!tokenInfo.value.refreshToken)
        return true
      if (!tokenInfo.value.refreshExpiresAt)
        return false
      return Date.now() >= tokenInfo.value.refreshExpiresAt
    })

    const hasLoginInfo = computed(() => !!tokenInfo.value.accessToken)

    const hasValidLogin = computed(() => hasLoginInfo.value && !isTokenExpired.value)

    async function postLogin(info: TokenInfo) {
      setTokenInfo(info)
      const userStore = useUserStore()
      await userStore.fetchUserInfo()
    }

    const login = async (payload: LoginPayload) => {
      try {
        const response = await loginApi(payload)
        const info = transformToken(response)
        await postLogin(info)
        uni.showToast({ title: '登录成功', icon: 'success' })
        return info
      }
      catch (error) {
        uni.showToast({ title: '登录失败，请检查账号', icon: 'none' })
        throw error
      }
    }

    const logout = () => {
      clearTokenInfo()
      const userStore = useUserStore()
      userStore.clearUserInfo()
    }

    const refreshToken = async () => {
      if (!isDoubleTokenMode) {
        throw new Error('当前模式不支持刷新令牌')
      }

      if (!tokenInfo.value.refreshToken) {
        throw new Error('缺少刷新令牌')
      }

      const response = await refreshTokenApi(tokenInfo.value.refreshToken)
      const info = transformToken(response)
      setTokenInfo(info)
      return info
    }

    const getValidToken = computed(() => {
      if (!hasLoginInfo.value)
        return ''
      return isTokenExpired.value ? '' : tokenInfo.value.accessToken
    })

    const tryGetValidToken = async () => {
      if (getValidToken.value)
        return getValidToken.value

      if (!isDoubleTokenMode || isRefreshTokenExpired.value)
        return ''

      try {
        await refreshToken()
        return tokenInfo.value.accessToken
      }
      catch (error) {
        console.error('刷新令牌失败', error)
        logout()
        return ''
      }
    }

    return {
      login,
      logout,
      refreshToken,
      tryGetValidToken,
      hasLogin: hasValidLogin,
      validToken: getValidToken,
      tokenInfo,
      setTokenInfo,
      clearTokenInfo,
    }
  },
  {
    persist: true,
  },
)
