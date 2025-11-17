<script setup lang="ts">
import { $t } from '@/locales';

defineOptions({
  name: 'ItemSearch'
});

interface Emits {
  (e: 'reset'): void;
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.SystemManage.ItemSearchParams>({ required: true });

const stockOptions = [
  { label: '全部', value: undefined },
  { label: '有货', value: true },
  { label: '缺货', value: false }
];

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
      <ElCollapseItem :title="$t('common.search')" name="item-search">
        <ElForm :model="model" label-position="right" :label-width="80">
          <ElRow :gutter="24">
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="餐点名称" prop="item_name">
                <ElInput v-model="model.item_name" placeholder="请输入餐点名称" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="描述" prop="description">
                <ElInput v-model="model.description" placeholder="请输入描述" clearable />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="库存状态" prop="in_stock">
                <ElSelect v-model="model.in_stock" placeholder="请选择状态" clearable>
                  <ElOption v-for="item in stockOptions" :key="String(item.value)" :label="item.label"
                    :value="item.value" />
                </ElSelect>
              </ElFormItem>
            </ElCol>
            <ElCol :lg="24" :md="24" :sm="24">
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
