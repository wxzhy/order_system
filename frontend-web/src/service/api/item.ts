import { alova } from '../request';

/**
 * 获取餐点列表
 *
 * @param params - 搜索参数
 */
export function fetchGetItemList(params?: Api.SystemManage.ItemSearchParams) {
    return alova.Get<Api.SystemManage.ItemList>('/item/', { params });
}

/**
 * 添加餐点
 *
 * @param data - 餐点数据
 */
export function addItem(data: Api.SystemManage.ItemEdit) {
    return alova.Post<Api.SystemManage.Item>('/item/', data);
}

/**
 * 更新餐点
 *
 * @param id - 餐点ID
 * @param data - 餐点数据
 */
export function updateItem(id: number, data: Api.SystemManage.ItemEdit) {
    return alova.Put<Api.SystemManage.Item>(`/item/${id}/`, data);
}

/**
 * 删除餐点
 *
 * @param id - 餐点ID
 */
export function deleteItem(id: number) {
    return alova.Delete(`/item/${id}/`);
}

/**
 * 批量删除餐点
 *
 * @param ids - 餐点ID列表
 */
export function batchDeleteItem(ids: number[]) {
    return alova.Post<Api.SystemManage.BatchDeleteResponse>('/item/batch-delete/', { ids });
}
