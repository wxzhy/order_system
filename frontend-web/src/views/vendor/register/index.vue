<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { addStore } from '@/service/api';
import { useAuthStore } from '@/store/modules/auth';

defineOptions({ name: 'VendorRegister' });

const router = useRouter();
const authStore = useAuthStore();

interface StoreForm {
    storeName: string;
    description: string;
    address: string;
    phone: string;
    hours: string;
}

const loading = ref(false);
const formRef = ref();
const formData = ref<StoreForm>({
    storeName: '',
    description: '',
    address: '',
    phone: '',
    hours: '09:00-21:00'
});

const rules = {
    storeName: [{ required: true, message: '请输入商家名称', trigger: 'blur' }],
    address: [{ required: true, message: '请输入商家地址', trigger: 'blur' }],
    phone: [
        { required: true, message: '请输入联系电话', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码', trigger: 'blur' }
    ],
    hours: [{ required: true, message: '请输入营业时间', trigger: 'blur' }]
};

async function handleSubmit() {
    try {
        await formRef.value?.validate();
        loading.value = true;

        await addStore({
            storeName: formData.value.storeName,
            description: formData.value.description || undefined,
            address: formData.value.address,
            phone: formData.value.phone,
            hours: formData.value.hours
        });

        ElMessage.success('商家信息注册成功，请等待管理员审核');

        // 刷新用户信息
        await authStore.getUserInfo();

        // 跳转到首页或商家管理页面
        router.push('/');
    } catch (error: any) {
        if (error?.message) {
            ElMessage.error(error.message);
        }
    } finally {
        loading.value = false;
    }
}

function handleCancel() {
    router.back();
}
</script>

<template>
    <div class="h-full flex-center">
        <ElCard class="w-600px">
            <template #header>
                <div class="flex items-center justify-between">
                    <h2 class="m-0">商家信息注册</h2>
                </div>
            </template>

            <ElAlert title="欢迎注册商家信息" type="info" description="请填写您的商家信息，提交后需要等待管理员审核通过才能正常使用。" :closable="false"
                class="mb-20px" />

            <ElForm ref="formRef" :model="formData" :rules="rules" label-width="100px" label-position="left">
                <ElFormItem label="商家名称" prop="storeName">
                    <ElInput v-model="formData.storeName" placeholder="请输入商家名称" />
                </ElFormItem>

                <ElFormItem label="商家简介" prop="description">
                    <ElInput v-model="formData.description" type="textarea" :rows="3" placeholder="请输入商家简介（可选）"
                        maxlength="200" show-word-limit />
                </ElFormItem>

                <ElFormItem label="商家地址" prop="address">
                    <ElInput v-model="formData.address" placeholder="请输入商家地址，例如：一食堂二楼" />
                </ElFormItem>

                <ElFormItem label="联系电话" prop="phone">
                    <ElInput v-model="formData.phone" placeholder="请输入联系电话" />
                </ElFormItem>

                <ElFormItem label="营业时间" prop="hours">
                    <ElInput v-model="formData.hours" placeholder="例如：09:00-21:00" />
                </ElFormItem>

                <ElFormItem>
                    <ElSpace :size="16">
                        <ElButton @click="handleCancel">取消</ElButton>
                        <ElButton type="primary" :loading="loading" @click="handleSubmit">提交注册</ElButton>
                    </ElSpace>
                </ElFormItem>
            </ElForm>
        </ElCard>
    </div>
</template>

<style scoped lang="scss">
.w-600px {
    width: 600px;
    max-width: 90vw;
}
</style>
