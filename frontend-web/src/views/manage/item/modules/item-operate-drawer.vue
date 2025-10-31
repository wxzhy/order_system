<script setup lang="ts">
import { computed, reactive, watch } from 'vue';
import type { FormInstance } from 'element-plus';
import { addItem, updateItem } from '@/service/api';
import { useFormRules } from '@/hooks/common/form';

defineOptions({
    name: 'ItemOperateDrawer'
});

interface Props {
    operateType: 'add' | 'edit';
    rowData?: Api.SystemManage.Item | null;
}

const props = defineProps<Props>();

interface Emits {
    (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
    default: false
});

const title = computed(() => (props.operateType === 'add' ? '新增餐点' : '编辑餐点'));

type Model = Api.SystemManage.ItemEdit;

const model: Model = reactive(createDefaultModel());

function createDefaultModel(): Model {
    return {
        itemName: '',
        description: '',
        imageURL: '',
        price: 0,
        quantity: 0,
        store_id: 1
    };
}

const { formRef, validate, restoreValidation } = useFormRules();
const { defaultRequiredRule } = useFormRules();

const rules = computed(() => {
    const baseRules: Record<string, App.Global.FormRule[]> = {
        itemName: [defaultRequiredRule],
        price: [defaultRequiredRule, { type: 'number', min: 0.01, message: '价格必须大于0', trigger: 'blur' }],
        quantity: [defaultRequiredRule, { type: 'number', min: 0, message: '库存不能为负数', trigger: 'blur' }],
        store_id: [defaultRequiredRule]
    };

    return baseRules;
});

function handleInitModel() {
    Object.assign(model, createDefaultModel());

    if (props.operateType === 'edit' && props.rowData) {
        Object.assign(model, {
            itemName: props.rowData.itemName,
            description: props.rowData.description || '',
            imageURL: props.rowData.imageURL || '',
            price: props.rowData.price,
            quantity: props.rowData.quantity,
            store_id: props.rowData.store_id
        });
    }
}

function closeDrawer() {
    visible.value = false;
}

async function handleSubmit() {
    await validate();

    try {
        if (props.operateType === 'add') {
            await addItem({
                itemName: model.itemName,
                description: model.description || null,
                imageURL: model.imageURL || null,
                price: model.price,
                quantity: model.quantity,
                store_id: model.store_id
            });
            window.$message?.success('添加成功');
        } else if (props.rowData) {
            await updateItem(props.rowData.id, {
                itemName: model.itemName,
                description: model.description || null,
                imageURL: model.imageURL || null,
                price: model.price,
                quantity: model.quantity,
                store_id: model.store_id
            });
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
            <ElFormItem label="餐点名称" prop="itemName">
                <ElInput v-model="model.itemName" placeholder="请输入餐点名称" />
            </ElFormItem>
            <ElFormItem label="价格 (¥)" prop="price">
                <ElInputNumber v-model="model.price" :min="0" :precision="2" :step="0.5" placeholder="请输入价格"
                    class="w-full" />
            </ElFormItem>
            <ElFormItem label="库存数量" prop="quantity">
                <ElInputNumber v-model="model.quantity" :min="0" :step="1" placeholder="请输入库存数量" class="w-full" />
            </ElFormItem>
            <ElFormItem label="所属商家ID" prop="store_id">
                <ElInputNumber v-model="model.store_id" :min="1" :step="1" placeholder="请输入商家ID" class="w-full" />
            </ElFormItem>
            <ElFormItem label="描述" prop="description">
                <ElInput v-model="model.description" type="textarea" :rows="3" placeholder="请输入餐点描述(可选)" />
            </ElFormItem>
            <ElFormItem label="图片URL" prop="imageURL">
                <ElInput v-model="model.imageURL" placeholder="请输入图片URL(可选)" />
            </ElFormItem>
        </ElForm>
        <template #footer>
            <div class="flex justify-end gap-12px">
                <ElButton @click="closeDrawer">取消</ElButton>
                <ElButton type="primary" @click="handleSubmit">确认</ElButton>
            </div>
        </template>
    </ElDrawer>
</template>
