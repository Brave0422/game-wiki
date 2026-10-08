<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-05T13:16:06+08:00
 * @description 文明六风云变幻百科入口，复用分类检索、收藏与图文词条详情。
 */
import { BookOpen, Compass } from "@lucide/vue";
import WikiCatalogView from "~/components/business/WikiCatalogView.vue";
import { CIVILIZATION_GAME } from "~/constants/games";
import { CIVILIZATION_CATEGORIES } from "~/constants/wiki";
import { CIVILIZATION_ENTRIES } from "~/utils/wiki-data";

definePageMeta({
  layout: "wiki-shell-layout",
  validate: (route) => CIVILIZATION_GAME.sections.some((section) => section.id === route.params.section),
});

useSeoMeta({
  title: "文明 VI 百科 · 风云变幻",
  description: "文明六中文图文百科，查阅文明与领袖能力、单位属性、区域建筑、世界奇观、科技市政、资源与游戏机制。",
});
</script>

<template>
  <div class="civilization-archive">
    <!-- 百科卷首沿用站点布局，以罗盘与章节导读呈现文明主题。 -->
    <div class="civilization-archive__intro">
      <div class="civilization-archive__title">
        <span class="civilization-archive__seal"><Compass :size="25" :stroke-width="1.25" /></span>
        <div><span class="eyebrow">THE CIVILOPEDIA</span><h2>文明百科</h2></div>
      </div>
      <p><BookOpen :size="14" />探索世界的每一种可能<span>选择章节，或搜索你想了解的事物。</span></p>
    </div>
    <WikiCatalogView
      :entries="CIVILIZATION_ENTRIES"
      :categories="CIVILIZATION_CATEGORIES"
      base-path="/games/civilization-vi/encyclopedia"
      game-name="CIVILIZATION VI"
      edition-label="风云变幻规则集"
    />
  </div>
</template>

<style scoped lang="scss">
.civilization-archive__intro {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 28px 0 23px;
  border-bottom: 1px solid var(--line);
  p {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin: 0;
    color: var(--secondary-text);
    font-size: 12px;
    > svg { color: var(--accent); }
    span { color: var(--muted); margin-left: 8px; }
  }
}
.civilization-archive__title {
  display: flex;
  align-items: center;
  gap: 13px;
  h2 { margin: 1px 0 0; font-family: "Georgia", "Noto Serif SC", "SimSun", serif; font-size: 24px; letter-spacing: 3px; }
  .eyebrow { color: var(--accent); letter-spacing: 2.5px; }
}
.civilization-archive__seal {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border: 1px solid var(--accent-border);
  border-radius: 50%;
  color: var(--accent);
}
@media (max-width: 760px) {
  .civilization-archive__intro { align-items: flex-start; flex-direction: column; gap: 13px; padding-top: 21px; }
  .civilization-archive__intro p span { display: none; }
}
</style>
