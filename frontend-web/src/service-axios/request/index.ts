import type { AxiosResponse } from 'axios';
import { BACKEND_ERROR_CODE, createFlatRequest, createRequest } from '@sa/axios';
import { useAuthStore } from '@/store/modules/auth';
import { localStg } from '@/utils/storage';
import { getServiceBaseURL } from '@/utils/service';
import { $t } from '@/locales';
import { getAuthorization, handleExpiredRequest, showErrorMsg } from './shared';
import type { RequestInstanceState } from './type';

const isHttpProxy = import.meta.env.DEV && import.meta.env.VITE_HTTP_PROXY === 'Y';
const { baseURL, otherBaseURL } = getServiceBaseURL(import.meta.env, isHttpProxy);

export const request = createFlatRequest(
  {
    baseURL,
    headers: {
      apifoxToken: 'XL299LiMEDZ0H5h3A29PxwQXdMJqWyY2'
    }
  },
  {
    defaultState: {
      errMsgStack: [],
      refreshTokenPromise: null
    } as RequestInstanceState,
    transform(response: AxiosResponse<any>) {
      // FastAPI returns data directly, not wrapped in { data: ... } structure
      return response.data;
    },
    async onRequest(config) {
      const Authorization = getAuthorization();
      Object.assign(config.headers, { Authorization });

      return config;
    },
    isBackendSuccess(response) {
      // FastAPI uses HTTP status codes for success/failure
      // Success is determined by HTTP 2xx status codes (handled by validateStatus)
      return response.status >= 200 && response.status < 300;
    },
    async onBackendFail(response, instance) {
      const authStore = useAuthStore();
      const statusCode = response.status;

      function handleLogout() {
        authStore.resetStore();
      }

      function logoutAndCleanup() {
        handleLogout();
        window.removeEventListener('beforeunload', handleLogout);

        const errorMsg = response.data?.detail || '';
        request.state.errMsgStack = request.state.errMsgStack.filter(msg => msg !== errorMsg);
      }

      // HTTP 401 Unauthorized - logout user
      if (statusCode === 401) {
        handleLogout();
        return null;
      }

      // HTTP 403 Forbidden - show modal and logout
      const errorMsg = response.data?.detail || '';
      if (statusCode === 403 && !request.state.errMsgStack?.includes(errorMsg)) {
        request.state.errMsgStack = [...(request.state.errMsgStack || []), errorMsg];

        // prevent the user from refreshing the page
        window.addEventListener('beforeunload', handleLogout);

        window.$messageBox
          ?.confirm(errorMsg, $t('common.error'), {
            confirmButtonText: $t('common.confirm'),
            cancelButtonText: $t('common.cancel'),
            type: 'error',
            closeOnClickModal: false,
            closeOnPressEscape: false
          })
          .then(() => {
            logoutAndCleanup();
          });

        return null;
      }

      // Handle token expiration (401) and refresh
      if (statusCode === 401) {
        const success = await handleExpiredRequest(request.state);
        if (success) {
          const Authorization = getAuthorization();
          Object.assign(response.config.headers, { Authorization });

          return instance.request(response.config) as Promise<AxiosResponse>;
        }
      }

      return null;
    },
    onError(error) {
      // when the request is fail, you can show error message

      let message = error.message;
      let statusCode = 0;

      // get backend error message from FastAPI's detail field
      if (error.code === BACKEND_ERROR_CODE && error.response) {
        statusCode = error.response.status;
        message = error.response?.data?.detail || message;
      }

      // the error message is displayed in the modal (HTTP 403)
      if (statusCode === 403) {
        return;
      }

      // when the token is expired (HTTP 401), refresh token and retry request, so no need to show error message
      if (statusCode === 401) {
        return;
      }

      showErrorMsg(request.state, message);
    }
  }
);

export const demoRequest = createRequest(
  {
    baseURL: otherBaseURL.demo
  },
  {
    transform(response: AxiosResponse<App.Service.DemoResponse>) {
      return response.data.result;
    },
    async onRequest(config) {
      const { headers } = config;

      // set token
      const token = localStg.get('token');
      const Authorization = token ? `Bearer ${token}` : null;
      Object.assign(headers, { Authorization });

      return config;
    },
    isBackendSuccess(response) {
      // when the backend response code is "200", it means the request is success
      // you can change this logic by yourself
      return response.data.status === '200';
    },
    async onBackendFail(_response) {
      // when the backend response code is not "200", it means the request is fail
      // for example: the token is expired, refresh token and retry request
    },
    onError(error) {
      // when the request is fail, you can show error message

      let message = error.message;

      // show backend error message
      if (error.code === BACKEND_ERROR_CODE) {
        message = error.response?.data?.message || message;
      }

      window.$message?.error(message);
    }
  }
);
