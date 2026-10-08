<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-04T17:43:08+08:00
 * @description 多游戏图鉴目录，负责分类、全文检索、获取筛选和链接式详情。
 */
import {
  ArrowDownWideNarrow,
  ArrowRight,
  Check,
  ChevronDown,
  Filter,
  Heart,
  LayoutGrid,
  List,
  Search,
  SearchX,
  Sparkles,
  X,
} from "@lucide/vue";
import WikiEntryCard from "./WikiEntryCard.vue";
import WikiEntryDetailDialog from "./WikiEntryDetailDialog.vue";
import { GAME_BASE_PATH, PAGE_SIZE, WIKI_CATEGORIES } from "~/constants/wiki";
import { matchesEntry, WIKI_ENTRIES } from "~/utils/wiki-data";
import { HADES_BOON_TAG_ORDER, HADES_GODS, getHadesBoonTagStyle } from "~/utils/hades-boons";
import type { WikiCategory, WikiCategoryDefinition, WikiEntry } from "~/types/wiki.types";

const props = withDefaults(defineProps<{
  entries?: WikiEntry[];
  categories?: WikiCategoryDefinition[];
  fixedCategory?: WikiCategory;
  basePath?: string;
  gameName?: string;
  editionLabel?: string;
}>(), {
  entries: () => WIKI_ENTRIES,
  categories: () => WIKI_CATEGORIES,
  basePath: `${GAME_BASE_PATH}/encyclopedia`,
  gameName: "NEON ABYSS",
  editionLabel: "PC 原版",
});

const route = useRoute();
const isCivilization = computed(() => props.gameName === "CIVILIZATION VI");
const baseURL = useRuntimeConfig().app.baseURL.replace(/\/$/, "");
const categoryImageById = computed(() => Object.fromEntries(props.categories.map((category) => [
  category.id,
  `${baseURL}/images/civilization-vi/icon_civilopedia_${category.id === 'leaders' ? 'civilizations' : category.id}.png`,
])));
const router = useRouter();
const { favoriteIds, toggleFavorite } = useWikiPreferences();
const searchText = ref(typeof route.query.q === "string" ? route.query.q : "");
const visibleCount = ref(PAGE_SIZE);
const viewMode = ref<"grid" | "list">("grid");
let searchTimeout: ReturnType<typeof setTimeout> | undefined;

const selectedCategory = computed<WikiCategory | "all">(() => {
  if (props.fixedCategory && route.query.favorites !== "1") return props.fixedCategory;
  return props.categories.find((category) => category.id === route.query.category)?.id ?? "all";
});
const hasBoonFilters = computed(() =>
  props.gameName === "HADES" && selectedCategory.value !== "weapons",
);
const selectedGod = computed(() => {
  if (!hasBoonFilters.value) return "";
  const value = route.query.god ?? route.query.tag;
  return HADES_GODS.find((god) => god.name === value)?.name ?? "";
});
const selectedTag = computed(() => {
  const value = typeof route.query.tag === "string" ? route.query.tag : "";
  return hasBoonFilters.value && HADES_GODS.some((god) => god.name === value)
    ? "" : value;
});
const isSpecialOnly = computed(() => route.query.special === "1");
const isFavoritesOnly = computed(() => route.query.favorites === "1");
const sortOrder = computed(() =>
  route.query.sort === "name" ? "name" : "default",
);
const categoryEntries = computed(() =>
  props.entries.filter(
    (entry) =>
      selectedCategory.value === "all" ||
      entry.category === selectedCategory.value,
  ),
);
const categoryCounts = computed(() =>
  Object.fromEntries(
    props.categories.map((category) => [
      category.id,
      props.entries.filter((entry) => entry.category === category.id).length,
    ]),
  ),
);
const selectedCategoryInfo = computed(() =>
  props.categories.find((category) => category.id === selectedCategory.value),
);
const heading = computed(() =>
  isFavoritesOnly.value
    ? "我的收藏"
    : `${selectedCategoryInfo.value?.label ?? "全部"}图鉴`,
);
const availableTags = computed(() => {
  const counts = new Map<string, number>();
  categoryEntries.value.forEach((entry) =>
    entry.tags.forEach((tag) => counts.set(tag, (counts.get(tag) ?? 0) + 1)),
  );
  if (hasBoonFilters.value) {
    return [...counts]
      .filter(([name]) => !HADES_GODS.some((god) => god.name === name))
      .sort((left, right) => HADES_BOON_TAG_ORDER.indexOf(left[0]) - HADES_BOON_TAG_ORDER.indexOf(right[0]))
      .map(([name, count]) => ({ name, count }));
  }
  return [...counts]
    .sort((left, right) => right[1] - left[1])
    .slice(0, 8)
    .map(([name, count]) => ({ name, count }));
});
const filteredEntries = computed(() => {
  const entries = categoryEntries.value.filter(
    (entry) =>
      matchesEntry(entry, searchText.value) &&
      (!selectedGod.value || entry.tags.includes(selectedGod.value)) &&
      (!selectedTag.value || entry.tags.includes(selectedTag.value)) &&
      (!isSpecialOnly.value || Boolean(entry.specialAcquisition)) &&
      (!isFavoritesOnly.value || favoriteIds.value.includes(entry.id)),
  );
  if (sortOrder.value === "name") {
    return [...entries].sort((left, right) =>
      left.name.localeCompare(right.name, "zh-CN"),
    );
  }
  const categoryRank = new Map(props.categories.map((category, index) => [category.id, index]));
  return [...entries].sort((left, right) => {
    const leftRank =
      (categoryRank.get(left.category) ?? props.categories.length) + (left.id.startsWith("0_") ? 0.5 : 0);
    const rightRank =
      (categoryRank.get(right.category) ?? props.categories.length) + (right.id.startsWith("0_") ? 0.5 : 0);
    return leftRank - rightRank;
  });
});
const visibleEntries = computed(() =>
  filteredEntries.value.slice(0, visibleCount.value),
);
const selectedEntry = computed(
  () => props.entries.find((entry) => entry.id === route.query.entry) ?? null,
);
const hasActiveFilters = computed(() =>
  Boolean(
    searchText.value ||
    selectedGod.value ||
    selectedTag.value ||
    isSpecialOnly.value ||
    (!props.fixedCategory && selectedCategory.value !== "all"),
  ),
);

