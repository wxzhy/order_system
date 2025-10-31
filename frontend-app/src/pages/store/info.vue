<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import type { IStore } from '@/api/store'
import { getStoreDetail } from '@/api/store'
import { getCommentList, createComment, type IComment } from '@/api/comment'
import { safeAreaInsets } from '@/utils/systemInfo'

defineOptions({ name: 'StoreInfo' })

// 餐厅信息
const storeInfo = ref<IStore | null>(null)
const storeId = ref<number>(0)
const loading = ref(false)

// 评论列表
const commentList = ref<IComment[]>([])
const commentLoading = ref(false)
const commentPage = ref(1)
const commentPageSize = 10
const hasMoreComments = ref(true)

// 新评论
const showCommentInput = ref(false)
const newCommentContent = ref('')
const submittingComment = ref(false)

// Tab 切换
const activeTab = ref<'intro' | 'comments'>('intro')

// 页面加载
onLoad((options) => {
  if (options?.id) {
    storeId.value = Number(options.id)
    fetchStoreInfo()
    fetchComments()
  }
})

// 获取餐厅信息
async function fetchStoreInfo() {
  loading.value = true
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
  finally {
    loading.value = false
  }
}

// 获取评论列表
async function fetchComments(isRefresh = false) {
  if (commentLoading.value)
    return

  if (isRefresh) {
    commentPage.value = 1
    hasMoreComments.value = true
  }

  commentLoading.value = true
  try {
    const skip = (commentPage.value - 1) * commentPageSize
    const data = await getCommentList({
      store_id: storeId.value,
      state: 'approved',
      skip,
      limit: commentPageSize,
    })

    const newComments = data.records || []

    if (isRefresh) {
      commentList.value = newComments
    }
    else {
      commentList.value = [...commentList.value, ...newComments]
    }

    hasMoreComments.value = commentList.value.length < data.total
    commentPage.value++
  }
  catch (error: any) {
    uni.showToast({
      title: error?.message || '获取评论失败',
      icon: 'none',
    })
  }
  finally {
    commentLoading.value = false
  }
}

// 加载更多评论
function loadMoreComments() {
  if (!commentLoading.value && hasMoreComments.value) {
    fetchComments()
  }
}

// 打开评论输入框
function openCommentInput() {
  showCommentInput.value = true
  newCommentContent.value = ''
}

// 关闭评论输入框
function closeCommentInput() {
  showCommentInput.value = false
  newCommentContent.value = ''
}

// 提交评论
async function submitComment() {
  if (!newCommentContent.value.trim()) {
    uni.showToast({
      title: '请输入评论内容',
      icon: 'none',
    })
    return
  }

  submittingComment.value = true
  try {
    await createComment({
      store_id: storeId.value,
      content: newCommentContent.value.trim(),
    })

    uni.showToast({
      title: '评论提交成功,等待审核',
      icon: 'success',
    })

    closeCommentInput()
    // 刷新评论列表
    setTimeout(() => {
      fetchComments(true)
    }, 500)
  }
  catch (error: any) {
    uni.showToast({
      title: error?.message || '评论提交失败',
      icon: 'none',
    })
  }
  finally {
    submittingComment.value = false
  }
}

// 去点餐
function goToOrder() {
  uni.navigateTo({
    url: `/pages/store/detail?id=${storeId.value}`,
  })
}

// 返回上一页
function goBack() {
  uni.navigateBack()
}

// 格式化时间
function formatTime(time: string) {
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1)
    return '刚刚'
  if (minutes < 60)
    return `${minutes}分钟前`
  if (hours < 24)
    return `${hours}小时前`
  if (days < 7)
    return `${days}天前`

  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

// 评论数量
const commentCount = computed(() => commentList.value.length)
</script>

