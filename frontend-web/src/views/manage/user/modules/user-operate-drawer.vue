<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { addUser, updateUser } from '@/service/api';
import { useForm, useFormRules } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({ name: 'UserOperateDrawer' });

interface Props {
  /** the type of operation */
  operateType: UI.TableOperateType;
  /** the edit row data */
  rowData?: Api.SystemManage.User | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
  default: false
});

const { formRef, validate, restoreValidation } = useForm();
const { defaultRequiredRule, formRules } = useFormRules();

const title = computed(() => {
  const titles: Record<UI.TableOperateType, string> = {
    add: '新增用户',
    edit: '编辑用户'
  };
  return titles[props.operateType];
});

interface Model {
  username: string;
  email: string;
  phone: string;
  password?: string;
  user_type: 'customer' | 'vendor' | 'admin';
}

const model = ref(createDefaultModel());

function createDefaultModel(): Model {
  return {
    username: '',
    email: '',
    phone: '',
    password: '',
    user_type: 'customer'
  };
}

const rules = computed(() => {
  const baseRules: Record<string, App.Global.FormRule[]> = {
    username: [defaultRequiredRule],
    email: [defaultRequiredRule, formRules.email],
    user_type: [defaultRequiredRule]
  };

  // 新增时密码必填,编辑时密码可选
  if (props.operateType === 'add') {
    baseRules.password = [defaultRequiredRule];
  }

  return baseRules;
});

const userTypeOptions = [
  { label: '管理员', value: 'admin' },
  { label: '商家', value: 'vendor' },
  { label: '顾客', value: 'customer' }
];

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    model.value = {
      username: props.rowData.username,
      email: props.rowData.email,
      phone: props.rowData.phone || '',
      user_type: props.rowData.user_type
    };
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  try {
    if (props.operateType === 'add') {
      await addUser({
        username: model.value.username,
        email: model.value.email,
        phone: model.value.phone || undefined,
        password: model.value.password,
        user_type: model.value.user_type
      });
      window.$message?.success('添加成功');
    } else if (props.rowData) {
      const updateData: any = {
        username: model.value.username,
        email: model.value.email,
        phone: model.value.phone || undefined,
        user_type: model.value.user_type
      };

      // 只有填写了密码才更新密码
      if (model.value.password) {
        updateData.password = model.value.password;
      }

      await updateUser(props.rowData.id, updateData);
      window.$message?.success('更新成功');
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
      <ElFormItem label="用户名" prop="username">
        <ElInput v-model="model.username" placeholder="请输入用户名" />
      </ElFormItem>
      <ElFormItem label="邮箱" prop="email">
        <ElInput v-model="model.email" placeholder="请输入邮箱" />
      </ElFormItem>
      <ElFormItem label="手机号" prop="phone">
        <ElInput v-model="model.phone" placeholder="请输入手机号(可选)" />
      </ElFormItem>
      <ElFormItem :label="operateType === 'add' ? '密码' : '密码(留空不修改)'" prop="password">
        <ElInput v-model="model.password" type="password" show-password
          :placeholder="operateType === 'add' ? '请输入密码' : '留空则不修改密码'" />
      </ElFormItem>
      <ElFormItem label="用户类型" prop="user_type">
        <ElSelect v-model="model.user_type" placeholder="请选择用户类型">
          <ElOption v-for="item in userTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </ElSelect>
      </ElFormItem>
    </ElForm>
    <template #footer>
      <ElSpace :size="16">
        <ElButton @click="closeDrawer">{{ $t('common.cancel') }}</ElButton>
        <ElButton type="primary" @click="handleSubmit">{{ $t('common.confirm') }}</ElButton>
      </ElSpace>
    </template>
  </ElDrawer>
</template>

<style scoped></style>
