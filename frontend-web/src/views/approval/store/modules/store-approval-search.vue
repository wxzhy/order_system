<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/locales';

interface Props {
  model: Api.SystemManage.StoreSearchParams;
}

defineOptions({ name: 'StoreApprovalSearch' });

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
</script>

<template>
  <ElCard class="card-wrapper">
    <ElCollapse>
      <ElCollapseItem :title="$t('common.search')" name="store-approval-search">
        <ElForm :model="model" label-position="right" :label-width="80">
          <ElRow :gutter="24">
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="商家名称" prop="name">
                <ElInput v-model="model.name" placeholder="请输入商家名称" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="所属用户" prop="owner_name">
                <ElInput v-model="model.owner_name" placeholder="请输入用户名" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="地址" prop="address">
                <ElInput v-model="model.address" placeholder="请输入地址" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="电话" prop="phone">
                <ElInput v-model="model.phone" placeholder="请输入电话" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="24" :md="24" :sm="12">
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
