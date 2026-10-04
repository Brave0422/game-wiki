<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-04T19:09:33+08:00
 * @description 提供游戏库首页的全站导航与主题切换。
 */
import { Gamepad2, Layers3, Moon, Sun } from "@lucide/vue";

const { isLightTheme, toggleTheme } = useWikiPreferences();
</script>

<template>
  <div class="library-layout">
    <header class="library-header">
      <div class="library-header__inner">
        <NuxtLink class="library-brand" to="/" aria-label="游戏图鉴首页">
          <span class="library-brand__mark"><Layers3 :size="23" /></span>
          <span><strong>游戏图鉴</strong><small>GAME WIKI</small></span>
        </NuxtLink>
        <nav class="library-navigation" aria-label="全站导航">
          <NuxtLink to="/" aria-current="page"
            ><Gamepad2 :size="17" />游戏库</NuxtLink
          >
        </nav>
        <div class="library-header__actions">
          <span>PC · 简体中文</span>
          <button
            class="icon-button"
            type="button"
            :aria-label="isLightTheme ? '切换深色主题' : '切换浅色主题'"
            @click="toggleTheme"
          >
            <Moon v-if="isLightTheme" :size="19" /><Sun v-else :size="19" />
          </button>
        </div>
      </div>
    </header>
    <main class="library-main"><slot /></main>
    <footer class="library-footer">
      <span
        >游戏图鉴
        <span class="library-footer__divider">/</span>
        游戏内资料，一处查阅。</span
      >
      <span>游戏图片与名称归各自权利人所有</span>
    </footer>
  </div>
</template>

<style scoped lang="scss">
.library-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.library-header {
  border-bottom: 1px solid var(--line);
  background: var(--sidebar-bg);
}
.library-header__inner {
  display: flex;
  align-items: center;
  gap: 62px;
  width: min(1320px, 100%);
  min-height: 87px;
  margin: 0 auto;
  padding: 0 44px;
}
.library-brand {
  display: flex;
  align-items: center;
  gap: 11px;
  text-decoration: none;
  strong {
    display: block;
    font-size: 18px;
    letter-spacing: 0.8px;
  }
  small {
    display: block;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 2.8px;
    color: var(--muted);
  }
}
.library-brand__mark {
  display: grid;
  place-items: center;
  width: 39px;
  height: 39px;
  border: 1px solid var(--accent-border);
  border-radius: 11px;
  color: var(--accent);
  background: var(--accent-soft);
}
.library-navigation {
  align-self: stretch;
  display: flex;
  a {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 2px 3px 0;
    border-bottom: 2px solid var(--accent);
    color: var(--accent);
    font-size: 13px;
    font-weight: 600;
    text-decoration: none;
  }
}
.library-header__actions {
  display: flex;
  align-items: center;
  gap: 22px;
  margin-left: auto;
  color: var(--muted);
  font-size: 11px;
}
.library-main {
  flex: 1;
  width: min(1320px, 100%);
  margin: 0 auto;
  padding: 62px 44px 80px;
}
.library-footer {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  width: min(1232px, calc(100% - 88px));
  margin: 0 auto;
  padding: 25px 0;
  border-top: 1px solid var(--line);
  color: var(--dimmed);
  font-size: 11px;
}
.library-footer__divider {
  margin: 0 10px;
  color: var(--line-strong);
}
@media (max-width: 800px) {
  .library-header__inner {
    gap: 30px;
    min-height: 75px;
    padding: 0 24px;
  }
  .library-main {
    padding: 42px 24px 60px;
  }
  .library-footer {
    width: calc(100% - 48px);
  }
}
@media (max-width: 520px) {
  .library-header__inner {
    gap: 22px;
    padding: 0 18px;
  }
  .library-brand strong {
    font-size: 16px;
  }
  .library-header__actions {
    gap: 0;
    > span {
      display: none;
    }
  }
  .library-main {
    padding: 34px 18px 50px;
  }
  .library-footer {
    flex-direction: column;
    gap: 5px;
    width: calc(100% - 36px);
  }
}
</style>
