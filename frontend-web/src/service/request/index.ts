import { createAlovaRequest } from '@sa/alova';
import { createAlovaMockAdapter } from '@sa/alova/mock';
import adapterFetch from '@sa/alova/fetch';
import { useAuthStore } from '@/store/modules/auth';
import { getServiceBaseURL } from '@/utils/service';
import { $t } from '@/locales';
import featureUsers20241014 from '../mocks/feature-users-20241014';
import { getAuthorization, handleRefreshToken, showErrorMsg } from './shared';
import type { RequestInstanceState } from './type';

const isHttpProxy = import.meta.env.DEV && import.meta.env.VITE_HTTP_PROXY === 'Y';
const { baseURL } = getServiceBaseURL(import.meta.env, isHttpProxy);

const state: RequestInstanceState = {
  errMsgStack: []
};
const mockAdapter = createAlovaMockAdapter([featureUsers20241014], {
  // using requestAdapter if not match mock request
  httpAdapter: adapterFetch(),

  // response delay time
  delay: 1000,

  // global mock toggle
  enable: true,
  matchMode: 'methodurl'
});
export const alova = createAlovaRequest(
  {
    baseURL,
    requestAdapter: import.meta.env.DEV ? mockAdapter : adapterFetch()
  },
  {
    onRequest({ config }) {
      const Authorization = getAuthorization();
      config.headers.Authorization = Authorization;
      config.headers.apifoxToken = 'XL299LiMEDZ0H5h3A29PxwQXdMJqWyY2';
    },
    tokenRefresher: {
      async isExpired(response) {
        // Check if response status is 401 (Unauthorized)
        return response.status === 401;
      },
      async handler() {
        await handleRefreshToken();
      }
    },
    async isBackendSuccess(response) {
      // FastAPI uses standard HTTP status codes
      // Success is indicated by 2xx status codes, which are already handled by the request adapter
      return response.status >= 200 && response.status < 300;
    },
    async transformBackendResponse(response) {
      // FastAPI returns data directly, not wrapped in a { data: ... } structure
      return await response.clone().json();
    },
    async onError(error, response) {
      const authStore = useAuthStore();

      let message = error.message;
      let statusCode = 0;

      if (response) {
        statusCode = response.status;
        try {
          const data = await response?.clone().json();
          // FastAPI returns error message in 'detail' field
          message = data.detail || error.message;
        } catch {
          // If response is not JSON, use default error message
          message = error.message;
        }
      }

      function handleLogout() {
        showErrorMsg(state, message);
        authStore.resetStore();
      }

      function logoutAndCleanup() {
        handleLogout();
        window.removeEventListener('beforeunload', handleLogout);
        state.errMsgStack = state.errMsgStack.filter(msg => msg !== message);
      }

      // HTTP 401 means unauthorized, logout user
      if (statusCode === 401) {
        handleLogout();
        throw error;
      }

      // HTTP 403 means forbidden, show modal and logout
      if (statusCode === 403 && !state.errMsgStack?.includes(message)) {
        state.errMsgStack = [...(state.errMsgStack || []), message];

        // prevent the user from refreshing the page
        window.addEventListener('beforeunload', handleLogout);

        if (window.$messageBox) {
          window.$messageBox({
            type: 'error',
            title: $t('common.error'),
            message,
            confirmButtonText: $t('common.confirm'),
            closeOnClickModal: false,
            closeOnPressEscape: false,
            callback() {
              logoutAndCleanup();
            }
          });
        }
        throw error;
      }
      showErrorMsg(state, message);
      throw error;
    }
  }
);
