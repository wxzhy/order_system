<script lang="ts" setup>
import { computed, reactive, ref, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import type { IUploadSuccessInfo, UpdateInfoPayload } from '@/api/types/login'
import { updateUserPassword, deleteUserAccount, updateInfo } from '@/api/login'
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

const SETTINGS_SECTIONS = {
  PROFILE: 'profile',
  PASSWORD: 'password',
  DELETE: 'delete',
} as const
type SettingsSection = (typeof SETTINGS_SECTIONS)[keyof typeof SETTINGS_SECTIONS]

const settingsCollapse = ref<SettingsSection[]>([])
const showProfileForm = computed(() => settingsCollapse.value.includes(SETTINGS_SECTIONS.PROFILE))
const profileSubmitting = ref(false)
const profileForm = reactive({
  username: '',
  email: '',
  phone: '',
})
const profileErrors = reactive({
  username: '',
  email: '',
  phone: '',
})

const showPasswordForm = computed(() => settingsCollapse.value.includes(SETTINGS_SECTIONS.PASSWORD))
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

const showDeleteForm = computed(() => settingsCollapse.value.includes(SETTINGS_SECTIONS.DELETE))
const deleteSubmitting = ref(false)
const deletePassword = ref('')
const deleteError = ref('')

const passwordPattern = /^.{6,}$/

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const phonePattern = /^[0-9+\-]{5,20}$/

type PasswordField = keyof typeof passwordErrors
type ProfileField = keyof typeof profileErrors

function handleSettingsCollapseChange(names: string[] | string) {
  const next = Array.isArray(names) ? (names as SettingsSection[]) : [names as SettingsSection]
  if (!isLoggedIn.value) {
    settingsCollapse.value = []
    handleLogin()
    return
  }
  settingsCollapse.value = next
}

function closeSettingSection(section: SettingsSection) {
  if (!settingsCollapse.value.includes(section))
    return
  settingsCollapse.value = settingsCollapse.value.filter((name) => name !== section)
}

function resetSectionState(section: SettingsSection) {
  if (section === SETTINGS_SECTIONS.PROFILE)
    resetProfileForm()
  else if (section === SETTINGS_SECTIONS.PASSWORD)
    resetPasswordForm()
  else
    resetDeleteState()
}

function resetDeleteState() {
  deletePassword.value = ''
  deleteError.value = ''
}

watch(
  settingsCollapse,
  (newVal, oldVal) => {
    if (oldVal) {
      const removed = oldVal.filter((name) => !newVal.includes(name))
      removed.forEach((section) => resetSectionState(section))
    }
    const openedProfile =
      (!oldVal || !oldVal.includes(SETTINGS_SECTIONS.PROFILE)) &&
      newVal.includes(SETTINGS_SECTIONS.PROFILE)
    if (openedProfile)
      syncProfileForm()
  },
  { deep: true },
)

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

function syncProfileForm() {
  if (!isLoggedIn.value) {
    profileForm.username = ''
    profileForm.email = ''
    profileForm.phone = ''
    return
  }
  profileForm.username = userInfo.value.username || ''
  profileForm.email = userInfo.value.email || ''
  profileForm.phone = userInfo.value.phone || ''
}

function resetProfileForm() {
  profileErrors.username = ''
  profileErrors.email = ''
  profileErrors.phone = ''
  if (isLoggedIn.value)
    syncProfileForm()
  else {
    profileForm.username = ''
    profileForm.email = ''
    profileForm.phone = ''
  }
}

function clearProfileError(field: ProfileField) {
  profileErrors[field] = ''
}

function validateProfileForm(): UpdateInfoPayload | null {
  profileErrors.username = ''
  profileErrors.email = ''
  profileErrors.phone = ''
  let valid = true

  const username = profileForm.username.trim()
  const email = profileForm.email.trim()
  const phone = profileForm.phone.trim()

  if (!username) {
    profileErrors.username = '请输入用户名'
    valid = false
  }

  if (!email) {
    profileErrors.email = '请输入邮箱'
    valid = false
  }
  else if (!emailPattern.test(email)) {
    profileErrors.email = '邮箱格式不正确'
    valid = false
  }

  if (phone && !phonePattern.test(phone)) {
    profileErrors.phone = '手机号格式不正确'
    valid = false
  }

  if (!valid)
    return null

  const payload: UpdateInfoPayload = {}
  if (username !== (userInfo.value.username || ''))
    payload.username = username
  if (email !== (userInfo.value.email || ''))
    payload.email = email
  if (phone && phone !== (userInfo.value.phone || ''))
    payload.phone = phone

  if (!Object.keys(payload).length) {
    uni.showToast({ title: '尚未修改任何信息', icon: 'none' })
    return null
  }

  return payload
}

async function handleProfileSubmit() {
  if (!isLoggedIn.value) {
    handleLogin()
    return
  }
  const payload = validateProfileForm()
  if (!payload)
    return

  profileSubmitting.value = true
  try {
    await updateInfo(payload)
    await userStore.fetchUserInfo()
    uni.showToast({ title: '资料已更新', icon: 'success' })
    closeSettingSection(SETTINGS_SECTIONS.PROFILE)
  }
  catch (error: any) {
    console.error('更新用户信息失败', error)
    const message = error?.data?.detail || error?.data?.msg || error?.data?.message || error?.errMsg || '更新失败，请稍后再试'
    if (message.includes('邮箱')) {
      profileErrors.email = message
    }
    else if (message.includes('用户名')) {
      profileErrors.username = message
    }
    else if (message.includes('手机号')) {
      profileErrors.phone = message
    }
    uni.showToast({ title: message, icon: 'none' })
  }
  finally {
    profileSubmitting.value = false
  }
}

function toggleProfileForm() {
  if (!isLoggedIn.value) {
    handleLogin()
    return
  }
  if (showProfileForm.value) {
    closeSettingSection(SETTINGS_SECTIONS.PROFILE)
  }
  else {
    settingsCollapse.value = [...settingsCollapse.value, SETTINGS_SECTIONS.PROFILE]
  }
}

function resetPasswordForm() {
  passwordErrors.oldPassword = ''
  passwordErrors.newPassword = ''
  passwordErrors.confirmPassword = ''
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

function clearPasswordError(field: PasswordField) {
  passwordErrors[field] = ''
}

function validatePasswordForm() {
  passwordErrors.oldPassword = ''
  passwordErrors.newPassword = ''
  passwordErrors.confirmPassword = ''
  let valid = true

  if (!passwordForm.oldPassword) {
    passwordErrors.oldPassword = '请输入当前密码'
    valid = false
  }

  if (!passwordForm.newPassword) {
    passwordErrors.newPassword = '请输入新密码'
    valid = false
  }
  else if (passwordForm.newPassword.length < 6) {
    passwordErrors.newPassword = '密码长度不能少于6位'
    valid = false
  }

  if (!passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = '请再次输入新密码'
    valid = false
  }
  else if (passwordForm.confirmPassword !== passwordForm.newPassword) {
    passwordErrors.confirmPassword = '两次输入的密码不一致'
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
    uni.showToast({ title: '密码修改成功', icon: 'success' })
    closeSettingSection(SETTINGS_SECTIONS.PASSWORD)
    resetPasswordForm()
  }
  catch (error: any) {
    console.error('修改密码失败', error)
    const message = error?.data?.detail || error?.data?.msg || error?.data?.message || error?.errMsg || '修改失败，请稍后再试'
    if (message.includes('当前密码') || message.includes('原密码') || message.includes('旧密码')) {
      passwordErrors.oldPassword = message
    }
    else if (message.includes('新密码')) {
      passwordErrors.newPassword = message
    }
    uni.showToast({ title: message, icon: 'none' })
  }
  finally {
    passwordSubmitting.value = false
  }
}

function togglePasswordForm() {
  if (!isLoggedIn.value) {
    handleLogin()
    return
  }
  if (showPasswordForm.value) {
    closeSettingSection(SETTINGS_SECTIONS.PASSWORD)
  }
  else {
    settingsCollapse.value = [...settingsCollapse.value, SETTINGS_SECTIONS.PASSWORD]
  }
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
        settingsCollapse.value = []
        resetProfileForm()
        resetPasswordForm()
        deletePassword.value = ''
        deleteError.value = ''
        uni.showToast({
          title: '已退出登录',
          icon: 'success',
        })
      }
    },
  })
}

