<script setup lang="tsx">
import { computed, reactive, ref, watch } from 'vue';
import { ElButton, ElCard, ElResult, ElSkeleton, ElTable, ElTableColumn } from 'element-plus';
import { useRoute } from 'vue-router';
import { fetchGetOrderList, updateOrder } from '@/service/api';
import { useUIPaginatedTable } from '@/hooks/common/table';
import { useTabStore } from '@/store/modules/tab';
import { useRouterPush } from '@/hooks/common/router';
import type { RouteKey } from '@elegant-router/types';
import { useVendorStoreStatus } from '@/hooks/business/vendor-store';
import { $t } from '@/locales';
import OrderApprovalSearch from './modules/order-approval-search.vue';

defineOptions({ name: 'OrderApprovalManage' });

const searchParams = reactive(getInitSearchParams());

function getInitSearchParams() {
  return {
    skip: 0,
    limit: 30,
    state: 'pending' as const,
    user_name: undefined,
    store_id: undefined,
    user_id: undefined
  };
}

const { store, state, exists, canManage, loading: statusLoading, errorMessage, forbidden, loadStatus } = useVendorStoreStatus();
const tabStore = useTabStore();
const { routerPushByKey } = useRouterPush();
const route = useRoute();
const handledForbidden = ref(false);
const storeId = computed(() => store.value?.id ?? null);

function createEmptyList(): Api.SystemManage.OrderList {
  return {
    records: [],
    total: 0,
    current: 1,
    size: searchParams.limit ?? 30
  };
}

const { columns, columnChecks, data, getData, getDataByPage, loading, mobilePagination } = useUIPaginatedTable<
  Api.SystemManage.OrderList,
  Api.SystemManage.Order
>({
  paginationProps: {
    currentPage: 1,
    pageSize: 30
  },
  api: async () => {
    if (!storeId.value || !canManage.value) {
      return createEmptyList();
    }

    searchParams.store_id = storeId.value;
    try {
      return await fetchGetOrderList(searchParams);
    } catch (error: any) {
      if (error?.response?.status === 403) {
        return createEmptyList();
      }
      throw error;
    }
  },
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
    { prop: 'user_name', label: '用户', width: 120 },
    {
      prop: 'total_amount',
      label: '订单金额',
      width: 120,
      align: 'center',
      formatter: (row: Api.SystemManage.Order) => {
        if (row.total_amount !== undefined) {
          return `￥${row.total_amount.toFixed(2)}`;
        }
        return '-';
      }
    },
    { prop: 'create_time', label: '创建时间', width: 180 },
    {
      prop: 'actions',
      label: $t('common.action'),
      width: 200,
      fixed: 'right',
      align: 'center',
      formatter: (row: Api.SystemManage.Order) => (
        <div class="flex-center gap-8px">
          <ElButton type="success" plain size="small" onClick={() => handleApprove(row.id, 'approved')}>
            审批通过
          </ElButton>
          <ElButton type="warning" plain size="small" onClick={() => handleApprove(row.id, 'cancelled')}>
            拒绝订单
          </ElButton>
        </div>
      )
    }
  ]
});

watch(
  () => forbidden.value,
  async val => {
    if (val && !handledForbidden.value) {
      handledForbidden.value = true;
      const message = errorMessage.value || '当前账号无权使用商家中心，将返回首页';
      window.$message?.error(message);
      const currentRouteName = route.name as RouteKey | undefined;
      await routerPushByKey('root');
      if (currentRouteName && currentRouteName !== 'root') {
        await tabStore.removeTabByRouteName(currentRouteName);
      }
    }
  }
);

watch(
  () => (canManage.value && storeId.value ? storeId.value : null),
  value => {
    if (value) {
      searchParams.store_id = value;
      getDataByPage();
    }
  },
  { immediate: true }
);

async function handleApprove(id: number, state: 'approved' | 'cancelled') {
  try {
    await updateOrder(id, { state });
    window.$message?.success(state === 'approved' ? '已批准订单' : '已拒绝订单');
    searchParams.skip = 0;
    await getData();
  } catch (error: any) {
    window.$message?.error(error?.message || '操作失败');
  }
}

function resetSearchParams() {
  Object.assign(searchParams, getInitSearchParams());
  if (storeId.value) {
    searchParams.store_id = storeId.value;
  }
}

const blockMessage = computed(() => {
  if (!exists.value) {
    return '您还未提交商家信息，请先完成商家注册。';
  }
  switch (state.value) {
    case 'pending':
      return '商家信息正在审核中，审核通过后即可审批订单。';
    case 'rejected':
      return '商家信息审核未通过，请在商家注册页面修改后重新提交。';
    default:
      return errorMessage.value || '暂时无法加载商家信息，请稍后再试。';
  }
});
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <OrderApprovalSearch v-model:model="searchParams" @reset="resetSearchParams" @search="getDataByPage" />

    <ElSkeleton v-if="statusLoading" animated :rows="6" />

    <ElResult
      v-else-if="!canManage"
      icon="info"
      title="暂无法审批订单"
      :sub-title="blockMessage"
    >
      <template #extra>
        <RouterLink to="/vendor/register">
          <ElButton type="primary">前往商家注册</ElButton>
        </RouterLink>
        <ElButton class="ml-12px" @click="loadStatus">刷新状态</ElButton>
      </template>
    </ElResult>

    <ElCard v-else class="card-wrapper sm:flex-1-hidden" body-class="ht50">
      <template #header>
        <div class="flex items-center justify-between">
          <p>待审批订单</p>
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
        <ElPagination
          v-if="mobilePagination.total"
          layout="total,prev,pager,next,sizes"
          v-bind="mobilePagination"
          @current-change="mobilePagination['current-change']"
          @size-change="mobilePagination['size-change']"
        />
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