<template>
  <view class="store-info-page">
    <!-- 头部导航 -->
    <view class="header" :style="{ paddingTop: `${(safeAreaInsets?.top || 0) + 10}px` }">
      <view class="header-back" @tap="goBack">
        <text class="back-icon">←</text>
      </view>
      <view class="header-title">
        餐厅详情
      </view>
      <view class="header-placeholder" />
    </view>

    <!-- 餐厅封面图 -->
    <view class="store-cover">
      <image v-if="storeInfo?.imageURL" class="cover-image" :src="storeInfo.imageURL" mode="aspectFill" />
      <view v-else class="cover-placeholder">
        <text class="placeholder-icon">🏪</text>
      </view>
    </view>

    <!-- 餐厅基本信息 -->
    <view v-if="storeInfo" class="store-basic">
      <view class="store-name">
        {{ storeInfo.storeName }}
      </view>
      <view class="store-meta-list">
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

    <!-- Tab 切换 -->
    <view class="tabs">
      <view class="tab-item" :class="{ active: activeTab === 'intro' }" @tap="activeTab = 'intro'">
        <text class="tab-text">餐厅介绍</text>
        <view v-if="activeTab === 'intro'" class="tab-indicator" />
      </view>
      <view class="tab-item" :class="{ active: activeTab === 'comments' }" @tap="activeTab = 'comments'">
        <text class="tab-text">顾客评价 ({{ commentCount }})</text>
        <view v-if="activeTab === 'comments'" class="tab-indicator" />
      </view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-area" scroll-y @scrolltolower="activeTab === 'comments' && loadMoreComments()">
      <!-- 餐厅介绍 -->
      <view v-if="activeTab === 'intro'" class="intro-section">
        <view class="section-title">
          <text class="title-icon">📖</text>
          <text class="title-text">餐厅简介</text>
        </view>
        <view class="intro-content">
          <text class="intro-text">{{ storeInfo?.description || '该餐厅暂无简介' }}</text>
        </view>

        <view class="section-title">
          <text class="title-icon">✨</text>
          <text class="title-text">特色推荐</text>
        </view>
        <view class="intro-content">
          <text class="intro-text">欢迎光临本店,我们提供优质的餐点和服务,期待您的品鉴!</text>
        </view>
      </view>

      <!-- 评论区 -->
      <view v-if="activeTab === 'comments'" class="comments-section">
        <view v-if="commentList.length > 0" class="comment-list">
          <view v-for="comment in commentList" :key="comment.id" class="comment-item">
            <view class="comment-header">
              <view class="comment-user">
                <view class="user-avatar">
                  <text class="avatar-text">{{ comment.user_name?.charAt(0) || '?' }}</text>
                </view>
                <view class="user-info">
                  <text class="user-name">{{ comment.user_name || '匿名用户' }}</text>
                  <text class="comment-time">{{ formatTime(comment.publish_time) }}</text>
                </view>
              </view>
            </view>
            <view class="comment-content">
              <text class="comment-text">{{ comment.content }}</text>
            </view>
          </view>
        </view>

        <view v-else-if="!commentLoading" class="empty-comments">
          <text class="empty-icon">💬</text>
          <text class="empty-text">暂无评价,快来抢沙发吧!</text>
        </view>

        <view v-if="commentLoading" class="loading-more">
          <text class="loading-text">加载中...</text>
        </view>

        <view v-if="!hasMoreComments && commentList.length > 0" class="no-more">
          <text class="no-more-text">没有更多了</text>
        </view>
      </view>
    </scroll-view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="comment-btn" @tap="openCommentInput">
        <text class="btn-icon">✍️</text>
        <text class="btn-text">写评价</text>
      </view>
      <view class="order-btn" @tap="goToOrder">
        <text class="order-text">去点餐</text>
      </view>
    </view>

    <!-- 评论输入弹窗 -->
    <view v-if="showCommentInput" class="comment-modal" @tap="closeCommentInput">
      <view class="comment-modal-content" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">写评价</text>
          <text class="modal-close" @tap="closeCommentInput">×</text>
        </view>
        <view class="modal-body">
          <textarea v-model="newCommentContent" class="comment-textarea" placeholder="分享你的用餐体验..." :maxlength="500"
            :auto-height="true" :show-confirm-bar="false" />
          <view class="textarea-counter">
            <text class="counter-text">{{ newCommentContent.length }}/500</text>
          </view>
        </view>
        <view class="modal-footer">
          <view class="modal-btn cancel" @tap="closeCommentInput">
            <text class="btn-text">取消</text>
          </view>
          <view class="modal-btn submit" :class="{ disabled: !newCommentContent.trim() || submittingComment }"
            @tap="submitComment">
            <text class="btn-text">{{ submittingComment ? '提交中...' : '提交' }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.store-info-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 120rpx;
}

.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10rpx 30rpx 20rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
  z-index: 100;
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

.store-cover {
  width: 100%;
  height: 400rpx;
  margin-top: 88rpx;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #e0e7ff 0%, #cfd9ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  font-size: 120rpx;
  opacity: 0.5;
}

