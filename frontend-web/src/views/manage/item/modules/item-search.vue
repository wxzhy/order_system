<script setup lang="ts">
import { $t } from '@/locales';

defineOptions({
    name: 'ItemSearch'
});

interface Props {
    model: Api.SystemManage.ItemSearchParams;
}

const props = defineProps<Props>();

interface Emits {
    (e: 'reset'): void;
    (e: 'search'): void;
}

const emit = defineEmits<Emits>();

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
    <ElCard>
        <ElForm :model="props.model" label-width="80px">
            <ElRow :gutter="16">
                <ElCol :span="6" :xs="24">
                    <ElFormItem label="商家ID">
                        <ElInputNumber v-model="props.model.store_id" placeholder="请输入商家ID" clearable class="w-full" />
                    </ElFormItem>
                </ElCol>
                <ElCol :span="6" :xs="24">
                    <ElFormItem label="库存状态">
                        <ElSelect v-model="props.model.in_stock" placeholder="请选择状态" clearable>
                            <ElOption v-for="item in stockOptions" :key="String(item.value)" :label="item.label"
                                :value="item.value" />
                        </ElSelect>
                    </ElFormItem>
                </ElCol>
                <ElCol :span="6" :xs="24">
                    <ElFormItem label="搜索">
                        <ElInput v-model="props.model.search" placeholder="餐点名称/描述" clearable />
                    </ElFormItem>
                </ElCol>
                <ElCol :span="6" :xs="24">
                    <ElFormItem label-width="0">
                        <div class="w-full flex gap-12px">
                            <ElButton type="primary" @click="search">
                                <template #icon>
                                    <icon-ic-round-search class="text-icon" />
                                </template>
                                {{ $t('common.search') }}
                            </ElButton>
                            <ElButton @click="reset">
                                <template #icon>
                                    <icon-ic-round-refresh class="text-icon" />
                                </template>
                                {{ $t('common.reset') }}
                            </ElButton>
                        </div>
                    </ElFormItem>
                </ElCol>
            </ElRow>
        </ElForm>
    </ElCard>
</template>
