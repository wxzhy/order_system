import type { PageResponse } from './types/common'
import { http } from '@/http/http'

/**
 * 餐点信息
 */
export interface IItem {
  id: number
  itemName: string
  description?: string
  imageURL?: string
  price: number
  quantity: number
  store_id: number
  store_name?: string
}

/**
 * 餐点列表查询参数
 */
export interface IItemListParams {
  skip?: number
  limit?: number
  store_id?: number
  store_name?: string
  item_name?: string
  description?: string
  min_price?: number
  max_price?: number
  in_stock?: boolean
}

/**
 * 获取餐点列表
 */
export function getItemList(params: IItemListParams) {
  return http<PageResponse<IItem>>({
    url: '/item/',
    method: 'GET',
    query: params,
  })
}

/**
 * 获取餐点详情
 */
export function getItemDetail(id: number) {
  return http<IItem>({
    url: `/item/${id}`,
    method: 'GET',
  })
}
