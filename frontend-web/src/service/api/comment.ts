import { alova } from '../request';

/**
 * 获取评论列表
 *
 * @param params - 搜索参数
 */
export function fetchGetCommentList(params?: Api.SystemManage.CommentSearchParams) {
    return alova.Get<Api.SystemManage.CommentList>('/comment/', { params });
}

/**
 * 获取评论详情
 *
 * @param id - 评论ID
 */
export function getComment(id: number) {
    return alova.Get<Api.SystemManage.Comment>(`/comment/${id}/`);
}

/**
 * 更新评论
 *
 * @param id - 评论ID
 * @param data - 评论数据
 */
export function updateComment(id: number, data: Api.SystemManage.CommentUpdate) {
    return alova.Put<Api.SystemManage.Comment>(`/comment/${id}/`, data);
}

/**
 * 删除评论
 *
 * @param id - 评论ID
 */
export function deleteComment(id: number) {
    return alova.Delete(`/comment/${id}/`);
}

/**
 * 批量删除评论
 *
 * @param ids - 评论ID列表
 */
export function batchDeleteComment(ids: number[]) {
    return alova.Post<Api.SystemManage.BatchDeleteResponse>('/comment/batch-delete/', { ids });
}

/**
 * 审核评论
 *
 * @param id - 评论ID
 * @param approved - 是否通过
 */
export function reviewComment(id: number, approved: boolean) {
    return alova.Post<Api.SystemManage.Comment>(`/comment/${id}/review/`, { approved });
}
