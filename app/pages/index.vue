<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-04T17:35:49+08:00
 * @description 展示可搜索的游戏库，由用户选择游戏进入对应内容专区。
 */
import { ArrowRight, Gamepad2, Search, X } from "@lucide/vue";
import GameLibraryCard from "~/components/business/GameLibraryCard.vue";
import {
  GAME_LIBRARY,
  NEON_ABYSS_GAME,
  getGameEntryPath,
} from "~/constants/games";

definePageMeta({ layout: "library-layout" });
useHead({ title: "游戏库" });

type LibraryFilter = "all" | "available" | "planned";
const searchTerm = ref("");
const activeFilter = ref<LibraryFilter>("all");
const filters: { id: LibraryFilter; label: string; count: number }[] = [
  { id: "all", label: "全部游戏", count: GAME_LIBRARY.length },
  {
    id: "available",
    label: "已收录",
    count: GAME_LIBRARY.filter((game) => game.status === "available").length,
  },
  {
    id: "planned",
    label: "待收录",
    count: GAME_LIBRARY.filter((game) => game.status === "planned").length,
  },
];
const visibleGames = computed(() => {
  const keyword = searchTerm.value.trim().toLocaleLowerCase();
  return GAME_LIBRARY.filter((game) => {
    const matchesStatus =
      activeFilter.value === "all" || game.status === activeFilter.value;
    const searchableText =
      `${game.name} ${game.englishName} ${game.shortName}`.toLocaleLowerCase();
    return matchesStatus && (!keyword || searchableText.includes(keyword));
  });
});
const neonEntryPath = getGameEntryPath(NEON_ABYSS_GAME);

function resetFilters(): void {
  searchTerm.value = "";
  activeFilter.value = "all";
}
</script>

<template>
  <div>
    <section class="library-intro" aria-labelledby="library-title">
      <div class="library-intro__copy">
        <span class="eyebrow">THE GAME LIBRARY</span>
        <h1 id="library-title">选择游戏，<span>查阅资料。</span></h1>
        <p>道具、武器、角色与游戏机制。找到正在玩的游戏，进入它的资料专区。</p>
      </div>
      <div class="library-intro__mark" aria-hidden="true">
        <Gamepad2 :size="68" :stroke-width="1" /><span>GAME WIKI</span>
      </div>
    </section>

    <section aria-label="游戏目录">
      <div class="library-toolbar">
        <div class="library-filters" role="group" aria-label="按收录状态筛选">
          <button
            v-for="filter in filters"
            :key="filter.id"
            type="button"
            :aria-pressed="activeFilter === filter.id"
            :class="{ 'is-active': activeFilter === filter.id }"
            @click="activeFilter = filter.id"
          >
            {{ filter.label }}<span>{{ filter.count }}</span>
          </button>
        </div>
        <div class="library-search">
          <Search :size="17" />
          <label for="game-search" class="sr-only">搜索游戏名称</label>
          <input
            id="game-search"
            v-model="searchTerm"
            type="search"
            placeholder="搜索游戏名称 / English name"
            autocomplete="off"
          />
          <button
            v-if="searchTerm"
            class="icon-button"
            type="button"
            aria-label="清除游戏搜索"
            @click="searchTerm = ''"
          >
            <X :size="15" />
          </button>
        </div>
      </div>
      <div v-if="visibleGames.length" class="game-grid">
        <GameLibraryCard
          v-for="game in visibleGames"
          :key="game.id"
          :game="game"
        />
      </div>
      <div v-else class="library-empty" role="status">
        <Search :size="28" />
        <h2>没有找到匹配的游戏</h2>
        <p>试试中文名、英文名，或查看全部游戏。</p>
        <button class="secondary-button" type="button" @click="resetFilters">
          查看全部游戏
        </button>
      </div>
      <p class="library-result" role="status" aria-live="polite">
        显示
        {{
          visibleGames.length
        }}
        个游戏<span>·</span>待收录游戏将在资料整理完成后开放
      </p>
    </section>

    <aside
      v-if="neonEntryPath"
      class="library-update"
      aria-label="目前开放的游戏资料"
    >
      <span class="library-update__icon"><Gamepad2 :size="21" /></span>
      <div>
        <strong>霓虹深渊资料已开放</strong>
        <p>道具、武器与宠物图鉴，以及机制与搭配攻略。</p>
      </div>
      <NuxtLink :to="neonEntryPath">查阅资料<ArrowRight :size="16" /></NuxtLink>
    </aside>
  </div>
