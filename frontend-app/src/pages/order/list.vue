<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import type { IOrder } from '@/api/order'
import { getOrderList } from '@/api/order'
import { useTokenStore } from '@/store/token'
import { LOGIN_PAGE } from '@/router/config'

definePage({
  style: {
    navigationBarTitleText: '我的订单',
  },
})

const tokenStore = useTokenStore()
const orders = ref<IOrder[]>([])
const loading = ref(false)
const refreshing = ref(false)

const statusMap: Record<string, { text: string; tagClass: string }> = {
  pending: { text: '待审核', tagClass: 'warning' },
  approved: { text: '已通过', tagClass: 'success' },
  completed: { text: '已完成', tagClass: 'success' },
  cancelled: { text: '已取消', tagClass: 'error' },
}

function getStatusConfig(state?: string) {
  if (!state)
    return { text: '未知状态', tagClass: 'info' }
  return statusMap[state] ?? { text: state, tagClass: 'info' }
}

function formatDateTime(value?: string) {
  if (!value)
    return '--'
  const date = new Date(value)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hour}:${minute}`
}

function formatAmount(order: IOrder) {
  const amount
    = typeof order.total_amount === 'number'
      ? order.total_amount
      : (order.items ?? []).reduce((sum, item) => sum + Number(item.item_price || 0) * Number(item.quantity || 0), 0)
  return amount.toFixed(2)
}

async function fetchOrders() {
  if (!tokenStore.hasLogin) {
    orders.value = []
    return
  }

  loading.value = true
  try {
    const res = await getOrderList({ limit: 50, skip: 0 })
    orders.value = res.records ?? []
  }
  catch (error) {
    console.error('获取订单列表失败', error)
    uni.showToast({
      title: '获取订单失败',
      icon: 'none',
    })
  }
  finally {
    loading.value = false
  }
}

async function handleRefresh() {
  if (!tokenStore.hasLogin) {
    uni.showToast({
      title: '请先登录',
      icon: 'none',
    })
    return
  }

  refreshing.value = true
  try {
    const res = await getOrderList({ limit: 50, skip: 0 })
    orders.value = res.records ?? []
  }
  catch (error) {
    console.error('刷新订单列表失败', error)
    uni.showToast({
      title: '刷新失败',
      icon: 'none',
    })
  }
  finally {
    refreshing.value = false
  }
}

function onRefresherRefresh() {
  handleRefresh()
}

function handleViewDetail(orderId: number) {
  uni.navigateTo({ url: `/pages/order/detail?id=${orderId}` })
}

function handleLogin() {
  uni.navigateTo({
    url: `${LOGIN_PAGE}?redirect=${encodeURIComponent('/pages/order/list')}`,
  })
}

onShow(() => {
  if (tokenStore.hasLogin) {
    fetchOrders()
  }
})
</script>

<template>
  <view class="order-list-page">
    <view v-if="!tokenStore.hasLogin" class="login-prompt">
      <view class="prompt-text">请先登录查看订单</view>
      <u-button class="login-button" type="primary" shape="circle" @click="handleLogin">
        去登录
      </u-button>
    </view>

    <view v-else class="order-container">
      <scroll-view
        class="scroll-container"
        scroll-y
        refresher-enabled
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresherRefresh"
      >
        <view v-if="loading && !orders.length" class="loading-state">
          <u-loading mode="circle" />
          <text class="loading-text">加载中...</text>
        </view>

        <view v-else-if="!orders.length" class="empty-state">
          <view class="empty-icon">📦</view>
          <view class="empty-text">暂无订单记录</view>
        </view>

        <view v-else class="order-list">
          <view v-for="order in orders" :key="order.id" class="order-card">
            <view class="card-header">
              <view class="store-name">{{ order.store_name || '餐厅订单' }}</view>
              <u-tag
                :text="getStatusConfig(order.state).text"
                :type="getStatusConfig(order.state).tagClass"
                plain
                shape="circle"
                size="mini"
              />
            </view>

            <view class="card-body">
              <view class="order-info">
                <text class="info-label">订单编号：</text>
                <text class="info-value">{{ order.id }}</text>
              </view>
              <view class="order-info">
                <text class="info-label">下单时间：</text>
                <text class="info-value">{{ formatDateTime(order.create_time) }}</text>
              </view>
              <view class="order-info">
                <text class="info-label">订单金额：</text>
                <text class="info-value amount">￥{{ formatAmount(order) }}</text>
              </view>
            </view>

            <view class="card-footer">
              <u-button
                class="detail-button"
                type="primary"
                size="mini"
                shape="circle"
                @click="handleViewDetail(order.id)"
              >
                查看详情
              </u-button>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="tabbar-safe-gap" />
  </view>
</template>

<style lang="scss" scoped>
$tabbar-gap: 180rpx;

.order-list-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: calc(#{$tabbar-gap} + env(safe-area-inset-bottom));
}

.login-prompt {
  padding: 120rpx 64rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 48rpx;
}

.prompt-text {
  font-size: 32rpx;
  color: #6b7280;
  text-align: center;
}

.login-button {
  width: 400rpx;
}

.order-container {
  height: 100vh;
}

.scroll-container {
  height: 100%;
  padding: 32rpx;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
  padding: 120rpx 0;
}

.loading-text {
  font-size: 28rpx;
  color: #6b7280;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 96rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #6b7280;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.order-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 28rpx;
  box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #f3f4f6;
}

.store-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
  flex: 1;
  margin-right: 16rpx;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.order-info {
  display: flex;
  align-items: center;
  font-size: 26rpx;
}

.info-label {
  color: #6b7280;
  min-width: 140rpx;
}

.info-value {
  color: #1f2937;
  flex: 1;
}

.amount {
  color: #ef4444;
  font-weight: 600;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
}

.detail-button {
  min-width: 160rpx;
}

.tabbar-safe-gap {
  height: $tabbar-gap;
  height: calc(#{$tabbar-gap} + env(safe-area-inset-bottom));
  flex-shrink: 0;
}
</style>
