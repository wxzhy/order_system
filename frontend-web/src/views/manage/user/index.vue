<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { ElButton, ElPopconfirm, ElTag } from 'element-plus';
import { batchDeleteUser, deleteUser, fetchGetUserList } from '@/service/api';
import { useTableOperate, useUIPaginatedTable } from '@/hooks/common/table';
import { $t } from '@/locales';
import UserOperateDrawer from './modules/user-operate-drawer.vue';
import UserSearch from './modules/user-search.vue';
import UserResetPassword from './modules/user-reset-password.vue';

defineOptions({ name: 'UserManage' });

const searchParams = reactive(getInitSearchParams());

function getInitSearchParams(): Api.SystemManage.UserSearchParams {
  return {
    skip: 0,
    limit: 30,
    user_type: undefined,
    search: undefined
  };
}

const { columns, columnChecks, data, getData, getDataByPage, loading, mobilePagination } = useUIPaginatedTable({
  paginationProps: {
    currentPage: 1,
    pageSize: 30
  },
  api: () => fetchGetUserList(searchParams),
  transform: response => {
    // Backend returns PageResponse format directly
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
    { prop: 'username', label: '用户名', minWidth: 120 },
    { prop: 'email', label: '邮箱', minWidth: 200 },
    { prop: 'phone', label: '手机号', width: 140 },
    {
      prop: 'user_type',
      label: '用户类型',
      width: 100,
      formatter: row => {
        const tagMap: Record<Api.SystemManage.UserType, UI.ThemeColor> = {
          admin: 'danger',
          vendor: 'warning',
          customer: 'primary'
        };

        const labelMap: Record<Api.SystemManage.UserType, string> = {
          admin: '管理员',
          vendor: '商家',
          customer: '顾客'
        };

        return <ElTag type={tagMap[row.user_type]}>{labelMap[row.user_type]}</ElTag>;
      }
    },
    { prop: 'create_time', label: '创建时间', width: 180 },
    {
      prop: 'operate',
      label: $t('common.operate'),
      align: 'center',
      width: 280,
      formatter: row => (
        <div class="flex-center gap-8px">
          <ElButton type="primary" plain size="small" onClick={() => edit(row.id)}>
            {$t('common.edit')}
          </ElButton>
          <ElButton type="warning" plain size="small" onClick={() => handleResetPassword(row.id, row.username)}>
            重置密码
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

const {
  drawerVisible,
  operateType,
  editingData,
  handleAdd,
  handleEdit,
  onBatchDeleted,
  onDeleted
  // closeDrawer
} = useTableOperate(data, 'id', getData);

// 存储选中的行数据
const selectedRows = ref<Api.SystemManage.User[]>([]);

// 重置密码相关
const resetPasswordVisible = ref(false);
const resetPasswordUserId = ref<number | null>(null);
const resetPasswordUsername = ref('');

function handleResetPassword(id: number, username: string) {
  resetPasswordUserId.value = id;
  resetPasswordUsername.value = username;
  resetPasswordVisible.value = true;
}

function onPasswordReset() {
  window.$message?.success('密码重置成功');
  getData();
}

async function handleBatchDelete() {
  if (selectedRows.value.length === 0) {
    window.$message?.warning('请选择要删除的用户');
    return;
  }

  try {
    const ids = selectedRows.value.map(row => row.id);
    const result = await batchDeleteUser(ids);
    window.$message?.success(result.message || `成功删除 ${result.success_count} 个用户`);
    selectedRows.value = [];
    onBatchDeleted();
  } catch (error: any) {
    window.$message?.error(error?.message || '批量删除失败');
  }
}

async function handleDelete(id: number) {
  try {
    await deleteUser(id);
    window.$message?.success('删除成功');
    onDeleted();
  } catch (error: any) {
    window.$message?.error(error?.message || '删除失败');
  }
}

function resetSearchParams() {
  Object.assign(searchParams, getInitSearchParams());
}

function edit(id: number) {
  handleEdit(id);
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <UserSearch v-model:model="searchParams" @reset="resetSearchParams" @search="getDataByPage" />
    <ElCard class="card-wrapper sm:flex-1-hidden" body-class="ht50">
      <template #header>
        <div class="flex items-center justify-between">
          <p>{{ $t('page.manage.user.title') }}</p>
          <TableHeaderOperation
            v-model:columns="columnChecks"
            :disabled-delete="selectedRows.length === 0"
            :loading="loading"
            @add="handleAdd"
            @delete="handleBatchDelete"
            @refresh="getData"
          />
        </div>
      </template>
      <div class="h-[calc(100%-50px)]">
        <ElTable
          v-loading="loading"
          height="100%"
          border
          class="sm:h-full"
          :data="data"
          row-key="id"
          @selection-change="selectedRows = $event"
        >
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
      <UserOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getDataByPage"
      />
      <UserResetPassword
        v-model:visible="resetPasswordVisible"
        :user-id="resetPasswordUserId"
        :username="resetPasswordUsername"
        @success="onPasswordReset"
      />
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
