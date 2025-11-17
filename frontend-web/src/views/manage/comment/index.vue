<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { ElButton, ElPopconfirm, ElTag } from 'element-plus';
import { batchDeleteComment, deleteComment, fetchGetCommentList, reviewComment } from '@/service/api';
import { useTableOperate, useUIPaginatedTable } from '@/hooks/common/table';
import { $t } from '@/locales';
import CommentOperateDrawer from './modules/comment-operate-drawer.vue';
import CommentSearch from './modules/comment-search.vue';

defineOptions({ name: 'CommentManage' });

const searchParams = reactive(getInitSearchParams());

function getInitSearchParams(): Api.SystemManage.CommentSearchParams {
    return {
        skip: 0,
        limit: 30,
        state: undefined,
        user_name: undefined,
        store_name: undefined,
        content: undefined,
        store_id: undefined,
        user_id: undefined
    };
}

const { columns, columnChecks, data, getData, getDataByPage, loading, mobilePagination } = useUIPaginatedTable({
    paginationProps: {
        currentPage: 1,
        pageSize: 30
    },
    api: () => fetchGetCommentList(searchParams),
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
        { prop: 'user_name', label: '用户名', width: 120 },
        { prop: 'store_name', label: '商家名称', width: 150 },
        { prop: 'content', label: '评论内容', minWidth: 250 },
        {
            prop: 'state',
            label: '审核状态',
            width: 120,
            align: 'center',
            formatter: (row: Api.SystemManage.Comment) => {
                const stateMap: Record<string, { label: string; type: 'success' | 'warning' | 'danger' }> = {
                    pending: { label: '待审核', type: 'warning' },
                    approved: { label: '已通过', type: 'success' },
                    rejected: { label: '已拒绝', type: 'danger' }
                };
                const state = stateMap[row.state] || { label: row.state, type: 'warning' };
                return <ElTag type={state.type}>{state.label}</ElTag>;
            }
        },
        { prop: 'publish_time', label: '发布时间', width: 180 },
        { prop: 'review_time', label: '审核时间', width: 180 },
        {
            prop: 'actions',
            label: $t('common.action'),
            width: 280,
            fixed: 'right',
            align: 'center',
            formatter: (row: Api.SystemManage.Comment) => (
                <div class="flex-center gap-8px">
                    {row.state === 'pending' && (
                        <>
                            <ElButton type="success" plain size="small" onClick={() => handleReview(row.id, true)}>
                                通过
                            </ElButton>
                            <ElButton type="warning" plain size="small" onClick={() => handleReview(row.id, false)}>
                                拒绝
                            </ElButton>
                        </>
                    )}
                    <ElButton type="primary" plain size="small" onClick={() => handleEdit(row.id)}>
                        {$t('common.edit')}
                    </ElButton>
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

const { drawerVisible, operateType, handleEdit, onBatchDeleted, onDeleted, editingData } = useTableOperate(
    data,
    'id',
    getData
);

const checkedRowKeys = ref<number[]>([]);

async function handleBatchDelete() {
    if (checkedRowKeys.value.length === 0) {
        window.$message?.warning('请至少选择一条数据');
        return;
    }

    try {
        const result = await batchDeleteComment(checkedRowKeys.value);
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
        await deleteComment(id);
        window.$message?.success('删除成功');
        onDeleted();
    } catch (error: any) {
        window.$message?.error(error?.message || '删除失败');
    }
}

async function handleReview(id: number, approved: boolean) {
    try {
        const state = approved ? 'approved' : 'rejected';
        await reviewComment(id, state);
        window.$message?.success(approved ? '审核通过' : '已拒绝');
        getData();
    } catch (error: any) {
        window.$message?.error(error?.message || '审核失败');
    }
}

function resetSearchParams() {
    Object.assign(searchParams, getInitSearchParams());
}
</script>

<template>
    <div class="h-full flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
        <CommentSearch v-model:model="searchParams" @reset="resetSearchParams" @search="getDataByPage" />
        <ElCard class="card-wrapper sm:flex-1-hidden" :body-style="{ flex: 1, overflow: 'hidden' }">
            <template #header>
                <div class="flex items-center justify-between">
                    <p class="m-0 text-16px font-600">评论列表</p>
                    <TableHeaderOperation v-model:columns="columnChecks" :disabled-delete="checkedRowKeys.length === 0"
                        :loading="loading" :disabled-add="true" @delete="handleBatchDelete" @refresh="getData" />
                </div>
            </template>
            <ElTable v-loading="loading" :data="data" border stripe height="100%"
                @selection-change="(rows: any[]) => (checkedRowKeys = rows.map(row => row.id))">
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
        <CommentOperateDrawer v-model:visible="drawerVisible" :operate-type="operateType" :row-data="editingData"
            @submitted="getDataByPage" />
    </div>
</template>

<style scoped lang="scss">
.card-wrapper {
    display: flex;
    flex-direction: column;
}
</style>
