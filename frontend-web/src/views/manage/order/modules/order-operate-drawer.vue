<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { getOrder, updateOrder } from '@/service/api';
import { useForm, useFormRules } from '@/hooks/common/form';

defineOptions({
  name: 'OrderOperateDrawer'
});

interface Props {
  operateType: 'add' | 'edit';
  rowData?: Api.SystemManage.Order | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
  default: false
});

const title = computed(() => (props.operateType === 'add' ? '新增订单' : '订单详情'));

type Model = {
  state: Api.SystemManage.OrderState;
};

const model: Model = reactive(createDefaultModel());

function createDefaultModel(): Model {
  return {
    state: 'pending'
  };
}

// 订单详情数据
const orderDetail = ref<Api.SystemManage.Order | null>(null);
const loadingDetail = ref(false);

const { formRef, validate, restoreValidation } = useForm();
const { defaultRequiredRule } = useFormRules();

const stateOptions = [
  { label: '待审核', value: 'pending' },
  { label: '已同意', value: 'approved' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
];

const rules = computed(() => {
  const baseRules: Record<string, App.Global.FormRule[]> = {
    state: [defaultRequiredRule]
  };

  return baseRules;
});

async function handleInitModel() {
  Object.assign(model, createDefaultModel());
  orderDetail.value = null;

  if (props.operateType === 'edit' && props.rowData) {
    // 获取完整订单信息
    try {
      loadingDetail.value = true;
      const orderData = await getOrder(props.rowData.id);
      orderDetail.value = orderData;
      Object.assign(model, {
        state: orderData.state
      });
    } catch (error) {
      Object.assign(model, {
        state: props.rowData.state
      });
    } finally {
      loadingDetail.value = false;
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
      await updateOrder(props.rowData.id, {
        state: model.state
      });
      window.$message?.success('更新成功');
    } else {
      window.$message?.warning('订单创建功能暂未开放');
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
  <ElDrawer v-model="visible" :title="title" :size="600">
    <ElForm ref="formRef" :model="model" :rules="rules" label-position="top">
      <!-- 订单基本信息 -->
      <ElDivider content-position="left">订单信息</ElDivider>

      <ElRow :gutter="16">
        <ElCol :span="12">
          <ElFormItem label="订单ID">
            <ElInput :value="props.rowData?.id" disabled />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="订单状态" prop="state">
            <ElSelect v-model="model.state" placeholder="请选择订单状态" class="w-full">
              <ElOption v-for="item in stateOptions" :key="item.value" :label="item.label" :value="item.value" />
            </ElSelect>
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="16">
        <ElCol :span="12">
          <ElFormItem label="用户ID">
            <ElInput :value="props.rowData?.user_id" disabled />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="商家ID">
            <ElInput :value="props.rowData?.store_id" disabled />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElRow :gutter="16">
        <ElCol :span="12">
          <ElFormItem label="创建时间">
            <ElInput :value="props.rowData?.create_time" disabled />
          </ElFormItem>
        </ElCol>
        <ElCol :span="12">
          <ElFormItem label="处理时间">
            <ElInput :value="props.rowData?.review_time || '未处理'" disabled />
          </ElFormItem>
        </ElCol>
      </ElRow>

      <ElFormItem label="订单总额">
        <ElInput :value="orderDetail?.total_amount ? `¥${orderDetail.total_amount.toFixed(2)}` : '-'" disabled />
      </ElFormItem>

      <!-- 订单项列表 -->
      <ElDivider content-position="left">订单项目</ElDivider>

      <ElCard v-loading="loadingDetail" shadow="never">
        <ElTable v-if="orderDetail?.items?.length" :data="orderDetail.items" border>
          <ElTableColumn prop="item_id" label="菜品ID" width="80" align="center" />
          <ElTableColumn prop="item_name" label="菜品名称" min-width="150">
            <template #default="{ row }">
              {{ row.item_name || '-' }}
            </template>
          </ElTableColumn>
          <ElTableColumn prop="quantity" label="数量" width="80" align="center" />
          <ElTableColumn prop="item_price" label="单价" width="100" align="right">
            <template #default="{ row }">
              ¥{{ row.item_price.toFixed(2) }}
            </template>
          </ElTableColumn>
          <ElTableColumn label="小计" width="100" align="right">
            <template #default="{ row }">
              ¥{{ (row.item_price * row.quantity).toFixed(2) }}
            </template>
          </ElTableColumn>
        </ElTable>
        <ElEmpty v-else description="暂无订单项" />
      </ElCard>

      <ElAlert v-if="props.operateType === 'edit'" title="提示" type="info" :closable="false" show-icon
        style="margin-top: 16px">
        <template #default>
          <p>仅支持修改订单状态</p>
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
