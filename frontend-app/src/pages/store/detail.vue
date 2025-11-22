<script setup lang="ts">
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getStoreDetail } from '@/api/store'
import { getStoreItems, type IItem } from '@/api/item'
import type { IStore } from '@/api/store'
import { LOGIN_PAGE } from '@/router/config'
import { useTokenStore } from '@/store/token'

// 餐厅信息
const storeInfo = ref<IStore | null>(null)
const storeId = ref<number>(0)
const tokenStore = useTokenStore()

// 餐点列表
const itemList = ref<IItem[]>([])
const loading = ref(false)
const finished = ref(false)

// 购物车
interface CartItem extends IItem {
  cartQuantity: number
}
const cart = ref<Map<number, CartItem>>(new Map())

// 显示购物车
const showCart = ref(false)

// 页面加载
onLoad((options) => {
  if (options?.id) {
    storeId.value = Number(options.id)
    fetchStoreInfo()
    fetchItemList()
  }
})

// 获取餐厅信息
async function fetchStoreInfo() {
  try {
    const data = await getStoreDetail(storeId.value)
    storeInfo.value = data
  }
  catch (error: any) {
    uni.showToast({
      title: error?.message || '获取餐厅信息失败',
      icon: 'none',
    })
  }
}

// 获取餐点列表
async function fetchItemList() {
  if (loading.value || finished.value)
    return

  loading.value = true
  try {
    const data = await getStoreItems(storeId.value, {
      skip: 0,
      limit: 100,
    })
    const records = data.records || []
    itemList.value = records.filter(item => item.quantity > 0)
    finished.value = true
  }
  catch (error: any) {
    uni.showToast({
      title: error?.message || '获取餐点列表失败',
      icon: 'none',
    })
  }
  finally {
    loading.value = false
  }
}

// 添加到购物车
function addToCart(item: IItem) {
  const cartItem = cart.value.get(item.id)
  if (cartItem) {
    if (cartItem.cartQuantity >= item.quantity) {
      uni.showToast({
        title: '库存不足',
        icon: 'none',
      })
      return
    }
    cartItem.cartQuantity++
  }
  else {
    cart.value.set(item.id, {
      ...item,
      cartQuantity: 1,
    })
  }
  cart.value = new Map(cart.value)
}

// 减少数量
function decreaseQuantity(itemId: number) {
  const cartItem = cart.value.get(itemId)
  if (cartItem) {
    if (cartItem.cartQuantity > 1) {
      cartItem.cartQuantity--
    }
    else {
      cart.value.delete(itemId)
    }
    cart.value = new Map(cart.value)
  }
}

// 增加数量
function increaseQuantity(itemId: number) {
  const cartItem = cart.value.get(itemId)
  if (cartItem) {
    if (cartItem.cartQuantity >= cartItem.quantity) {
      uni.showToast({
        title: '库存不足',
        icon: 'none',
      })
      return
    }
    cartItem.cartQuantity++
    cart.value = new Map(cart.value)
  }
}

// 获取商品在购物车的数量
function getCartQuantity(itemId: number): number {
  return cart.value.get(itemId)?.cartQuantity || 0
}

// 购物车商品列表
const cartItems = computed(() => Array.from(cart.value.values()))

// 购物车总数量
const cartTotalQuantity = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.cartQuantity, 0)
})

// 购物车总价
const cartTotalPrice = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.price * item.cartQuantity, 0)
})

// 清空购物车
function clearCart() {
  cart.value.clear()
  cart.value = new Map(cart.value)
  showCart.value = false
}

// 提交订单
function navigateToLoginForOrder() {
  const redirect = encodeURIComponent(`/pages/store/detail?id=${storeId.value}`)
  uni.navigateTo({
    url: `${LOGIN_PAGE}?redirect=${redirect}`,
  })
}

function ensureLoginForOrder() {
  if (tokenStore.hasLogin)
    return true

  uni.showToast({
    title: '登录后才能下单',
    icon: 'none',
  })
  setTimeout(() => {
    navigateToLoginForOrder()
  }, 500)
  return false
}

function goToCheckout() {
  if (!ensureLoginForOrder())
    return

  if (cart.value.size === 0) {
    uni.showToast({
      title: '请先选择餐点',
      icon: 'none',
    })
    return
  }

  const orderPreview = {
    storeId: storeId.value,
    storeName: storeInfo.value?.storeName || (storeInfo.value as any)?.name || '',
    items: cartItems.value.map(item => ({
      id: item.id,
      itemName: item.itemName,
      price: item.price,
      quantity: item.cartQuantity,
    })),
    totalPrice: cartTotalPrice.value,
  }

  try {
    uni.setStorageSync('pendingOrder', orderPreview)
  }
  catch (error) {
    console.error('缓存待提交订单失败', error)
    uni.showToast({
      title: '系统错误，请稍后重试',
      icon: 'none',
    })
    return
  }

  uni.navigateTo({
    url: '/pages/order/checkout',
  })
}

