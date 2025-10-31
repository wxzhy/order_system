<script setup lang="tsx">
import { reactive } from 'vue';
import { ElButton, ElPopconfirm, ElTag } from 'element-plus';
import { batchDeleteOrder, deleteOrder, fetchGetOrderList, updateOrder } from '@/service/api';
import { useTableOperate, useUIPaginatedTable } from '@/hooks/common/table';
import { $t } from '@/locales';
import OrderOperateDrawer from './modules/order-operate-drawer.vue';
import OrderSearch from './modules/order-search.vue';

defineOptions({ name: 'OrderManage' });

const searchParams = reactive(getInitSearchParams());

function getInitSearchParams(): Api.SystemManage.OrderSearchParams {
    return {
        skip: 0,
        limit: 30,
        state: undefined,
        search: undefined,
        store_id: undefined,
        user_id: undefined
    };
}

const { columns, columnChecks, data, getData, getDataByPage, loading, mobilePagination } = useUIPaginatedTable({
    paginationProps: {
        currentPage: 1,
        pageSize: 30
    },
    api: () => fetchGetOrderList(searchParams),
    transform: response => {
        const { records = [], total = 0, current = 1, size = 30 } = response || {};
        return {
            data: records,
            pageNum: current,
            pageSize: size,
            total
        };
    },
    onPaginationParamsChange: params => {
        const currentPage = params.currentPage ?? 1;
        const pageSize = params.pageSize ?? 30;
        searchParams.skip = (currentPage - 1) * pageSize;
        searchParams.limit = pageSize;
    },
    columns: () => [
        { prop: 'selection', type: 'selection', width: 48 },
        { prop: 'index', type: 'index', label: $t('common.index'), width: 64 },
        { prop: 'id', label: '订单ID', width: 80, align: 'center' },
        { prop: 'user_id', label: '用户ID', width: 100, align: 'center' },
        { prop: 'user_name', label: '用户名', width: 120, align: 'center' },
        { prop: 'store_id', label: '商家ID', width: 100, align: 'center' },
        { prop: 'store_name', label: '商家名称', width: 150, align: 'center' },
        {
            prop: 'total_amount',
            label: '订单金额',
            width: 120,
            align: 'center',
            formatter: (row: Api.SystemManage.Order) => {
                if (row.total_amount !== undefined) {
                    return `¥${row.total_amount.toFixed(2)}`;
                }
                return '-';
            }
        },
        {
            prop: 'state',
            label: '订单状态',
            width: 120,
            align: 'center',
            formatter: (row: Api.SystemManage.Order) => {
                const stateMap: Record<
                    string,
                    { label: string; type: 'success' | 'warning' | 'info' | 'danger' }
                > = {
                    pending: { label: '待审核', type: 'warning' },
                    approved: { label: '已同意', type: 'info' },
                    completed: { label: '已完成', type: 'success' },
                    cancelled: { label: '已取消', type: 'danger' }
                };
                const state = stateMap[row.state] || { label: row.state, type: 'info' };
                return <ElTag type={state.type}>{state.label}</ElTag>;
            }
        },
        { prop: 'create_time', label: '创建时间', width: 180 },
        { prop: 'review_time', label: '处理时间', width: 180 },
        {
            prop: 'actions',
            label: $t('common.action'),
            width: 320,
            fixed: 'right',
            align: 'center',
            formatter: (row: Api.SystemManage.Order) => (
                <div class="flex-center gap-8px">
                    <ElButton type="primary" plain size="small" onClick={() => handleEdit(row.id)}>
                        详情
                    </ElButton>
                    {row.state === 'pending' && (
                        <>
                            <ElButton type="success" plain size="small" onClick={() => handleApprove(row.id, 'approved')}>
                                批准
                            </ElButton>
                            <ElButton type="warning" plain size="small" onClick={() => handleApprove(row.id, 'cancelled')}>
                                拒绝
                            </ElButton>
                        </>
                    )}
                    <ElPopconfirm title={$t('common.confirmDelete')} onConfirm={() => handleDelete(row.id)}>
                        {{
                            reference: () => (
                                <ElButton type="danger" plain size="small">
                                    {$t('common.delete')}
                                </ElButton>
                            )
                        }}
                    </ElPopconfirm>
                </div>
            )
        }
    ]
});

const {
    drawerVisible,
    operateType,
    handleAdd,
    handleEdit,
    checkedRowKeys,
    onBatchDeleted,
    onDeleted,
    editingData
    // @ts-ignore
} = useTableOperate(data, 'id', getData);

async function handleBatchDelete() {
    if (checkedRowKeys.value.length === 0) {
        window.$message?.warning('请至少选择一条数据');
        return;
    }

    try {
        const result = await batchDeleteOrder(checkedRowKeys.value);
        if (result.success_count > 0) {
            window.$message?.success(`成功删除 ${result.success_count} 条数据`);
            onBatchDeleted();
        }
        if (result.failed_count > 0) {
            window.$message?.warning(`${result.failed_count} 条数据删除失败: ${result.message}`);
        }
    } catch (error: any) {
        window.$message?.error(error?.message || '批量删除失败');
    }
}

async function handleDelete(id: number) {
    try {
        await deleteOrder(id);
        window.$message?.success('删除成功');
        onDeleted();
    } catch (error: any) {
        window.$message?.error(error?.message || '删除失败');
    }
}

async function handleApprove(id: number, state: 'approved' | 'cancelled') {
    try {
        await updateOrder(id, { state });
        window.$message?.success(state === 'approved' ? '已批准' : '已拒绝');
        getData();
    } catch (error: any) {
        window.$message?.error(error?.message || '审批失败');
    }
}

function resetSearchParams() {
    Object.assign(searchParams, getInitSearchParams());
}
</script>

<template>
    <div class="h-full flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
        <OrderSearch v-model:model="searchParams" @reset="resetSearchParams" @search="getDataByPage" />
        <ElCard class="sm:flex-1-hidden card-wrapper" :body-style="{ flex: 1, overflow: 'hidden' }">
            <template #header>
                <div class="flex justify-between items-center">
                    <p class="text-16px font-600 m-0">订单列表</p>
                    <TableHeaderOperation v-model:columns="columnChecks" :disabled-delete="checkedRowKeys.length === 0"
                        :loading="loading" @add="handleAdd" @delete="handleBatchDelete" @refresh="getData">
                        <template #default><span></span></template>
                    </TableHeaderOperation>
                </div>
            </template>
            <ElTable v-loading="loading" :data="data" border stripe height="100%"
                @selection-change="(rows: Api.SystemManage.Order[]) => (checkedRowKeys = rows.map(row => row.id))">
                <template v-for="column in columns" :key="column.prop">
                    <ElTableColumn v-if="!column.hidden" v-bind="column" />
                </template>
            </ElTable>
            <template #footer>
                <ElPagination v-model:current-page="mobilePagination.currentPage"
                    v-model:page-size="mobilePagination.pageSize" :total="mobilePagination.total"
                    :page-sizes="[30, 50, 100]" :background="true" layout="total, prev, pager, next, sizes"
                    @current-change="getDataByPage" @size-change="getDataByPage" />
            </template>
        </ElCard>
        <OrderOperateDrawer v-model:visible="drawerVisible" :operate-type="operateType" :row-data="editingData"
            @submitted="getDataByPage" />
    </div>
</template>

<style scoped lang="scss">
.card-wrapper {
    display: flex;
    flex-direction: column;
}
</style>
