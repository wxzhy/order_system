<script setup lang="tsx">
import { reactive } from 'vue';
import { ElButton, ElCard, ElTable, ElTableColumn } from 'element-plus';
import { fetchGetCommentList, reviewComment } from '@/service/api';
import { useUIPaginatedTable } from '@/hooks/common/table';
import { $t } from '@/locales';
import CommentApprovalSearch from './modules/comment-approval-search.vue';

defineOptions({ name: 'CommentApprovalManage' });

const searchParams = reactive(getInitSearchParams());

function getInitSearchParams() {
  return {
    skip: 0,
    limit: 30,
    state: 'pending' as const,
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
    { prop: 'index', type: 'index', label: $t('common.index'), width: 64 },
    { prop: 'user_name', label: '用户名', width: 120 },
    { prop: 'store_name', label: '商家名称', width: 150 },
    { prop: 'content', label: '评论内容', minWidth: 300, showOverflowTooltip: true },
    {
      prop: 'rating',
      label: '评分',
      width: 100,
      align: 'center',
      formatter: (row: Api.SystemManage.Comment) => row.rating || '-'
    },
    { prop: 'create_time', label: '创建时间', width: 180 },
    {
      prop: 'actions',
      label: $t('common.action'),
      width: 200,
      fixed: 'right',
      align: 'center',
      formatter: (row: Api.SystemManage.Comment) => (
        <div class="flex-center gap-8px">
          <ElButton type="success" plain size="small" onClick={() => handleReview(row.id, true)}>
            批准
          </ElButton>
          <ElButton type="warning" plain size="small" onClick={() => handleReview(row.id, false)}>
            拒绝
          </ElButton>
        </div>
      )
    }
  ]
});

async function handleReview(id: number, approved: boolean) {
  try {
    const state = approved ? 'approved' : 'rejected';
    await reviewComment(id, state);
    window.$message?.success(approved ? '已批准' : '已拒绝');
    // 强制刷新数据
    searchParams.skip = 0;
    await getData();
  } catch (error: any) {
    window.$message?.error(error?.message || '审批失败');
  }
}

function resetSearchParams() {
  Object.assign(searchParams, getInitSearchParams());
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <CommentApprovalSearch v-model:model="searchParams" @reset="resetSearchParams" @search="getDataByPage" />
    <ElCard class="card-wrapper sm:flex-1-hidden" body-class="ht50">
      <template #header>
        <div class="flex items-center justify-between">
          <p>评论审批列表</p>
          <TableHeaderOperation v-model:columns="columnChecks" :loading="loading" @refresh="getData">
            <template #default><span></span></template>
          </TableHeaderOperation>
        </div>
      </template>
      <div class="h-[calc(100%-50px)]">
        <ElTable v-loading="loading" height="100%" border class="sm:h-full" :data="data" row-key="id">
          <ElTableColumn v-for="col in columns" :key="col.prop" v-bind="col" />
        </ElTable>
      </div>
      <div class="mt-20px flex justify-end">
        <ElPagination v-if="mobilePagination.total" layout="total,prev,pager,next,sizes" v-bind="mobilePagination"
          @current-change="mobilePagination['current-change']" @size-change="mobilePagination['size-change']" />
      </div>
    </ElCard>
  </div>
</template>

<style lang="scss" scoped>
:deep(.el-card) {
  .ht50 {
    height: calc(100% - 50px);
  }
}
</style>
