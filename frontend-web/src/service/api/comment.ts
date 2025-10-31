import { alova } from '../request';

/**
/** get comment list */
export function fetchGetCommentList(params?: CommentSearchParams) {
  return alova.Get<Api.SystemManage.CommentList>('/comment', {
    params,
    cacheFor: 0 // 禁用缓存，确保刷新按钮能够获取最新数据
  });
}

/**
 * 获取评论详情
 *
 * @param id - 评论ID
 */
export function getComment(id: number) {
  return alova.Get<Api.SystemManage.Comment>(`/comment/${id}`);
}

/**
 * 更新评论
 *
 * @param id - 评论ID
 * @param data - 评论数据
 */
export function updateComment(id: number, data: Api.SystemManage.CommentUpdate) {
  return alova.Put<Api.SystemManage.Comment>(`/comment/${id}`, data);
}

/**
 * 删除评论
 *
 * @param id - 评论ID
 */
export function deleteComment(id: number) {
  return alova.Delete(`/comment/${id}`);
}

/**
 * 批量删除评论
 *
 * @param ids - 评论ID列表
 */
export function batchDeleteComment(ids: number[]) {
  return alova.Post<Api.SystemManage.BatchDeleteResponse>('/comment/batch-delete', { ids });
}

/**
 * 审核评论
 *
 * @param id - 评论ID
 * @param state - 审核状态: 'approved' | 'rejected'
 */
export function reviewComment(id: number, state: 'approved' | 'rejected') {
  return alova.Post<Api.SystemManage.Comment>(`/comment/${id}/review`, { state });
}
