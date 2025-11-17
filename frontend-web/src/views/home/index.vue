<script setup lang="ts">
import HeaderBanner from './modules/header-banner.vue';
import CardData from './modules/card-data.vue';
</script>

<template>
  <ElSpace direction="vertical" fill class="full-space pb-0" :size="0">
    <HeaderBanner class="mb-16px" />
    <CardData />
  </ElSpace>
</template>

<style scoped lang="scss">
.full-space {
  > :deep(.el-space__item) {
    width: 100%;
  }
}
</style>
