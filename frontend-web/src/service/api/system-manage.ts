import { alova } from '../request';

/** get user list */
export function fetchGetUserList(params?: { skip?: number; limit?: number; user_type?: string; search?: string }) {
  return alova.Get<Api.SystemManage.UserList>('/user/', { params });
}

export type UserModel = {
  username?: string;
  email?: string;
  phone?: string;
  password?: string;
  user_type?: string;
};

/** add user - 管理员功能 (需要单独实现) */
export function addUser(data: UserModel) {
  return alova.Post<Api.Auth.UserInfo>('/user/', data);
}

/** update user */
export function updateUser(id: number, data: UserModel) {
  return alova.Put<Api.Auth.UserInfo>(`/user/${id}/`, data);
}

/** delete user */
export function deleteUser(id: number) {
  return alova.Delete<null>(`/user/${id}/`);
}

/** batch delete user */
export function batchDeleteUser(ids: number[]) {
  return alova.Post<{ success_count: number; failed_count: number; failed_ids: number[]; message: string }>(
    '/user/batch-delete/',
    { ids }
  );
}

/** reset user password - 管理员重置用户密码 */
export function resetUserPassword(id: number, newPassword: string = '123456') {
  return alova.Put<{ message: string }>(`/user/${id}/reset-password/`, undefined, {
    params: { new_password: newPassword }
  });
}

/** get role list */
export function fetchGetRoleList(params?: Api.SystemManage.RoleSearchParams) {
  return alova.Get<Api.SystemManage.RoleList>('/systemManage/getRoleList', { params });
}

/**
 * get all roles
 *
 * these roles are all enabled
 */
export function fetchGetAllRoles() {
  return alova.Get<Api.SystemManage.AllRole[]>('/systemManage/getAllRoles');
}

/** get menu list */
export function fetchGetMenuList() {
  return alova.Get<Api.SystemManage.MenuList>('/systemManage/getMenuList/v2');
}

/** get all pages */
export function fetchGetAllPages() {
  return alova.Get<string[]>('/systemManage/getAllPages');
}

/** get menu tree */
export function fetchGetMenuTree() {
  return alova.Get<Api.SystemManage.MenuTree[]>('/systemManage/getMenuTree');
}