</template>

<style scoped lang="scss">
.library-intro {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 50px;
  padding: 8px 0 20px;
}
.library-intro__copy {
  position: relative;
  z-index: 1;
  .eyebrow {
    color: var(--accent);
    font-size: 10px;
    letter-spacing: 2.8px;
  }
  h1 {
    margin: 17px 0 17px;
    font-size: clamp(30px, 3.4vw, 43px);
    font-weight: 650;
    line-height: 1.3;
    letter-spacing: 1px;
    span {
      color: var(--secondary-text);
    }
  }
  p {
    margin-bottom: 0;
    color: var(--muted);
    font-size: 13px;
  }
}
.library-intro__mark {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 174px;
  height: 145px;
  padding: 15px 0;
  border: 1px solid var(--accent-border);
  border-radius: 30px;
  color: var(--accent);
  background: radial-gradient(
    ellipse at center,
    var(--accent-soft),
    transparent 80%
  );
  transform: rotate(-7deg);
  span {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 3px;
    opacity: 0.7;
  }
}
.library-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  margin-bottom: 24px;
}
.library-filters {
  display: flex;
  gap: 7px;
  button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 9px 13px;
    border: 1px solid transparent;
    border-radius: 7px;
    color: var(--muted);
    font-size: 12px;
    font-weight: 500;
    span {
      padding: 0 5px;
      border-radius: 3px;
      font-size: 10px;
      background: var(--hover);
    }
    &:hover {
      color: var(--text);
    }
    &.is-active {
      border-color: var(--accent-border);
      color: var(--accent);
      background: var(--accent-soft);
      span {
        background: var(--accent-border);
      }
    }
  }
}
.library-search {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 318px;
  min-height: 40px;
  padding: 0 11px 0 13px;
  border: 1px solid var(--line);
  border-radius: 7px;
  color: var(--muted);
  background: var(--panel);
  &:focus-within {
    border-color: var(--accent);
  }
  input {
    width: 100%;
    min-width: 0;
    padding: 10px 0;
    outline: none;
    border: 0;
    color: var(--text);
    background: transparent;
    font-size: 11px;
    &::placeholder {
      color: var(--dimmed);
    }
    &::-webkit-search-cancel-button {
      display: none;
    }
  }
  .icon-button {
    width: 23px;
    height: 23px;
    flex-shrink: 0;
  }
}
.game-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 21px;
}
.library-result {
  display: flex;
  gap: 10px;
  margin: 18px 0 0;
  color: var(--dimmed);
  font-size: 10px;
  span {
    color: var(--line-strong);
  }
}
.library-update {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 45px;
  padding: 23px 25px;
  border: 1px solid var(--line);
  border-radius: 11px;
  background: linear-gradient(105deg, var(--accent-soft), transparent 85%);
  strong {
    font-size: 13px;
    font-weight: 600;
  }
  p {
    margin: 5px 0 0;
    color: var(--muted);
    font-size: 11px;
  }
  a {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: auto;
    color: var(--accent);
    font-size: 12px;
    text-decoration: none;
  }
}
.library-update__icon {
  display: grid;
  place-items: center;
  width: 43px;
  height: 43px;
  flex-shrink: 0;
  border: 1px solid var(--accent-border);
  border-radius: 11px;
  color: var(--accent);
  background: var(--accent-soft);
}
.library-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  padding: 30px;
  border: 1px dashed var(--line-strong);
  border-radius: 12px;
  color: var(--muted);
  h2 {
    margin: 16px 0 6px;
    color: var(--text);
    font-size: 17px;
  }
  p {
    font-size: 12px;
  }
}
@media (max-width: 1150px) {
  .game-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 800px) {
  .library-intro {
    margin-bottom: 34px;
  }
  .library-intro__mark {
    display: none;
  }
  .library-toolbar {
    flex-wrap: wrap;
    gap: 17px;
  }
  .library-search {
    width: 100%;
  }
}
@media (max-width: 520px) {
  .library-intro__copy h1 {
    font-size: 29px;
  }
  .game-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 18px;
  }
  .library-result {
    display: block;
    span {
      margin: 0 7px;
    }
  }
  .library-update {
    flex-wrap: wrap;
    padding: 19px;
    gap: 13px;
    a {
      width: 100%;
      margin-left: 56px;
    }
  }
}
</style>
