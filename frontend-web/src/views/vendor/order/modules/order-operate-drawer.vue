<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { getOrder, updateOrder } from '@/service/api';
import { useForm, useFormRules } from '@/hooks/common/form';

defineOptions({
    name: 'VendorOrderOperateDrawer'
});

interface Props {
    operateType: 'add' | 'edit';
    rowData?: Api.SystemManage.Order | null;
}

const props = defineProps<Props>();

interface Emits {
    (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
    default: false
});

const title = computed(() => (props.operateType === 'add' ? '新增订单' : '订单详情'));

// 订单详情数据
const orderDetail = ref<Api.SystemManage.Order | null>(null);
const loadingDetail = ref(false);
const submitting = ref(false);

async function handleInitModel() {
    orderDetail.value = null;

    if (props.operateType === 'edit' && props.rowData) {
        // 获取完整订单信息
        try {
            loadingDetail.value = true;
            const orderData = await getOrder(props.rowData.id);
            orderDetail.value = orderData;
        } catch (error) {
            // 如果获取失败，使用传入的基本数据
            console.error('获取订单详情失败:', error);
        } finally {
            loadingDetail.value = false;
        }
    }
}

function closeDrawer() {
    visible.value = false;
}

async function handleApprove() {
    if (!props.rowData) return;

    try {
        submitting.value = true;
        await updateOrder(props.rowData.id, {
            state: 'approved'
        });
        window.$message?.success('订单已审批通过');
        closeDrawer();
        emit('submitted');
    } catch (error: any) {
        window.$message?.error(error?.message || '审批失败');
    } finally {
        submitting.value = false;
    }
}

async function handleReject() {
    if (!props.rowData) return;

    try {
        submitting.value = true;
        await updateOrder(props.rowData.id, {
            state: 'cancelled'
        });
        window.$message?.success('订单已拒绝');
        closeDrawer();
        emit('submitted');
    } catch (error: any) {
        window.$message?.error(error?.message || '拒绝失败');
    } finally {
        submitting.value = false;
    }
}

watch(visible, () => {
    if (visible.value) {
        handleInitModel();
    }
});
</script>

<template>
    <ElDrawer v-model="visible" :title="title" :size="600">
        <div v-loading="loadingDetail">
            <!-- 订单基本信息 -->
            <ElDivider content-position="left">订单信息</ElDivider>

            <ElRow :gutter="16">
                <ElCol :span="12">
                    <ElFormItem label="订单ID">
                        <ElInput :value="props.rowData?.id" disabled />
                    </ElFormItem>
                </ElCol>
                <ElCol :span="12">
                    <ElFormItem label="订单状态">
                        <ElTag v-if="props.rowData?.state === 'pending'" type="warning">待审核</ElTag>
                        <ElTag v-else-if="props.rowData?.state === 'approved'" type="info">已同意</ElTag>
                        <ElTag v-else-if="props.rowData?.state === 'completed'" type="success">已完成</ElTag>
                        <ElTag v-else-if="props.rowData?.state === 'cancelled'" type="danger">已取消</ElTag>
                        <ElTag v-else>{{ props.rowData?.state }}</ElTag>
                    </ElFormItem>
                </ElCol>
            </ElRow>

            <ElRow :gutter="16">
                <ElCol :span="12">
                    <ElFormItem label="用户名">
                        <ElInput :value="props.rowData?.user_name || '-'" disabled />
                    </ElFormItem>
                </ElCol>
                <ElCol :span="12">
                    <ElFormItem label="商家名称">
                        <ElInput :value="props.rowData?.store_name || '-'" disabled />
                    </ElFormItem>
                </ElCol>
            </ElRow>

            <ElRow :gutter="16">
                <ElCol :span="12">
                    <ElFormItem label="创建时间">
                        <ElInput :value="props.rowData?.create_time" disabled />
                    </ElFormItem>
                </ElCol>
                <ElCol :span="12">
                    <ElFormItem label="处理时间">
                        <ElInput :value="props.rowData?.review_time || '未处理'" disabled />
                    </ElFormItem>
                </ElCol>
            </ElRow>

            <ElFormItem label="订单总额">
                <ElInput :value="orderDetail?.total_amount ? `¥${orderDetail.total_amount.toFixed(2)}` : '-'"
                    disabled />
            </ElFormItem>

            <!-- 订单项列表 -->
            <ElDivider content-position="left">订单项目</ElDivider>

            <ElCard shadow="never">
                <ElTable v-if="orderDetail?.items?.length" :data="orderDetail.items" border>
                    <ElTableColumn prop="item_id" label="菜品ID" width="80" align="center" />
                    <ElTableColumn prop="item_name" label="菜品名称" min-width="150">
                        <template #default="{ row }">
                            {{ row.item_name || '-' }}
                        </template>
                    </ElTableColumn>
                    <ElTableColumn prop="quantity" label="数量" width="80" align="center" />
                    <ElTableColumn prop="item_price" label="单价" width="100" align="right">
                        <template #default="{ row }">¥{{ row.item_price.toFixed(2) }}</template>
                    </ElTableColumn>
                    <ElTableColumn label="小计" width="100" align="right">
                        <template #default="{ row }">¥{{ (row.item_price * row.quantity).toFixed(2) }}</template>
                    </ElTableColumn>
                </ElTable>
                <ElEmpty v-else description="暂无订单项" />
            </ElCard>
        </div>

        <template #footer>
            <div class="flex justify-end gap-12px">
                <ElButton @click="closeDrawer">关闭</ElButton>
                <template v-if="props.rowData?.state === 'pending'">
                    <ElButton type="danger" :loading="submitting" @click="handleReject">拒绝订单</ElButton>
                    <ElButton type="primary" :loading="submitting" @click="handleApprove">审批通过</ElButton>
                </template>
            </div>
        </template>
    </ElDrawer>
</template>