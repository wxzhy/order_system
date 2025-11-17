<script lang="ts" setup>
import { computed, reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { LOGIN_PAGE } from '@/router/config'
import { sendEmailCode } from '@/api/login'
import { useTokenStore } from '@/store/token'
import { tabbarList } from '@/tabbar/config'
import { isPageTabbar } from '@/tabbar/store'
import { ensureDecodeURIComponent, parseUrlToObj } from '@/utils'

definePage({
  style: {
    navigationBarTitleText: '邮箱验证码登录',
  },
})

const form = reactive({
  email: '',
  verificationCode: '',
})

const errors = reactive({
  email: '',
  verificationCode: '',
})

const isLoading = ref(false)
const isSendingCode = ref(false)
const countdown = ref(0)
const redirectUrl = ref('')
const tokenStore = useTokenStore()

const canSendCode = computed(() => Boolean(form.email.trim()) && !isSendingCode.value && countdown.value === 0)

const codeButtonText = computed(() => {
  if (countdown.value > 0)
    return `${countdown.value}秒后重试`
  if (isSendingCode.value)
    return '发送中...'
  return '获取验证码'
})

onLoad((options) => {
  if (options?.redirect) {
    redirectUrl.value = ensureDecodeURIComponent(options.redirect)
  }
  else {
    redirectUrl.value = tabbarList[0].pagePath
  }
})

function clearError(field: 'email' | 'verificationCode') {
  errors[field] = ''
}

function validateEmail() {
  errors.email = ''
  if (!form.email.trim()) {
    errors.email = '请输入邮箱地址'
    return false
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.email.trim())) {
    errors.email = '请输入有效的邮箱地址'
    return false
  }
  return true
}

function validateForm() {
  errors.email = ''
  errors.verificationCode = ''
  let valid = true

  if (!validateEmail()) {
    valid = false
  }

  if (!form.verificationCode.trim()) {
    errors.verificationCode = '请输入验证码'
    valid = false
  }
  else if (form.verificationCode.trim().length !== 6) {
    errors.verificationCode = '验证码应为6位'
    valid = false
  }

  return valid
}

function startCountdown() {
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

async function handleSendCode() {
  if (!canSendCode.value)
    return

  if (!validateEmail())
    return

  isSendingCode.value = true
  try {
    await sendEmailCode({
      email: form.email.trim(),
      scene: 'login',
    })
    uni.showToast({ title: '验证码已发送', icon: 'success' })
    startCountdown()
  }
  catch (error) {
    console.error('发送验证码失败', error)
    uni.showToast({ title: '发送验证码失败', icon: 'error' })
  }
  finally {
    isSendingCode.value = false
  }
}

function goToPasswordLogin() {
  uni.redirectTo({ url: LOGIN_PAGE })
}

function redirectAfterLogin() {
  let target = redirectUrl.value || tabbarList[0].pagePath
  if (!target.startsWith('/'))
    target = `/${target}`

  const { path } = parseUrlToObj(target)
  if (isPageTabbar(path)) {
    uni.switchTab({ url: target })
    return
  }

  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack()
  }
  else {
    uni.redirectTo({ url: target })
  }
}

async function handleLogin() {
  if (!validateForm())
    return

  if (tokenStore.hasLogin) {
    uni.navigateBack()
    return
  }

  isLoading.value = true
  try {
    await tokenStore.emailLogin({
      email: form.email.trim(),
      verification_code: form.verificationCode.trim(),
    })
    redirectAfterLogin()
  }
  catch (error) {
    console.error('登录失败', error)
  }
  finally {
    isLoading.value = false
  }
}
</script>

