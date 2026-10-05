/**
 * @author Brave
 * @date 2026-10-04T23:23:17+08:00
 * @description 统一哈迪斯神祇和祝福稀有度的配色，供筛选、卡片与详情复用。
 */
import type { CSSProperties } from 'vue';
import type { WikiEntry } from '~/types/wiki.types';

interface HadesBoonTheme {
  name: string;
  rgb: string;
}

/** 来自 LootData.lua 的 LootColor；哈迪斯之援使用 Color.lua 的 HadesVoice。 */
export const HADES_GODS: readonly HadesBoonTheme[] = [
  { name: '宙斯', rgb: '255 255 64' },
  { name: '波塞冬', rgb: '0 200 255' },
  { name: '雅典娜', rgb: '96 64 255' },
  { name: '阿佛洛狄忒', rgb: '255 50 240' },
  { name: '阿尔忒弥斯', rgb: '110 255 0' },
  { name: '阿瑞斯', rgb: '255 20 0' },
  { name: '狄俄尼索斯', rgb: '200 0 255' },
  { name: '得墨忒耳', rgb: '96 189 255' },
  { name: '赫尔墨斯', rgb: '255 90 0' },
  { name: '混沌', rgb: '100 25 255' },
  { name: '哈迪斯', rgb: '242 79 66' },
];

/** 来自 Color.lua 的 BoonPatchLegendary 与 BoonPatchDuo，双重祝福优先。 */
const HADES_BOON_RARITIES: readonly HadesBoonTheme[] = [
  { name: '双重祝福', rgb: '210 255 97' },
  { name: '传奇祝福', rgb: '255 144 0' },
];

export const HADES_BOON_TAG_ORDER = [
  '普通祝福', '传奇祝福', '双重祝福', '攻击', '特殊攻击',
  '投弹', '冲刺', '援助', '贝奥武夫形态',
];

/** 按稀有度、所属神祇确定卡片颜色，避免双重祝福被首位神祇覆盖。 */
export function getHadesBoonTheme(entry: WikiEntry | null): HadesBoonTheme | undefined {
  if (entry?.category !== 'boons' || !entry.id.startsWith('hades-')) return;
  return HADES_BOON_RARITIES.find((theme) => entry.tags.includes(theme.name))
    ?? HADES_GODS.find((theme) => entry.tags.includes(theme.name));
}

/** 将游戏原色传给 CSS，淡背景与文字对比度由深浅主题共同计算。 */
export function getHadesBoonThemeStyle(theme: HadesBoonTheme | undefined): CSSProperties | undefined {
  return theme ? { '--boon-rgb': theme.rgb } : undefined;
}

/** 为神祇或稀有度标签提供相同的颜色变量。 */
export function getHadesBoonTagStyle(tag: string): CSSProperties | undefined {
  return getHadesBoonThemeStyle(
    [...HADES_GODS, ...HADES_BOON_RARITIES].find((theme) => theme.name === tag),
  );
}
