<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useAppStore } from '@/store/modules/app';
import { useAuthStore } from '@/store/modules/auth';
import { fetchPersonalStats } from '@/service/api';
import { $t } from '@/locales';

defineOptions({ name: 'HeaderBanner' });

const appStore = useAppStore();
const authStore = useAuthStore();

const gap = computed(() => (appStore.isMobile ? 0 : 16));

interface StatisticData {
  id: string;
  title: string;
  value: number;
  formatter?: (value: number) => string;
}

const personalStats = ref<Api.Stats.PersonalResponse | null>(null);
const loading = ref(false);

async function loadPersonalStats() {
  if (loading.value) {
    return;
  }
  if (!authStore.isLogin) {
    personalStats.value = null;
    return;
  }

  loading.value = true;
  try {
    personalStats.value = await fetchPersonalStats();
  } catch {
    personalStats.value = null;
  } finally {
    loading.value = false;
  }
}

onMounted(loadPersonalStats);

watch(
  () => authStore.userInfo.id,
  (id, prevId) => {
    if (!id || id === prevId) {
      return;
    }
    loadPersonalStats();
  }
);

const statisticData = computed<StatisticData[]>(() => {
  const stats = personalStats.value;

  if (!stats) {
    return [];
  }

  if (stats.user_type === 'vendor' && stats.vendor) {
    const vendor = stats.vendor;
    return [
      {
        id: 'vendor-items',
        title: $t('page.home.vendorItems'),
        value: vendor.item_total
      },
      {
        id: 'vendor-orders',
        title: $t('page.home.vendorOrders'),
        value: vendor.order_pending,
        formatter: (val: number) => `${val}/${vendor.order_total}`
      }
    ];
  }

  if (stats.user_type === 'admin' && stats.admin) {
    return [
      {
        id: 'admin-store',
        title: $t('page.home.adminPendingStores'),
        value: stats.admin.pending_store_review
      },
      {
        id: 'admin-comment',
        title: $t('page.home.adminPendingComments'),
        value: stats.admin.pending_comment_review
      }
    ];
  }

  if (stats.user_type === 'customer' && stats.customer) {
    return [
      {
        id: 'customer-orders',
        title: $t('page.home.customerOrders'),
        value: stats.customer.order_total
      },
      {
        id: 'customer-pending',
        title: $t('page.home.customerPendingOrders'),
        value: stats.customer.order_pending
      }
    ];
  }

  return [];
});

const vendorStoreNotice = computed(() => {
  if (authStore.userInfo.user_type !== 'vendor') {
    return null;
  }

  const vendor = personalStats.value?.vendor;

  if (!vendor) {
    return null;
  }

  if (!vendor.store_exists) {
    return { type: 'warning' as const, text: $t('page.home.vendorStoreMissing') };
  }

  if (vendor.store_state === 'pending') {
    return { type: 'info' as const, text: $t('page.home.vendorStorePending') };
  }

  if (vendor.store_state === 'disabled') {
    return { type: 'danger' as const, text: $t('page.home.vendorStoreDisabled') };
  }

  return null;
});
</script>

<template>
  <ElCard class="card-wrapper">
    <ElRow :gutter="gap" class="px-8px">
      <ElCol :md="18" :sm="24">
        <div class="flex-y-center">
          <div class="size-72px shrink-0 overflow-hidden rd-1/2">
            <img src="@/assets/imgs/soybean.jpg" class="size-full" />
          </div>
          <div class="pl-12px">
            <h3 class="text-18px font-semibold">
              {{ $t('page.home.greeting', { userName: authStore.userInfo.username || '--' }) }}
            </h3>
            <p class="text-#999 leading-30px">{{ $t('page.home.weatherDesc') }}</p>
            <div v-if="vendorStoreNotice" class="mt-8px">
              <ElTag :type="vendorStoreNotice.type" effect="plain">{{ vendorStoreNotice.text }}</ElTag>
            </div>
          </div>
        </div>
      </ElCol>
      <ElCol :md="6" :sm="24" class="flex flex-col items-end">
        <div class="mb-8px text-13px text-#909399">
          {{ $t('page.home.personalOverview') }}
        </div>
        <ElSpace v-if="statisticData.length" direction="horizontal" class="w-full justify-end" :size="24">
          <ElStatistic v-for="item in statisticData" :key="item.id" class="whitespace-nowrap" v-bind="item" />
        </ElSpace>
        <div v-else class="text-12px text-#c0c4cc">
          {{ $t('page.home.personalOverviewEmpty') }}
        </div>
      </ElCol>
    </ElRow>
  </ElCard>
</template>

<style scoped></style>
