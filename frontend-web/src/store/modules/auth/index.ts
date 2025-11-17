import { computed, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';
import { defineStore } from 'pinia';
import { useLoading } from '@sa/hooks';
import { fetchEmailCodeLogin, fetchGetUserInfo, fetchLogin, fetchVendorStoreStatus } from '@/service/api';
import type { VendorStoreStatus } from '@/service/api/store';
import { alova } from '@/service/request';
import { useRouterPush } from '@/hooks/common/router';
import { localStg } from '@/utils/storage';
import { SetupStoreId } from '@/enum';
import { $t } from '@/locales';
import { useRouteStore } from '../route';
import { useTabStore } from '../tab';
import { clearAuthStorage, getToken } from './shared';

export const useAuthStore = defineStore(SetupStoreId.Auth, () => {
  const route = useRoute();
  const authStore = useAuthStore();
  const routeStore = useRouteStore();
  const tabStore = useTabStore();
  const { toLogin, redirectFromLogin } = useRouterPush(false);
  const { loading: loginLoading, startLoading, endLoading } = useLoading();

  const token = ref(getToken());

  const userInfo: Api.Auth.UserInfo = reactive({
    id: 0,
    username: '',
    email: '',
    phone: '',
    user_type: 'customer',
    create_time: ''
  });
  const vendorStoreStatus = ref<VendorStoreStatus | null>(null);

  /** is super role in static route */
  const isStaticSuper = computed(() => {
    const { VITE_AUTH_ROUTE_MODE, VITE_STATIC_SUPER_ROLE } = import.meta.env;

    return VITE_AUTH_ROUTE_MODE === 'static' && userInfo.user_type === VITE_STATIC_SUPER_ROLE;
  });

  /** Is login */
  const isLogin = computed(() => Boolean(token.value));

  function clearAlovaCache() {
    try {
      alova.l1Cache?.clear?.();
    } catch (error) {
      /* noop */
    }
    try {
      alova.l2Cache?.clear?.();
    } catch (error) {
      /* noop */
    }
  }

  /** Reset auth store */
  async function resetStore() {
    recordUserId();

    // Clear auth credentials and alova caches to avoid stale validation errors
    clearAuthStorage();
    clearAlovaCache();
    vendorStoreStatus.value = null;

    // 清除路由状态
    routeStore.resetStore();

    // 清除标签页缓存和状态
    await tabStore.clearTabs();
    localStg.remove('globalTabs');

    // 重置 auth store 状态
    authStore.$reset();

    // 跳转到登录页
    if (!route.meta.constant) {
      await toLogin();
    }
  }

  /** Record the user ID of the previous login session Used to compare with the current user ID on next login */
  function recordUserId() {
    if (!userInfo.id) {
      return;
    }

    // Store current user ID locally for next login comparison
    localStg.set('lastLoginUserId', String(userInfo.id));
  }

  /**
   * Check if current login user is different from previous login user. If different, clear all tabs.
   *
   * @returns {boolean} Whether to clear all tabs
   */
  function checkTabClear(): boolean {
    if (!userInfo.id) {
      return false;
    }

    const lastLoginUserId = localStg.get('lastLoginUserId');

    if (lastLoginUserId !== String(userInfo.id)) {
      // When switching accounts only clear tab cache to keep other local data intact
      localStg.remove('globalTabs');
      tabStore.clearTabs();

      return true;
    }

    return false;
  }

  async function handlePostLogin(redirect: boolean) {
    const isClear = checkTabClear();
    let needRedirect = redirect;

    if (isClear) {
      needRedirect = false;
    }

    await redirectFromLogin(needRedirect);

    window.$notification?.success({
      title: $t('page.login.common.loginSuccess'),
      message: $t('page.login.common.welcomeBack', { userName: userInfo.username }),
      duration: 4500
    });
  }

  /**
   * Login
   *
   * @param userName User name
   * @param password Password
   * @param [redirect=true] Whether to redirect after login. Default is `true`
   */
  async function login(userName: string, password: string, redirect = true) {
    startLoading();

    try {
      const loginToken = await fetchLogin(userName, password);

      if (loginToken) {
        const pass = await loginByToken(loginToken);

        if (pass) {
          await handlePostLogin(redirect);
        }
      } else {
        resetStore();
      }
    } finally {
      endLoading();
    }
  }

  async function loginWithEmailCode(email: string, code: string, redirect = true) {
    startLoading();

    try {
      const loginToken = await fetchEmailCodeLogin(email, code);

      if (loginToken) {
        const pass = await loginByToken(loginToken);

        if (pass) {
          await handlePostLogin(redirect);
        }
      } else {
        resetStore();
      }
    } finally {
      endLoading();
    }
  }

  async function loginByToken(loginToken: Api.Auth.LoginToken) {
    // 1. stored in the localStorage, the later requests need it in headers
    localStg.set('token', loginToken.access_token);
    localStg.set('refreshToken', loginToken.refresh_token);

    // 2. 清除用户信息的 API 缓存，确保获取最新的用户数据
    // 使用 l2Cache.remove 来清除特定 API 的缓存，而不是清除整个 localStorage
    const getUserInfoMethod = fetchGetUserInfo();
    try {
      // 使用 method 的 key 来移除缓存
      alova.l2Cache?.remove(getUserInfoMethod.key);
    } catch (error) {
      // 如果移除失败，忽略错误继续执行
    }

    // 3. get user info
    const pass = await getUserInfo();

    if (pass) {
      token.value = loginToken.access_token;
      if (userInfo.user_type === 'vendor') {
        await refreshVendorStoreStatus(true);
      } else {
        vendorStoreStatus.value = null;
      }

      return true;
    }

    return false;
  }

  async function getUserInfo() {
    const info = await fetchGetUserInfo();

    if (info) {
      // update store
      Object.assign(userInfo, info);

      return true;
    }

    return false;
  }

  async function initUserInfo() {
    const hasToken = getToken();

    if (hasToken) {
      const pass = await getUserInfo();

      if (!pass) {
        resetStore();
      } else if (userInfo.user_type === 'vendor') {
        await refreshVendorStoreStatus(true);
      } else {
        vendorStoreStatus.value = null;
      }
    }
  }

  async function refreshVendorStoreStatus(force = false) {
    if (userInfo.user_type !== 'vendor') {
      vendorStoreStatus.value = null;
      return;
    }

    if (!force && vendorStoreStatus.value) {
      return;
    }

    try {
      vendorStoreStatus.value = await fetchVendorStoreStatus();
    } catch {
      vendorStoreStatus.value = null;
    }
  }

  const hasVendorStore = computed(() => Boolean(vendorStoreStatus.value?.exists));
  const canManageVendorStore = computed(() => Boolean(vendorStoreStatus.value?.can_manage));

  return {
    token,
    userInfo,
    isStaticSuper,
    isLogin,
    loginLoading,
    resetStore,
    login,
    loginWithEmailCode,
    initUserInfo,
    refreshVendorStoreStatus,
    vendorStoreStatus,
    hasVendorStore,
    canManageVendorStore
  };
});
