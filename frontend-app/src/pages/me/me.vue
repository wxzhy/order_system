<script lang="ts" setup>
import { computed, reactive, ref, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import dayjs from 'dayjs'
import type { IUploadSuccessInfo } from '@/api/types/login'
import type { IOrder } from '@/api/order'
import { getOrderList } from '@/api/order'
import { updateUserPassword } from '@/api/login'
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
const fullWidthButtonStyle = 'width: 100%; height: 88rpx;'

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
const idText = computed(() =>
  isLoggedIn.value ? `ID: ${userInfo.value.userId ?? userInfo.value.id ?? '-'}` : '登录后可查看个人信息',
)
const emailText = computed(() => (isLoggedIn.value ? userInfo.value.email || '未填写邮箱' : '登录后可查看邮箱'))
const phoneText = computed(() => (isLoggedIn.value ? userInfo.value.phone || '未填写手机号' : '登录后可查看手机号'))
const tipsText = computed(() => (isLoggedIn.value ? '欢迎使用食堂餐点预约系统' : '登录后可查看订单和个人资料'))

const orders = ref<IOrder[]>([])
const ordersLoading = ref(false)
const ordersLoaded = ref(false)
const ordersError = ref('')

const showPasswordForm = ref(false)
const passwordSubmitting = ref(false)
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})
const passwordErrors = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

type PasswordField = keyof typeof passwordErrors

const orderStatusMap: Record<string, { text: string; tagClass: string }> = {
  pending: { text: '待审核', tagClass: 'pending' },
  approved: { text: '已通过', tagClass: 'approved' },
  completed: { text: '已完成', tagClass: 'completed' },
  cancelled: { text: '已取消', tagClass: 'cancelled' },
}

function resolveOrderStatus(state: string | undefined) {
  if (!state)
    return { text: '未知状态', tagClass: 'default' }
  return orderStatusMap[state] ?? { text: state, tagClass: 'default' }
}

function formatDateTime(value?: string) {
  if (!value)
    return '--'
  return dayjs(value).format('YYYY-MM-DD HH:mm')
}

function formatAmount(order: IOrder) {
  const amount =
    typeof order.total_amount === 'number'
      ? order.total_amount
      : (order.items ?? []).reduce((sum, item) => sum + Number(item.item_price || 0) * Number(item.quantity || 0), 0)
  return amount.toFixed(2)
}

async function fetchOrders(forceRefresh = false) {
  if (!isLoggedIn.value) {
    orders.value = []
    ordersLoaded.value = false
    ordersError.value = ''
    ordersLoading.value = false
    return
  }

  if (ordersLoading.value && !forceRefresh)
    return

  ordersLoading.value = true
  ordersError.value = ''
  try {
    const res = await getOrderList({ limit: 20, skip: 0 })
    orders.value = res.records ?? []
  }
  catch (error) {
    console.error('获取订单列表失败', error)
    ordersError.value = '订单数据获取失败，请稍后重试'
  }
  finally {
    ordersLoading.value = false
    ordersLoaded.value = true
  }
}

function resetPasswordForm() {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordErrors.oldPassword = ''
  passwordErrors.newPassword = ''
  passwordErrors.confirmPassword = ''
}

function clearPasswordError(field: PasswordField) {
  passwordErrors[field] = ''
}

function togglePasswordForm() {
  if (!isLoggedIn.value) {
    handleLogin()
    return
  }
  showPasswordForm.value = !showPasswordForm.value
  if (!showPasswordForm.value)
    resetPasswordForm()
}

function validatePasswordForm() {
  let valid = true
  passwordErrors.oldPassword = ''
  passwordErrors.newPassword = ''
  passwordErrors.confirmPassword = ''

  if (!passwordForm.oldPassword) {
    passwordErrors.oldPassword = '请输入当前密码'
    valid = false
  }
  if (!passwordForm.newPassword) {
    passwordErrors.newPassword = '请输入新密码'
    valid = false
  }
  else if (passwordForm.newPassword.length < 6) {
    passwordErrors.newPassword = '新密码长度不能少于6位'
    valid = false
  }
  if (!passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = '请再次输入新密码'
    valid = false
  }
  else if (passwordForm.confirmPassword !== passwordForm.newPassword) {
    passwordErrors.confirmPassword = '两次输入的新密码不一致'
    valid = false
  }

  return valid
}

async function handlePasswordSubmit() {
  if (!isLoggedIn.value) {
    handleLogin()
    return
  }
  if (!validatePasswordForm())
    return

  passwordSubmitting.value = true
  try {
    await updateUserPassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword,
    })
    uni.showToast({ title: '密码已更新', icon: 'success' })
    resetPasswordForm()
    showPasswordForm.value = false
  }
  catch (error) {
    console.error('修改密码失败', error)
    uni.showToast({ title: '修改失败，请稍后重试', icon: 'none' })
  }
  finally {
    passwordSubmitting.value = false
  }
}

