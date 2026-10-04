<script setup lang="ts">
/**
 * @author Brave
 * @date 2026-10-04T17:43:08+08:00
 * @description 使用原生对话框展示词条完整效果、成长说明、特殊获取和可分享链接。
 */
import {
  ArrowUpRight,
  Check,
  Heart,
  Link,
  PackageOpen,
  Sparkles,
  X,
} from '@lucide/vue';
import type { WikiEntry } from '~/types/wiki.types';
import { WIKI_CATEGORIES } from '~/constants/wiki';

const props = defineProps<{ entry: WikiEntry | null; isFavorite: boolean }>();
const emit = defineEmits<{ close: []; 'toggle-favorite': [id: string] }>();
const dialog = ref<HTMLDialogElement | null>(null);
const copyStatus = ref('');
let previousOverflow = '';
let hasScrollLock = false;
const baseURL = useRuntimeConfig().app.baseURL;
const categoryLabel = computed(
  () =>
    WIKI_CATEGORIES.find((category) => category.id === props.entry?.category)
      ?.label ?? '词条',
);
const imageUrl = computed(
  () =>
    `${baseURL.replace(/\/$/, '')}/${props.entry?.image.replace(/^\//, '') ?? ''}`,
);

watch(
  () => props.entry,
  async () => {
    copyStatus.value = '';
    await nextTick();
    if (props.entry && dialog.value && !dialog.value.open) {
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      hasScrollLock = true;
      dialog.value.showModal();
    } else if (!props.entry && dialog.value?.open) {
      dialog.value.close();
      releaseScrollLock();
    }
  },
  { immediate: true },
);

/** 只在点到原生对话框外部遮罩时关闭，保留内容区的点击。 */
function handleBackdropClick(event: MouseEvent): void {
  const bounds = dialog.value?.getBoundingClientRect();
  if (
    bounds &&
    event.target === dialog.value &&
    (event.clientX < bounds.left ||
      event.clientX > bounds.right ||
      event.clientY < bounds.top ||
      event.clientY > bounds.bottom)
  )
    emit('close');
}

async function handleCopyLink(): Promise<void> {
  try {
    await navigator.clipboard.writeText(window.location.href);
    copyStatus.value = '链接已复制';
  } catch {
    copyStatus.value = '请复制地址栏中的词条链接';
  }
}

function releaseScrollLock(): void {
  if (!hasScrollLock) return;
  document.body.style.overflow = previousOverflow;
  hasScrollLock = false;
}

onBeforeUnmount(releaseScrollLock);
</script>

<template>
  <dialog
    ref="dialog"
    class="entry-dialog"
    aria-labelledby="entry-detail-title"
    @cancel.prevent="emit('close')"
    @click="handleBackdropClick"
  >
    <template v-if="entry">
      <header class="entry-dialog__header">
        <span class="eyebrow">NEON ABYSS / {{ categoryLabel }}</span
        ><button
          type="button"
          class="icon-button"
          aria-label="关闭词条详情"
          @click="emit('close')"
        >
          <X :size="20" />
        </button>
      </header>
      <div class="entry-dialog__identity">
        <span class="entry-dialog__image"
          ><img
            class="pixel-image"
            :src="imageUrl"
            :alt="entry.name"
            width="76"
            height="76"
        /></span>
        <div>
          <h2 id="entry-detail-title">{{ entry.name }}</h2>
          <p v-if="entry.englishName">{{ entry.englishName }}</p>
          <div class="detail-tags">
            <span>{{ categoryLabel }}</span
            ><span v-for="tag in entry.tags" :key="tag">{{ tag }}</span>
          </div>
        </div>
      </div>
      <section class="detail-section">
        <h3>作用效果</h3>
        <p class="detail-description">{{ entry.description }}</p>
      </section>
      <section v-if="entry.specialAcquisition" class="special-acquisition">
        <h3><Sparkles :size="15" />特殊获取方式</h3>
        <p>{{ entry.specialAcquisition }}</p>
      </section>
      <section v-if="entry.acquisition" class="detail-section">
        <h3><PackageOpen :size="15" />获取说明</h3>
        <p>{{ entry.acquisition }}</p>
      </section>
      <section v-if="entry.notes?.length" class="detail-section">
        <h3>{{ entry.category === 'pets' ? '成长与补充说明' : '补充说明' }}</h3>
        <ul>
          <li v-for="note in entry.notes" :key="note">{{ note }}</li>
        </ul>
      </section>
      <section v-if="entry.sources?.length" class="detail-sources">
        <h3>参考资料</h3>
        <a
          v-for="(source, index) in entry.sources"
          :key="`${source.url}-${index}`"
          :href="source.url"
          target="_blank"
          rel="noopener noreferrer"
          >{{ source.label }}<ArrowUpRight :size="12"
        /></a>
      </section>
      <footer class="entry-dialog__footer">
        <button
          type="button"
          class="secondary-button"
          :class="{ 'is-favorite': isFavorite }"
          :aria-pressed="isFavorite"
          @click="emit('toggle-favorite', entry.id)"
        >
          <Heart :size="15" :fill="isFavorite ? 'currentColor' : 'none'" />{{
            isFavorite ? '已收藏' : '收藏词条'
          }}</button
        ><button type="button" class="secondary-button" @click="handleCopyLink">
          <Check v-if="copyStatus === '链接已复制'" :size="15" /><Link
            v-else
            :size="15"
          />{{ copyStatus === '链接已复制' ? copyStatus : '分享词条' }}
        </button>
      </footer>
      <p
        v-if="copyStatus && copyStatus !== '链接已复制'"
        class="copy-status"
        aria-live="polite"
      >
        {{ copyStatus }}
      </p>
    </template>
  </dialog>
