<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { addStore, updateMyStore } from '@/service/api';
import { useAuthStore } from '@/store/modules/auth';
import { useTabStore } from '@/store/modules/tab';
import { useRouterPush } from '@/hooks/common/router';
import type { RouteKey } from '@elegant-router/types';
import { useVendorStoreStatus } from '@/hooks/business/vendor-store';

defineOptions({ name: 'VendorRegister' });

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const tabStore = useTabStore();
const { routerPushByKey } = useRouterPush();
const { status, store, state, exists, loading: statusLoading, errorMessage, forbidden, loadStatus } =
  useVendorStoreStatus(false);

interface StoreForm {
  storeName: string;
  description: string;
  address: string;
  phone: string;
  hours: string;
  imageURL: string;
}

const formRef = ref();
const submitLoading = ref(false);
const formData = reactive<StoreForm>({
  storeName: '',
  description: '',
  address: '',
  phone: '',
  hours: '09:00-21:00',
  imageURL: ''
});

const rules = {
  storeName: [{ required: true, message: '请输入商家名称', trigger: 'blur' }],
  address: [{ required: true, message: '请输入商家地址', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系方式', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' }
  ],
  hours: [{ required: true, message: '请输入营业时间', trigger: 'blur' }]
};

const statusTagType = computed<'success' | 'warning' | 'danger' | 'info'>(() => {
  switch (state.value) {
    case 'approved':
      return 'success';
    case 'pending':
      return 'warning';
    case 'rejected':
      return 'danger';
    default:
      return 'info';
  }
});

const statusAlertType = computed<'success' | 'warning' | 'error' | 'info'>(() => {
  switch (state.value) {
    case 'approved':
      return 'success';
    case 'pending':
      return 'warning';
    case 'rejected':
      return 'error';
    default:
      return 'info';
  }
});

const statusText = computed(() => {
  switch (state.value) {
    case 'approved':
      return '审核已通过';
    case 'pending':
      return '审核中';
    case 'rejected':
      return '审核未通过';
    default:
      return '未提交';
  }
});

const statusDescription = computed(() => {
  switch (state.value) {
    case 'approved':
      return '商家信息已审核通过，可以开始管理餐点和订单。您可以随时修改商家信息，修改后无需重新审核。';
    case 'pending':
      return '商家信息正在审核中，请耐心等待。审核通过前可以修改信息并重新提交。';
    case 'rejected':
      return '商家信息审核未通过，请根据反馈修改信息后重新提交。';
    default:
      return '尚未提交商家信息，请填写以下表单完成注册。';
  }
});

const showStoreSummary = computed(() => Boolean(exists.value && store.value));
const handledForbidden = ref(false);
const reviewTime = computed(() => store.value?.review_time ?? null);

function fillFormWithStore() {
  if (store.value) {
    formData.storeName = store.value.storeName ?? '';
    formData.description = store.value.description ?? '';
    formData.address = store.value.address ?? '';
    formData.phone = store.value.phone ?? '';
    formData.hours = store.value.hours ?? '09:00-21:00';
    formData.imageURL = store.value.imageURL ?? '';
  } else {
    formData.storeName = '';
    formData.description = '';
    formData.address = '';
    formData.phone = '';
    formData.hours = '09:00-21:00';
    formData.imageURL = '';
  }
}

async function initializeStatus() {
  await loadStatus();
  fillFormWithStore();
}

watch(
  () => forbidden.value,
  async val => {
    if (val && !handledForbidden.value) {
      handledForbidden.value = true;
      const message = errorMessage.value || '当前账号无权访问商家中心，将返回首页';
      window.$message?.error(message);

      const currentRouteName = route.name as RouteKey | undefined;

      await routerPushByKey('root');

      if (currentRouteName && currentRouteName !== 'root') {
        await tabStore.removeTabByRouteName(currentRouteName);
      }
    }
  }
);

onMounted(() => {
  initializeStatus();
});

watch(store, () => {
  fillFormWithStore();
});

