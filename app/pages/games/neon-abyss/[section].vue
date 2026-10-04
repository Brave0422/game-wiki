<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-04T17:35:49+08:00
 * @description 按霓虹深渊的栏目配置校验路由，展示百科或攻略。
 */
import WikiCatalogView from "~/components/business/WikiCatalogView.vue";
import WikiGuidesView from "~/components/business/WikiGuidesView.vue";
import { NEON_ABYSS_GAME } from "~/constants/games";

definePageMeta({
  layout: "wiki-shell-layout",
  validate: (route) =>
    NEON_ABYSS_GAME.sections.some(
      (section) => section.id === route.params.section,
    ),
});

const route = useRoute();
const sectionLabel = computed(
  () =>
    NEON_ABYSS_GAME.sections.find(
      (section) => section.id === route.params.section,
    )?.label ?? "百科",
);
useSeoMeta({
  title: () => `霓虹深渊${sectionLabel.value}`,
  description:
    "霓虹深渊 PC 版道具、武器和宠物图鉴，查询效果、主动能力、进化与特殊获取方式。",
});
</script>

<template>
  <WikiCatalogView v-if="route.params.section === 'encyclopedia'" />
  <WikiGuidesView v-else-if="route.params.section === 'guides'" />
</template>
