<script setup lang="ts">
import { ref, watch } from 'vue';
import { resetUserPassword } from '@/service/api';
import { useForm, useFormRules } from '@/hooks/common/form';

defineOptions({ name: 'UserResetPassword' });

interface Props {
    /** the user id */
    userId?: number | null;
    /** the username */
    username?: string;
}

const props = defineProps<Props>();

interface Emits {
    (e: 'success'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
    default: false
});

const { formRef, validate, restoreValidation } = useForm();
const { defaultRequiredRule } = useFormRules();

const model = ref({
    newPassword: '123456'
});

const rules = {
    newPassword: [defaultRequiredRule]
};

function closeDialog() {
    visible.value = false;
}

async function handleSubmit() {
    await validate();

    if (!props.userId) {
        window.$message?.error('用户ID不存在');
        return;
    }

    try {
        await resetUserPassword(props.userId, model.value.newPassword);
        window.$message?.success('密码重置成功');
        closeDialog();
        emit('success');
    } catch (error: any) {
        window.$message?.error(error?.message || '密码重置失败');
    }
}

watch(visible, () => {
    if (visible.value) {
        model.value.newPassword = '123456';
        restoreValidation();
    }
});
</script>

<template>
    <ElDialog v-model="visible" title="重置密码" width="400px" :close-on-click-modal="false">
        <ElForm ref="formRef" :model="model" :rules="rules" label-width="100px">
            <ElFormItem label="用户名">
                <ElInput :model-value="username" disabled />
            </ElFormItem>
            <ElFormItem label="新密码" prop="newPassword">
                <ElInput v-model="model.newPassword" type="password" show-password placeholder="请输入新密码" />
            </ElFormItem>
            <ElAlert type="info" :closable="false" show-icon>
                <template #title>
                    <span class="text-14px">默认密码为 123456，可以自定义修改</span>
                </template>
            </ElAlert>
        </ElForm>
        <template #footer>
            <ElSpace :size="16">
                <ElButton @click="closeDialog">取消</ElButton>
                <ElButton type="primary" @click="handleSubmit">确认重置</ElButton>
            </ElSpace>
        </template>
    </ElDialog>
</template>

<style scoped></style>
