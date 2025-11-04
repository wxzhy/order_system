<script setup lang="ts">
import { computed, ref } from 'vue';
import { fetchRegister } from '@/service/api';
import { useRouterPush } from '@/hooks/common/router';
import { useForm, useFormRules } from '@/hooks/common/form';
import { useEmailCaptcha } from '@/hooks/business/captcha';
import { $t } from '@/locales';

defineOptions({ name: 'Register' });

const { toggleLoginModule } = useRouterPush();
const { formRef, validate } = useForm();

interface FormModel {
  username: string;
  email: string;
  phone: string;
  verification_code: string;
  password: string;
  confirmPassword: string;
  user_type: 'customer' | 'vendor';
}

const model = ref<FormModel>({
  username: '',
  email: '',
  phone: '',
  verification_code: '',
  password: '',
  confirmPassword: '',
  user_type: 'customer'
});

const submitLoading = ref(false);
const { label, isCounting, loading: captchaLoading, getCaptcha } = useEmailCaptcha('register');

const rules = computed<Record<string, App.Global.FormRule[]>>(() => {
  const { formRules, createConfirmPwdRule, defaultRequiredRule } = useFormRules();

  return {
    username: formRules.userName,
    email: formRules.email,
    phone: formRules.phone,
    verification_code: formRules.code,
    password: formRules.pwd,
    confirmPassword: createConfirmPwdRule(model.value.password),
    user_type: [defaultRequiredRule]
  };
});

async function handleSubmit() {
  await validate();
  submitLoading.value = true;

  try {
    await fetchRegister({
      username: model.value.username,
      email: model.value.email,
      verification_code: model.value.verification_code,
      phone: model.value.phone,
      password: model.value.password,
      user_type: model.value.user_type
    });

    window.$message?.success($t('page.login.register.success'));
    toggleLoginModule('pwd-login');
  } catch (error: any) {
    const message = error?.message || $t('page.login.register.error');
    window.$message?.error(message);
  } finally {
    submitLoading.value = false;
  }
}
</script>

<template>
  <ElForm ref="formRef" :model="model" :rules="rules" size="large" :show-label="false" @keyup.enter="handleSubmit">
    <ElFormItem prop="user_type">
      <ElRadioGroup v-model="model.user_type" class="account-type-radio">
        <ElRadioButton value="customer">
          <ElIcon class="mr-4px">
            <icon-mdi:account />
          </ElIcon>
          普通用户
        </ElRadioButton>
        <ElRadioButton value="vendor">
          <ElIcon class="mr-4px">
            <icon-mdi:store />
          </ElIcon>
          商家
        </ElRadioButton>
      </ElRadioGroup>
    </ElFormItem>
    <ElAlert v-if="model.user_type === 'vendor'" type="info" :closable="false" class="mb-16px">
      <template #title>
        <span class="text-12px">注册商家账户后,需要在商家中心完善店铺信息并等待审核</span>
      </template>
    </ElAlert>
    <ElFormItem prop="username">
      <ElInput v-model="model.username" :placeholder="$t('page.login.common.userNamePlaceholder')" />
    </ElFormItem>
    <ElFormItem prop="email">
      <ElInput v-model="model.email" :placeholder="$t('page.login.common.emailPlaceholder')" />
    </ElFormItem>
    <ElFormItem prop="verification_code">
      <div class="w-full flex-y-center gap-16px">
        <ElInput v-model="model.verification_code" :placeholder="$t('page.login.common.codePlaceholder')" />
        <ElButton
          size="large"
          :disabled="isCounting"
          :loading="captchaLoading"
          @click="getCaptcha(model.email)"
        >
          {{ label }}
        </ElButton>
      </div>
    </ElFormItem>
    <ElFormItem prop="phone">
      <ElInput v-model="model.phone" :placeholder="$t('page.login.common.phonePlaceholder')" />
    </ElFormItem>
    <ElFormItem prop="password">
      <ElInput v-model="model.password" type="password" show-password-on="click"
        :placeholder="$t('page.login.common.passwordPlaceholder')" />
    </ElFormItem>
    <ElFormItem prop="confirmPassword">
      <ElInput v-model="model.confirmPassword" type="password" show-password-on="click"
        :placeholder="$t('page.login.common.confirmPasswordPlaceholder')" />
    </ElFormItem>
    <ElSpace direction="vertical" :size="18" fill class="w-full">
      <ElButton type="primary" size="large" round block :loading="submitLoading" @click="handleSubmit">
        {{ $t('common.confirm') }}
      </ElButton>
      <ElButton size="large" round @click="toggleLoginModule('pwd-login')">
        {{ $t('page.login.common.back') }}
      </ElButton>
    </ElSpace>
  </ElForm>
</template>

<style scoped>
.account-type-radio {
  width: 100%;
  display: flex;
}

.account-type-radio :deep(.el-radio-button) {
  flex: 1;
}

.account-type-radio :deep(.el-radio-button__inner) {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 20px;
}
</style>
