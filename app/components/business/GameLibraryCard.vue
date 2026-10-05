<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-04T19:09:33+08:00
 * @description 展示游戏封面、开放状态和独立栏目，已开放游戏可进入专区。
 */
import {
  ArrowUpRight,
  BookOpen,
  Gamepad2,
  Layers3,
  Map,
  Puzzle,
  Trophy,
  Sparkles,
  Swords,
} from "@lucide/vue";
import { NuxtLink } from "#components";
import { getGameEntryPath } from "~/constants/games";
import type { GameDefinition } from "~/types/game.types";

const props = defineProps<{ game: GameDefinition }>();
const entryPath = computed(() => getGameEntryPath(props.game));
const baseUrl = useRuntimeConfig().app.baseURL.replace(/\/$/, "");
const sectionIcons = {
  "book-open": BookOpen,
  map: Map,
  puzzle: Puzzle,
  layers: Layers3,
  trophy: Trophy,
  sparkles: Sparkles,
  swords: Swords,
};
</script>

<template>
  <component
    :is="entryPath ? NuxtLink : 'article'"
    :to="entryPath ?? undefined"
    class="game-card"
    :class="{ 'game-card--available': entryPath }"
    :style="{ '--game-accent': game.accent ?? 'var(--accent)' }"
  >
    <div class="game-card__cover">
      <img
        v-if="game.cover"
        :src="`${baseUrl}${game.cover}`"
        :alt="`${game.name}游戏封面`"
        width="460"
        height="215"
      />
      <Gamepad2 v-else :size="44" />
      <span class="game-card__status" :class="{ 'is-available': entryPath }"
        ><span />{{ entryPath ? "已收录" : "待收录" }}</span
      >
    </div>
    <div class="game-card__body">
      <div class="game-card__title">
        <h2>{{ game.name }}</h2>
        <ArrowUpRight v-if="entryPath" :size="20" />
      </div>
      <p class="game-card__english">{{ game.englishName }}</p>
      <div class="game-card__genres">
        <span v-for="genre in game.genres" :key="genre">{{ genre }}</span>
      </div>
      <div class="game-card__bottom">
        <template v-if="entryPath">
          <span v-for="section in game.sections" :key="section.id"
            ><component :is="sectionIcons[section.icon]" :size="14" />{{
              section.label
            }}</span
          >
          <span class="game-card__entry">进入专区</span>
        </template>
        <span v-else class="game-card__pending">资料整理中，敬请期待</span>
      </div>
    </div>
  </component>
</template>

<style scoped lang="scss">
.game-card {
  display: block;
  overflow: hidden;
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 13px;
  background: var(--panel);
  text-decoration: none;
  transition:
    border-color 160ms ease,
    transform 160ms ease,
    box-shadow 160ms ease;
}
.game-card--available:hover {
  transform: translateY(-4px);
  border-color: var(--game-accent);
  box-shadow: var(--shadow);
  .game-card__title > svg {
    color: var(--game-accent);
    transform: translate(2px, -2px);
  }
}
.game-card__cover {
  position: relative;
  display: grid;
  place-items: center;
  aspect-ratio: 460 / 215;
  overflow: hidden;
  background: var(--hover);
  color: var(--dimmed);
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}
.game-card__status {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 9px;
  border: 1px solid #ffffff1c;
  border-radius: 5px;
  background: #111217de;
  color: #c3c4d1;
  font-size: 10px;
  backdrop-filter: blur(8px);
  > span {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: currentColor;
  }
  &.is-available {
    color: #77dfc2;
  }
}
.game-card__body {
  padding: 20px 20px 0;
}
.game-card__title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  h2 {
    margin: 0;
    font-size: 19px;
    font-weight: 650;
    letter-spacing: 0.3px;
  }
  > svg {
    color: var(--muted);
    transition: transform 160ms ease;
  }
}
.game-card__english {
  margin: 4px 0 15px;
  min-height: 18px;
  color: var(--muted);
  font-size: 10px;
}
.game-card__genres {
  display: flex;
  gap: 7px;
  margin-bottom: 21px;
  span {
    padding: 2px 7px;
    border: 1px solid var(--line);
    border-radius: 4px;
    color: var(--secondary-text);
    font-size: 10px;
  }
}
.game-card__bottom {
  display: flex;
  align-items: center;
  gap: 13px;
  min-height: 51px;
  border-top: 1px solid var(--line);
  color: var(--secondary-text);
  font-size: 11px;
  > span {
    display: flex;
    align-items: center;
    gap: 5px;
  }
}
.game-card__entry {
  margin-left: auto;
  color: var(--accent);
  font-size: 10px;
}
.game-card__pending {
  color: var(--dimmed);
}
@media (prefers-reduced-motion: reduce) {
  .game-card,
  .game-card__title > svg {
    transition: none;
  }
  .game-card--available:hover {
    transform: none;
  }
}
</style>
