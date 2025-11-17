<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getOrderDetail } from '@/api/order'

const order = ref<Awaited<ReturnType<typeof getOrderDetail>> | null>(null)
const loading = ref(false)

const statusMap: Record<string, { text: string; type: 'warning' | 'success' | 'error' | 'info' }> = {
  pending: { text: '待审核', type: 'warning' },
  approved: { text: '已通过', type: 'success' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'error' },
}

function getStatusConfig(state?: string) {
  if (!state)
    return { text: '未知状态', type: 'info' as const }
  return statusMap[state] ?? { text: state, type: 'info' as const }
}

onLoad(async (options) => {
  if (!options?.id) {
    uni.showToast({
      title: "未找到订单",
      icon: "none",
    })
    setTimeout(() => {
      uni.navigateBack()
    }, 500)
    return
  }

  loading.value = true
  try {
    const data = await getOrderDetail(Number(options.id))
    order.value = data
  }
  catch (error: any) {
    uni.showToast({
      title: error?.message || "获取订单失败",
      icon: "none",
    })
  }
  finally {
    loading.value = false
  }
})
</script>

<template>
  <view class="order-detail-page">
    <view v-if="loading" class="loading">加载中...</view>
    <view v-else-if="order" class="content">
      <view class="section">
        <view class="section-title">订单状态</view>
        <view class="status">
          <u-tag
            :text="getStatusConfig(order.state).text"
            :type="getStatusConfig(order.state).type"
            plain
            shape="circle"
          />
        </view>
        <view class="detail-row">订单编号：{{ order.id }}</view>
        <view class="detail-row">下单时间：{{ order.create_time }}</view>
      </view>

      <view class="section">
        <view class="section-title">餐厅信息</view>
        <view class="detail-row">{{ order.store_name }}</view>
      </view>

      <view class="section">
        <view class="section-title">餐点列表</view>
        <view v-for="item in order.items" :key="item.id" class="item-row">
          <view class="item-name">{{ item.item_name }}</view>
          <view class="item-quantity">x{{ item.quantity }}</view>
          <view class="item-price">￥{{ (item.item_price * item.quantity).toFixed(2) }}</view>
        </view>
        <view class="total-row" v-if="order.total_amount">
          <text>合计</text>
          <text class="total-amount">￥{{ order.total_amount.toFixed(2) }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.order-detail-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding: 32rpx;
  box-sizing: border-box;
}

.loading {
  margin-top: 120rpx;
  text-align: center;
  color: #6b7280;
  font-size: 28rpx;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.section {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 28rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  margin-bottom: 16rpx;
  color: #1f2937;
}

.status {
  display: inline-flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.detail-row {
  font-size: 28rpx;
  color: #4b5563;
  margin-bottom: 8rpx;
}

.item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 28rpx;
  color: #4b5563;
  padding: 16rpx 0;
  border-bottom: 1px solid #f3f4f6;
}

.item-name {
  flex: 1;
  margin-right: 16rpx;
}

.item-quantity {
  width: 80rpx;
  text-align: right;
}

.item-price {
  width: 160rpx;
  text-align: right;
  color: #ef4444;
}

.total-row {
  margin-top: 16rpx;
  display: flex;
  justify-content: space-between;
  font-size: 30rpx;
  font-weight: 600;
}

.total-amount {
  color: #ef4444;
}
</style>

