<script lang="ts" setup>
import { computed, reactive, ref, onUnmounted } from 'vue'
import { sendEmailCode, register as registerApi } from '@/api/login'
import { LOGIN_PAGE } from '@/router/config'

definePage({
  style: {
    navigationBarTitleText: '注册',
  },
})

const form = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  verificationCode: '',
})

const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  verificationCode: '',
})

const isSubmitting = ref(false)
const isSendingCode = ref(false)
const countdown = ref(0)

let timer: number | null = null

const canSendCode = computed(() => Boolean(form.email.trim()) && !isSendingCode.value && countdown.value === 0)

const sendButtonText = computed(() => {
  if (isSendingCode.value)
    return '发送中...'
  if (countdown.value > 0)
    return `${countdown.value}s后重发`
  return '获取验证码'
})

function clearError(field: keyof typeof errors) {
  errors[field] = ''
}

function validateEmail(email: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

function startCountdown(seconds = 60) {
  countdown.value = seconds
  timer = setInterval(() => {
    if (countdown.value <= 1) {
      stopCountdown()
      return
    }
    countdown.value -= 1
  }, 1000)
}

function stopCountdown() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  countdown.value = 0
}

async function handleSendCode() {
  errors.email = ''

  const email = form.email.trim()
  if (!email) {
    errors.email = '请输入邮箱'
    return
  }
  if (!validateEmail(email)) {
    errors.email = '邮箱格式不正确'
    return
  }

  isSendingCode.value = true
  try {
    await sendEmailCode({
      email,
      scene: 'register',
    })
    uni.showToast({ title: '验证码已发送', icon: 'success' })
    startCountdown()
  }
  catch (error) {
    console.error('发送验证码失败', error)
    uni.showToast({ title: '发送失败，请稍后重试', icon: 'none' })
  }
  finally {
    isSendingCode.value = false
  }
}

function validateForm() {
  errors.username = ''
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''
  errors.verificationCode = ''
  let valid = true

  if (!form.username.trim()) {
    errors.username = '请输入用户名'
    valid = false
  }

  const email = form.email.trim()
  if (!email) {
    errors.email = '请输入邮箱'
    valid = false
  }
  else if (!validateEmail(email)) {
    errors.email = '邮箱格式不正确'
    valid = false
  }

  if (!form.verificationCode.trim()) {
    errors.verificationCode = '请输入邮箱验证码'
    valid = false
  }
  else if (form.verificationCode.trim().length !== 6) {
    errors.verificationCode = '验证码长度为6位'
    valid = false
  }

  if (!form.password) {
    errors.password = '请输入密码'
    valid = false
  }
  else if (form.password.length < 6) {
    errors.password = '密码长度不能少于6位'
    valid = false
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = '请再次输入密码'
    valid = false
  }
  else if (form.confirmPassword !== form.password) {
    errors.confirmPassword = '两次输入的密码不一致'
    valid = false
  }

  return valid
}

async function handleSubmit() {
  if (!validateForm())
    return

  isSubmitting.value = true
  try {
    await registerApi({
      username: form.username.trim(),
      email: form.email.trim(),
      phone: form.phone.trim() || undefined,
      password: form.password,
      verification_code: form.verificationCode.trim(),
    })
    uni.showToast({ title: '注册成功，前往登录', icon: 'success' })
    stopCountdown()
    setTimeout(() => {
      uni.redirectTo({ url: LOGIN_PAGE })
    }, 800)
  }
  catch (error: any) {
    console.error('注册失败', error)
    const message = error?.data?.detail || error?.data?.msg || error?.data?.message || error?.errMsg || '注册失败，请稍后再试'
    if (message.includes('邮箱'))
      errors.email = message
    else if (message.includes('验证码'))
      errors.verificationCode = message
    else if (message.includes('用户名'))
      errors.username = message
    uni.showToast({ title: message, icon: 'none' })
  }
  finally {
    isSubmitting.value = false
  }
}

onUnmounted(() => {
  stopCountdown()
})
</script>