// 返回上一页
function goBack() {
  uni.navigateBack()
}
</script>

<template>
  <view class="store-detail-page">
    <!-- 头部导航 -->
    <view class="header">
      <view class="header-back" @tap="goBack">
        <text class="back-icon">←</text>
      </view>
      <view class="header-title">店铺详情</view>
      <view class="header-placeholder" />
    </view>

    <!-- 餐厅信息 -->
    <view v-if="storeInfo" class="store-info">
      <image v-if="storeInfo.imageURL" class="store-image" :src="storeInfo.imageURL" mode="aspectFill" />
      <view v-else class="store-image-placeholder">
        <text class="placeholder-text">暂无图片</text>
      </view>
      <view class="store-details">
        <view class="store-name">{{ storeInfo.storeName }}</view>
        <view class="store-description">{{ storeInfo.description || '暂无描述' }}</view>
        <view class="store-meta">
          <view class="meta-item">
            <text class="meta-icon">📍</text>
            <text class="meta-text">{{ storeInfo.address }}</text>
          </view>
          <view class="meta-item">
            <text class="meta-icon">🕐</text>
            <text class="meta-text">{{ storeInfo.hours || '营业时间未设置' }}</text>
          </view>
          <view class="meta-item">
            <text class="meta-icon">📞</text>
            <text class="meta-text">{{ storeInfo.phone }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 餐点列表 -->
    <view class="items-section">
      <view class="section-title">
        <text class="title-text">菜品列表</text>
        <text class="title-count">({{ itemList.length }}道菜)</text>
      </view>

      <view v-if="itemList.length > 0" class="items-list">
        <view v-for="item in itemList" :key="item.id" class="item-card">
          <image v-if="item.imageURL" class="item-image" :src="item.imageURL" mode="aspectFill" />
          <view v-else class="item-image-placeholder">
            <text class="placeholder-icon">🍽️</text>
          </view>

          <view class="item-info">
            <view class="item-name">{{ item.itemName }}</view>
            <view class="item-description">{{ item.description || '暂无描述' }}</view>
            <view class="item-footer">
              <view class="item-price">
                <text class="price-symbol">¥</text>
                <text class="price-value">{{ item.price.toFixed(2) }}</text>
              </view>
              <view class="item-stock">库存: {{ item.quantity }}</view>
            </view>
          </view>

          <view class="item-actions">
            <view v-if="getCartQuantity(item.id) === 0" class="add-button" @tap="addToCart(item)">
              <text class="add-text">+</text>
            </view>
            <view v-else class="quantity-control">
              <view class="control-button" @tap="decreaseQuantity(item.id)">
                <text class="control-text">-</text>
              </view>
              <view class="quantity-display">
                <text class="quantity-text">{{ getCartQuantity(item.id) }}</text>
              </view>
              <view class="control-button" @tap="increaseQuantity(item.id)">
                <text class="control-text">+</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view v-else-if="!loading" class="empty-state">
        <text class="empty-icon">🍽️</text>
        <text class="empty-text">该餐厅暂无可售餐点</text>
      </view>

      <view v-if="loading" class="loading-state">
        <text class="loading-text">加载中...</text>
      </view>
    </view>

    <!-- 底部购物车栏 -->
    <view v-if="cartTotalQuantity > 0" class="cart-bar">
      <view class="cart-info" @tap="showCart = !showCart">
        <view class="cart-icon-wrapper">
          <text class="cart-icon">🛒</text>
          <view v-if="cartTotalQuantity > 0" class="cart-badge">
            <text class="badge-text">{{ cartTotalQuantity }}</text>
          </view>
        </view>
        <view class="cart-price">
          <text class="price-symbol">¥</text>
          <text class="price-value">{{ cartTotalPrice.toFixed(2) }}</text>
        </view>
      </view>
      <view class="cart-submit" @tap="goToCheckout">
        <text class="submit-text">去结算</text>
      </view>
    </view>

    <!-- 购物车弹窗 -->
    <view v-if="showCart" class="cart-modal" @tap="showCart = false">
      <view class="cart-content" @tap.stop>
        <view class="cart-header">
          <text class="cart-title">购物车</text>
          <text class="cart-clear" @tap="clearCart">清空</text>
        </view>
        <scroll-view class="cart-items" scroll-y>
          <view v-for="item in cartItems" :key="item.id" class="cart-item">
            <view class="cart-item-info">
              <view class="cart-item-name">{{ item.itemName }}</view>
              <view class="cart-item-price">¥{{ item.price.toFixed(2) }}</view>
            </view>
            <view class="cart-item-actions">
              <view class="control-button small" @tap="decreaseQuantity(item.id)">
                <text class="control-text">-</text>
              </view>
              <view class="quantity-display small">
                <text class="quantity-text">{{ item.cartQuantity }}</text>
              </view>
              <view class="control-button small" @tap="increaseQuantity(item.id)">
                <text class="control-text">+</text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.store-detail-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding-bottom: 120rpx;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 30rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
}

