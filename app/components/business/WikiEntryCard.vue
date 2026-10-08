<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-04T17:43:08+08:00
 * @description 以图文卡片或列表展示词条，并提供收藏和详情入口。
 */
import { ArrowUpRight, Heart, Sparkles } from '@lucide/vue';
import type { WikiEntry } from '~/types/wiki.types';
import { HADES_GODS, getHadesBoonTheme, getHadesBoonThemeStyle, getHadesBoonTagStyle } from '~/utils/hades-boons';

const props = defineProps<{
  entry: WikiEntry;
  isFavorite: boolean;
  viewMode: 'grid' | 'list';
}>();
const emit = defineEmits<{
  open: [id: string];
  'toggle-favorite': [id: string];
}>();
const baseURL = useRuntimeConfig().app.baseURL;
const imageUrl = computed(
  () => `${baseURL.replace(/\/$/, '')}/${props.entry.image.replace(/^\//, '')}`,
);
const cardDescription = computed(() =>
  props.entry.id.startsWith('0_') && props.entry.notes?.length
    ? props.entry.notes[0]
    : props.entry.description,
);
const boonTheme = computed(() => getHadesBoonTheme(props.entry));
const isCivilization = computed(() => props.entry.id.startsWith('civ6-'));
const boonTags = computed(() => props.entry.tags.filter((tag) =>
  HADES_GODS.some((god) => god.name === tag) || tag === '传奇祝福' || tag === '双重祝福',
));
</script>

<template>
  <article
    class="entry-card"
    :class="{ 'entry-card--list': viewMode === 'list', 'entry-card--weapon': Boolean(entry.aspects?.length), 'entry-card--boon': Boolean(boonTheme), 'entry-card--civilization': isCivilization }"
    :style="getHadesBoonThemeStyle(boonTheme)"
  >
    <button
      type="button"
      class="entry-card__open"
      :aria-label="`查看${entry.name}的${isCivilization ? '介绍与属性' : '效果与获取方式'}`"
      @click="emit('open', entry.id)"
    >
      <div class="entry-card__top">
        <span class="entry-card__image"
          ><img
            :class="{ 'pixel-image': !entry.id.startsWith('hades-') && !isCivilization }"
            :src="imageUrl"
            :alt="entry.name"
            loading="lazy"
            width="48"
            height="48"
        /></span>
        <div class="entry-card__title">
          <h3>{{ entry.name }}</h3>
          <span v-if="entry.englishName">{{ entry.englishName }}</span>
        </div>
      </div>
      <p class="entry-card__description">{{ cardDescription }}</p>
      <div v-if="isCivilization && entry.stats?.length" class="entry-card__stats">
        <span v-for="stat in entry.stats.slice(0, 2)" :key="stat.label">{{ stat.label }} <strong>{{ stat.value }}</strong></span>
      </div>
      <div class="entry-card__bottom">
        <div v-if="boonTheme" class="entry-card__tags">
          <span v-for="tag in boonTags" :key="tag" class="entry-card__boon-tag" :style="getHadesBoonTagStyle(tag)">{{ tag }}</span>
          <Sparkles v-if="entry.specialAcquisition" :size="10" aria-label="有前置条件" />
        </div>
        <span v-else-if="entry.specialAcquisition" class="entry-card__special"
          ><Sparkles :size="10" />特殊获取</span
        ><span v-else class="entry-card__tag">{{
          entry.tags[0] || '效果说明'
        }}</span
        ><ArrowUpRight :size="13" />
      </div>
    </button>
    <button
      type="button"
      class="entry-card__favorite"
      :class="{ 'is-favorite': isFavorite }"
      :aria-label="`${isFavorite ? '取消收藏' : '收藏'}${entry.name}`"
      :aria-pressed="isFavorite"
      @click="emit('toggle-favorite', entry.id)"
    >
      <Heart :size="14" :fill="isFavorite ? 'currentColor' : 'none'" />
    </button>
  </article>
</template>

