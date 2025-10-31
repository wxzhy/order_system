<script setup lang="ts">
import { onMounted, ref } from 'vue';
import type { TabPaneName } from 'element-plus';
import { ElButton, ElCard, ElTabPane, ElTable, ElTableColumn, ElTag, ElTabs } from 'element-plus';
import {
  fetchGetCommentList,
  fetchGetOrderList,
  fetchGetStoreList,
  reviewComment,
  reviewStore,
  updateOrder
} from '@/service/api';

defineOptions({ name: 'ApprovalManage' });

// Tab active key
const activeTab = ref('store');

// Store approval data
const storeData = ref<Api.SystemManage.Store[]>([]);
const storeLoading = ref(false);

// Order approval data
const orderData = ref<Api.SystemManage.Order[]>([]);
const orderLoading = ref(false);

// Comment approval data
const commentData = ref<Api.SystemManage.Comment[]>([]);
const commentLoading = ref(false);

// Get pending stores
async function getPendingStores() {
  storeLoading.value = true;
  try {
    const response = await fetchGetStoreList({ skip: 0, limit: 100, state: 'pending' });
    storeData.value = response?.records || [];
  } catch (error: any) {
    window.$message?.error(error?.message || '获取待审核商家失败');
  } finally {
    storeLoading.value = false;
  }
}

// Get pending orders
async function getPendingOrders() {
  orderLoading.value = true;
  try {
    const response = await fetchGetOrderList({ skip: 0, limit: 100, state: 'pending' });
    orderData.value = response?.records || [];
  } catch (error: any) {
    window.$message?.error(error?.message || '获取待审核订单失败');
  } finally {
    orderLoading.value = false;
  }
}

// Get pending comments
async function getPendingComments() {
  commentLoading.value = true;
  try {
    const response = await fetchGetCommentList({ skip: 0, limit: 100, state: 'pending' });
    commentData.value = response?.records || [];
  } catch (error: any) {
    window.$message?.error(error?.message || '获取待审核评论失败');
  } finally {
    commentLoading.value = false;
  }
}

// Handle store review
async function handleStoreReview(id: number, state: 'approved' | 'rejected') {
    try {
        await reviewStore(id, { state });
        window.$message?.success(state === 'approved' ? '已批准' : '已拒绝');
        getPendingStores();
    } catch (error: any) {
        window.$message?.error(error?.message || '审批失败');
    }
}

// Handle order review
async function handleOrderReview(id: number, state: 'approved' | 'cancelled') {
    try {
        await updateOrder(id, { state });
        window.$message?.success(state === 'approved' ? '已批准' : '已拒绝');
        getPendingOrders();
    } catch (error: any) {
        window.$message?.error(error?.message || '审批失败');
    }
}

// Handle comment review
async function handleCommentReview(id: number, approved: boolean) {
  try {
    const state = approved ? 'approved' : 'rejected';
    await reviewComment(id, state);
    window.$message?.success(approved ? '已批准' : '已拒绝');
    getPendingComments();
  } catch (error: any) {
    window.$message?.error(error?.message || '审批失败');
  }
}

// Handle tab change
function handleTabChange(tab: TabPaneName) {
  const tabStr = String(tab);
  if (tabStr === 'store') {
    getPendingStores();
  } else if (tabStr === 'order') {
    getPendingOrders();
  } else if (tabStr === 'comment') {
    getPendingComments();
  }
}

onMounted(() => {
  getPendingStores();
});
</script>

