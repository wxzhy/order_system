<script setup lang="ts">
import { $t } from '@/locales';

defineOptions({
    name: 'CommentSearch'
});

interface Props {
    model: Api.SystemManage.CommentSearchParams;
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
    <ElCard class="card-wrapper">
        <ElCollapse>
            <ElCollapseItem :title="$t('common.search')" name="comment-search">
                <ElForm :model="props.model" label-position="right" :label-width="80">
                    <ElRow :gutter="24">
                        <ElCol :lg="6" :md="8" :sm="12">
                            <ElFormItem label="审核状态" prop="state">
                                <ElSelect v-model="props.model.state" placeholder="请选择状态" clearable>
                                    <ElOption v-for="item in stateOptions" :key="item.value" :label="item.label"
                                        :value="item.value" />
                                </ElSelect>
                            </ElFormItem>
                        </ElCol>
                        <ElCol :lg="6" :md="8" :sm="12">
                            <ElFormItem label="用户名" prop="user_name">
                                <ElInput v-model="props.model.user_name" placeholder="请输入用户名" clearable />
                            </ElFormItem>
                        </ElCol>
                        <ElCol :lg="6" :md="8" :sm="12">
                            <ElFormItem label="商家名称" prop="store_name">
                                <ElInput v-model="props.model.store_name" placeholder="请输入商家名称" clearable />
                            </ElFormItem>
                        </ElCol>
                        <ElCol :lg="6" :md="8" :sm="12">
                            <ElFormItem label="评论内容" prop="content">
                                <ElInput v-model="props.model.content" placeholder="请输入评论内容" clearable />
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
