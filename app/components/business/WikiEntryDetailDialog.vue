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
import { CIVILIZATION_CATEGORIES, HADES_CATEGORIES, WIKI_CATEGORIES } from '~/constants/wiki';
import { getHadesBoonTheme, getHadesBoonThemeStyle, getHadesBoonTagStyle } from '~/utils/hades-boons';

const props = withDefaults(
  defineProps<{
    entry: WikiEntry | null;
    isFavorite: boolean;
    gameName?: string;
  }>(),
  { gameName: 'NEON ABYSS' },
);
const emit = defineEmits<{ close: []; 'toggle-favorite': [id: string] }>();
const dialog = ref<HTMLDialogElement | null>(null);
const copyStatus = ref('');
let isMounted = false;
let previousOverflow = '';
let hasScrollLock = false;
const baseURL = useRuntimeConfig().app.baseURL;
const categoryLabel = computed(
  () =>
    [...WIKI_CATEGORIES, ...HADES_CATEGORIES, ...CIVILIZATION_CATEGORIES].find((category) => category.id === props.entry?.category)
      ?.label ?? '词条',
);
const isCivilization = computed(() => props.entry?.id.startsWith('civ6-') ?? false);
const detailTags = computed(() => props.entry?.tags.filter((tag) => tag !== categoryLabel.value) ?? []);
const imageUrl = computed(
  () =>
    `${baseURL.replace(/\/$/, '')}/${props.entry?.image.replace(/^\//, '') ?? ''}`,
);

/** 初次从分享链接进入时，必须等对话框已挂载到文档后再调用 showModal。 */
function syncEntryDialog(): void {
  if (!isMounted) return;
  if (props.entry && dialog.value && !dialog.value.open) {
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    hasScrollLock = true;
    dialog.value.showModal();
  } else if (!props.entry && dialog.value?.open) {
    dialog.value.close();
    releaseScrollLock();
  }
}