.header-back {
  width: 80rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 40rpx;
  font-weight: bold;
}

.header-title {
  flex: 1;
  text-align: center;
  font-size: 36rpx;
  font-weight: bold;
}

.header-placeholder {
  width: 80rpx;
}

.store-info {
  margin: 30rpx;
  background: white;
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
}

.store-image {
  width: 100%;
  height: 400rpx;
}

.store-image-placeholder {
  width: 100%;
  height: 400rpx;
  background: linear-gradient(135deg, #e0e7ff 0%, #cfd9ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-text {
  color: #a5b4fc;
  font-size: 28rpx;
}

.store-details {
  padding: 30rpx;
}

.store-name {
  font-size: 40rpx;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 16rpx;
}

.store-description {
  font-size: 28rpx;
  color: #6b7280;
  line-height: 1.6;
  margin-bottom: 24rpx;
}

.store-meta {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.meta-icon {
  font-size: 28rpx;
}

.meta-text {
  font-size: 26rpx;
  color: #6b7280;
}

.items-section {
  margin: 30rpx;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 24rpx;
}

.title-text {
  font-size: 36rpx;
  font-weight: bold;
  color: #1f2937;
}

.title-count {
  font-size: 26rpx;
  color: #9ca3af;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.item-card {
  background: white;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  gap: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.item-image {
  width: 160rpx;
  height: 160rpx;
  border-radius: 16rpx;
  flex-shrink: 0;
}

.item-image-placeholder {
  width: 160rpx;
  height: 160rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #e0e7ff 0%, #cfd9ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.placeholder-icon {
  font-size: 60rpx;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.item-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 8rpx;
}

.item-description {
  font-size: 24rpx;
  color: #9ca3af;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.item-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12rpx;
}

.item-price {
  display: flex;
  align-items: baseline;
  color: #ef4444;
}

.price-symbol {
  font-size: 24rpx;
  font-weight: bold;
}

.price-value {
  font-size: 36rpx;
  font-weight: bold;
}

.item-stock {
  font-size: 24rpx;
  color: #9ca3af;
}

.item-actions {
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-button {
  width: 60rpx;
  height: 60rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
}

.add-text {
  color: white;
  font-size: 40rpx;
  font-weight: bold;
  line-height: 1;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.control-button {
  width: 60rpx;
  height: 60rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);

  &.small {
    width: 48rpx;
    height: 48rpx;
  }
}

.control-text {
  color: white;
  font-size: 32rpx;
  font-weight: bold;
  line-height: 1;
}

.quantity-display {
  min-width: 60rpx;
  text-align: center;

  &.small {
    min-width: 48rpx;
  }
}

.quantity-text {
  font-size: 28rpx;
  font-weight: bold;
  color: #1f2937;
}

.empty-state {
  padding: 120rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.empty-icon {
  font-size: 120rpx;
  opacity: 0.5;
}

.empty-text {
  font-size: 28rpx;
  color: #9ca3af;
}

.loading-state {
  padding: 60rpx 0;
  text-align: center;
}

.loading-text {
  font-size: 28rpx;
  color: #9ca3af;
}

.cart-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 20rpx 30rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.cart-info {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.cart-icon-wrapper {
  position: relative;
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cart-icon {
  font-size: 40rpx;
}

.cart-badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  background: #ef4444;
  border-radius: 50%;
  min-width: 36rpx;
  height: 36rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8rpx;
}

.badge-text {
  color: white;
  font-size: 20rpx;
  font-weight: bold;
}

.cart-price {
  display: flex;
  align-items: baseline;
  color: #ef4444;

  .price-symbol {
    font-size: 24rpx;
    font-weight: bold;
  }

  .price-value {
    font-size: 40rpx;
    font-weight: bold;
  }
}

.cart-submit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24rpx 60rpx;
  border-radius: 48rpx;
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
}

.submit-text {
  color: white;
  font-size: 32rpx;
  font-weight: bold;
}

.cart-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 200;
  display: flex;
  align-items: flex-end;
}

.cart-content {
  background: white;
  border-radius: 40rpx 40rpx 0 0;
  width: 100%;
  max-height: 60vh;
  display: flex;
  flex-direction: column;
}

.cart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx;
  border-bottom: 1px solid #e5e7eb;
}

.cart-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1f2937;
}

.cart-clear {
  font-size: 28rpx;
  color: #ef4444;
}

.cart-items {
  flex: 1;
  padding: 0 30rpx;
}

.cart-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx 0;
  border-bottom: 1px solid #f3f4f6;
}

.cart-item-info {
  flex: 1;
}

.cart-item-name {
  font-size: 28rpx;
  color: #1f2937;
  margin-bottom: 8rpx;
}

.cart-item-price {
  font-size: 24rpx;
  color: #ef4444;
  font-weight: bold;
}

.cart-item-actions {
  display: flex;
  align-items: center;
  gap: 16rpx;
}
</style>