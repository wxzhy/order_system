<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { createReusableTemplate } from '@vueuse/core';
import { fetchSiteStats } from '@/service/api';
import { $t } from '@/locales';

defineOptions({ name: 'CardData' });

interface CardData {
  key: string;
  title: string;
  value: number;
  unit: string;
  decimals?: number;
  color: {
    start: string;
    end: string;
  };
  icon: string;
}

const siteStats = ref<Api.Stats.SiteResponse | null>(null);
const loading = ref(false);

async function loadSiteStats() {
  if (loading.value) {
    return;
  }

  loading.value = true;
  try {
    siteStats.value = await fetchSiteStats();
  } catch {
    siteStats.value = null;
  } finally {
    loading.value = false;
  }
}

onMounted(loadSiteStats);

const cardData = computed<CardData[]>(() => {
  const stats = siteStats.value;

  return [
    {
      key: 'userTotal',
      title: $t('page.home.userTotal'),
      value: stats?.user_total ?? 0,
      unit: '',
      color: {
        start: '#5c6bc0',
        end: '#3949ab'
      },
      icon: 'ic:round-group'
    },
    {
      key: 'merchantTotal',
      title: $t('page.home.merchantTotal'),
      value: stats?.merchant_total ?? 0,
      unit: '',
      color: {
        start: '#29b6f6',
        end: '#0288d1'
      },
      icon: 'mdi:storefront'
    },
    {
      key: 'orderTotal',
      title: $t('page.home.orderTotal'),
      value: stats?.order_total ?? 0,
      unit: '',
      color: {
        start: '#66bb6a',
        end: '#388e3c'
      },
      icon: 'mdi:clipboard-list-outline'
    },
    {
      key: 'amountTotal',
      title: $t('page.home.amountTotal'),
      value: Number((stats?.turnover_total ?? 0).toFixed(2)),
      unit: '¥',
      decimals: 2,
      color: {
        start: '#ffa726',
        end: '#fb8c00'
      },
      icon: 'mdi:currency-cny'
    }
  ];
});

interface GradientBgProps {
  gradientColor: string;
}

const [DefineGradientBg, GradientBg] = createReusableTemplate<GradientBgProps>();

function getGradientColor(color: CardData['color']) {
  return `linear-gradient(to bottom right, ${color.start}, ${color.end})`;
}
</script>

<template>
  <ElCard class="card-wrapper">
    <!-- define component start: GradientBg -->
    <DefineGradientBg v-slot="{ $slots, gradientColor }">
      <div class="rd-8px px-16px pb-4px pt-8px text-white" :style="{ backgroundImage: gradientColor }">
        <component :is="$slots.default" />
      </div>
    </DefineGradientBg>
    <!-- define component end: GradientBg -->
    <ElRow :gutter="16">
      <ElCol v-for="item in cardData" :key="item.key" :lg="6" :md="12" :sm="24" class="my-8px">
        <GradientBg :gradient-color="getGradientColor(item.color)" class="flex-1">
          <h3 class="text-16px">{{ item.title }}</h3>
          <div class="flex justify-between pt-12px">
            <SvgIcon :icon="item.icon" class="text-32px" />
            <CountTo
              :prefix="item.unit"
              :start-value="0"
              :end-value="item.value"
              :decimals="item.decimals ?? 0"
              class="text-30px text-white dark:text-dark"
            />
          </div>
        </GradientBg>
      </ElCol>
    </ElRow>
  </ElCard>
</template>

<style scoped></style>
