<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-04T17:43:08+08:00
 * @description 展示有来源支持的霓虹深渊道具联动与特殊机制攻略。
 */
import { ArrowUpRight, BookOpen, ChevronDown, Lightbulb } from '@lucide/vue';
import { WIKI_GUIDES } from '~/utils/wiki-data';

const expandedGuideId = ref<string | null>(null);
</script>

<template>
  <section aria-labelledby="guides-heading">
    <div class="module-heading">
      <div>
        <h2 id="guides-heading">机制与搭配攻略</h2>
        <p>围绕局内机制，查阅道具联动、武器用途与宠物合体。</p>
      </div>
      <span class="eyebrow">{{ WIKI_GUIDES.length }} 篇攻略</span>
    </div>
    <div v-if="WIKI_GUIDES.length" class="guide-grid">
      <article v-for="guide in WIKI_GUIDES" :key="guide.id" class="guide-card">
        <span class="guide-icon"><Lightbulb :size="22" /></span
        ><span class="eyebrow">BUILD & MECHANICS</span>
        <h3>{{ guide.title }}</h3>
        <p>{{ guide.summary }}</p>
        <button
          class="text-button"
          type="button"
          :aria-expanded="expandedGuideId === guide.id"
          @click="
            expandedGuideId = expandedGuideId === guide.id ? null : guide.id
          "
        >
          {{ expandedGuideId === guide.id ? '收起内容' : '阅读攻略'
          }}<ChevronDown
            :size="14"
            :class="{ 'is-expanded': expandedGuideId === guide.id }"
          />
        </button>
        <div v-if="expandedGuideId === guide.id" class="guide-content">
          <p v-for="paragraph in guide.paragraphs" :key="paragraph">
            {{ paragraph }}
          </p>
          <div class="guide-sources">
            <span>参考资料</span
            ><a
              v-for="source in guide.sources"
              :key="source.url"
              :href="source.url"
              target="_blank"
              rel="noopener noreferrer"
              >{{ source.label }} <ArrowUpRight :size="12"
            /></a>
          </div>
        </div>
      </article>
    </div>
    <div v-else class="empty-state">
      <BookOpen :size="36" />
      <h3>攻略正在整理</h3>
      <p>先通过百科查询具体的道具效果、武器能力和宠物说明。</p>
      <NuxtLink class="secondary-button" to="/games/neon-abyss/encyclopedia"
        >查阅百科</NuxtLink
      >
    </div>
  </section>
</template>

<style scoped lang="scss">
.guide-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
  gap: 18px;
  align-items: start;
}
.guide-card {
  padding: 23px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel);
  > .eyebrow {
    display: block;
    margin: 18px 0 9px;
  }
  h3 {
    font-size: 17px;
    margin-bottom: 11px;
  }
  > p {
    min-height: 58px;
    color: var(--secondary-text);
    font-size: 12px;
    line-height: 1.9;
    margin-bottom: 19px;
  }
}
.guide-icon {
  display: grid;
  place-items: center;
  width: 43px;
  height: 43px;
  border: 1px solid var(--accent-border);
  border-radius: 8px;
  color: var(--accent);
  background: var(--accent-soft);
}
.is-expanded {
  transform: rotate(180deg);
}
.guide-content {
  padding-top: 18px;
  margin-top: 18px;
  border-top: 1px solid var(--line);
  p {
    font-size: 12px;
    color: var(--secondary-text);
    line-height: 1.95;
    white-space: pre-line;
  }
}
.guide-sources {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin-top: 18px;
  > span {
    font-size: 10px;
    color: var(--muted);
  }
  a {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 10px;
    text-decoration: none;
    color: var(--accent);
  }
}
@media (max-width: 580px) {
  .guide-grid {
    grid-template-columns: 1fr;
  }
}
</style>