<style scoped lang="scss">
.entry-card {
  position: relative;
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--panel);
  transition:
    border-color 0.16s,
    transform 0.16s;
  &:hover {
    border-color: var(--accent-border);
    transform: translateY(-2px);
    .entry-card__bottom > svg {
      color: var(--accent);
    }
  }
}
.entry-card--boon {
  background: color-mix(in srgb, rgb(var(--boon-rgb)) 7%, var(--panel));
  border-color: color-mix(in srgb, rgb(var(--boon-rgb)) 22%, var(--line));
  &:hover,
  &:focus-within {
    border-color: rgb(var(--boon-rgb));
    .entry-card__bottom > svg {
      color: rgb(var(--boon-rgb));
    }
  }
  .entry-card__open:focus-visible {
    outline-color: rgb(var(--boon-rgb));
    outline-offset: -3px;
  }
  .entry-card__image {
    background: color-mix(in srgb, rgb(var(--boon-rgb)) 10%, var(--icon-bg));
  }
}
.entry-card--civilization {
  border-radius: 5px;
  border-top: 2px solid var(--accent-border);
  .entry-card__image {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border-color: var(--accent-border);
    background: radial-gradient(circle at 40% 30%, #275575, #0b243b 75%);
    box-shadow: inset 0 0 0 3px #ffffff06, 0 2px 5px #00000015;
    img { width: 56px; height: 56px; }
  }
  .entry-card__title h3 { font-family: "Georgia", "Noto Serif SC", "SimSun", serif; font-size: 16px; }
  .entry-card__description { -webkit-line-clamp: 3; }
}
.entry-card__stats {
  display: flex;
  flex-wrap: wrap;
  gap: 5px 12px;
  margin: -5px 0 12px;
  color: var(--muted);
  font-size: 10px;
  span { max-width: 100%; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  strong { color: var(--secondary-text); font-weight: 500; }
}
.entry-card__tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  > svg {
    color: var(--special);
  }
}
.entry-card__boon-tag {
  padding: 2px 6px;
  border-radius: 3px;
  color: color-mix(in srgb, rgb(var(--boon-rgb)) var(--boon-text-mix), var(--text));
  background: color-mix(in srgb, rgb(var(--boon-rgb)) 10%, var(--panel));
}
.entry-card__open {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  padding: 19px 17px 14px;
  text-align: left;
}
.entry-card__top {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 53px;
  padding-right: 5px;
}
.entry-card__image {
  display: grid;
  place-items: center;
  width: 55px;
  height: 55px;
  flex-shrink: 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--icon-bg);
  img {
    width: 39px;
    height: 39px;
    object-fit: contain;
  }
}
.entry-card__title {
  min-width: 0;
  padding-right: 10px;
  h3 {
    margin: 0 0 5px;
    font-size: 14px;
    font-weight: 600;
    line-height: 1.5;
    overflow-wrap: anywhere;
  }
  > span {
    display: block;
    font-size: 10px;
    line-height: 1.45;
    color: var(--muted);
    overflow-wrap: anywhere;
  }
}
.entry-card--weapon .entry-card__image {
  width: 76px;
  height: 76px;
  img { width: 66px; height: 66px; }
}
.entry-card__description {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 15px 0 15px;
  min-height: 57px;
  color: var(--secondary-text);
  font-size: 12px;
  line-height: 1.75;
}
.entry-card__bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 7px;
  margin-top: auto;
  padding-top: 11px;
  border-top: 1px solid var(--line);
  font-size: 9px;
  color: var(--dimmed);
}
.entry-card__tag {
  padding: 2px 6px;
  color: var(--muted);
  background: var(--hover);
  border-radius: 3px;
}
.entry-card__special {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--special);
}
.entry-card__favorite {
  position: absolute;
  z-index: 1;
  top: 9px;
  right: 8px;
  display: grid;
  place-items: center;
  width: 25px;
  height: 25px;
  color: var(--dimmed);
  border-radius: 5px;
  &:hover {
    color: var(--accent);
    background: var(--hover);
  }
  &.is-favorite {
    color: var(--accent);
  }
}
.entry-card--list {
  .entry-card__stats { display: none; }
  .entry-card__open {
    display: grid;
    grid-template-columns: 230px minmax(0, 1fr) 104px;
    align-items: center;
    gap: 22px;
    padding: 14px 43px 14px 16px;
  }
  .entry-card__description {
    min-height: 0;
    margin: 0;
    -webkit-line-clamp: 2;
  }
  .entry-card__bottom {
    margin: 0;
    border: 0;
    padding: 0;
  }
  .entry-card__favorite {
    top: 50%;
    transform: translateY(-50%);
    right: 11px;
  }
}
@media (max-width: 1100px) {
  .entry-card--list .entry-card__open {
    grid-template-columns: 190px minmax(0, 1fr);
  }
  .entry-card--list .entry-card__bottom {
    display: none;
  }
}
@media (max-width: 580px) {
  .entry-card--list .entry-card__open {
    display: flex;
    align-items: stretch;
    gap: 8px;
  }
  .entry-card--list .entry-card__description {
    -webkit-line-clamp: 3;
  }
  .entry-card__title h3 {
    font-size: 14px;
  }
  .entry-card__description {
    font-size: 12px;
  }
}
</style>
