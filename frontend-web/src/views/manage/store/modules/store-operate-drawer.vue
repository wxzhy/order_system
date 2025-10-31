<script setup lang="ts">
import { computed, reactive, watch } from 'vue';
import type { FormInstance } from 'element-plus';
import { addStore, updateStore } from '@/service/api';
import { useFormRules } from '@/hooks/common/form';

defineOptions({
    name: 'StoreOperateDrawer'
});

interface Props {
    operateType: 'add' | 'edit';
    rowData?: Api.SystemManage.Store | null;
}

const props = defineProps<Props>();

interface Emits {
    (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
    default: false
});

const title = computed(() => (props.operateType === 'add' ? '新增商家' : '编辑商家'));

type Model = Pick<Api.SystemManage.Store, 'storeName' | 'description' | 'address' | 'phone' | 'hours' | 'imageURL'>;

const model: Model = reactive(createDefaultModel());

function createDefaultModel(): Model {
    return {
        storeName: '',
        description: '',
        address: '',
        phone: '',
        hours: '',
        imageURL: ''
    };
}

const { formRef, validate, restoreValidation } = useFormRules();
const { defaultRequiredRule } = useFormRules();

const rules = computed(() => {
    const baseRules: Record<string, App.Global.FormRule[]> = {
        storeName: [defaultRequiredRule],
        address: [defaultRequiredRule],
        phone: [defaultRequiredRule]
    };

    return baseRules;
});

function handleInitModel() {
    Object.assign(model, createDefaultModel());

    if (props.operateType === 'edit' && props.rowData) {
        Object.assign(model, {
            storeName: props.rowData.storeName,
            description: props.rowData.description || '',
            address: props.rowData.address,
            phone: props.rowData.phone,
            hours: props.rowData.hours || '',
            imageURL: props.rowData.imageURL || ''
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
            await addStore({
                storeName: model.storeName,
                description: model.description || undefined,
                address: model.address,
                phone: model.phone,
                hours: model.hours || undefined,
                imageURL: model.imageURL || undefined
            });
            window.$message?.success('添加成功');
        } else if (props.rowData) {
            await updateStore(props.rowData.id, {
                storeName: model.storeName,
                description: model.description || undefined,
                address: model.address,
                phone: model.phone,
                hours: model.hours || undefined,
                imageURL: model.imageURL || undefined
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
            <ElFormItem label="商家名称" prop="storeName">
                <ElInput v-model="model.storeName" placeholder="请输入商家名称" />
            </ElFormItem>
            <ElFormItem label="地址" prop="address">
                <ElInput v-model="model.address" placeholder="请输入地址" />
            </ElFormItem>
            <ElFormItem label="电话" prop="phone">
                <ElInput v-model="model.phone" placeholder="请输入电话" />
            </ElFormItem>
            <ElFormItem label="营业时间" prop="hours">
                <ElInput v-model="model.hours" placeholder="例如: 09:00-22:00" />
            </ElFormItem>
            <ElFormItem label="描述" prop="description">
                <ElInput v-model="model.description" type="textarea" :rows="3" placeholder="请输入商家描述" />
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
