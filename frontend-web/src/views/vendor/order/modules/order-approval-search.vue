<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/locales';

interface Props {
  model: Api.SystemManage.OrderSearchParams;
}

defineOptions({ name: 'OrderApprovalSearch' });

const props = defineProps<Props>();

interface Emits {
  (e: 'reset'): void;
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const model = computed({
  get() {
    return props.model;
  },
  set(value) {
    Object.assign(props.model, value);
  }
});

function reset() {
  emit('reset');
}

function search() {
  emit('search');
}

const stateOptions = [
  { label: '全部', value: undefined },
  { label: '待审核', value: 'pending' },
  { label: '已同意', value: 'approved' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
];
</script>

<template>
  <ElCard class="card-wrapper">
    <ElCollapse>
      <ElCollapseItem :title="$t('common.search')" name="order-approval-search">
        <ElForm :model="model" label-position="right" :label-width="80">
          <ElRow :gutter="24">
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="订单状态" prop="state">
                <ElSelect v-model="model.state" placeholder="请选择状态" clearable>
                  <ElOption v-for="item in stateOptions" :key="item.value || 'all'" :label="item.label"
                    :value="item.value" />
                </ElSelect>
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="用户名" prop="user_name">
                <ElInput v-model="model.user_name" placeholder="请输入用户名" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="12" :md="8" :sm="24">
              <ElSpace class="w-full justify-end" alignment="end">
                <ElButton @click="reset">
                  <template #icon>
                    <icon-ic-round-refresh class="text-icon" />
                  </template>
                  {{ $t('common.reset') }}
                </ElButton>
                <ElButton type="primary" @click="search">
                  <template #icon>
                    <icon-ic-round-search class="text-icon" />
                  </template>
                  {{ $t('common.search') }}
                </ElButton>
              </ElSpace>
            </ElCol>
          </ElRow>
        </ElForm>
      </ElCollapseItem>
    </ElCollapse>
  </ElCard>
</template>

<style scoped></style>