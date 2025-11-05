<script lang="ts" setup>
import { computed, reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { REGISTER_PAGE, RESET_PASSWORD_PAGE } from '@/router/config'
import { useTokenStore } from '@/store/token'
import { tabbarList } from '@/tabbar/config'
import { isPageTabbar } from '@/tabbar/store'
import { ensureDecodeURIComponent, parseUrlToObj } from '@/utils'

definePage({
  style: {
    navigationBarTitleText: '登录',
  },
})

const form = reactive({
  username: '',
  password: '',
})

const errors = reactive({
  username: '',
  password: '',
})

const isLoading = ref(false)
const showPassword = ref(false)
const redirectUrl = ref('')

const passwordInputType = computed(() => (showPassword.value ? 'text' : 'password'))
const tokenStore = useTokenStore()

onLoad((options) => {
  if (options?.redirect) {
    redirectUrl.value = ensureDecodeURIComponent(options.redirect)
  }
  else {
    redirectUrl.value = tabbarList[0].pagePath
  }
})

function clearError(field: 'username' | 'password') {
  errors[field] = ''
}

function validateForm() {
  errors.username = ''
  errors.password = ''
  let valid = true

  if (!form.username.trim()) {
    errors.username = '请输入用户名、邮箱或手机号'
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

  return valid
}

function togglePasswordVisibility() {
  showPassword.value = !showPassword.value
}

function goToRegister() {
  uni.navigateTo({ url: REGISTER_PAGE })
}

function goToResetPassword() {
  uni.navigateTo({ url: RESET_PASSWORD_PAGE })
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
    await tokenStore.login({
      username: form.username.trim(),
      password: form.password,
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
  <view class="login-page">
    <view class="header">
      <view class="title">
        食堂餐点预约系统
      </view>
      <view class="subtitle">
        欢迎登录
      </view>
    </view>

    <view class="form-card">
      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          用户名 / 邮箱 / 手机号
        </view>
        <view class="input-wrapper">
          <input
            v-model="form.username"
            class="form-input"
            type="text"
            placeholder="请输入用户名、邮箱或手机号"
            :disabled="isLoading"
            @input="clearError('username')"
          >
        </view>
        <view v-if="errors.username" class="error-text">
          {{ errors.username }}
        </view>
      </view>

      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          密码
        </view>
        <view class="input-wrapper password-wrapper">
          <input
            v-model="form.password"
            class="form-input"
            :type="passwordInputType"
            placeholder="请输入密码"
            :disabled="isLoading"
            @input="clearError('password')"
          >
          <view class="password-toggle" @tap="togglePasswordVisibility">
            <text class="toggle-icon">{{ showPassword ? '隐藏' : '显示' }}</text>
          </view>
        </view>
        <view v-if="errors.password" class="error-text">
          {{ errors.password }}
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
          <text>还没有账号？</text>
          <text class="link-text" @tap="goToRegister">立即注册</text>
        </view>
        <view class="link-item">
          <text>忘记密码？</text>
          <text class="link-text" @tap="goToResetPassword">重置密码</text>
        </view>
      </view>
    </view>

    <view class="footer-note">
      登录即表示同意本系统的用户协议与隐私政策
    </view>
  </view>
</template>

<style lang="scss" scoped>
.login-page {
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

.password-wrapper {
  display: flex;
  align-items: center;
}

.form-input {
  width: 100%;
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

.password-toggle {
  position: absolute;
  right: 24rpx;
  top: 50%;
  transform: translateY(-50%);
  padding: 8rpx;
  font-size: 26rpx;
  color: #667eea;
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
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  text-align: center;

  .link-item {
    font-size: 26rpx;
    color: #666666;
  }

  .link-text {
    color: #667eea;
    margin-left: 8rpx;
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
