<script setup lang="ts">
import { useForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({ name: 'UserSearch' });

interface Emits {
  (e: 'reset'): void;
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const { formRef, restoreValidation } = useForm();

const model = defineModel<Api.SystemManage.UserSearchParams>('model', { required: true });

const userTypeOptions = [
  { label: '管理员', value: 'admin' },
  { label: '商家', value: 'vendor' },
  { label: '顾客', value: 'customer' }
];

async function reset() {
  await restoreValidation();
  emit('reset');
}

function search() {
  emit('search');
}
</script>

<template>
  <ElCard class="card-wrapper">
    <ElCollapse>
      <ElCollapseItem :title="$t('common.search')" name="user-search">
        <ElForm ref="formRef" :model="model" label-position="right" :label-width="80">
          <ElRow :gutter="24">
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="搜索" prop="search">
                <ElInput v-model="model.search" placeholder="用户名/邮箱/手机号" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="用户类型" prop="user_type">
                <ElSelect v-model="model.user_type" clearable placeholder="请选择用户类型">
                  <ElOption
                    v-for="item in userTypeOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  ></ElOption>
                </ElSelect>
              </ElFormItem>
            </ElCol>
            <ElCol :lg="12" :md="24" :sm="24">
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
