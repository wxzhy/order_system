<script setup lang="ts">
import { reactive, ref } from "vue"
import { onLoad } from "@dcloudio/uni-app"
import { createOrder, type IOrderItemCreate } from "@/api/order"

definePage({
  style: {
    navigationBarTitleText: '确认订单',
  },
})

interface PendingOrderItem {
  id: number
  itemName: string
  price: number
  quantity: number
}

interface PendingOrder {
  storeId: number
  storeName: string
  items: PendingOrderItem[]
  totalPrice: number
}

const pendingOrder = ref<PendingOrder | null>(null)
const submitting = ref(false)

const form = reactive({
  contactPhone: "",
  pickupTime: "",
})

onLoad(() => {
  const data = uni.getStorageSync("pendingOrder") as PendingOrder | undefined
  if (data && data.items && data.items.length > 0) {
    pendingOrder.value = data
  }
  else {
    uni.showToast({
      title: "暂无待提交的订单",
      icon: "none",
    })
    setTimeout(() => {
      uni.navigateBack()
    }, 500)
  }
})

function validateForm() {
  if (!pendingOrder.value)
    return false

  if (!form.contactPhone.trim()) {
    uni.showToast({
      title: "请输入联系电话",
      icon: "none",
    })
    return false
  }
  return true
}

async function submitOrder() {
  if (!validateForm())
    return

  if (!pendingOrder.value)
    return

  const items: IOrderItemCreate[] = pendingOrder.value.items.map(item => ({
    item_id: item.id,
    quantity: item.quantity,
  }))

  try {
    submitting.value = true
    const order = await createOrder({
      store_id: pendingOrder.value.storeId,
      items,
      contact_phone: form.contactPhone.trim(),
      pickup_time: form.pickupTime || undefined,
    })

    uni.removeStorageSync("pendingOrder")
    uni.showToast({
      title: "下单成功",
      icon: "success",
    })

    setTimeout(() => {
      uni.redirectTo({
        url: `/pages/order/detail?id=${order.id}`,
      })
    }, 800)
  }
  catch (error: any) {
    uni.showToast({
      title: error?.message || "提交订单失败",
      icon: "none",
    })
  }
  finally {
    submitting.value = false
  }
}
</script>

<template>
  <view class="checkout-page">
    <view v-if="pendingOrder" class="content">
      <view class="section">
        <view class="section-title">订单信息</view>
        <view class="store-name">{{ pendingOrder.storeName }}</view>
        <view class="item-list">
          <view v-for="item in pendingOrder.items" :key="item.id" class="item-row">
            <view class="item-name">{{ item.itemName }}</view>
            <view class="item-quantity">x{{ item.quantity }}</view>
            <view class="item-price">￥{{ (item.price * item.quantity).toFixed(2) }}</view>
          </view>
        </view>
        <view class="total-row">
          <text>合计</text>
          <text class="total-amount">￥{{ pendingOrder.totalPrice.toFixed(2) }}</text>
        </view>
      </view>

      <view class="section">
        <view class="section-title">取餐信息</view>
        <view class="form-item">
          <view class="label">联系电话</view>
          <input v-model="form.contactPhone" class="input" type="text" placeholder="请输入联系电话" />
        </view>
        <view class="form-item">
          <view class="label">取餐时间</view>
          <input v-model="form.pickupTime" class="input" type="datetime-local" placeholder="可选择预计取餐时间" />
        </view>
      </view>

      <button class="submit-btn" type="primary" :loading="submitting" @tap="submitOrder">
        {{ submitting ? "提交中..." : "确认下单" }}
      </button>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.checkout-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding: 32rpx;
  box-sizing: border-box;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

.section {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 28rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  margin-bottom: 24rpx;
  color: #1f2937;
}

.store-name {
  font-size: 30rpx;
  font-weight: 500;
  margin-bottom: 16rpx;
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.item-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 28rpx;
  color: #4b5563;
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
  margin-top: 24rpx;
  display: flex;
  justify-content: space-between;
  font-size: 30rpx;
  font-weight: 600;
  color: #1f2937;
}

.total-amount {
  color: #ef4444;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.label {
  font-size: 28rpx;
  color: #4b5563;
}

.input {
  height: 80rpx;
  padding: 0 24rpx;
  border: 1px solid #e5e7eb;
  border-radius: 12rpx;
  background: #f9fafb;
  font-size: 28rpx;
  box-sizing: border-box;
}

.submit-btn {
  margin-top: 16rpx;
  width: 100%;
  height: 92rpx;
  border-radius: 16rpx;
  font-size: 32rpx;
}
</style>