/** 保留其它筛选项更新 URL，让分类和词条链接能够直接分享或刷新。 */
async function updateQuery(
  values: Record<string, string | null>,
): Promise<void> {
  const query = { ...route.query };
  Object.entries(values).forEach(([key, value]) => {
    if (value === null || value === "") delete query[key];
    else query[key] = value;
  });
  await router.replace({ query });
}

function handleQuery(values: Record<string, string | null>): void {
  updateQuery(values).catch((error: unknown) =>
    console.error("筛选链接更新失败", error),
  );
}

/** 切换类型时把旧链接中的神祇标签迁移到独立条件，保留组合筛选。 */
function handleTagFilter(tag: string | null): void {
  handleQuery(hasBoonFilters.value ? { tag, god: selectedGod.value || null } : { tag });
}

/** 重置检索条件时保留当前百科或收藏浏览模式。 */
function handleClearFilters(): void {
  searchText.value = "";
  handleQuery({
    q: null,
    tag: null,
    god: null,
    special: null,
    category: null,
  });
}

function handleSearchSubmit(): void {
  clearTimeout(searchTimeout);
  handleQuery({ q: searchText.value.trim() || null });
}

watch(searchText, (value) => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(
    () => handleQuery({ q: value.trim() || null }),
    180,
  );
});
watch(
  () => route.query.q,
  (value) => {
    const nextValue = typeof value === "string" ? value : "";
    if (searchText.value.trim() !== nextValue) searchText.value = nextValue;
  },
);
watch(filteredEntries, () => {
  visibleCount.value = PAGE_SIZE;
});
onUnmounted(() => clearTimeout(searchTimeout));
</script>

