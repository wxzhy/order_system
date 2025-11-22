<script setup lang="tsx">
import { computed, reactive, ref, watch, watchEffect } from 'vue';
import { useRouter } from 'vue-router';
import { ElButton, ElImage, ElPopconfirm, ElResult, ElSkeleton, ElTag } from 'element-plus';
import { batchDeleteItem, deleteItem, fetchGetItemList } from '@/service/api';
import { useTableOperate, useUIPaginatedTable } from '@/hooks/common/table';
import { useVendorStoreStatus } from '@/hooks/business/vendor-store';
import { $t } from '@/locales';
import ItemOperateDrawer from './modules/item-operate-drawer.vue';
import ItemSearch from './modules/item-search.vue';

defineOptions({ name: 'ItemManage' });

const searchParams = reactive(getInitSearchParams());

function getInitSearchParams(): Api.SystemManage.ItemSearchParams {
  return {
    skip: 0,
    limit: 30,
    store_id: undefined,
    item_name: undefined,
    description: undefined,
    min_price: undefined,
    max_price: undefined,
    in_stock: undefined
  };
}

const { store, state, exists, canManage, loading: statusLoading, errorMessage, loadStatus } = useVendorStoreStatus();
const storeId = computed(() => store.value?.id ?? null);
const router = useRouter();
const redirectHandled = ref(false);

function createEmptyList(): Api.SystemManage.ItemList {
  return {
    records: [],
    total: 0,
    current: 1,
    size: searchParams.limit ?? 30
  };
}

const {
  columns,
  columnChecks,
  data,
  getData,
  getDataByPage,
  loading,
  mobilePagination
} = useUIPaginatedTable<Api.SystemManage.ItemList, Api.SystemManage.Item>({
  paginationProps: {
    currentPage: 1,
    pageSize: 30
  },
  columns: () => [],
  api: async () => {
    if (!storeId.value || !canManage.value) {
      return createEmptyList();
    }

    searchParams.store_id = storeId.value;
    try {
      return await fetchGetItemList(searchParams);
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
  immediatelyColumns: false
});

const { drawerVisible, operateType, handleAdd, handleEdit, onBatchDeleted, onDeleted, editingData } = useTableOperate(
  data,
  'id',
  getData
);

columns.value = [
  { prop: 'selection', type: 'selection', width: 48 },
  { prop: 'index', type: 'index', label: $t('common.index'), width: 64 },
  {
    prop: 'imageURL',
    label: '图片',
    width: 100,
    align: 'center',
    formatter: (row: Api.SystemManage.Item) => {
      if (row.imageURL) {
        return (
          <ElImage
            src={row.imageURL}
            preview-src-list={[row.imageURL]}
            fit="cover"
            style="width: 60px; height: 60px; border-radius: 4px;"
          />
        );
      }
      return <span class="text-#ccc">暂无图片</span>;
    }
  },
  { prop: 'itemName', label: '餐点名称', minWidth: 150 },
  { prop: 'description', label: '描述', minWidth: 200 },
  {
    prop: 'price',
    label: '价格',
    width: 100,
    align: 'center',
    formatter: (row: Api.SystemManage.Item) => `￥${row.price.toFixed(2)}`
  },
  {
    prop: 'quantity',
    label: '库存',
    width: 100,
    align: 'center',
    formatter: (row: Api.SystemManage.Item) => {
      if (row.quantity > 0) {
        return <ElTag type="success">{row.quantity}</ElTag>;
      }
      return <ElTag type="danger">缺货</ElTag>;
    }
  },
  {
    prop: 'actions',
    label: $t('common.action'),
    width: 200,
    fixed: 'right',
    align: 'center',
    formatter: (row: Api.SystemManage.Item) => (
      <div class="flex-center gap-8px">
        <ElButton type="primary" plain size="small" onClick={() => handleEdit(row)}>
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
];

const checkedRowKeys = ref<number[]>([]);


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

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    window.$message?.warning('请先选择至少一条记录');
    return;
  }

  try {
    const result = await batchDeleteItem(checkedRowKeys.value);
    if (result.success_count > 0) {
      window.$message?.success(`成功删除 ${result.success_count} 条记录`);
      onBatchDeleted();
    }
    if (result.failed_count > 0) {
      window.$message?.warning(`${result.failed_count} 条记录删除失败: ${result.message}`);
    }
  } catch (error: any) {
    window.$message?.error(error?.message || '批量删除失败');
  }
}

async function handleDelete(id: number) {
  try {
    await deleteItem(id);
    onDeleted();
  } catch (error: any) {
    window.$message?.error(error?.message || '删除失败');
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
      return '商家信息正在审核中，审核通过后即可管理餐点。';
    case 'rejected':
      return '商家信息审核未通过，请在商家注册页面修改后重新提交。';
    default:
      return errorMessage.value || '暂时无法加载商家信息，请稍后再试。';
  }
});

watchEffect(() => {
  if (statusLoading.value || canManage.value || redirectHandled.value) {
    return;
  }

  redirectHandled.value = true;
  const message = blockMessage.value || '当前账号无权使用商家功能，请前往商家注册';
  window.$message?.error(message);

  const redirectQuery =
    router.currentRoute.value.fullPath && router.currentRoute.value.fullPath !== '/vendor/register'
      ? { redirect: router.currentRoute.value.fullPath }
      : undefined;

  router.replace({
    name: 'vendor_register',
    query: redirectQuery
  });
});
</script>

<template>
  <div class="h-full flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <ElSkeleton v-if="statusLoading" animated :rows="6" />

    <template v-else>
      <ElResult v-if="!canManage" icon="info" title="当前无法管理餐点" :sub-title="blockMessage">
        <template #extra>
          <RouterLink to="/vendor/register">
            <ElButton type="primary">前往商家注册</ElButton>
          </RouterLink>
          <ElButton class="ml-12px" @click="loadStatus">刷新状态</ElButton>
        </template>
      </ElResult>

      <template v-else>
        <ItemSearch v-model="searchParams" @reset="resetSearchParams" @search="getDataByPage" />

        <ElCard class="card-wrapper sm:flex-1-hidden" :body-style="{ flex: 1, overflow: 'hidden' }">
          <template #header>
            <div class="flex items-center justify-between">
              <p class="m-0 text-16px font-600">餐点列表</p>
              <TableHeaderOperation v-model:columns="columnChecks" :disabled-delete="checkedRowKeys.length === 0"
                :loading="loading" @add="handleAdd" @delete="handleBatchDelete" @refresh="getData" />
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
              v-model:page-size="mobilePagination.pageSize" :total="mobilePagination.total" :page-sizes="[30, 50, 100]"
              :background="true" layout="total, prev, pager, next, sizes" @current-change="getDataByPage"
              @size-change="getDataByPage" />
          </template>
        </ElCard>

        <ItemOperateDrawer v-model:visible="drawerVisible" :operate-type="operateType" :row-data="editingData"
          :store-id="storeId ?? undefined" @submitted="getDataByPage" />
      </template>
    </template>
  </div>
</template>

<style scoped lang="scss">
.card-wrapper {
  display: flex;
  flex-direction: column;
}
</style>