watch(
  () => props.entry,
  async () => {
    copyStatus.value = '';
    await nextTick();
    syncEntryDialog();
  },
  { flush: 'post' },
);
const boonTheme = computed(() => getHadesBoonTheme(props.entry));
onMounted(() => {
  isMounted = true;
  syncEntryDialog();
});

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
    :class="{ 'entry-dialog--boon': Boolean(boonTheme), 'entry-dialog--civilization': isCivilization }"
    :style="getHadesBoonThemeStyle(boonTheme)"
    aria-labelledby="entry-detail-title"
    @cancel.prevent="emit('close')"
    @click="handleBackdropClick"
  >
    <template v-if="entry">
      <header class="entry-dialog__header">
        <span class="eyebrow">{{ gameName }} / {{ categoryLabel }}</span
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
            :class="{ 'pixel-image': !entry.id.startsWith('hades-') && !isCivilization }"
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
            ><span
              v-for="tag in detailTags"
              :key="tag"
              :class="{ 'detail-tags__boon': Boolean(boonTheme && getHadesBoonTagStyle(tag)) }"
              :style="boonTheme ? getHadesBoonTagStyle(tag) : undefined"
            >{{ tag }}</span>
          </div>
        </div>
      </div>
      <section class="detail-section">
        <h3>{{ isCivilization ? '百科介绍' : entry.category === 'characters' ? '角色特性' : '作用效果' }}</h3>
        <p class="detail-description">{{ entry.description }}</p>
      </section>
      <section v-if="entry.stats?.length" class="detail-section">
        <h3>{{ entry.category === 'characters' ? '初始属性' : '属性说明' }}</h3>
        <dl class="detail-stats">
          <div v-for="stat in entry.stats" :key="stat.label">
            <dt>{{ stat.label }}</dt>
            <dd>{{ stat.value }}</dd>
          </div>
        </dl>
      </section>
      <!-- 每种形态独立列出 I–V 级效果、相邻级增量及本级消耗。 -->
      <section v-if="entry.aspects?.length" class="detail-section">
        <h3>武器形态与升级</h3>
        <p>每级消耗泰坦之血。I 级是首次解锁的效果，增量从 II 级起与上一级比较。</p>
        <article
          v-for="aspect in entry.aspects"
          :key="aspect.id"
          class="weapon-aspect"
        >
          <div class="weapon-aspect__identity">
            <img
              :src="`${baseURL.replace(/\/$/, '')}${aspect.image}`"
              :alt="aspect.name"
              width="64"
              height="64"
              loading="lazy"
            />
            <h4>{{ aspect.name }}</h4>
          </div>
          <p>{{ aspect.description }}</p>
          <p class="weapon-aspect__acquisition">
            <strong>解锁：</strong>{{ aspect.acquisition }}
          </p>
          <div class="aspect-table-wrapper">
            <table class="aspect-table">
              <caption>{{ aspect.upgradeLabel }}</caption>
              <thead>
                <tr>
                  <th scope="col">等级</th>
                  <th scope="col">升级后属性</th>
                  <th scope="col">本级变化</th>
                  <th scope="col">泰坦之血</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="level in aspect.levels" :key="level.level">
                  <th scope="row">{{ ['I', 'II', 'III', 'IV', 'V'][level.level - 1] }}</th>
                  <td>{{ level.value }}</td>
                  <td>{{ level.delta }}</td>
                  <td>{{ level.cost }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </section>
      <section v-if="entry.specialAcquisition" class="special-acquisition">
        <h3>
          <Sparkles :size="15" />{{ entry.category === 'boons' ? '前置获取条件' : '特殊获取方式' }}
        </h3>
        <p>{{ entry.specialAcquisition }}</p>
      </section>
      <section v-if="entry.acquisition" class="detail-section">
        <h3><PackageOpen :size="15" />{{ isCivilization ? '解锁与使用' : '获取说明' }}</h3>
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
.entry-dialog--boon {
  background: color-mix(in srgb, rgb(var(--boon-rgb)) 5%, var(--panel-raised));
  border-color: rgb(var(--boon-rgb));
  .entry-dialog__image {
    background: color-mix(in srgb, rgb(var(--boon-rgb)) 10%, var(--icon-bg));
  }
}
.entry-dialog--civilization {
  border-radius: 5px;
  border-top: 3px solid var(--accent);
  .entry-dialog__image {
    width: 108px;
    height: 108px;
    border-radius: 50%;
    background: radial-gradient(circle at 40% 30%, #275575, #0b243b 75%);
    border-color: var(--accent-border);
    img { width: 96px; height: 96px; }
  }
  .entry-dialog__identity h2 { font-family: "Georgia", "Noto Serif SC", "SimSun", serif; }
}
.detail-tags span.detail-tags__boon {
  color: color-mix(in srgb, rgb(var(--boon-rgb)) var(--boon-text-mix), var(--text));
  background: color-mix(in srgb, rgb(var(--boon-rgb)) 10%, var(--panel));
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
    object-fit: contain;
  }
}
.detail-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin: 0;
  > div { padding: 12px; border: 1px solid var(--line); border-radius: 7px; background: var(--panel); }
  dt { font-size: 11px; color: var(--muted); }
  dd { margin: 6px 0 0; font-size: 13px; line-height: 1.7; overflow-wrap: anywhere; }
}
.weapon-aspect {
  margin-top: 18px;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--panel);
  p + p { margin-top: 9px; }
}
.weapon-aspect__identity {
  display: flex; align-items: center; gap: 14px; margin-bottom: 12px;
  img { object-fit: contain; }
  h4 { margin: 0; font-size: 15px; }
}
.weapon-aspect__acquisition { font-size: 12px; }
.aspect-table-wrapper { overflow-x: auto; margin-top: 14px; }
.aspect-table {
  width: 100%; border-collapse: collapse; font-size: 11px; text-align: left;
  caption { text-align: left; color: var(--accent); margin-bottom: 9px; font-weight: 600; }
  th, td { padding: 9px 8px; border-bottom: 1px solid var(--line); line-height: 1.7; }
  thead { color: var(--muted); }
  tbody td:nth-child(3) { color: var(--accent); }
}
@media (max-width: 480px) {
  .detail-stats { grid-template-columns: 1fr; }
  .weapon-aspect { padding: 12px; }
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
