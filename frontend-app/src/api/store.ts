import type { PageResponse } from './types/common'
import { http } from '@/http/http'

/**
 * 餐厅信息
 */
export interface IStore {
    id: number
    storeName: string
    description?: string
    address: string
    phone: string
    hours?: string
    imageURL?: string
    state: string
    publish_time: string
    review_time?: string
    owner_id: number
    owner_name?: string
}

/**
 * 查询餐厅列表参数
 */
export interface IStoreListParams {
    skip?: number
    limit?: number
    state?: string
    name?: string
    owner_name?: string
    address?: string
    phone?: string
    owner_id?: number
}

/**
 * 获取餐厅列表
 * @param params 查询参数
 */
export function getStoreList(params?: IStoreListParams) {
    return http.get<PageResponse<IStore>>('/store/', params)
}

/**
 * 获取餐厅详情
 * @param id 餐厅ID
 */
export function getStoreDetail(id: number) {
    return http.get<IStore>(`/store/${id}`)
}