<template>
  <view class="email-login-page">
    <view class="header">
      <view class="title">
        食堂餐点预约系统
      </view>
      <view class="subtitle">
        邮箱验证码登录
      </view>
    </view>

    <view class="form-card">
      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          邮箱地址
        </view>
        <view class="input-wrapper">
          <input
            v-model="form.email"
            class="form-input"
            type="text"
            placeholder="请输入邮箱地址"
            :disabled="isLoading"
            @input="clearError('email')"
          >
        </view>
        <view v-if="errors.email" class="error-text">
          {{ errors.email }}
        </view>
      </view>

      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          验证码
        </view>
        <view class="input-wrapper code-wrapper">
          <input
            v-model="form.verificationCode"
            class="form-input"
            type="number"
            maxlength="6"
            placeholder="请输入6位验证码"
            :disabled="isLoading"
            @input="clearError('verificationCode')"
          >
          <button
            class="code-button"
            :class="{ disabled: !canSendCode }"
            :disabled="!canSendCode"
            @tap="handleSendCode"
          >
            {{ codeButtonText }}
          </button>
        </view>
        <view v-if="errors.verificationCode" class="error-text">
          {{ errors.verificationCode }}
        </view>
      </view>

      <view class="button-group">
        <button
          class="login-button"
          :class="{ loading: isLoading }"
          :disabled="isLoading"
          @tap="handleLogin"
        >
          {{ isLoading ? '登录中...' : '登录' }}
        </button>
      </view>

      <view class="footer-links">
        <view class="link-item">
          <text class="link-text" @tap="goToPasswordLogin">使用密码登录</text>
        </view>
      </view>
    </view>

    <view class="footer-note">
      登录即表示同意本系统的用户协议与隐私政策
    </view>
  </view>
</template>

<style lang="scss" scoped>
.email-login-page {
  min-height: 100vh;
  padding: 40rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
}

.header {
  margin-top: 80rpx;
  text-align: center;
  color: #ffffff;

  .title {
    font-size: 48rpx;
    font-weight: 700;
    margin-bottom: 16rpx;
  }

  .subtitle {
    font-size: 28rpx;
    opacity: 0.9;
  }
}

.form-card {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.1);
}

.form-item {
  margin-bottom: 36rpx;

  .form-label {
    font-size: 28rpx;
    color: #333333;
    margin-bottom: 16rpx;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8rpx;
  }

  .required {
    color: #ef4444;
  }
}

.input-wrapper {
  position: relative;
  border: 2rpx solid #e0e0e0;
  border-radius: 12rpx;
  background: #f8f9fa;
  transition: all 0.3s ease;

  &:focus-within {
    border-color: #667eea;
    background: #ffffff;
  }
}

.code-wrapper {
  display: flex;
  align-items: center;
  padding-right: 0;
}

.form-input {
  flex: 1;
  padding: 24rpx;
  font-size: 28rpx;
  color: #333333;
  background: transparent;
  border: none;

  &::placeholder {
    color: #999999;
  }

  &:disabled {
    opacity: 0.6;
  }
}

.code-button {
  flex-shrink: 0;
  margin: 8rpx;
  padding: 16rpx 24rpx;
  font-size: 26rpx;
  color: #ffffff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8rpx;
  white-space: nowrap;

  &::after {
    display: none;
  }

  &.disabled {
    opacity: 0.5;
    background: #cccccc;
  }
}

.error-text {
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #ef4444;
}

.button-group {
  margin-top: 50rpx;
}

.login-button {
  width: 100%;
  padding: 28rpx;
  font-size: 32rpx;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12rpx;
  box-shadow: 0 8rpx 20rpx rgba(102, 126, 234, 0.5);
  transition: all 0.3s ease;

  &::after {
    display: none;
  }

  &.loading {
    opacity: 0.7;
  }

  &:disabled {
    opacity: 0.6;
  }
}

.footer-links {
  margin-top: 40rpx;
  text-align: center;

  .link-item {
    font-size: 26rpx;
    color: #666666;
  }

  .link-text {
    color: #667eea;
    text-decoration: underline;
  }
}

.footer-note {
  margin-top: 60rpx;
  text-align: center;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.5;
}
</style>
