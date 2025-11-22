import type { PageResponse } from './types/common'
import { http } from '@/http/http'

/**
 * 评论信息
 */
export interface IComment {
  id: number
  content: string
  publish_time: string
  review_time?: string
  state: string
  user_id: number
  user_name?: string
  store_id: number
  store_name?: string
}

/**
 * 创建评论
 */
export interface ICommentCreate {
  content: string
  store_id: number
}

/**
 * 评论列表查询参数
 */
export interface ICommentListParams {
  skip?: number
  limit?: number
  store_id?: number
  state?: string
}

/**
 * 获取评论列表
 */
export function getCommentList(params: ICommentListParams) {
  return http<PageResponse<IComment>>({
    url: '/comment/',
    method: 'GET',
    query: params,
  })
}

/**
 * 创建评论
 */
export function createComment(data: ICommentCreate) {
  return http<IComment>({
    url: '/comment/',
    method: 'POST',
    data,
  })
}

/**
 * 删除评论
 */
export function deleteComment(id: number) {
  return http<{ message: string }>({
    url: `/comment/${id}`,
    method: 'DELETE',
  })
}