function handleViewOrder(orderId: number) {
  uni.navigateTo({ url: `/pages/order/detail?id=${orderId}` })
}

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
        orders.value = []
        ordersLoaded.value = false
        ordersError.value = ''
        ordersLoading.value = false
        showPasswordForm.value = false
        resetPasswordForm()
        uni.showToast({
          title: '已退出登录',
          icon: 'success',
        })
      }
    },
  })
}

watch(
  isLoggedIn,
  (logged) => {
    if (logged) {
      userStore.fetchUserInfo().catch((error) => {
        console.warn('刷新用户信息失败', error)
      })
      fetchOrders()
    }
    else {
      orders.value = []
      ordersLoaded.value = false
      ordersError.value = ''
      ordersLoading.value = false
      showPasswordForm.value = false
      resetPasswordForm()
    }
  },
  { immediate: true },
)

onShow(() => {
  if (isLoggedIn.value) {
    userStore.fetchUserInfo().catch((error) => {
      console.warn('刷新用户信息失败', error)
    })
    fetchOrders()
  }
})

function displayStateText(state: string | undefined) {
  return resolveOrderStatus(state).text
}

function displayStateClass(state: string | undefined) {
  return `status-${resolveOrderStatus(state).tagClass}`
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
        <view v-if="isLoggedIn" class="user-contact">
          邮箱：{{ emailText }}
        </view>
        <view v-if="isLoggedIn" class="user-contact">
          手机号：{{ phoneText }}
        </view>
        <view class="user-tips">
          {{ tipsText }}
        </view>
      </view>
    </view>

    <view v-if="isLoggedIn" class="orders-section card">
      <view class="section-header">
        <view class="section-title">我的订单</view>
        <view class="section-actions">
          <u-button class="refresh-button" type="primary" plain shape="circle" size="mini" :loading="ordersLoading"
            :disabled="ordersLoading" @click="fetchOrders(true)">
            刷新
          </u-button>
        </view>
      </view>
      <view v-if="ordersLoading && !ordersLoaded" class="orders-placeholder">正在加载订单...</view>
      <view v-else-if="ordersError" class="orders-error">{{ ordersError }}</view>
      <view v-else-if="!orders.length" class="orders-placeholder">暂无订单记录</view>
      <view v-else class="order-list">
        <view v-for="(order, index) in orders" :key="order.id"
          :class="['order-item', { 'order-item--last': index === orders.length - 1 }]">
          <view class="order-header">
            <view class="order-title">{{ order.store_name || '餐厅订单' }}</view>
            <view class="order-status">
              <text :class="['status-tag', displayStateClass(order.state)]">{{ displayStateText(order.state) }}</text>
            </view>
          </view>
          <view class="order-meta">订单编号：{{ order.id }}</view>
          <view class="order-meta">下单时间：{{ formatDateTime(order.create_time) }}</view>
          <view class="order-meta">订单金额：￥{{ formatAmount(order) }}</view>
          <view class="order-actions">
            <u-button class="order-button" type="primary" size="mini" shape="circle" @click="handleViewOrder(order.id)">
              查看详情
            </u-button>
          </view>
        </view>
      </view>
    </view>

    <view v-if="isLoggedIn" class="password-section card">
      <view class="section-title">账户安全</view>
      <view class="section-subtitle">修改登录密码，保障账户安全</view>
      <u-button class="toggle-password-button" type="primary" plain shape="circle" :custom-style="fullWidthButtonStyle"
        @click="togglePasswordForm">
        {{ showPasswordForm ? '收起修改密码' : '修改密码' }}
      </u-button>
      <view v-if="showPasswordForm" class="password-form">
        <view class="form-item">
          <view class="form-label">当前密码</view>
          <input v-model="passwordForm.oldPassword" class="form-input" type="password" placeholder="请输入当前密码"
            @input="clearPasswordError('oldPassword')" />
          <view v-if="passwordErrors.oldPassword" class="form-error">{{ passwordErrors.oldPassword }}</view>
        </view>
        <view class="form-item">
          <view class="form-label">新密码</view>
          <input v-model="passwordForm.newPassword" class="form-input" type="password" placeholder="请输入新密码"
            @input="clearPasswordError('newPassword')" />
          <view v-if="passwordErrors.newPassword" class="form-error">{{ passwordErrors.newPassword }}</view>
        </view>
        <view class="form-item">
          <view class="form-label">确认新密码</view>
          <input v-model="passwordForm.confirmPassword" class="form-input" type="password" placeholder="请再次输入新密码"
            @input="clearPasswordError('confirmPassword')" />
          <view v-if="passwordErrors.confirmPassword" class="form-error">{{ passwordErrors.confirmPassword }}</view>
        </view>
        <view class="password-actions">
          <u-button class="password-cancel-button" type="primary" plain shape="circle" :disabled="passwordSubmitting"
            @click="togglePasswordForm">
            取消
          </u-button>
          <u-button class="password-submit-button" type="primary" shape="circle" :loading="passwordSubmitting"
            :disabled="passwordSubmitting" @click="handlePasswordSubmit">
            保存
          </u-button>
        </view>
      </view>
    </view>

    <view v-if="isLoggedIn" class="action-section">
      <u-button class="action-button" type="error" shape="circle" :custom-style="fullWidthButtonStyle"
        @click="handleLogout">
        退出登录
      </u-button>
    </view>
    <view class="tabbar-safe-gap" />
  </view>
</template>

<style lang="scss" scoped>
$tabbar-gap: 180rpx;

%safe-area-padding {
  padding-bottom: $tabbar-gap;
  padding-bottom: calc(#{$tabbar-gap} + constant(safe-area-inset-bottom));
  padding-bottom: calc(#{$tabbar-gap} + env(safe-area-inset-bottom));
}

.section-safe-bottom {
  @extend %safe-area-padding;
}

.profile-container {
  min-height: 100vh;
  padding: 32rpx;
  box-sizing: border-box;
  background-color: #f7f8fa;
  display: flex;
  flex-direction: column;
  gap: 32rpx;
  padding-bottom: calc(80rpx + #{$tabbar-gap});
  padding-bottom: calc(80rpx + #{$tabbar-gap} + constant(safe-area-inset-bottom));
  padding-bottom: calc(80rpx + #{$tabbar-gap} + env(safe-area-inset-bottom));
}

.card {
  background-color: #ffffff;
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.08);
}

.user-info-section {
  display: flex;
  align-items: center;
  gap: 32rpx;
  position: relative;
  @extend .card;
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
.user-tips,
.user-contact {
  font-size: 26rpx;
  color: #6b7280;
}

.user-contact {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.orders-section {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 16rpx;
}

.section-actions {
  margin-left: auto;
  display: flex;
  justify-content: flex-end;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.section-subtitle {
  font-size: 26rpx;
  color: #6b7280;
  margin-top: 8rpx;
}

.refresh-button {
  min-width: 160rpx;
}

.orders-placeholder {
  font-size: 26rpx;
  color: #6b7280;
}

.orders-error {
  font-size: 26rpx;
  color: #ef4444;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.order-item {
  padding: 24rpx;
  border-radius: 20rpx;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.order-item--last {
  margin-bottom: 0;
}

.order-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.order-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #111827;
}

.order-meta {
  font-size: 26rpx;
  color: #4b5563;
}

.order-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12rpx;
}

.order-button {
  min-width: 180rpx;
}

.status-tag {
  padding: 8rpx 20rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  font-weight: 500;
  background: #f3f4f6;
  color: #4b5563;
}

.status-pending {
  background: #fff7ed;
  color: #d97706;
}

.status-approved,
.status-completed {
  background: #ecfdf5;
  color: #047857;
}

.status-cancelled {
  background: #fef2f2;
  color: #dc2626;
}

.status-default {
  background: #e5e7eb;
  color: #4b5563;
}

.password-section {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.toggle-password-button {
  width: 100%;
}

.password-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 8rpx;
}

.password-cancel-button,
.password-submit-button {
  flex: 1;
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  background: #f9fafb;
  border-radius: 20rpx;
  padding: 24rpx;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.form-label {
  font-size: 26rpx;
  color: #374151;
}

.form-input {
  width: 100%;
  padding: 22rpx 24rpx;
  border-radius: 12rpx;
  background: #ffffff;
  border: 2rpx solid #e5e7eb;
  font-size: 28rpx;
  box-sizing: border-box;
}

.form-error {
  font-size: 24rpx;
  color: #ef4444;
}

.action-section {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  position: relative;
  z-index: 0;
}

.action-button {
  width: 100%;
  font-size: 32rpx;
  font-weight: 600;
  position: relative;
  z-index: 0;
}

:deep(.action-button.u-button) {
  position: relative;
  z-index: 0;
}

.tabbar-safe-gap {
  flex-shrink: 0;
  height: $tabbar-gap;
  height: calc(#{$tabbar-gap} + constant(safe-area-inset-bottom));
  height: calc(#{$tabbar-gap} + env(safe-area-inset-bottom));
}
</style>
