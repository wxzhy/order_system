import { alova } from '../request';

/**
 * 获取订单列表
 *
 * @param params - 搜索参数
 */
export function fetchGetOrderList(params?: Api.SystemManage.OrderSearchParams) {
    return alova.Get<Api.SystemManage.OrderList>('/order', {
        params,
        cacheFor: 0 // 禁用缓存，确保刷新按钮能够获取最新数据
    });
}

/**
 * 获取订单详情
 *
 * @param id - 订单ID
 */
export function getOrder(id: number) {
    return alova.Get<Api.SystemManage.Order>(`/order/${id}`);
}

/**
 * 更新订单状态
 *
 * @param id - 订单ID
 * @param data - 订单数据
 */
export function updateOrder(id: number, data: Api.SystemManage.OrderUpdate) {
    return alova.Put<Api.SystemManage.Order>(`/order/${id}`, data);
}

/**
 * 删除订单
 *
 * @param id - 订单ID
 */
export function deleteOrder(id: number) {
    return alova.Delete(`/order/${id}`);
}

/**
 * 批量删除订单
 *
 * @param ids - 订单ID列表
 */
export function batchDeleteOrder(ids: number[]) {
    return alova.Post<Api.SystemManage.BatchDeleteResponse>('/order/batch-delete', { ids });
}
