<script setup lang="ts">
import { $t } from '@/locales';

defineOptions({
    name: 'StoreSearch'
});

interface Props {
    model: Api.SystemManage.StoreSearchParams;
}

const props = defineProps<Props>();

interface Emits {
    (e: 'reset'): void;
    (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const stateOptions = [
    { label: '全部', value: '' },
    { label: '待审核', value: 'pending' },
    { label: '已通过', value: 'approved' },
    { label: '已拒绝', value: 'rejected' }
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
                    <ElFormItem label="状态">
                        <ElSelect v-model="props.model.state" placeholder="请选择状态" clearable>
                            <ElOption v-for="item in stateOptions" :key="item.value" :label="item.label"
                                :value="item.value" />
                        </ElSelect>
                    </ElFormItem>
                </ElCol>
                <ElCol :span="6" :xs="24">
                    <ElFormItem label="搜索">
                        <ElInput v-model="props.model.search" placeholder="商家名称/地址/电话" clearable />
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
