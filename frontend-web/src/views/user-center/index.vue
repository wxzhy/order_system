<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import type { FormRules } from 'element-plus';
import { fetchChangePassword, fetchDeleteAccount, fetchGetUserInfo, fetchUpdateProfile } from '@/service/api';
import { useAuthStore } from '@/store/modules/auth';
import { $t } from '@/locales';

defineOptions({ name: 'UserCenter' });

const authStore = useAuthStore();
const loading = ref(false);
const activeTab = ref('profile');

// 删除账号对话框
const deleteDialogVisible = ref(false);
const deletePassword = ref('');
const deleteLoading = ref(false);

// 用户信息表单
const userForm = reactive({
  username: '',
  email: '',
  phone: '',
  user_type: ''
});

// 修改密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const passwordFormRef = ref();

// 表单验证规则
const userFormRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }]
};

const passwordFormRules: FormRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
};

// 用户类型显示
const userTypeLabel = computed(() => {
  const typeMap: Record<string, string> = {
    customer: '普通用户',
    vendor: '商家用户',
    admin: '管理员'
  };
  return typeMap[userForm.user_type] || userForm.user_type;
});

// 加载用户信息
async function loadUserInfo() {
  loading.value = true;
  try {
    const data = await fetchGetUserInfo();
    if (data) {
      userForm.username = data.username;
      userForm.email = data.email;
      userForm.phone = data.phone || '';
      userForm.user_type = data.user_type;
    }
  } catch (error: any) {
    window.$message?.error(error?.message || '加载用户信息失败');
  } finally {
    loading.value = false;
  }
}

// 更新个人信息
async function handleUpdateProfile() {
  loading.value = true;
  try {
    await fetchUpdateProfile({
      username: userForm.username,
      email: userForm.email,
      phone: userForm.phone || undefined
    });
    window.$message?.success('个人信息更新成功');
    // 更新store中的用户信息
    await authStore.initUserInfo();
  } catch (error: any) {
    window.$message?.error(error?.message || '更新失败');
  } finally {
    loading.value = false;
  }
}

// 修改密码
async function handleChangePassword() {
  if (!passwordFormRef.value) return;

  await passwordFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return;

    loading.value = true;
    try {
      await fetchChangePassword(passwordForm.oldPassword, passwordForm.newPassword);
      window.$message?.success('密码修改成功，请重新登录');
      // 重置表单
      passwordForm.oldPassword = '';
      passwordForm.newPassword = '';
      passwordForm.confirmPassword = '';
      passwordFormRef.value?.resetFields();
      // 退出登录
      setTimeout(() => {
        authStore.resetStore();
      }, 1500);
    } catch (error: any) {
      window.$message?.error(error?.message || '密码修改失败');
    } finally {
      loading.value = false;
    }
  });
}

// 打开删除账号对话框
function openDeleteDialog() {
  deletePassword.value = '';
  deleteDialogVisible.value = true;
}

// 关闭删除账号对话框
function closeDeleteDialog() {
  deleteDialogVisible.value = false;
  deletePassword.value = '';
}

// 删除账号
async function handleDeleteAccount() {
  if (!deletePassword.value) {
    window.$message?.warning('请输入密码');
    return;
  }

  deleteLoading.value = true;
  try {
    await fetchDeleteAccount(deletePassword.value);
    window.$message?.success('账号已删除');
    closeDeleteDialog();
    // 退出登录
    setTimeout(() => {
      authStore.resetStore();
    }, 1500);
  } catch (error: any) {
    window.$message?.error(error?.message || '删除失败');
  } finally {
    deleteLoading.value = false;
  }
}

// 初始化加载
loadUserInfo();
</script>

<template>
  <div class="h-full overflow-y-auto">
    <NCard :title="$t('common.userCenter')" :bordered="false" class="h-full card-wrapper">
      <ElTabs v-model="activeTab" class="user-center-tabs">
        <!-- 个人信息标签页 -->
        <ElTabPane label="个人信息" name="profile">
          <div class="max-w-600px">
            <ElForm :model="userForm" :rules="userFormRules" label-width="100px" :disabled="loading">
              <ElFormItem label="用户名" prop="username">
                <ElInput v-model="userForm.username" placeholder="请输入用户名" />
              </ElFormItem>

              <ElFormItem label="邮箱" prop="email">
                <ElInput v-model="userForm.email" placeholder="请输入邮箱" />
              </ElFormItem>

              <ElFormItem label="手机号" prop="phone">
                <ElInput v-model="userForm.phone" placeholder="请输入手机号" />
              </ElFormItem>

              <ElFormItem label="用户类型">
                <ElInput :value="userTypeLabel" disabled />
              </ElFormItem>

              <ElFormItem>
                <ElButton type="primary" :loading="loading" @click="handleUpdateProfile">保存修改</ElButton>
              </ElFormItem>
            </ElForm>
          </div>
        </ElTabPane>

        <!-- 修改密码标签页 -->
        <ElTabPane label="修改密码" name="password">
          <div class="max-w-600px">
            <ElForm ref="passwordFormRef" :model="passwordForm" :rules="passwordFormRules" label-width="120px"
              :disabled="loading">
              <ElFormItem label="当前密码" prop="oldPassword">
                <ElInput v-model="passwordForm.oldPassword" type="password" placeholder="请输入当前密码" show-password />
              </ElFormItem>

              <ElFormItem label="新密码" prop="newPassword">
                <ElInput v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码（至少6位）" show-password />
              </ElFormItem>

              <ElFormItem label="确认新密码" prop="confirmPassword">
                <ElInput v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
              </ElFormItem>

              <ElFormItem>
                <ElButton type="primary" :loading="loading" @click="handleChangePassword">修改密码</ElButton>
                <ElButton :disabled="loading" @click="passwordFormRef?.resetFields()">重置</ElButton>
              </ElFormItem>
            </ElForm>
          </div>
        </ElTabPane>

        <!-- 账户安全标签页 -->
        <ElTabPane label="账户安全" name="security">
          <div class="max-w-600px">
            <ElAlert title="危险操作" type="error" :closable="false" show-icon style="margin-bottom: 20px;">
              删除账号后，您的所有数据将被永久删除且无法恢复，请谨慎操作。
            </ElAlert>
            <ElButton type="danger" :loading="loading" @click="openDeleteDialog">删除我的账号</ElButton>
          </div>
        </ElTabPane>
      </ElTabs>

      <!-- 删除账号确认对话框 -->
      <ElDialog v-model="deleteDialogVisible" title="删除账号" width="500px" :close-on-click-modal="false">
        <ElAlert title="警告" type="error" :closable="false" show-icon style="margin-bottom: 20px;">
          此操作不可撤销！删除账号后，您的所有数据将被永久删除。
        </ElAlert>
        <ElForm label-width="100px">
          <ElFormItem label="输入密码" required>
            <ElInput v-model="deletePassword" type="password" placeholder="请输入密码以确认删除" show-password />
          </ElFormItem>
        </ElForm>
        <template #footer>
          <ElButton @click="closeDeleteDialog">取消</ElButton>
          <ElButton type="danger" :loading="deleteLoading" @click="handleDeleteAccount">确认删除</ElButton>
        </template>
      </ElDialog>
    </NCard>
  </div>
</template>

<style scoped>
.user-center-tabs {
  margin-top: 20px;
}

.user-center-tabs :deep(.el-tabs__content) {
  padding-top: 20px;
}
</style>
