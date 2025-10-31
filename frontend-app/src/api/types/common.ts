/**
 * 分页响应
 */
export interface PageResponse<T> {
    records: T[]
    total: number
    current: number
    size: number
}
