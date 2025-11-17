import { computed, ref } from 'vue';
import { fetchVendorStoreStatus } from '@/service/api';
import type { VendorStoreStatus } from '@/service/api/store';

export function useVendorStoreStatus(loadImmediate = true) {
  const status = ref<VendorStoreStatus | null>(null);
  const loading = ref(false);
  const errorMessage = ref<string | null>(null);
  const errorStatus = ref<number | null>(null);

  async function loadStatus() {
    loading.value = true;
    errorMessage.value = null;
    errorStatus.value = null;

    try {
      const response = await fetchVendorStoreStatus();
      status.value = response;
    } catch (error: any) {
      const responseStatus = error?.response?.status ?? error?.status ?? null;
      errorStatus.value = typeof responseStatus === 'number' ? responseStatus : null;
      errorMessage.value = error?.message || '无法获取商家信息状态';

      if (errorStatus.value === 403) {
        status.value = {
          exists: false,
          state: null,
          can_manage: false,
          store: null
        };
      } else {
        status.value = null;
      }
    } finally {
      loading.value = false;
    }
  }

  if (loadImmediate) {
    loadStatus();
  }

  const exists = computed(() => Boolean(status.value?.exists));
  const state = computed(() => status.value?.state ?? null);
  const canManage = computed(() => Boolean(status.value?.can_manage));
  const store = computed(() => status.value?.store ?? null);
  const forbidden = computed(() => errorStatus.value === 403);

  return {
    status,
    loading,
    errorMessage,
    errorStatus,
    exists,
    state,
    canManage,
    store,
    forbidden,
    loadStatus
  };
}
