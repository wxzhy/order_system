<script lang="ts" setup>
import iconPng from '@/assets/icon.png';

defineOptions({ name: 'SystemLogo' });
</script>

<template>
  <img :src="iconPng" alt="logo" class="logo-image" />
</template>

<style scoped>
.logo-image {
  width: 1em;
  height: 1em;
  object-fit: contain;
}
</style>