function toggleDeleteForm() {
  if (!isLoggedIn.value) {
    handleLogin()
    return
  }
  if (showDeleteForm.value) {
    closeSettingSection(SETTINGS_SECTIONS.DELETE)
  }
  else {
    settingsCollapse.value = [...settingsCollapse.value, SETTINGS_SECTIONS.DELETE]
  }
}

async function handleDeleteAccount() {
  if (!isLoggedIn.value) {
    handleLogin()
    return
  }

  deleteError.value = ''

  if (!deletePassword.value) {
    deleteError.value = '请输入密码'
    return
  }

  uni.showModal({
    title: '警告',
    content: '删除账号后，您的所有数据将被永久删除且无法恢复。确定要继续吗？',
    confirmText: '确认删除',
    confirmColor: '#e74c3c',
    success: async (res) => {
      if (res.confirm) {
        deleteSubmitting.value = true
        try {
          await deleteUserAccount(deletePassword.value)
          uni.showToast({ title: '账号已删除', icon: 'success' })
          // 清空状态并退出登录
          tokenStore.logout()
          settingsCollapse.value = []
          resetProfileForm()
          resetPasswordForm()
          deletePassword.value = ''
          deleteError.value = ''
        }
        catch (error) {
          console.error('删除账号失败', error)
          deleteError.value = '删除失败，请检查密码是否正确'
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
        finally {
          deleteSubmitting.value = false
        }
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
      syncProfileForm()
    }
    else {
      settingsCollapse.value = []
      resetProfileForm()
      resetPasswordForm()
      deletePassword.value = ''
      deleteError.value = ''
    }
  },
  { immediate: true },
)

watch(
  userInfo,
  () => {
    if (isLoggedIn.value && showProfileForm.value)
      syncProfileForm()
  },
)

onShow(() => {
  if (isLoggedIn.value) {
    userStore.fetchUserInfo().catch((error) => {
      console.warn('刷新用户信息失败', error)
    })
    syncProfileForm()
  }
})
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

    <view v-if="isLoggedIn" class="profile-edit-section card">
      <view class="section-title">个人资料</view>
      <view class="section-subtitle">可修改用户名、邮箱和联系电话</view>
      <u-button class="toggle-profile-button" type="primary" plain shape="circle" :custom-style="fullWidthButtonStyle"
        @click="toggleProfileForm">
        {{ showProfileForm ? '收起编辑表单' : '编辑个人资料' }}
      </u-button>
      <view v-if="showProfileForm" class="profile-form">
        <view class="form-item">
          <view class="form-label">用户名</view>
          <input v-model="profileForm.username" class="form-input" type="text" placeholder="请输入用户名"
            @input="clearProfileError('username')" />
          <view v-if="profileErrors.username" class="form-error">{{ profileErrors.username }}</view>
        </view>
        <view class="form-item">
          <view class="form-label">邮箱</view>
          <input v-model="profileForm.email" class="form-input" type="email" placeholder="请输入邮箱"
            @input="clearProfileError('email')" />
          <view v-if="profileErrors.email" class="form-error">{{ profileErrors.email }}</view>
        </view>
        <view class="form-item">
          <view class="form-label">手机号</view>
          <input v-model="profileForm.phone" class="form-input" type="tel" placeholder="请输入手机号"
            @input="clearProfileError('phone')" />
          <view v-if="profileErrors.phone" class="form-error">{{ profileErrors.phone }}</view>
        </view>
        <view class="profile-actions">
          <u-button class="profile-cancel-button" type="primary" plain shape="circle" :disabled="profileSubmitting"
            @click="toggleProfileForm">
            取消
          </u-button>
          <u-button class="profile-submit-button" type="primary" shape="circle" :loading="profileSubmitting"
            :disabled="profileSubmitting" @click="handleProfileSubmit">
            保存
          </u-button>
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

    <view v-if="isLoggedIn" class="delete-section card">
      <view class="section-title">删除账号</view>
      <view class="section-subtitle warning-text">删除账号后，您的所有数据将被永久删除且无法恢复</view>
      <u-button class="toggle-delete-button" type="error" plain shape="circle" :custom-style="fullWidthButtonStyle"
        @click="toggleDeleteForm">
        {{ showDeleteForm ? '取消删除' : '删除我的账号' }}
      </u-button>
      <view v-if="showDeleteForm" class="delete-form">
        <view class="form-item">
          <view class="form-label">确认密码</view>
          <input v-model="deletePassword" class="form-input" type="password" placeholder="请输入密码以确认删除" />
          <view v-if="deleteError" class="form-error">{{ deleteError }}</view>
        </view>
        <view class="delete-actions">
          <u-button class="delete-cancel-button" type="primary" plain shape="circle" :disabled="deleteSubmitting"
            @click="toggleDeleteForm">
            取消
          </u-button>
          <u-button class="delete-submit-button" type="error" shape="circle" :loading="deleteSubmitting"
            :disabled="deleteSubmitting" @click="handleDeleteAccount">
            确认删除
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

.profile-edit-section {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  background: #f9fafb;
  border-radius: 20rpx;
  padding: 24rpx;
}

.profile-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 8rpx;
}

.profile-cancel-button,
.profile-submit-button {
  flex: 1;
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

.delete-section {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.warning-text {
  color: #ef4444;
}

.toggle-delete-button {
  width: 100%;
}

.delete-form {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  background: #fef2f2;
  border-radius: 20rpx;
  padding: 24rpx;
  border: 2rpx solid #fee2e2;
}

.delete-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 8rpx;
}

.delete-cancel-button,
.delete-submit-button {
  flex: 1;
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
  min-height: 88rpx;
  border-radius: 12rpx;
  background: #ffffff;
  border: 2rpx solid #e5e7eb;
  box-sizing: border-box;
}

:deep(.form-input .uni-input-wrapper) {
  min-height: 88rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
}

:deep(.form-input .uni-input-input) {
  flex: 1;
  min-height: 44rpx;
  font-size: 28rpx;
  line-height: 1.4;
}

:deep(.form-input .uni-input-placeholder) {
  font-size: 28rpx;
  color: #9ca3af;
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