<template>
  <view class="register-page">
    <view class="header">
      <view class="title">
        创建新账号
      </view>
      <view class="subtitle">
        填写信息完成注册
      </view>
    </view>

    <view class="form-card">
      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          用户名
        </view>
        <input
          v-model="form.username"
          class="form-input"
          type="text"
          placeholder="请输入用户名"
          :disabled="isSubmitting"
          @input="clearError('username')"
        >
        <view v-if="errors.username" class="error-text">
          {{ errors.username }}
        </view>
      </view>

      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          邮箱
        </view>
        <input
          v-model="form.email"
          class="form-input"
          type="text"
          placeholder="请输入邮箱"
          :disabled="isSubmitting"
          @input="clearError('email')"
        >
        <view v-if="errors.email" class="error-text">
          {{ errors.email }}
        </view>
      </view>

      <view class="form-item code-item">
        <view class="form-label">
          <text class="required">*</text>
          邮箱验证码
        </view>
        <view class="code-wrapper">
          <input
            v-model="form.verificationCode"
            class="form-input"
            type="text"
            maxlength="6"
            placeholder="请输入6位验证码"
            :disabled="isSubmitting"
            @input="clearError('verificationCode')"
            inputmode="numeric"
          >
          <button
            class="code-button"
            :disabled="!canSendCode"
            @tap="handleSendCode"
          >
            {{ sendButtonText }}
          </button>
        </view>
        <view v-if="errors.verificationCode" class="error-text">
          {{ errors.verificationCode }}
        </view>
      </view>

      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          密码
        </view>
        <input
          v-model="form.password"
          class="form-input"
          type="password"
          placeholder="请输入密码"
          :disabled="isSubmitting"
          @input="clearError('password')"
        >
        <view v-if="errors.password" class="error-text">
          {{ errors.password }}
        </view>
      </view>

      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          确认密码
        </view>
        <input
          v-model="form.confirmPassword"
          class="form-input"
          type="password"
          placeholder="请再次输入密码"
          :disabled="isSubmitting"
          @input="clearError('confirmPassword')"
        >
        <view v-if="errors.confirmPassword" class="error-text">
          {{ errors.confirmPassword }}
        </view>
      </view>

      <view class="form-item">
        <view class="form-label">
          手机号（选填）
        </view>
        <input
          v-model="form.phone"
          class="form-input"
          type="text"
          placeholder="请输入手机号"
          :disabled="isSubmitting"
        >
      </view>

      <view class="button-group">
        <button
          class="register-button"
          :class="{ loading: isSubmitting }"
          :disabled="isSubmitting"
          @tap="handleSubmit"
        >
          {{ isSubmitting ? '注册中...' : '注册' }}
        </button>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.register-page {
  min-height: 100vh;
  padding: 40rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-sizing: border-box;
}

.header {
  margin-top: 60rpx;
  text-align: center;
  color: #ffffff;

  .title {
    font-size: 44rpx;
    font-weight: 700;
    margin-bottom: 12rpx;
  }

  .subtitle {
    font-size: 28rpx;
    opacity: 0.9;
  }
}

.form-card {
  margin-top: 40rpx;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 50rpx 36rpx 60rpx;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.1);
}

.form-item {
  margin-bottom: 32rpx;

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

.form-input {
  width: 100%;
  padding: 22rpx 24rpx;
  border-radius: 12rpx;
  border: 2rpx solid #e0e0e0;
  background: #f8f9fa;
  font-size: 28rpx;
  transition: all 0.3s ease;

  &:focus {
    border-color: #667eea;
    background: #ffffff;
  }

  &:disabled {
    opacity: 0.6;
  }
}

.code-item {
  .code-wrapper {
    display: flex;
    gap: 16rpx;
    align-items: center;
  }

  .code-button {
    min-width: 160rpx;
    padding: 20rpx 24rpx;
    font-size: 26rpx;
    color: #ffffff;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 12rpx;

    &::after {
      display: none;
    }

    &:disabled {
      opacity: 0.6;
    }
  }
}

.error-text {
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #ef4444;
}

.button-group {
  margin-top: 40rpx;
}

.register-button {
  width: 100%;
  padding: 28rpx;
  font-size: 32rpx;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12rpx;
  box-shadow: 0 8rpx 20rpx rgba(102, 126, 234, 0.5);

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
</style>

