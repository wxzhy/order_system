declare namespace Api {
  /**
   * namespace SystemManage
   *
   * backend api module: "systemManage"
   */
  namespace SystemManage {
    type CommonSearchParams = Pick<Common.PaginatingCommonParams, 'current' | 'size'>;

    /** role */
    type Role = Common.CommonRecord<{
      /** role name */
      roleName: string;
      /** role code */
      roleCode: string;
      /** role description */
      roleDesc: string;
    }>;

    /** role search params */
    type RoleSearchParams = CommonType.RecordNullable<
      Pick<Api.SystemManage.Role, 'roleName' | 'roleCode' | 'status'> & CommonSearchParams
    >;

    /** role list */
    type RoleList = Common.PaginatingQueryRecord<Role>;

    /** all role */
    type AllRole = Pick<Role, 'id' | 'roleName' | 'roleCode'>;

    /**
     * user type
     *
     * - "customer": customer
     * - "vendor": vendor
     * - "admin": admin
     */
    type UserType = 'customer' | 'vendor' | 'admin';

    /** user */
    type User = {
      id: number;
      username: string;
      email: string;
      phone: string | null;
      user_type: UserType;
      create_time: string;
    };

    /** user search params */
    type UserSearchParams = {
      skip?: number;
      limit?: number;
      user_type?: string;
      search?: string;
    };

    /** user list - matches backend PageResponse */
    type UserList = {
      records: User[];
      total: number;
      current: number;
      size: number;
    };

    /**
     * store state
     *
     * - "pending": pending review
     * - "approved": approved
     * - "rejected": rejected
     */
    type StoreState = 'pending' | 'approved' | 'rejected';

    /** store */
    type Store = {
      id: number;
      storeName: string;
      description: string | null;
      address: string;
      phone: string;
      hours: string | null;
      imageURL: string | null;
      state: StoreState;
      publish_time: string;
      review_time: string | null;
      owner_id: number;
    };

    /** store search params */
    type StoreSearchParams = {
      skip?: number;
      limit?: number;
      state?: string;
      search?: string;
    };

    /** store list - matches backend PageResponse */
    type StoreList = {
      records: Store[];
      total: number;
      current: number;
      size: number;
    };

    /**
     * menu type
     *
     * - "1": directory
     * - "2": menu
     */
    type MenuType = '1' | '2';

    type MenuButton = {
      /**
       * button code
       *
       * it can be used to control the button permission
       */
      code: string;
      /** button description */
      desc: string;
    };

    /**
     * icon type
     *
     * - "1": iconify icon
     * - "2": local icon
     */
    type IconType = '1' | '2';

    type MenuPropsOfRoute = Pick<
      import('vue-router').RouteMeta,
      | 'i18nKey'
      | 'keepAlive'
      | 'constant'
      | 'order'
      | 'href'
      | 'hideInMenu'
      | 'activeMenu'
      | 'multiTab'
      | 'fixedIndexInTab'
      | 'query'
    >;

    type Menu = Common.CommonRecord<{
      /** parent menu id */
      parentId: number;
      /** menu type */
      menuType: MenuType;
      /** menu name */
      menuName: string;
      /** route name */
      routeName: string;
      /** route path */
      routePath: string;
      /** component */
      component?: string;
      /** iconify icon name or local icon name */
      icon: string;
      /** icon type */
      iconType: IconType;
      /** buttons */
      buttons?: MenuButton[] | null;
      /** children menu */
      children?: Menu[] | null;
    }> &
      MenuPropsOfRoute;

    /** menu list */
    type MenuList = Common.PaginatingQueryRecord<Menu>;

    type MenuTree = {
      id: number;
      label: string;
      pId: number;
      children?: MenuTree[];
    };

    /** item - 餐点 */
    type Item = {
      id: number;
      itemName: string;
      description: string | null;
      imageURL: string | null;
      price: number;
      quantity: number;
      store_id: number;
    };

    /** item edit params */
    type ItemEdit = Pick<Item, 'itemName' | 'description' | 'imageURL' | 'price' | 'quantity' | 'store_id'>;

    /** item search params */
    type ItemSearchParams = {
      skip?: number;
      limit?: number;
      store_id?: number;
      search?: string;
      min_price?: number;
      max_price?: number;
      in_stock?: boolean;
    };

    /** item list */
    type ItemList = {
      records: Item[];
      total: number;
      current: number;
      size: number;
    };

    /** batch delete response */
    type BatchDeleteResponse = {
      success_count: number;
      failed_count: number;
      failed_ids: number[];
      message: string;
    };

    /**
     * order state
     *
     * - "pending": 待审核
     * - "approved": 已同意
     * - "completed": 已完成
     * - "cancelled": 已取消
     */
    type OrderState = 'pending' | 'approved' | 'completed' | 'cancelled';

    /** order item - 订单餐点项 */
    type OrderItem = {
      id: number;
      quantity: number;
      item_price: number;
      item_id: number;
    };

    /** order - 订单 */
    type Order = {
      id: number;
      create_time: string;
      review_time: string | null;
      state: OrderState;
      user_id: number;
      store_id: number;
      items: OrderItem[];
      total_amount?: number;
    };

    /** order update params */
    type OrderUpdate = {
      state?: OrderState;
    };

    /** order search params */
    type OrderSearchParams = {
      skip?: number;
      limit?: number;
      state?: OrderState | string;
      search?: string;
      store_id?: number;
      user_id?: number;
    };

    /** order list */
    type OrderList = {
      records: Order[];
      total: number;
      current: number;
      size: number;
    };

    /**
     * comment state
     *
     * - "pending": 未审核
     * - "approved": 审核通过
     * - "rejected": 审核未通过
     */
    type CommentState = 'pending' | 'approved' | 'rejected';

    /** comment - 评论 */
    type Comment = {
      id: number;
      content: string;
      publish_time: string;
      review_time: string | null;
      state: CommentState;
      user_id: number;
      store_id: number;
    };

    /** comment update params */
    type CommentUpdate = {
      content?: string;
      state?: CommentState;
    };

    /** comment search params */
    type CommentSearchParams = {
      skip?: number;
      limit?: number;
      state?: CommentState | string;
      search?: string;
      store_id?: number;
      user_id?: number;
    };

    /** comment list */
    type CommentList = {
      records: Comment[];
      total: number;
      current: number;
      size: number;
    };
  }
}
