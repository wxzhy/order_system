<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouterPush } from '@/hooks/common/router';
import { useForm, useFormRules } from '@/hooks/common/form';
import { useEmailCaptcha } from '@/hooks/business/captcha';
import { useAuthStore } from '@/store/modules/auth';

defineOptions({ name: 'CodeLogin' });

const authStore = useAuthStore();
const { toggleLoginModule } = useRouterPush();
const { formRef, validate } = useForm();
const { label, isCounting, loading, getCaptcha } = useEmailCaptcha('login');

interface FormModel {
  email: string;
  code: string;
}

const model = ref<FormModel>({ email: '', code: '' });

const rules = computed<Record<keyof FormModel, App.Global.FormRule[]>>(() => {
  const { formRules } = useFormRules();

  return { email: formRules.email, code: formRules.code };
});

async function handleSubmit() {
  await validate();
  await authStore.loginWithEmailCode(model.value.email, model.value.code);
}
</script>

<template>
  <ElForm ref="formRef" :model="model" :rules="rules" size="large" :show-label="false" @keyup.enter="handleSubmit">
    <ElFormItem prop="email">
      <ElInput v-model="model.email" :placeholder="$t('page.login.common.emailPlaceholder')" />
    </ElFormItem>
    <ElFormItem prop="code">
      <div class="w-full flex-y-center gap-16px">
        <ElInput v-model="model.code" :placeholder="$t('page.login.common.codePlaceholder')" />
        <ElButton size="large" :disabled="isCounting" :loading="loading" @click="getCaptcha(model.email)">
          {{ label }}
        </ElButton>
      </div>
    </ElFormItem>
    <ElSpace direction="vertical" :size="18" fill class="w-full">
      <ElButton type="primary" size="large" round block :loading="authStore.loginLoading" @click="handleSubmit">
        {{ $t('common.confirm') }}
      </ElButton>
      <ElButton size="large" round block @click="toggleLoginModule('pwd-login')">
        {{ $t('page.login.common.back') }}
      </ElButton>
    </ElSpace>
  </ElForm>
</template>

<style scoped></style>