<template>
  <section class="catalog" :class="{ 'catalog--civilization': isCivilization }" aria-labelledby="catalog-heading">
    <!-- 分类与效果筛选仅在浏览器中处理本地图鉴。 -->
    <div v-if="!fixedCategory || isFavoritesOnly" class="category-tabs" aria-label="图鉴分类">
      <button
        type="button"
        :class="{ 'is-active': selectedCategory === 'all' }"
        :aria-pressed="selectedCategory === 'all'"
        @click="handleQuery({ category: null, tag: null, god: null })"
      >
        <img v-if="isCivilization" :src="`${baseURL}/images/civilization-vi/icon_civilopedia_concepts.png`" alt="" width="23" height="23" />
        全部图鉴 <span>{{ entries.length }}</span></button
      ><button
        v-for="category in categories"
        :key="category.id"
        type="button"
        :class="{ 'is-active': selectedCategory === category.id }"
        :aria-pressed="selectedCategory === category.id"
        @click="handleQuery({ category: category.id, tag: null, god: null })"
      >
        <img v-if="isCivilization" :src="categoryImageById[category.id]" alt="" width="23" height="23" />
        {{ category.label }} <span>{{ categoryCounts[category.id] }}</span>
      </button>
    </div>

    <div class="catalog-title">
      <div>
        <h2 id="catalog-heading">
          {{ heading }}<span>{{ filteredEntries.length }}</span>
        </h2>
        <p>
          {{
            isFavoritesOnly
              ? "把常用词条留在手边，收藏保存在当前浏览器。"
              : (selectedCategoryInfo?.caption ??
                (isCivilization ? "查阅文明特色、城市建设、研究发展与胜利机制。" : "查询图鉴作用、属性与获取条件。"))
          }}
        </p>
      </div>
      <div class="catalog-title__hint"><span class="status-dot" />{{ editionLabel }}</div>
    </div>

    <div class="catalog-toolbar">
      <form
        class="catalog-search"
        role="search"
        @submit.prevent="handleSearchSubmit"
      >
        <Search :size="17" /><label for="wiki-search" class="sr-only"
          >{{ isCivilization ? '搜索名称、能力或解锁条件' : '搜索名称、效果或获取方式' }}</label
        ><input
          id="wiki-search"
          v-model="searchText"
          type="search"
          :placeholder="isCivilization ? '搜索文明、领袖、科技或解锁条件…' : '搜索名称、效果或获取方式…'"
          autocomplete="off"
        /><button
          v-if="searchText"
          type="button"
          class="icon-button"
          aria-label="清空搜索"
          @click="searchText = ''"
        >
          <X :size="14" /></button
        ><kbd v-else>Ctrl K</kbd>
      </form>
      <button
        v-if="categoryEntries.some((entry) => entry.specialAcquisition)"
        type="button"
        class="filter-button"
        :class="{ 'is-active': isSpecialOnly }"
        :aria-pressed="isSpecialOnly"
        @click="handleQuery({ special: isSpecialOnly ? null : '1' })"
      >
        <Sparkles :size="14" /><span>{{ fixedCategory === 'boons' ? '有前置条件' : '特殊获取' }}</span>
        <Check v-if="isSpecialOnly" :size="13" />
      </button>
    </div>

    <!-- 神祇与祝福类型独立筛选，兼容旧链接中使用 tag 的神祇条件。 -->
    <div v-if="hasBoonFilters" class="effect-tags god-tags" aria-label="众神筛选">
      <span class="effect-tags__label"><Sparkles :size="12" />众神</span>
      <button
        type="button"
        :class="{ 'is-active': !selectedGod }"
        :aria-pressed="!selectedGod"
        @click="handleQuery({ god: null, tag: selectedTag || null })"
      >全部</button>
      <button
        v-for="god in HADES_GODS"
        :key="god.name"
        type="button"
        class="boon-filter"
        :class="{ 'is-active': selectedGod === god.name }"
        :style="getHadesBoonTagStyle(god.name)"
        :aria-pressed="selectedGod === god.name"
        @click="handleQuery({ god: selectedGod === god.name ? null : god.name, tag: selectedTag || null })"
      >{{ god.name }}</button>
    </div>

    <div v-if="availableTags.length" class="effect-tags" aria-label="效果标签">
      <span class="effect-tags__label"><Filter :size="12" />{{ hasBoonFilters ? '祝福' : isCivilization ? '类型' : '效果' }}</span>
      <button
        type="button"
        :class="{ 'is-active': !selectedTag }"
        :aria-pressed="!selectedTag"
        @click="handleTagFilter(null)"
      >
        全部</button
      ><button
        v-for="tag in availableTags"
        :key="tag.name"
        type="button"
        :class="{ 'is-active': selectedTag === tag.name, 'boon-filter': hasBoonFilters && Boolean(getHadesBoonTagStyle(tag.name)) }"
        :style="hasBoonFilters ? getHadesBoonTagStyle(tag.name) : undefined"
        :aria-pressed="selectedTag === tag.name"
        @click="
          handleTagFilter(selectedTag === tag.name ? null : tag.name)
        "
      >
        {{ tag.name }}</button
      ><button
        v-if="
          selectedTag && !availableTags.some((tag) => tag.name === selectedTag)
        "
        type="button"
        class="is-active"
        @click="handleTagFilter(null)"
      >
        {{ selectedTag }} <X :size="10" />
      </button>
    </div>

    <div class="results-heading">
      <div aria-live="polite">
        找到 <strong>{{ filteredEntries.length }}</strong> 个条目<button
          v-if="hasActiveFilters"
          type="button"
          @click="handleClearFilters"
        >
          重置筛选 <X :size="11" />
        </button>
      </div>
      <div class="results-actions">
        <label class="sort-select"
          ><ArrowDownWideNarrow :size="13" /><span class="sr-only"
            >图鉴排序</span
          ><select
            :value="sortOrder"
            @change="
              handleQuery({
                sort:
                  ($event.target as HTMLSelectElement).value === 'name'
                    ? 'name'
                    : null,
              })
            "
          >
            <option value="default">默认顺序</option>
            <option value="name">名称排序</option></select
          ><ChevronDown :size="11"
        /></label>
        <div class="view-switch" aria-label="显示方式">
          <button
            type="button"
            :class="{ 'is-active': viewMode === 'grid' }"
            :aria-pressed="viewMode === 'grid'"
            aria-label="卡片视图"
            @click="viewMode = 'grid'"
          >
            <LayoutGrid :size="15" /></button
          ><button
            type="button"
            :class="{ 'is-active': viewMode === 'list' }"
            :aria-pressed="viewMode === 'list'"
            aria-label="列表视图"
            @click="viewMode = 'list'"
          >
            <List :size="16" />
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="visibleEntries.length"
      class="entry-grid"
      :class="{ 'entry-grid--list': viewMode === 'list' }"
    >
      <WikiEntryCard
        v-for="entry in visibleEntries"
        :key="entry.id"
        :entry="entry"
        :is-favorite="favoriteIds.includes(entry.id)"
        :view-mode="viewMode"
        @open="handleQuery({ entry: $event })"
        @toggle-favorite="toggleFavorite"
      />
    </div>
    <div v-else class="empty-state">
      <Heart v-if="isFavoritesOnly && !favoriteIds.length" :size="36" /><SearchX
        v-else
        :size="36"
      />
      <h3>
        {{
          isFavoritesOnly && !favoriteIds.length
            ? "还没有收藏的词条"
            : "没有找到匹配的条目"
        }}
      </h3>
      <p>
        {{
          isFavoritesOnly && !favoriteIds.length
            ? "点击图鉴卡片上的爱心，将常用词条加入收藏。"
            : isFavoritesOnly
              ? "试试中文名、英文名或作用关键词，也可以清除筛选查看全部收藏。"
              : "试试中文名、英文名或作用关键词，也可以清除筛选查看全部图鉴。"
        }}
      </p>
      <NuxtLink
        v-if="isFavoritesOnly && (!favoriteIds.length || !hasActiveFilters)"
        :to="basePath"
        class="secondary-button"
      >
        查看全部图鉴 <ArrowRight :size="14" />
      </NuxtLink>
      <button
        v-else
        type="button"
        class="secondary-button"
        @click="handleClearFilters"
      >
        {{ isFavoritesOnly ? "重置筛选" : "查看全部图鉴" }}
        <ArrowRight :size="14" />
      </button>
    </div>

    <div v-if="visibleEntries.length" class="load-more">
      <span
        >已展示 {{ visibleEntries.length }} /
        {{ filteredEntries.length }} 个条目</span
      ><button
        v-if="visibleEntries.length < filteredEntries.length"
        type="button"
        class="secondary-button"
        @click="visibleCount += PAGE_SIZE"
      >
        加载更多 <ChevronDown :size="14" /></button
      ><span v-else class="load-more__end">已展示全部结果</span>
    </div>
    <WikiEntryDetailDialog
      :entry="selectedEntry"
      :game-name="gameName"
      :is-favorite="
        selectedEntry ? favoriteIds.includes(selectedEntry.id) : false
      "
      @close="handleQuery({ entry: null })"
      @toggle-favorite="toggleFavorite"
    />
  </section>
