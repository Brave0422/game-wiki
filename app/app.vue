<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-04T17:35:49+08:00
 * @description 游戏百科应用入口，提供统一布局和全局样式。
 */
import "~/assets/styles/main.scss";
import "~/assets/styles/civilization.scss";

useHead({ htmlAttrs: { lang: "zh-CN" }, titleTemplate: "%s · 游戏图鉴" });
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