async function handleSubmit() {
  await formRef.value?.validate();

  submitLoading.value = true;

  try {
    const payload = {
      storeName: formData.storeName,
      description: formData.description || undefined,
      address: formData.address,
      phone: formData.phone,
      hours: formData.hours,
      imageURL: formData.imageURL || undefined
    };

    if (exists.value) {
      await updateMyStore(payload);
      ElMessage.success('商家信息已更新，修改立即生效。');
    } else {
      await addStore(payload);
      ElMessage.success('商家信息提交成功，请等待审核。');
    }

    await authStore.initUserInfo();
    await loadStatus();
  } catch (error: any) {
    ElMessage.error(error?.message || '提交失败，请稍后重试');
  } finally {
    submitLoading.value = false;
  }
}

function handleBack() {
  router.back();
}
</script>

<template>
  <div class="vendor-register">
    <ElCard class="status-card">
      <template #header>
        <div class="status-header">
          <h2 class="m-0">商家审核状态</h2>
          <ElTag :type="statusTagType">{{ statusText }}</ElTag>
        </div>
      </template>

      <ElSkeleton v-if="statusLoading" animated :rows="4" />
      <template v-else>
        <ElAlert v-if="errorMessage" type="error" :title="errorMessage" show-icon :closable="false" />
        <template v-else>
          <ElAlert :title="statusDescription" :type="statusAlertType" show-icon :closable="false" />

          <ElDescriptions v-if="showStoreSummary" class="mt-16px" :column="1" border>
            <ElDescriptionsItem label="商家名称">{{ store?.storeName }}</ElDescriptionsItem>
            <ElDescriptionsItem label="地址">{{ store?.address }}</ElDescriptionsItem>
            <ElDescriptionsItem label="联系方式">{{ store?.phone }}</ElDescriptionsItem>
            <ElDescriptionsItem label="营业时间">{{ store?.hours || '未填写' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="审核通过时间">
              {{ reviewTime ? new Date(reviewTime).toLocaleString() : '未审核' }}
            </ElDescriptionsItem>
          </ElDescriptions>
        </template>
      </template>
    </ElCard>

    <ElCard class="form-card">
      <template #header>
        <div class="status-header">
          <h2 class="m-0">{{ exists ? '修改商家信息' : '商家信息注册' }}</h2>
        </div>
      </template>

      <ElForm ref="formRef" :model="formData" :rules="rules" label-width="100px" label-position="left">
        <ElFormItem label="商家名称" prop="storeName">
          <ElInput v-model="formData.storeName" placeholder="请输入商家名称" />
        </ElFormItem>

        <ElFormItem label="商家简介" prop="description">
          <ElInput v-model="formData.description" type="textarea" :rows="3" placeholder="请输入商家简介（可选）" maxlength="200"
            show-word-limit />
        </ElFormItem>

        <ElFormItem label="商家地址" prop="address">
          <ElInput v-model="formData.address" placeholder="请输入商家地址，如：一食堂一层" />
        </ElFormItem>

        <ElFormItem label="联系方式" prop="phone">
          <ElInput v-model="formData.phone" placeholder="请输入联系方式" />
        </ElFormItem>

        <ElFormItem label="营业时间" prop="hours">
          <ElInput v-model="formData.hours" placeholder="例如：09:00-21:00" />
        </ElFormItem>

        <ElFormItem label="宣传图片" prop="imageURL">
          <ElInput v-model="formData.imageURL" placeholder="请输入宣传图片 URL（可选）" />
        </ElFormItem>

        <ElFormItem>
          <ElSpace :size="16">
            <ElButton @click="handleBack">返回</ElButton>
            <ElButton type="primary" :loading="submitLoading" @click="handleSubmit">
              {{ exists ? '提交修改' : '提交注册' }}
            </ElButton>
          </ElSpace>
        </ElFormItem>
      </ElForm>
    </ElCard>
  </div>
</template>

<style scoped lang="scss">
.vendor-register {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

.status-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

@media (min-width: 1024px) {
  .vendor-register {
    flex-direction: row;
    align-items: flex-start;
  }

  .status-card {
    width: 360px;
    flex-shrink: 0;
  }

  .form-card {
    flex: 1;
  }
}
</style>
