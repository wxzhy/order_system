<script lang="ts" setup>
import type { IStore } from '@/api/store'
import { getStoreList } from '@/api/store'
import { safeAreaInsets } from '@/utils/systemInfo'

defineOptions({ name: 'Home' })
definePage({
  type: 'home',
  style: { navigationBarTitleText: '餐厅列表' },
})

const storeList = ref<IStore[]>([])
const loading = ref(false)
const hasMore = ref(true)
const page = ref(1)
const pageSize = 10

async function fetchStoreList(isRefresh = false) {
  if (loading.value)
    return

  if (isRefresh) {
    page.value = 1
    hasMore.value = true
  }

  loading.value = true

  try {
    const skip = (page.value - 1) * pageSize
    const res = await getStoreList({ skip, limit: pageSize, state: 'approved' })
    const newStores = res.records || []

    if (isRefresh) {
      storeList.value = newStores
    }
    else {
      storeList.value = [...storeList.value, ...newStores]
    }

    hasMore.value = storeList.value.length < res.total
    page.value++
  }
  catch (error) {
    console.error('获取餐厅列表失败', error)
    uni.showToast({ title: '获取餐厅列表失败', icon: 'none' })
  }
  finally {
    loading.value = false
  }
}

function onRefresh() {
  fetchStoreList(true)
}

function onLoadMore() {
  if (!loading.value && hasMore.value)
    fetchStoreList()
}

function viewStoreDetail(store: IStore) {
  uni.navigateTo({ url: `/pages-sub/store/detail?id=${store.id}` })
}

onLoad(() => {
  fetchStoreList(true)
})
</script>

<template>
  <view class="store-list-page">
    <view class="header" :style="{ paddingTop: `${safeAreaInsets?.top || 0}px` }">
      <view class="header-content">
        <view class="title">
          餐点订购系统
        </view>

        <view class="subtitle">
          选择您喜欢的餐厅
        </view>
      </view>
    </view>

    <scroll-view class="store-list-container" :refresher-enabled="true" :refresher-triggered="loading && page === 1"
      scroll-y @scrolltolower="onLoadMore" @refresherrefresh="onRefresh">
      <view class="store-list">
        <view v-for="store in storeList" :key="store.id" class="store-item" @click="viewStoreDetail(store)">
          <view class="store-image-wrapper">
            <image v-if="store.imageURL" :src="store.imageURL" class="store-image" mode="aspectFill" />

            <view v-else class="store-image-placeholder">
              <text class="placeholder-text">暂无图片</text>
            </view>
          </view>

          <view class="store-info">
            <view class="store-name">
              {{ store.storeName }}
            </view>

            <view v-if="store.description" class="store-description">
              {{ store.description }}
            </view>

            <view class="store-meta">
              <view class="meta-item">
                <text class="icon">📍</text>

                <text class="meta-text">{{ store.address }}</text>
              </view>

              <view v-if="store.hours" class="meta-item">
                <text class="icon">🕐</text>

                <text class="meta-text">{{ store.hours }}</text>
              </view>

              <view class="meta-item">
                <text class="icon">📞</text>

                <text class="meta-text">{{ store.phone }}</text>
              </view>
            </view>
          </view>
        </view>

        <view v-if="!loading && storeList.length === 0" class="empty-state">
          <view class="empty-icon">
            🍽️
          </view>

          <view class="empty-text">
            暂无餐厅信息
          </view>
        </view>

        <view v-if="loading" class="loading-more">
          <text class="loading-text">加载中...</text>
        </view>

        <view v-else-if="!hasMore && storeList.length > 0" class="no-more">
          <text class="no-more-text">没有更多了</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<style lang="scss" scoped>
.store-list-page {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 40rpx;

  .header-content {
    padding: 40rpx 32rpx 0;
    text-align: center;

    .title {
      font-size: 44rpx;
      font-weight: bold;
      color: #ffffff;
      margin-bottom: 12rpx;
    }

    .subtitle {
      font-size: 26rpx;
      color: rgba(255, 255, 255, 0.9);
    }
  }
}

.store-list-container {
  flex: 1;
  margin-top: -20rpx;
}

.store-list {
  padding: 0 32rpx 32rpx;
}

.store-item {
  background: #ffffff;
  border-radius: 16rpx;
  margin-bottom: 24rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;

  &:active {
    transform: scale(0.98);
  }
}

.store-image-wrapper {
  width: 100%;
  height: 360rpx;
  position: relative;
  overflow: hidden;
}

.store-image {
  width: 100%;
  height: 100%;
  display: block;
}

.store-image-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
  display: flex;
  align-items: center;
  justify-content: center;

  .placeholder-text {
    font-size: 28rpx;
    color: #999999;
  }
}

.store-info {
  padding: 32rpx;
}

.store-name {
  font-size: 36rpx;
  font-weight: bold;
  color: #333333;
  margin-bottom: 16rpx;
}

.store-description {
  font-size: 28rpx;
  color: #666666;
  line-height: 1.6;
  margin-bottom: 20rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
  text-overflow: ellipsis;
}

.store-meta {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.meta-item {
  display: flex;
  align-items: center;
  font-size: 24rpx;
  color: #999999;

  .icon {
    margin-right: 8rpx;
    font-size: 28rpx;
  }

  .meta-text {
    flex: 1;
    line-height: 1.5;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;

  .empty-icon {
    font-size: 120rpx;
    margin-bottom: 32rpx;
  }

  .empty-text {
    font-size: 28rpx;
    color: #999999;
  }
}

.loading-more,
.no-more {
  text-align: center;
  padding: 32rpx 0;

  .loading-text,
  .no-more-text {
    font-size: 24rpx;
    color: #999999;
  }
}
</style>