<template>
    <div class="h-full flex-col-stretch gap-16px overflow-hidden">
        <ElCard class="flex-1-hidden">
            <template #header>
                <div class="flex items-center justify-between">
                    <h2 class="text-18px font-600 m-0">审批看板</h2>
                    <div class="flex gap-12px">
                        <ElTag type="warning">待审核商家: {{ storeData.length }}</ElTag>
                        <ElTag type="warning">待审核订单: {{ orderData.length }}</ElTag>
                        <ElTag type="warning">待审核评论: {{ commentData.length }}</ElTag>
                    </div>
                </div>
            </template>

            <ElTabs v-model="activeTab" @tab-change="handleTabChange">
                <!-- Store Approval Tab -->
                <ElTabPane label="商家审批" name="store">
                    <ElTable v-loading="storeLoading" :data="storeData" border stripe height="500">
                        <ElTableColumn type="index" label="序号" width="64" align="center" />
                        <ElTableColumn prop="id" label="商家ID" width="100" align="center" />
                        <ElTableColumn prop="name" label="商家名称" width="200" />
                        <ElTableColumn prop="description" label="描述" min-width="200" show-overflow-tooltip />
                        <ElTableColumn prop="owner_name" label="所有者" width="120" />
                        <ElTableColumn prop="create_time" label="创建时间" width="180" />
                        <ElTableColumn label="操作" width="200" fixed="right" align="center">
                            <template #default="{ row }">
                                <div class="flex-center gap-8px">
                                    <ElButton type="success" plain size="small" @click="handleStoreReview(row.id, 'approved')">
                                        批准
                                    </ElButton>
                                    <ElButton type="warning" plain size="small" @click="handleStoreReview(row.id, 'rejected')">
                                        拒绝
                                    </ElButton>
                                </div>
                            </template>
                        </ElTableColumn>
                    </ElTable>
                </ElTabPane>

                <!-- Order Approval Tab -->
                <ElTabPane label="订单审批" name="order">
                    <ElTable v-loading="orderLoading" :data="orderData" border stripe height="500">
                        <ElTableColumn type="index" label="序号" width="64" align="center" />
                        <ElTableColumn prop="id" label="订单ID" width="100" align="center" />
                        <ElTableColumn prop="user_id" label="用户ID" width="100" align="center" />
                        <ElTableColumn prop="store_id" label="商家ID" width="100" align="center" />
                        <ElTableColumn label="订单金额" width="120" align="right">
                            <template #default="{ row }">
                                {{ row.total_amount !== undefined ? `¥${row.total_amount.toFixed(2)}` : '-' }}
                            </template>
                        </ElTableColumn>
                        <ElTableColumn prop="create_time" label="创建时间" width="180" />
                        <ElTableColumn label="操作" width="200" fixed="right" align="center">
                            <template #default="{ row }">
                                <div class="flex-center gap-8px">
                                    <ElButton type="success" plain size="small" @click="handleOrderReview(row.id, 'approved')">
                                        批准
                                    </ElButton>
                                    <ElButton type="warning" plain size="small" @click="handleOrderReview(row.id, 'cancelled')">
                                        拒绝
                                    </ElButton>
                                </div>
                            </template>
                        </ElTableColumn>
                    </ElTable>
                </ElTabPane>

                <!-- Comment Approval Tab -->
                <ElTabPane label="评论审批" name="comment">
                    <ElTable v-loading="commentLoading" :data="commentData" border stripe height="500">
                        <ElTableColumn type="index" label="序号" width="64" align="center" />
                        <ElTableColumn prop="id" label="评论ID" width="100" align="center" />
                        <ElTableColumn prop="user_id" label="用户ID" width="100" align="center" />
                        <ElTableColumn prop="item_id" label="商品ID" width="100" align="center" />
                        <ElTableColumn prop="content" label="评论内容" min-width="300" show-overflow-tooltip />
                        <ElTableColumn label="评分" width="100" align="center">
                            <template #default="{ row }">
                                {{ row.rating || '-' }}
                            </template>
                        </ElTableColumn>
                        <ElTableColumn prop="create_time" label="创建时间" width="180" />
                        <ElTableColumn label="操作" width="200" fixed="right" align="center">
                            <template #default="{ row }">
                                <div class="flex-center gap-8px">
                                    <ElButton type="success" plain size="small" @click="handleCommentReview(row.id, true)">
                                        批准
                                    </ElButton>
                                    <ElButton type="warning" plain size="small" @click="handleCommentReview(row.id, false)">
                                        拒绝
                                    </ElButton>
                                </div>
                            </template>
                        </ElTableColumn>
                    </ElTable>
                </ElTabPane>
            </ElTabs>
        </ElCard>
    </div>
</template>

<style scoped lang="scss">
.flex-1-hidden {
    flex: 1;
    overflow: hidden;
}

.flex-center {
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
