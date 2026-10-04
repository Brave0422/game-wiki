<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-04T17:35:49+08:00
 * @description 使用顶部导航整合游戏切换、内容栏目和收藏，提供搜索快捷键与主题切换。
 */
import {
  ArrowLeft,
  ArrowUpRight,
  BookOpen,
  Check,
  ChevronsUpDown,
  Command,
  ExternalLink,
  Heart,
  Layers3,
  LibraryBig,
  Map,
  Moon,
  Puzzle,
  Search,
  Sun,
  Trophy,
  X,
} from "@lucide/vue";
import {
  GAME_LIBRARY,
  NEON_ABYSS_GAME,
  getGameById,
  getGameEntryPath,
} from "~/constants/games";
import { GAME_BASE_PATH } from "~/constants/wiki";
import { WIKI_ENTRIES } from "~/utils/wiki-data";

const route = useRoute();
const router = useRouter();
const currentGame = computed(
  () => getGameById(route.path.split("/")[2] ?? "") ?? NEON_ABYSS_GAME,
);
const { favoriteIds, isLightTheme, toggleTheme } = useWikiPreferences();
const isGameMenuOpen = ref(false);
const isSourceDialogOpen = ref(false);
const sourceDialog = ref<HTMLDialogElement | null>(null);
const activeSection = computed(() =>
  String(route.params.section ?? "encyclopedia"),
);
const isFavoritesView = computed(
  () => activeSection.value === "encyclopedia" && route.query.favorites === "1",
);
const sectionIcons = {
  "book-open": BookOpen,
  map: Map,
  puzzle: Puzzle,
  layers: Layers3,
  trophy: Trophy,
};
const knownFavoritesCount = computed(
  () =>
    WIKI_ENTRIES.filter((entry) => favoriteIds.value.includes(entry.id)).length,
);
const heroImagePath = `${useRuntimeConfig().app.baseURL.replace(/\/$/, "")}/images/neon-abyss/steam-header.jpg`;

/** 将站内搜索导航至当前百科，并把焦点交给搜索输入框。 */
async function handleFocusSearch(): Promise<void> {
  if (isSourceDialogOpen.value) {
    sourceDialog.value?.close();
    isSourceDialogOpen.value = false;
  }
  if (activeSection.value !== "encyclopedia")
    await router.push(`${GAME_BASE_PATH}/encyclopedia`);
  else if (route.query.entry)
    await router.replace({ query: { ...route.query, entry: undefined } });
  await nextTick();
  document.getElementById("wiki-search")?.focus();
}

function handleKeyboard(event: KeyboardEvent): void {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    handleFocusSearch().catch((error: unknown) =>
      console.error("搜索导航失败", error),
    );
  }
  if (event.key === "Escape") isGameMenuOpen.value = false;
}

watch(isSourceDialogOpen, async (isOpen) => {
  await nextTick();
  if (isOpen) sourceDialog.value?.showModal();
  else sourceDialog.value?.close();
});

onMounted(() => window.addEventListener("keydown", handleKeyboard));
onUnmounted(() => window.removeEventListener("keydown", handleKeyboard));
</script>

