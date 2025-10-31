<script setup lang="ts">
import { computed, reactive, watch } from 'vue';
import { getOrder, updateOrder } from '@/service/api';
import { useFormRules } from '@/hooks/common/form';

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

const title = computed(() => (props.operateType === 'add' ? '新增订单' : '编辑订单'));

type Model = {
    state: Api.SystemManage.OrderState;
};

const model: Model = reactive(createDefaultModel());

function createDefaultModel(): Model {
    return {
        state: 'pending'
    };
}

const { formRef, validate, restoreValidation } = useFormRules();
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

    if (props.operateType === 'edit' && props.rowData) {
        // 获取完整订单信息
        try {
            const orderData = await getOrder(props.rowData.id);
            Object.assign(model, {
                state: orderData.state
            });
        } catch (error) {
            Object.assign(model, {
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
    <ElDrawer v-model="visible" :title="title" :size="360">
        <ElForm ref="formRef" :model="model" :rules="rules" label-position="top">
            <ElFormItem label="订单状态" prop="state">
                <ElSelect v-model="model.state" placeholder="请选择订单状态" class="w-full">
                    <ElOption v-for="item in stateOptions" :key="item.value" :label="item.label" :value="item.value" />
                </ElSelect>
            </ElFormItem>

            <ElAlert v-if="props.operateType === 'edit'" title="提示" type="info" :closable="false" show-icon>
                <template #default>
                    <p>仅支持修改订单状态</p>
                    <p v-if="props.rowData">订单ID: {{ props.rowData.id }}</p>
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
