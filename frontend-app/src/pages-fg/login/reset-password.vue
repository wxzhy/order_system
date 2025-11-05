<script lang="ts" setup>
import { computed, reactive, ref, onUnmounted } from 'vue'
import { resetPassword, sendEmailCode } from '@/api/login'
import { LOGIN_PAGE } from '@/router/config'

definePage({
  style: {
    navigationBarTitleText: '重置密码',
  },
})

const form = reactive({
  email: '',
  verificationCode: '',
  newPassword: '',
  confirmPassword: '',
})

const errors = reactive({
  email: '',
  verificationCode: '',
  newPassword: '',
  confirmPassword: '',
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
      scene: 'reset-password',
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
  errors.email = ''
  errors.verificationCode = ''
  errors.newPassword = ''
  errors.confirmPassword = ''
  let valid = true

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

  if (!form.newPassword) {
    errors.newPassword = '请输入新密码'
    valid = false
  }
  else if (form.newPassword.length < 6) {
    errors.newPassword = '密码长度不能少于6位'
    valid = false
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = '请再次输入新密码'
    valid = false
  }
  else if (form.confirmPassword !== form.newPassword) {
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
    await resetPassword({
      email: form.email.trim(),
      verification_code: form.verificationCode.trim(),
      new_password: form.newPassword,
    })
    uni.showToast({ title: '密码已重置', icon: 'success' })
    stopCountdown()
    setTimeout(() => {
      uni.redirectTo({ url: LOGIN_PAGE })
    }, 800)
  }
  catch (error) {
    console.error('重置密码失败', error)
    uni.showToast({ title: '重置失败，请稍后重试', icon: 'none' })
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
  <view class="reset-page">
    <view class="header">
      <view class="title">
        重置密码
      </view>
      <view class="subtitle">
        输入邮箱并完成验证
      </view>
    </view>

    <view class="form-card">
      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          邮箱
        </view>
        <input
          v-model="form.email"
          class="form-input"
          type="text"
          placeholder="请输入注册邮箱"
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
          新密码
        </view>
        <input
          v-model="form.newPassword"
          class="form-input"
          type="password"
          placeholder="请输入新密码"
          :disabled="isSubmitting"
          @input="clearError('newPassword')"
        >
        <view v-if="errors.newPassword" class="error-text">
          {{ errors.newPassword }}
        </view>
      </view>

      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          确认新密码
        </view>
        <input
          v-model="form.confirmPassword"
          class="form-input"
          type="password"
          placeholder="请再次输入新密码"
          :disabled="isSubmitting"
          @input="clearError('confirmPassword')"
        >
        <view v-if="errors.confirmPassword" class="error-text">
          {{ errors.confirmPassword }}
        </view>
      </view>

      <view class="button-group">
        <button
          class="submit-button"
          :class="{ loading: isSubmitting }"
          :disabled="isSubmitting"
          @tap="handleSubmit"
        >
          {{ isSubmitting ? '提交中...' : '提交' }}
        </button>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.reset-page {
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

.submit-button {
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

