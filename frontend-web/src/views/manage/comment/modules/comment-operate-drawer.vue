<script setup lang="ts">
import { computed, reactive, watch } from 'vue';
import { getComment, updateComment } from '@/service/api';
import { useFormRules } from '@/hooks/common/form';

defineOptions({
    name: 'CommentOperateDrawer'
});

interface Props {
    operateType: 'add' | 'edit';
    rowData?: Api.SystemManage.Comment | null;
}

const props = defineProps<Props>();

interface Emits {
    (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
    default: false
});

const title = computed(() => (props.operateType === 'add' ? '新增评论' : '编辑评论'));

type Model = {
    content: string;
    state: Api.SystemManage.CommentState;
};

const model: Model = reactive(createDefaultModel());

function createDefaultModel(): Model {
    return {
        content: '',
        state: 'pending'
    };
}

const { formRef, validate, restoreValidation } = useFormRules();
const { defaultRequiredRule } = useFormRules();

const stateOptions = [
    { label: '待审核', value: 'pending' },
    { label: '已通过', value: 'approved' },
    { label: '已拒绝', value: 'rejected' }
];

const rules = computed(() => {
    const baseRules: Record<string, App.Global.FormRule[]> = {
        content: [defaultRequiredRule],
        state: [defaultRequiredRule]
    };

    return baseRules;
});

async function handleInitModel() {
    Object.assign(model, createDefaultModel());

    if (props.operateType === 'edit' && props.rowData) {
        try {
            const commentData = await getComment(props.rowData.id);
            Object.assign(model, {
                content: commentData.content,
                state: commentData.state
            });
        } catch (error) {
            Object.assign(model, {
                content: props.rowData.content,
                state: props.rowData.state
            });
        }
    }
}

function closeDrawer() {
    visible.value = false;
}

async function handleSubmit() {
    await validate();

    try {
        if (props.operateType === 'edit' && props.rowData) {
            await updateComment(props.rowData.id, {
                content: model.content,
                state: model.state
            });
            window.$message?.success('更新成功');
        } else {
            window.$message?.warning('评论创建功能暂未开放');
            closeDrawer();
            return;
        }

        closeDrawer();
        emit('submitted');
    } catch (error: any) {
        window.$message?.error(error?.message || '操作失败');
    }
}

watch(visible, () => {
    if (visible.value) {
        handleInitModel();
        restoreValidation();
    }
});
</script>

<template>
    <ElDrawer v-model="visible" :title="title" :size="360">
        <ElForm ref="formRef" :model="model" :rules="rules" label-position="top">
            <ElFormItem label="评论内容" prop="content">
                <ElInput v-model="model.content" type="textarea" :rows="5" placeholder="请输入评论内容" />
            </ElFormItem>

            <ElFormItem label="审核状态" prop="state">
                <ElSelect v-model="model.state" placeholder="请选择审核状态" class="w-full">
                    <ElOption v-for="item in stateOptions" :key="item.value" :label="item.label" :value="item.value" />
                </ElSelect>
            </ElFormItem>

            <ElAlert v-if="props.operateType === 'edit'" title="提示" type="info" :closable="false" show-icon>
                <template #default>
                    <p>可以修改评论内容和审核状态</p>
                    <p v-if="props.rowData">评论ID: {{ props.rowData.id }}</p>
                    <p v-if="props.rowData">用户ID: {{ props.rowData.user_id }}</p>
                    <p v-if="props.rowData">商家ID: {{ props.rowData.store_id }}</p>
                </template>
            </ElAlert>
        </ElForm>
        <template #footer>
            <div class="flex justify-end gap-12px">
                <ElButton @click="closeDrawer">取消</ElButton>
                <ElButton type="primary" @click="handleSubmit">确认</ElButton>
            </div>
        </template>
    </ElDrawer>
</template>
