import type { IItem } from './item'
import { http } from '@/http/http'

/**
 * 订单项
 */
export interface IOrderItem {
  id: number
  item_id: number
  item_name?: string
  quantity: number
  item_price: number
  item?: IItem
}

/**
 * 订单信息
 */
export interface IOrder {
  id: number
  create_time: string
  review_time?: string
  state: string
  user_id: number
  user_name?: string
  store_id: number
  store_name?: string
  items: IOrderItem[]
  total_amount?: number
}

/**
 * 创建订单项
 */
export interface IOrderItemCreate {
  item_id: number
  quantity: number
}

/**
 * 创建订单
 */
export interface IOrderCreate {
  store_id: number
  items: IOrderItemCreate[]
  contact_phone?: string
  pickup_time?: string
}

/**
 * 创建订单
 */
export function createOrder(data: IOrderCreate) {
  return http<IOrder>({
    url: '/order/',
    method: 'POST',
    data,
  })
}

/**
 * 获取订单列表
 */
export function getOrderList(params?: { skip?: number, limit?: number }) {
  return http<{ records: IOrder[], total: number }>({
    url: '/order/',
    method: 'GET',
    query: params,
  })
}

/**
 * 获取订单详情
 */
export function getOrderDetail(id: number) {
  return http<IOrder>({
    url: `/order/${id}`,
    method: 'GET',
  })
}