<template>
  <div class="wiki-shell">
    <div class="main-shell">
      <!-- 全站与游戏切换集中于页头，游戏内容栏目只在下方导航展示。 -->
      <header class="topbar">
        <div class="topbar__inner">
          <NuxtLink class="brand" to="/" aria-label="游戏图鉴首页">
            <span class="brand-mark"><Layers3 :size="23" /></span>
            <span><strong>游戏图鉴</strong><small>GAME WIKI</small></span>
          </NuxtLink>
          <div class="game-picker">
            <button
              class="game-picker__trigger"
              type="button"
              aria-label="切换游戏"
              :aria-expanded="isGameMenuOpen"
              aria-controls="game-switcher"
              @click="isGameMenuOpen = !isGameMenuOpen"
            >
              <span class="game-avatar">NA</span
              ><span
                ><strong>{{ currentGame.name }}</strong
                ><small>{{
                  currentGame.englishName.toUpperCase()
                }}</small></span
              ><ChevronsUpDown :size="15" />
            </button>
            <div v-if="isGameMenuOpen" id="game-switcher" class="game-menu">
              <span class="eyebrow">切换游戏</span>
              <template v-for="game in GAME_LIBRARY" :key="game.id">
                <NuxtLink
                  v-if="getGameEntryPath(game)"
                  :to="getGameEntryPath(game) ?? '/'"
                  @click="isGameMenuOpen = false"
                  >{{ game.name
                  }}<Check v-if="game.id === currentGame.id" :size="15"
                /></NuxtLink>
                <span v-else class="game-menu__upcoming"
                  >{{ game.name }}<small>待收录</small></span
                >
              </template>
            </div>
          </div>
          <NuxtLink class="library-return" to="/" aria-label="返回游戏库"
            ><ArrowLeft :size="15" /><span>游戏库</span></NuxtLink
          >
          <div class="topbar-actions">
            <button
              class="quick-search"
              type="button"
              @click="handleFocusSearch"
            >
              <Search :size="16" /><span>搜索游戏资料</span
              ><kbd><Command :size="11" /> K</kbd>
            </button>
            <button
              class="icon-button"
              type="button"
              aria-label="资料来源"
              @click="isSourceDialogOpen = true"
            >
              <LibraryBig :size="18" />
            </button>
            <button
              class="icon-button theme-button"
              type="button"
              :aria-label="isLightTheme ? '切换深色主题' : '切换浅色主题'"
              @click="toggleTheme"
            >
              <Moon v-if="isLightTheme" :size="19" /><Sun v-else :size="19" />
            </button>
          </div>
        </div>
      </header>

      <main class="page-shell">
        <section class="game-hero" aria-labelledby="game-title">
          <div
            class="game-hero__art"
            :style="{ backgroundImage: `url(${heroImagePath})` }"
          />
          <div class="game-hero__content">
            <div class="game-hero__kicker">
              <span>{{ currentGame.englishName.toUpperCase() }}</span
              ><span class="platform-badge">PC</span>
            </div>
            <h1 id="game-title">{{ currentGame.name }}</h1>
            <p>道具效果、武器能力、宠物进化，一处查阅。</p>
            <div class="hero-meta">
              <span
                ><BookOpen :size="13" />{{
                  WIKI_ENTRIES.length
                }}
                个图鉴条目</span
              ><span class="hero-divider" /><span>PC 1.5.3.2 · 中文资料</span>
            </div>
          </div>
        </section>

        <nav class="section-tabs" :aria-label="`${currentGame.name}内容导航`">
          <NuxtLink
            v-for="section in currentGame.sections"
            :key="section.id"
            :to="`/games/${currentGame.id}/${section.id}`"
            :class="{
              'is-active': activeSection === section.id && !isFavoritesView,
            }"
            :aria-current="
              activeSection === section.id && !isFavoritesView
                ? 'page'
                : undefined
            "
            ><component :is="sectionIcons[section.icon]" :size="17" />{{
              section.label
            }}<span v-if="section.id === 'encyclopedia'" class="tab-count">{{
              WIKI_ENTRIES.length
            }}</span></NuxtLink
          >
          <NuxtLink
            class="section-tabs__favorites"
            :to="`${GAME_BASE_PATH}/encyclopedia?favorites=1`"
            :class="{ 'is-active': isFavoritesView }"
            :aria-current="isFavoritesView ? 'page' : undefined"
            ><Heart :size="17" />我的收藏<span class="tab-count">{{
              knownFavoritesCount
            }}</span></NuxtLink
          >
        </nav>

        <slot />
        <footer class="page-footer">
          <span>游戏图鉴 · 霓虹深渊 PC 版</span
          ><button type="button" @click="isSourceDialogOpen = true">
            资料与图片来源 <ExternalLink :size="12" />
          </button>
        </footer>
      </main>
    </div>

    <dialog
      ref="sourceDialog"
      class="source-dialog"
      aria-labelledby="sources-title"
      @cancel="isSourceDialogOpen = false"
      @close="isSourceDialogOpen = false"
    >
      <div class="source-dialog__header">
        <span class="eyebrow">ABOUT THE ARCHIVE</span
        ><button
          class="icon-button"
          type="button"
          aria-label="关闭资料来源"
          @click="isSourceDialogOpen = false"
        >
          <X :size="20" />
        </button>
      </div>
      <h2 id="sources-title">资料与图片来源</h2>
      <p>
        图鉴名称、基础效果与像素图标来自霓虹深渊 PC
        游戏资源。特殊获取条件和进阶说明参考下列资料，具体出处也会在相关词条中列出。
      </p>
      <a
        href="https://www.veewo.com/na-log?lang=zh"
        target="_blank"
        rel="noopener noreferrer"
        >Veewo Games · 官方更新日志 <ArrowUpRight :size="16"
      /></a>
      <a
        href="https://neonabyss.fandom.com/wiki/Neon_Abyss_Wiki"
        target="_blank"
        rel="noopener noreferrer"
        >Neon Abyss Wiki · PC 版资料 <ArrowUpRight :size="16"
      /></a>
      <a
        href="https://store.steampowered.com/app/788100/Neon_Abyss/"
        target="_blank"
        rel="noopener noreferrer"
        >Steam · 游戏主视觉 <ArrowUpRight :size="16"
      /></a>
      <p class="source-dialog__note">
        游戏图片与原始文本归原权利人所有。不同版本可能存在效果差异，获取说明以词条注明的条件为准。
      </p>
    </dialog>
  </div>
