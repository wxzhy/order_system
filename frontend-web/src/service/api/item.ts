import { alova } from '../request';

/**
/** get item list */
export function fetchGetItemList(params?: ItemSearchParams) {
  return alova.Get<Api.SystemManage.ItemList>('/item', {
    params,
    cacheFor: 0 // 禁用缓存，确保刷新按钮能够获取最新数据
  });
}

/**
 * 添加餐点
 *
 * @param data - 餐点数据
 */
export function addItem(data: Api.SystemManage.ItemEdit) {
  return alova.Post<Api.SystemManage.Item>('/item', data);
}

/**
 * 更新餐点
 *
 * @param id - 餐点ID
 * @param data - 餐点数据
 */
export function updateItem(id: number, data: Api.SystemManage.ItemEdit) {
  return alova.Put<Api.SystemManage.Item>(`/item/${id}`, data);
}

/**
 * 删除餐点
 *
 * @param id - 餐点ID
 */
export function deleteItem(id: number) {
  return alova.Delete(`/item/${id}`);
}

/**
 * 批量删除餐点
 *
 * @param ids - 餐点ID列表
 */
export function batchDeleteItem(ids: number[]) {
  return alova.Post<Api.SystemManage.BatchDeleteResponse>('/item/batch-delete', { ids });
}