</template>

<style scoped lang="scss">
.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  padding-top: 23px;
  button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 13px;
    border: 1px solid transparent;
    border-radius: 6px;
    font-size: 12px;
    color: var(--muted);
    span {
      font-size: 9px;
      color: var(--dimmed);
    }
    &:hover {
      background: var(--hover);
    }
    &.is-active {
      color: var(--accent);
      background: var(--accent-soft);
      border-color: var(--accent-border);
      span {
        color: var(--accent);
        opacity: 0.75;
      }
    }
  }
}
.catalog-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin: 27px 0 20px;
  h2 {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
    font-size: 20px;
    font-weight: 600;
    letter-spacing: 0.2px;
    > span {
      padding: 1px 6px;
      border: 1px solid var(--line);
      border-radius: 4px;
      font-size: 10px;
      font-weight: 400;
      color: var(--muted);
    }
  }
  p {
    font-size: 11px;
    color: var(--muted);
    margin: 0;
  }
}
.catalog-title__hint {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  font-size: 10px;
  .status-dot {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--accent);
  }
}
.catalog-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
}
.catalog-search {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
  height: 42px;
  padding: 0 12px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 7px;
  color: var(--muted);
  &:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px var(--accent-soft);
  }
  input {
    width: 100%;
    min-width: 0;
    outline: 0;
    border: 0;
    background: transparent;
    color: var(--text);
    font-size: 12px;
    line-height: 40px;
    &::placeholder {
      color: var(--muted);
    }
    &::-webkit-search-cancel-button {
      -webkit-appearance: none;
    }
  }
  kbd {
    white-space: nowrap;
    padding: 1px 5px;
    color: var(--dimmed);
    border: 1px solid var(--line);
    border-radius: 3px;
    font-size: 9px;
    font-family: inherit;
  }
  .icon-button {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
  }
}
.filter-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 42px;
  padding: 0 13px;
  color: var(--secondary-text);
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 7px;
  font-size: 11px;
  white-space: nowrap;
  &:hover {
    border-color: var(--line-strong);
  }
  &.is-active {
    background: var(--accent-soft);
    border-color: var(--accent-border);
    color: var(--accent);
  }
}
.effect-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 7px;
  margin: 14px 0 23px;
  button {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    color: var(--muted);
    font-size: 10px;
    border-radius: 4px;
    &:hover {
      background: var(--hover);
    }
    &.is-active {
      background: var(--hover);
      color: var(--secondary-text);
    }
  }
}
.effect-tags__label {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--dimmed);
  font-size: 10px;
  margin-right: 5px;
}
.god-tags {
  margin-bottom: 0;
  + .effect-tags {
    margin-top: 10px;
  }
}
.effect-tags button.boon-filter {
  border: 1px solid transparent;
  color: color-mix(in srgb, rgb(var(--boon-rgb)) var(--boon-text-mix), var(--text));
  background: color-mix(in srgb, rgb(var(--boon-rgb)) 8%, var(--panel));
  transition: border-color 0.16s, background-color 0.16s;
  &:hover,
  &:focus-visible,
  &.is-active {
    border-color: rgb(var(--boon-rgb));
    background: color-mix(in srgb, rgb(var(--boon-rgb)) 16%, var(--panel));
  }
  &:focus-visible {
    outline-color: rgb(var(--boon-rgb));
  }
}
.results-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  color: var(--muted);
  font-size: 10px;
  strong {
    font-weight: 500;
    color: var(--secondary-text);
  }
  > div:first-child {
    display: flex;
    align-items: center;
    gap: 5px;
    flex-wrap: wrap;
    > button {
      display: flex;
      align-items: center;
      gap: 3px;
      margin-left: 9px;
      color: var(--accent);
      font-size: 10px;
    }
  }
}
.results-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}
.sort-select {
  display: flex;
  align-items: center;
  gap: 5px;
  select {
    appearance: none;
    background: transparent;
    border: 0;
    color: var(--muted);
    font-size: 10px;
    cursor: pointer;
    padding: 3px 0;
    option {
      background: var(--panel);
      color: var(--text);
    }
  }
}
.view-switch {
  display: flex;
  padding: 2px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 5px;
  button {
    display: grid;
    place-items: center;
    width: 28px;
    height: 24px;
    color: var(--dimmed);
    border-radius: 3px;
    &.is-active {
      color: var(--secondary-text);
      background: var(--hover);
    }
  }
}
.entry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(205px, 1fr));
  gap: 15px;
}
.entry-grid--list {
  grid-template-columns: 1fr;
  gap: 10px;
}
.load-more {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 13px;
  padding: 28px 0 5px;
  font-size: 10px;
  color: var(--muted);
}
.load-more__end {
  color: var(--dimmed);
  font-size: 9px;
}
@media (min-width: 1650px) {
  .entry-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }
  .entry-grid--list {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 1050px) {
  .catalog-toolbar {
    flex-wrap: wrap;
  }
  .catalog-search {
    flex-basis: 100%;
  }
  .entry-grid {
    grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
    gap: 12px;
  }
  .entry-grid--list {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 580px) {
  .catalog-title__hint {
    display: none;
  }
  .catalog-title {
    margin-top: 21px;
  }
  .category-tabs {
    gap: 4px;
    button {
      padding: 6px 8px;
      font-size: 11px;
      gap: 5px;
    }
  }
  .catalog-search kbd {
    display: none;
  }
  .results-actions {
    gap: 8px;
  }
  .sort-select > svg {
    display: none;
  }
  .effect-tags {
    gap: 3px;
    margin-bottom: 17px;
  }
  .god-tags {
    margin-bottom: 0;
  }
  .entry-grid {
    grid-template-columns: 1fr;
  }
  .catalog-search input {
    font-size: 12px;
  }
}
</style>
