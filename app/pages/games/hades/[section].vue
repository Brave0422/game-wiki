<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-04T21:44:36+08:00
 * @description 哈迪斯祝福和武器专区，共用全站图鉴、检索、收藏及详情展示。
 */
import WikiCatalogView from "~/components/business/WikiCatalogView.vue";
import { HADES_GAME } from "~/constants/games";
import { HADES_CATEGORIES } from "~/constants/wiki";
import { HADES_ENTRIES } from "~/utils/wiki-data";

definePageMeta({
  layout: "wiki-shell-layout",
  validate: (route) => HADES_GAME.sections.some((section) => section.id === route.params.section),
});
const route = useRoute();
const category = computed(() => route.params.section === "weapons" ? "weapons" : "boons");
useSeoMeta({
  title: () => `哈迪斯${category.value === "boons" ? "祝福" : "武器"}图鉴`,
  description: "哈迪斯 PC 版众神祝福、前置获取条件、六种武器与二十四种形态的逐级属性和升级消耗。",
});
</script>

<template>
  <WikiCatalogView
    :key="String(route.params.section)"
    :entries="HADES_ENTRIES"
    :categories="HADES_CATEGORIES"
    :fixed-category="category"
    :base-path="`/games/hades/${category}`"
    game-name="HADES"
  />
</template>
