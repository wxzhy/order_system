<script lang="ts" setup>
import { computed } from 'vue'
import type { IUploadSuccessInfo } from '@/api/types/login'
import { storeToRefs } from 'pinia'
import { LOGIN_PAGE } from '@/router/config'
import { useUserStore } from '@/store'
import { useTokenStore } from '@/store/token'
import { useUpload } from '@/utils/uploadFile'

definePage({
  style: {
    navigationBarTitleText: '我的',
  },
})

const defaultAvatar = '/static/images/default-avatar.png'

const userStore = useUserStore()
const tokenStore = useTokenStore()
const { userInfo } = storeToRefs(userStore)

const { run: uploadAvatar } = useUpload<IUploadSuccessInfo>(
  '/upload',
  {},
  {
    onSuccess: (res) => {
      userStore.setUserAvatar(res.url)
    },
  },
)

const isLoggedIn = computed(() => tokenStore.hasLogin)
const avatarSrc = computed(() => (isLoggedIn.value && userInfo.value.avatar ? userInfo.value.avatar : defaultAvatar))
const displayName = computed(() => (isLoggedIn.value ? (userInfo.value.username || '未设置用户名') : '点击登录'))
const idText = computed(() => (isLoggedIn.value ? `ID: ${userInfo.value.userId ?? userInfo.value.id ?? '-'}` : '登录后可查看个人信息'))
const tipsText = computed(() => (isLoggedIn.value ? '欢迎使用食堂餐点预约系统' : '登录后可查看订单和个人资料'))

function handleLogin() {
  uni.navigateTo({
    url: `${LOGIN_PAGE}?redirect=${encodeURIComponent('/pages/me/me')}`,
  })
}

function handleAvatarTap() {
  if (!isLoggedIn.value) {
    handleLogin()
    return
  }
  uploadAvatar()
}

function handleLogout() {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        tokenStore.logout()
        uni.showToast({
          title: '已退出登录',
          icon: 'success',
        })
      }
    },
  })
}
</script>

<template>
  <view class="profile-container">
    <view class="user-info-section">
      <view class="avatar-wrapper" @tap="handleAvatarTap">
        <image :src="avatarSrc" mode="scaleToFill" class="avatar-image" />
        <view v-if="!isLoggedIn" class="avatar-overlay">登录</view>
      </view>
      <view class="user-details">
        <view class="username" @tap="handleAvatarTap">
          {{ displayName }}
        </view>
        <view class="user-id">
          {{ idText }}
        </view>
        <view class="user-tips">
          {{ tipsText }}
        </view>
      </view>
    </view>

    <view class="action-section">
      <button
        v-if="isLoggedIn"
        type="warn"
        class="action-button"
        @tap="handleLogout"
      >
        退出登录
      </button>
      <button
        v-else
        type="primary"
        class="action-button"
        @tap="handleLogin"
      >
        立即登录
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.profile-container {
  min-height: 100vh;
  padding: 32rpx;
  box-sizing: border-box;
  background-color: #f7f8fa;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 40rpx;
}

.user-info-section {
  display: flex;
  align-items: center;
  padding: 40rpx;
  background-color: #ffffff;
  border-radius: 24rpx;
  box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.08);
}

.avatar-wrapper {
  width: 160rpx;
  height: 160rpx;
  margin-right: 32rpx;
  position: relative;
  border-radius: 50%;
  overflow: hidden;
  border: 4rpx solid #f4f4f5;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.avatar-image {
  width: 100%;
  height: 100%;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.45);
  color: #ffffff;
  font-size: 28rpx;
  letter-spacing: 4rpx;
}

.user-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.username {
  font-size: 36rpx;
  font-weight: 600;
  color: #111827;
}

.user-id,
.user-tips {
  font-size: 26rpx;
  color: #6b7280;
}

.action-section {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.action-button {
  width: 100%;
  padding: 28rpx;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: 600;

  &::after {
    display: none;
  }
}
</style>
