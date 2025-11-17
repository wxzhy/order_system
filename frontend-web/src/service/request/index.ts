import { createAlovaRequest } from '@sa/alova';
<<<<<<< HEAD
import { createAlovaMockAdapter } from '@sa/alova/mock';
=======
>>>>>>> HEAD@{1}
import adapterFetch from '@sa/alova/fetch';
import { useAuthStore } from '@/store/modules/auth';
import { getServiceBaseURL } from '@/utils/service';
import { $t } from '@/locales';
<<<<<<< HEAD
import featureUsers20241014 from '../mocks/feature-users-20241014';
=======
>>>>>>> HEAD@{1}
import { getAuthorization, handleRefreshToken, showErrorMsg } from './shared';
import type { RequestInstanceState } from './type';

const isHttpProxy = import.meta.env.DEV && import.meta.env.VITE_HTTP_PROXY === 'Y';
const { baseURL } = getServiceBaseURL(import.meta.env, isHttpProxy);

const state: RequestInstanceState = {
  errMsgStack: []
};
<<<<<<< HEAD
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
=======

export const alova = createAlovaRequest(
  {
    baseURL,
    requestAdapter: adapterFetch()
>>>>>>> HEAD@{1}
  },
  {
    onRequest({ config }) {
      const Authorization = getAuthorization();
      config.headers.Authorization = Authorization;
<<<<<<< HEAD
      config.headers.apifoxToken = 'XL299LiMEDZ0H5h3A29PxwQXdMJqWyY2';
=======
>>>>>>> HEAD@{1}
    },
    tokenRefresher: {
      async isExpired(response) {
        if (response.url?.includes('/auth/login')) {
          return false;
        }

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
      let isLoginRequest = false;

      if (response) {
        statusCode = response.status;
        isLoginRequest = response.url?.includes('/auth/login') ?? false;
        try {
          const data = await response?.clone().json();
          // FastAPI returns error message in 'detail' field
          message = data.detail || error.message;
        } catch {
          // If response is not JSON, use default error message
          message = error.message;
        }
      }

      function handleUnauthorized() {
        showErrorMsg(state, message);
        authStore.resetStore();
      }

      // HTTP 401 means unauthorized, logout user
      if (statusCode === 401) {
        if (isLoginRequest) {
          showErrorMsg(state, message);
          throw error;
        }

        handleUnauthorized();
        throw error;
      }

      // HTTP 403 means forbidden, only show error message and allow caller to handle
      if (statusCode === 403) {
        showErrorMsg(state, message);
        throw error;
      }
      showErrorMsg(state, message);
      throw error;
    }
  }
);