</template>

<style scoped lang="scss">
.topbar {
  position: relative;
  z-index: 30;
  border-bottom: 1px solid var(--line);
  background: var(--sidebar-bg);
}
.topbar__inner {
  display: flex;
  align-items: center;
  gap: 30px;
  width: min(1570px, 100%);
  min-height: 87px;
  margin: 0 auto;
  padding: 0 38px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  flex-shrink: 0;
  color: var(--text);
  text-decoration: none;
  strong {
    display: block;
    font-size: 18px;
    letter-spacing: 0.8px;
  }
  small {
    display: block;
    margin-top: 2px;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 2.8px;
    color: var(--muted);
  }
}
.brand-mark {
  display: grid;
  place-items: center;
  width: 39px;
  height: 39px;
  color: var(--accent);
  background: var(--accent-soft);
  border: 1px solid var(--accent-border);
  border-radius: 11px;
}
.game-picker {
  position: relative;
  width: 190px;
  flex-shrink: 0;
}
.game-picker__trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  text-align: left;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  strong {
    display: block;
    font-size: 12px;
  }
  small {
    display: block;
    margin-top: 2px;
    font-size: 9px;
    letter-spacing: 1.1px;
    color: var(--muted);
  }
  > svg {
    margin-left: auto;
    color: var(--muted);
  }
}
.game-avatar {
  display: grid;
  place-items: center;
  width: 31px;
  height: 31px;
  flex-shrink: 0;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1px;
  color: #ffc7f0;
  background: linear-gradient(135deg, #4b1e62, #1c2848);
}
.game-menu {
  position: absolute;
  top: calc(100% + 7px);
  inset-inline: 0;
  z-index: 10;
  padding: 13px;
  background: var(--panel-raised);
  border: 1px solid var(--line-strong);
  border-radius: 9px;
  box-shadow: var(--shadow);
  > a,
  .game-menu__upcoming {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 9px 0;
    font-size: 12px;
    text-decoration: none;
  }
  > a {
    color: var(--accent);
  }
  small {
    font-size: 10px;
  }
}
.game-menu__upcoming {
  color: var(--muted);
}
.library-return {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 0;
  color: var(--muted);
  font-size: 11px;
  white-space: nowrap;
  text-decoration: none;
  &:hover {
    color: var(--accent);
  }
}
.topbar-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-left: auto;
  color: var(--muted);
}
.quick-search {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 10px;
  width: 246px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--panel);
  color: var(--muted);
  font-size: 11px;
  kbd {
    display: flex;
    align-items: center;
    gap: 3px;
    padding: 2px 4px;
    margin-left: auto;
    background: var(--hover);
    border: 1px solid var(--line);
    border-radius: 3px;
    font-family: inherit;
    font-size: 10px;
  }
}
.page-shell {
  max-width: 1570px;
  margin: 0 auto;
  padding: 29px 38px 0;
}
.game-hero {
  position: relative;
  isolation: isolate;
  min-height: 203px;
  overflow: hidden;
  border: 1px solid var(--hero-line);
  border-radius: 12px;
  background: #111523;
}
.game-hero__art {
  position: absolute;
  inset: 0 0 0 28%;
  z-index: -2;
  background-size: cover;
  background-position: right 43%;
  opacity: 0.6;
}
.game-hero::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background: linear-gradient(
    90deg,
    #121524 5%,
    rgba(18, 21, 36, 0.96) 29%,
    rgba(18, 21, 36, 0.65) 50%,
    rgba(18, 21, 36, 0.1) 100%
  );
}
.game-hero__content {
  padding: 27px 31px;
  h1 {
    color: #f4f3ff;
    font-size: 31px;
    font-weight: 700;
    letter-spacing: 2px;
    margin: 11px 0 8px;
  }
  p {
    color: #b7b4ca;
    font-size: 12px;
    margin: 0;
  }
}
.game-hero__kicker {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #aca8c5;
  font-size: 9px;
  letter-spacing: 3px;
}
.platform-badge {
  padding: 2px 6px;
  border: 1px solid #454258;
  border-radius: 3px;
  font-size: 9px;
  letter-spacing: 0.5px;
  color: #ccc7e2;
}
.hero-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 21px;
  font-size: 10px;
  color: #aaa5bd;
  > span {
    display: flex;
    align-items: center;
    gap: 6px;
  }
}
.hero-divider {
  width: 1px;
  height: 9px;
  background: #514b65;
}
.section-tabs {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  gap: 32px;
  margin-top: 11px;
  border-bottom: 1px solid var(--line);
  background: var(--page-bg);
  a {
    position: relative;
    display: flex;
    align-items: center;
    gap: 8px;
    min-height: 56px;
    color: var(--muted);
    text-decoration: none;
    font-size: 13px;
  }
  a.is-active {
    color: var(--text);
    &::after {
      content: "";
      position: absolute;
      inset: auto 0 -1px;
      height: 2px;
      border-radius: 2px;
      background: var(--accent);
    }
    > svg {
      color: var(--accent);
    }
  }
}
.section-tabs__favorites {
  margin-left: auto;
}
.tab-count {
  background: var(--hover);
  color: var(--muted);
  border: 1px solid var(--line);
  padding: 1px 5px;
  font-size: 9px;
  border-radius: 4px;
}
.page-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 26px 0;
  margin-top: 32px;
  border-top: 1px solid var(--line);
  color: var(--dimmed);
  font-size: 10px;
  button {
    display: flex;
    align-items: center;
    gap: 5px;
    color: var(--muted);
    font-size: 10px;
  }
}
.source-dialog {
  width: min(540px, calc(100% - 40px));
  padding: 25px;
  color: var(--text);
  background: var(--panel-raised);
  border: 1px solid var(--line-strong);
  border-radius: 13px;
  box-shadow: var(--shadow);
  &::backdrop {
    background: rgba(5, 8, 15, 0.72);
    backdrop-filter: blur(5px);
  }
  h2 {
    font-size: 21px;
    margin: 17px 0 14px;
  }
  p {
    color: var(--secondary-text);
    font-size: 13px;
    line-height: 1.9;
  }
  a {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    color: var(--accent);
    text-decoration: none;
    font-size: 13px;
    padding: 14px 0;
    border-bottom: 1px solid var(--line);
  }
  .source-dialog__note {
    font-size: 11px;
    color: var(--muted);
    margin-bottom: 0;
  }
}
.source-dialog__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
@media (min-width: 1700px) {
  .game-hero__art {
    background-position: right 46%;
  }
}
@media (max-width: 1050px) {
  .topbar__inner {
    gap: 20px;
    padding-inline: 25px;
  }
  .page-shell {
    padding-inline: 25px;
  }
  .quick-search {
    width: auto;
    padding: 8px;
    span,
    kbd {
      display: none;
    }
  }
}
@media (max-width: 760px) {
  .topbar__inner {
    min-height: 75px;
    gap: 18px;
    padding-inline: 18px;
  }
  .brand > span:last-child {
    display: none;
  }
  .topbar-actions {
    gap: 10px;
  }
  .page-shell {
    padding: 18px 18px 0;
  }
  .game-hero__content {
    padding: 24px;
  }
  .game-hero__art {
    left: 20%;
    opacity: 0.4;
  }
  .hero-meta {
    flex-wrap: wrap;
  }
  .section-tabs {
    gap: 24px;
  }
}
@media (max-width: 520px) {
  .game-picker {
    display: none;
  }
  .page-shell {
    padding-inline: 13px;
  }
  .game-hero__content {
    padding: 22px 17px;
    h1 {
      font-size: 27px;
    }
    p {
      max-width: 195px;
      font-size: 11px;
      line-height: 1.7;
    }
  }
  .hero-meta {
    font-size: 9px;
    gap: 8px;
  }
  .section-tabs {
    gap: 20px;
    a {
      gap: 6px;
      font-size: 12px;
    }
  }
  .tab-count {
    display: none;
  }
  .page-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
