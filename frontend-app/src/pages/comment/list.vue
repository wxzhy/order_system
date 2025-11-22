<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import type { IComment } from '@/api/comment'
import { getCommentList, deleteComment } from '@/api/comment'
import { useTokenStore } from '@/store/token'
import { LOGIN_PAGE } from '@/router/config'

definePage({
    style: {
        navigationBarTitleText: '我的评论',
    },
})

const tokenStore = useTokenStore()
const comments = ref<IComment[]>([])
const loading = ref(false)
const refreshing = ref(false)
const deletingIds = ref<Set<number>>(new Set())

const statusMap: Record<string, { text: string; tagClass: string }> = {
    pending: { text: '待审核', tagClass: 'warning' },
    approved: { text: '已通过', tagClass: 'success' },
    rejected: { text: '已驳回', tagClass: 'error' },
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

async function fetchComments() {
    if (!tokenStore.hasLogin) {
        comments.value = []
        return
    }

    loading.value = true
    try {
        const res = await getCommentList({ limit: 50, skip: 0 })
        comments.value = res.records ?? []
    }
    catch (error) {
        console.error('获取评论列表失败', error)
        uni.showToast({
            title: '获取评论失败',
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
        const res = await getCommentList({ limit: 50, skip: 0 })
        comments.value = res.records ?? []
    }
    catch (error) {
        console.error('刷新评论列表失败', error)
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

function handleDelete(commentId: number) {
    uni.showModal({
        title: '确认删除',
        content: '确定要删除这条评论吗？',
        success: async (res) => {
            if (res.confirm) {
                deletingIds.value.add(commentId)
                try {
                    await deleteComment(commentId)
                    uni.showToast({
                        title: '删除成功',
                        icon: 'success',
                    })
                    // 从列表中移除已删除的评论
                    comments.value = comments.value.filter(c => c.id !== commentId)
                }
                catch (error) {
                    console.error('删除评论失败', error)
                    uni.showToast({
                        title: '删除失败',
                        icon: 'none',
                    })
                }
                finally {
                    deletingIds.value.delete(commentId)
                }
            }
        },
    })
}

function handleLogin() {
    uni.navigateTo({
        url: `${LOGIN_PAGE}?redirect=${encodeURIComponent('/pages/comment/list')}`,
    })
}

onShow(() => {
    if (tokenStore.hasLogin) {
        fetchComments()
    }
})
</script>

<template>
    <view class="comment-list-page">
        <view v-if="!tokenStore.hasLogin" class="login-prompt">
            <view class="prompt-text">请先登录查看评论</view>
            <u-button class="login-button" type="primary" shape="circle" @click="handleLogin">
                去登录
            </u-button>
        </view>

        <view v-else class="comment-container">
            <scroll-view class="scroll-container" scroll-y refresher-enabled :refresher-triggered="refreshing"
                @refresherrefresh="onRefresherRefresh">
                <view v-if="loading && !comments.length" class="loading-state">
                    <u-loading mode="circle" />
                    <text class="loading-text">加载中...</text>
                </view>

                <view v-else-if="!comments.length" class="empty-state">
                    <view class="empty-icon">💬</view>
                    <view class="empty-text">暂无评论记录</view>
                </view>

                <view v-else class="comment-list">
                    <view v-for="comment in comments" :key="comment.id" class="comment-card">
                        <view class="card-header">
                            <view class="store-name">{{ comment.store_name || '餐厅评论' }}</view>
                            <u-tag :text="getStatusConfig(comment.state).text"
                                :type="getStatusConfig(comment.state).tagClass" plain shape="circle" size="mini" />
                        </view>

                        <view class="card-body">
                            <view class="comment-content">{{ comment.content }}</view>
                            <view class="comment-meta">
                                <text class="meta-label">提交时间：</text>
                                <text class="meta-value">{{ formatDateTime(comment.publish_time) }}</text>
                            </view>
                            <view v-if="comment.review_time" class="comment-meta">
                                <text class="meta-label">审核时间：</text>
                                <text class="meta-value">{{ formatDateTime(comment.review_time) }}</text>
                            </view>
                        </view>

                        <view class="card-footer">
                            <u-button class="delete-button" type="error" plain size="mini" shape="circle"
                                :loading="deletingIds.has(comment.id)" :disabled="deletingIds.has(comment.id)"
                                @click="handleDelete(comment.id)">
                                删除评论
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

.comment-list-page {
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

.comment-container {
    height: 100vh;
}

.scroll-container {
    height: 100%;
    padding: 32rpx;
    box-sizing: border-box;
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

.comment-list {
    display: flex;
    flex-direction: column;
    gap: 24rpx;
}

.comment-card {
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

.comment-content {
    font-size: 28rpx;
    color: #1f2937;
    line-height: 1.6;
    padding: 16rpx;
    background: #f9fafb;
    border-radius: 12rpx;
}

.comment-meta {
    display: flex;
    align-items: center;
    font-size: 24rpx;
}

.meta-label {
    color: #6b7280;
    min-width: 140rpx;
}

.meta-value {
    color: #1f2937;
    flex: 1;
}

.card-footer {
    display: flex;
    justify-content: flex-end;
}

.delete-button {
    min-width: 160rpx;
}

.tabbar-safe-gap {
    height: $tabbar-gap;
    height: calc(#{$tabbar-gap} + env(safe-area-inset-bottom));
    flex-shrink: 0;
}
</style>