</template>

<style scoped lang="scss">
.entry-dialog {
  width: min(650px, calc(100vw - 36px));
  max-height: calc(100dvh - 64px);
  padding: 27px 30px 25px;
  background: var(--panel-raised);
  color: var(--text);
  border: 1px solid var(--line-strong);
  border-radius: 14px;
  box-shadow: var(--shadow);
  overscroll-behavior: contain;
  &::backdrop {
    background: #060811b8;
    backdrop-filter: blur(6px);
  }
}
.entry-dialog__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 23px;
}
.entry-dialog__identity {
  display: flex;
  align-items: center;
  gap: 22px;
  padding-bottom: 25px;
  border-bottom: 1px solid var(--line);
  > div {
    min-width: 0;
  }
  h2 {
    font-size: 25px;
    margin-bottom: 4px;
  }
  p {
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 11px;
  }
}
.entry-dialog__image {
  display: grid;
  place-items: center;
  width: 92px;
  height: 92px;
  flex-shrink: 0;
  background: var(--icon-bg);
  border: 1px solid var(--line);
  border-radius: 12px;
  img {
    width: 64px;
    height: 64px;
  }
}
.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  span {
    padding: 2px 7px;
    color: var(--muted);
    background: var(--hover);
    border-radius: 4px;
    font-size: 10px;
  }
}
.detail-section {
  margin-top: 24px;
  h3 {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 13px;
    margin-bottom: 10px;
  }
  p,
  li {
    color: var(--secondary-text);
    font-size: 13px;
    line-height: 1.9;
    overflow-wrap: anywhere;
  }
  p {
    white-space: pre-line;
    margin: 0;
  }
  ul {
    margin: 0;
    padding-left: 18px;
  }
  li + li {
    margin-top: 8px;
  }
}
.special-acquisition {
  margin-top: 22px;
  padding: 16px 18px;
  background: var(--special-soft);
  border: 1px solid color-mix(in srgb, var(--special) 24%, transparent);
  border-radius: 8px;
  h3 {
    display: flex;
    align-items: center;
    gap: 7px;
    color: var(--special);
    font-size: 12px;
    margin-bottom: 9px;
  }
  p {
    font-size: 12px;
    color: var(--secondary-text);
    margin: 0;
    line-height: 1.9;
  }
}
.detail-sources {
  margin-top: 26px;
  padding-top: 19px;
  border-top: 1px solid var(--line);
  h3 {
    color: var(--muted);
    font-size: 10px;
    font-weight: 500;
    margin-bottom: 8px;
  }
  a {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin: 0 15px 7px 0;
    font-size: 10px;
    color: var(--accent);
    text-decoration: none;
  }
}
.entry-dialog__footer {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
  .is-favorite {
    color: var(--accent);
    border-color: var(--accent-border);
    background: var(--accent-soft);
  }
}
.copy-status {
  margin: 12px 0 0;
  font-size: 11px;
  color: var(--muted);
}
@media (max-width: 580px) {
  .entry-dialog {
    padding: 20px;
  }
  .entry-dialog__identity {
    gap: 16px;
    h2 {
      font-size: 21px;
    }
  }
  .entry-dialog__image {
    width: 75px;
    height: 75px;
    img {
      width: 51px;
      height: 51px;
    }
  }
}
</style>