.store-basic {
  background: white;
  padding: 40rpx 30rpx;
  border-radius: 0 0 24rpx 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.store-name {
  font-size: 44rpx;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 24rpx;
}

.store-meta-list {
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
  flex: 1;
}

.tabs {
  display: flex;
  background: white;
  margin-bottom: 20rpx;
  padding: 0 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.tab-item {
  flex: 1;
  padding: 30rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.tab-text {
  font-size: 28rpx;
  color: #6b7280;
  font-weight: 500;
  transition: all 0.3s;
}

.tab-item.active .tab-text {
  color: #667eea;
  font-weight: bold;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  width: 60rpx;
  height: 6rpx;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 3rpx;
}

.content-area {
  height: calc(100vh - 520rpx - 120rpx);
  background: white;
  margin: 0 20rpx 20rpx;
  border-radius: 24rpx;
  padding: 30rpx;
}

.intro-section {
  .section-title {
    display: flex;
    align-items: center;
    gap: 12rpx;
    margin-bottom: 24rpx;
    margin-top: 30rpx;

    &:first-child {
      margin-top: 0;
    }
  }

  .title-icon {
    font-size: 32rpx;
  }

  .title-text {
    font-size: 32rpx;
    font-weight: bold;
    color: #1f2937;
  }

  .intro-content {
    background: #f9fafb;
    padding: 30rpx;
    border-radius: 16rpx;
    margin-bottom: 20rpx;
  }

  .intro-text {
    font-size: 28rpx;
    color: #4b5563;
    line-height: 1.8;
  }
}

.comments-section {
  .comment-list {
    display: flex;
    flex-direction: column;
    gap: 30rpx;
  }

  .comment-item {
    background: #f9fafb;
    padding: 24rpx;
    border-radius: 16rpx;
  }

  .comment-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16rpx;
  }

  .comment-user {
    display: flex;
    align-items: center;
    gap: 16rpx;
  }

  .user-avatar {
    width: 60rpx;
    height: 60rpx;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .avatar-text {
    color: white;
    font-size: 24rpx;
    font-weight: bold;
  }

  .user-info {
    display: flex;
    flex-direction: column;
    gap: 4rpx;
  }

  .user-name {
    font-size: 26rpx;
    color: #1f2937;
    font-weight: 500;
  }

  .comment-time {
    font-size: 22rpx;
    color: #9ca3af;
  }

  .comment-content {
    .comment-text {
      font-size: 26rpx;
      color: #4b5563;
      line-height: 1.6;
    }
  }
}

.empty-comments {
  padding: 120rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.empty-icon {
  font-size: 100rpx;
  opacity: 0.3;
}

.empty-text {
  font-size: 28rpx;
  color: #9ca3af;
}

.loading-more {
  padding: 40rpx 0;
  text-align: center;
}

.loading-text {
  font-size: 24rpx;
  color: #9ca3af;
}

.no-more {
  padding: 40rpx 0;
  text-align: center;
}

.no-more-text {
  font-size: 24rpx;
  color: #d1d5db;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 20rpx 30rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.comment-btn {
  flex: 1;
  background: #f3f4f6;
  padding: 24rpx 30rpx;
  border-radius: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
}

.btn-icon {
  font-size: 28rpx;
}

.btn-text {
  font-size: 28rpx;
  color: #4b5563;
  font-weight: 500;
}

.order-btn {
  flex: 2;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24rpx 60rpx;
  border-radius: 48rpx;
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.order-text {
  color: white;
  font-size: 32rpx;
  font-weight: bold;
}

.comment-modal {
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

.comment-modal-content {
  background: white;
  border-radius: 40rpx 40rpx 0 0;
  width: 100%;
  padding: 30rpx;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 20rpx;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 30rpx;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1f2937;
}

.modal-close {
  font-size: 48rpx;
  color: #9ca3af;
  line-height: 1;
}

.modal-body {
  flex: 1;
  margin-bottom: 30rpx;
}

.comment-textarea {
  width: 100%;
  min-height: 300rpx;
  padding: 24rpx;
  background: #f9fafb;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #1f2937;
  line-height: 1.6;
}

.textarea-counter {
  margin-top: 12rpx;
  text-align: right;
}

.counter-text {
  font-size: 24rpx;
  color: #9ca3af;
}

.modal-footer {
  display: flex;
  gap: 20rpx;
}

.modal-btn {
  flex: 1;
  padding: 28rpx;
  border-radius: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;

  &.cancel {
    background: #f3f4f6;

    .btn-text {
      color: #6b7280;
    }
  }

  &.submit {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

    .btn-text {
      color: white;
    }

    &.disabled {
      opacity: 0.5;
    }
  }

  .btn-text {
    font-size: 28rpx;
    font-weight: 500;
  }
}
</style>
