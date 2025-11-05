import { alova } from '../request';

export type StoreModel = {
    storeName?: string;
    description?: string;
    address?: string;
    phone?: string;
    hours?: string;
    imageURL?: string;
    state?: string;
};

export type StoreSearchParams = {
    skip?: number;
    limit?: number;
    state?: string;
    name?: string;
    owner_name?: string;
    address?: string;
    phone?: string;
};

export type VendorStoreStatus = {
    exists: boolean;
    state?: Api.SystemManage.StoreState | null;
    can_manage: boolean;
    store?: Api.SystemManage.Store | null;
};

/** get store list */
export function fetchGetStoreList(params?: StoreSearchParams) {
    return alova.Get<Api.SystemManage.StoreList>('/store', {
        params,
        cacheFor: 0 // 禁用缓存，确保刷新按钮能够获取最新数据
    });
}

/** add store - 管理员功能 */
export function addStore(data: StoreModel) {
    return alova.Post<Api.SystemManage.Store>('/store', data);
}

export function fetchMyStore() {
    return alova.Get<Api.SystemManage.Store>('/store/my');
}

export function fetchVendorStoreStatus() {
    return alova.Get<VendorStoreStatus>('/store/my/status');
}

export function updateMyStore(data: StoreModel) {
    return alova.Put<Api.SystemManage.Store>('/store/my', data);
}


/** update store */
export function updateStore(id: number, data: StoreModel) {
    return alova.Put<Api.SystemManage.Store>(`/store/${id}`, data);
}

/** delete store */
export function deleteStore(id: number) {
    return alova.Delete<null>(`/store/${id}`);
}

/** batch delete store */
export function batchDeleteStore(ids: number[]) {
    return alova.Post<{ success_count: number; failed_count: number; failed_ids: number[]; message: string }>(
        '/store/batch-delete',
        { ids }
    );
}

/** review store - 管理员审核 */
export function reviewStore(id: number, data: { state: string; review_comment?: string }) {
    return alova.Post<Api.SystemManage.Store>(`/store/${id}/review`, data);
}
