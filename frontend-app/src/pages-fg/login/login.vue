<script lang="ts" setup>
import { REGISTER_PAGE } from '@/router/config'
import { useTokenStore } from '@/store/token'
import { useUserStore } from '@/store/user'
import { tabbarList } from '@/tabbar/config'
import { isPageTabbar } from '@/tabbar/store'
import { ensureDecodeURIComponent } from '@/utils'
import { parseUrlToObj } from '@/utils/index'

definePage({
  style: {
    navigationBarTitleText: '登录',
  },
})

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: '',
})

// 表单验证错误信息
const errors = reactive({
  username: '',
  password: '',
})

// 是否正在登录
const isLoading = ref(false)

// 是否显示密码
const showPassword = ref(false)

// 密码输入框类型
const passwordInputType = computed(() => (showPassword.value ? 'text' : 'text'))

const redirectUrl = ref('')
onLoad((options) => {
  console.log('login options: ', options)
  if (options.redirect) {
    redirectUrl.value = ensureDecodeURIComponent(options.redirect)
  }
  else {
    redirectUrl.value = tabbarList[0].pagePath
  }
  console.log('redirectUrl.value: ', redirectUrl.value)
})

const userStore = useUserStore()
const tokenStore = useTokenStore()

// 表单验证
function validateForm() {
  let isValid = true
  errors.username = ''
  errors.password = ''

  // 验证用户名
  if (!loginForm.username.trim()) {
    errors.username = '请输入用户名/邮箱/手机号'
    isValid = false
  }

  // 验证密码
  if (!loginForm.password) {
    errors.password = '请输入密码'
    isValid = false
  }
  else if (loginForm.password.length < 6) {
    errors.password = '密码长度至少6位'
    isValid = false
  }

  return isValid
}

// 清除错误信息
function clearError(field: 'username' | 'password') {
  errors[field] = ''
}

// 执行登录
async function doLogin() {
  // 验证表单
  if (!validateForm()) {
    return
  }

  if (tokenStore.hasLogin) {
    uni.navigateBack()
    return
  }

  isLoading.value = true

  try {
    // 调用登录接口
    await tokenStore.login({
      username: loginForm.username.trim(),
      password: loginForm.password,
    })
    console.log('登录成功，跳转到:', redirectUrl.value)

    // 登录成功后跳转
    let path = redirectUrl.value
    if (!path.startsWith('/')) {
      path = `/${path}`
    }
    const { path: _path, query } = parseUrlToObj(path)
    console.log('_path:', _path, 'query:', query, 'path:', path)
    console.log('isPageTabbar(_path):', isPageTabbar(_path))

    if (isPageTabbar(_path)) {
      // 经过我的测试 switchTab 不能带 query 参数, 不管是放到 url  还是放到 query ,
      // 最后跳转过去的时候都会丢失 query 信息
      uni.switchTab({
        url: path,
      })
    }
    else {
      // 自己决定是 redirectTo 还是 navigateBack
      uni.navigateBack()
    }
  }
  catch (error: any) {
    console.error('登录失败', error)
    // tokenStore.login 已经处理了错误提示
  }
  finally {
    isLoading.value = false
  }
}

// 跳转到注册页面
function goToRegister() {
  uni.navigateTo({
    url: REGISTER_PAGE,
  })
}

// 切换密码显示状态
function togglePasswordVisibility() {
  showPassword.value = !showPassword.value
}
</script>

<template>
  <view class="login-container">
    <!-- 头部标题 -->
    <view class="header">
      <view class="title">
        餐点订购系统
      </view>
      <view class="subtitle">
        欢迎登录
      </view>
    </view>

    <!-- 登录表单 -->
    <view class="form-container">
      <!-- 用户名输入 -->
      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          用户名/邮箱/手机号
        </view>
        <view class="input-wrapper">
          <input v-model="loginForm.username" class="form-input" type="text" placeholder="请输入用户名、邮箱或手机号"
            :disabled="isLoading" @input="clearError('username')">
        </view>
        <view v-if="errors.username" class="error-text">
          {{ errors.username }}
        </view>
      </view>

      <!-- 密码输入 -->
      <view class="form-item">
        <view class="form-label">
          <text class="required">*</text>
          密码
        </view>
        <view class="input-wrapper password-wrapper">
          <input v-model="loginForm.password" class="form-input" type="text" :password="!showPassword"
            placeholder="请输入密码" :disabled="isLoading" @input="clearError('password')">
          <view class="password-toggle" @click="togglePasswordVisibility">
            <text class="toggle-icon">{{ showPassword ? '👁️' : '👁️‍🗨️' }}</text>
          </view>
        </view>
        <view v-if="errors.password" class="error-text">
          {{ errors.password }}
        </view>
      </view>

      <!-- 登录按钮 -->
      <view class="button-group">
        <button class="login-button" :class="{ loading: isLoading }" :disabled="isLoading" @click="doLogin">
          {{ isLoading ? '登录中...' : '登录' }}
        </button>
      </view>

      <!-- 底部链接 -->
      <view class="footer-links">
        <view class="link-item">
          <text>还没有账号？</text>
          <text class="link-text" @click="goToRegister">立即注册</text>
        </view>
      </view>
    </view>

    <!-- 底部提示 -->
    <view class="bottom-tips">
      <text class="tips-text">登录即表示您同意相关用户协议和隐私政策</text>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40rpx;
  display: flex;
  flex-direction: column;
}

.header {
  margin-top: 80rpx;
  margin-bottom: 60rpx;
  text-align: center;

  .title {
    font-size: 48rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 20rpx;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  }

  .subtitle {
    font-size: 28rpx;
    color: rgba(255, 255, 255, 0.9);
  }
}

.form-container {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.form-item {
  margin-bottom: 40rpx;

  .form-label {
    font-size: 28rpx;
    color: #333333;
    margin-bottom: 16rpx;
    font-weight: 500;

    .required {
      color: #ff4444;
      margin-right: 4rpx;
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

    &.password-wrapper {
      display: flex;
      align-items: center;
    }
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
    padding: 8rpx;
    cursor: pointer;

    .toggle-icon {
      font-size: 32rpx;
    }
  }

  .error-text {
    font-size: 24rpx;
    color: #ff4444;
    margin-top: 12rpx;
    padding-left: 4rpx;
  }
}

.button-group {
  margin-top: 60rpx;

  .login-button {
    width: 100%;
    padding: 28rpx;
    font-size: 32rpx;
    font-weight: bold;
    color: #ffffff;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 12rpx;
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;

    &:active {
      transform: translateY(2px);
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }

    &.loading {
      opacity: 0.7;
    }

    &:disabled {
      opacity: 0.6;
      transform: none !important;
    }
  }
}

.footer-links {
  margin-top: 40rpx;
  text-align: center;

  .link-item {
    font-size: 26rpx;
    color: #666666;

    .link-text {
      color: #667eea;
      font-weight: 500;
      margin-left: 8rpx;
      text-decoration: underline;
    }
  }
}

.bottom-tips {
  margin-top: auto;
  padding: 40rpx 0;
  text-align: center;

  .tips-text {
    font-size: 22rpx;
    color: rgba(255, 255, 255, 0.8);
  }
}
</style>
