/**
 * @author Brave
 * @date 2026-10-04T17:35:49+08:00
 * @description 校验本地条目并合并经来源核对的获取方式和进阶说明。
 */
import rawEntries from '~/data/neon-abyss.entries.json';
import rawSupplements from '~/data/neon-abyss.supplements.json';
import rawGuides from '~/data/neon-abyss.guides.json';
import rawCharacters from '~/data/neon-abyss.characters.json';
import rawHadesEntries from '~/data/hades.entries.json';
import type { WikiEntry, WikiGuide, WikiSupplement } from '~/types/wiki.types';

/** 统一名称与查询文本，使空格、大小写和常见标点不影响搜索。 */
export function normalizeSearch(value: string): string {
  return value
    .normalize('NFKC')
    .toLocaleLowerCase()
    .replace(/[\s·・’'“”"\-_:：，,。!！?？]/g, '');
}

function isStringArray(value: unknown): value is string[] {
  return (
    Array.isArray(value) && value.every((item) => typeof item === 'string')
  );
}

function isEntry(value: unknown): value is WikiEntry {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    typeof value.id === 'string' &&
    'name' in value &&
    typeof value.name === 'string' &&
    'category' in value &&
    ['items', 'weapons', 'pets', 'characters', 'boons'].includes(String(value.category)) &&
    'description' in value &&
    typeof value.description === 'string' &&
    'image' in value &&
    typeof value.image === 'string' &&
    'tags' in value &&
    isStringArray(value.tags)
  );
}

function isSupplement(value: unknown): value is WikiSupplement {
  return (
    typeof value === 'object' &&
    value !== null &&
    'name' in value &&
    typeof value.name === 'string' &&
    'sources' in value &&
    Array.isArray(value.sources)
  );
}

function isGuide(value: unknown): value is WikiGuide {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    typeof value.id === 'string' &&
    'title' in value &&
    typeof value.title === 'string' &&
    'summary' in value &&
    typeof value.summary === 'string' &&
    'paragraphs' in value &&
    isStringArray(value.paragraphs) &&
    'sources' in value &&
    Array.isArray(value.sources)
  );
}

const sourceEntries: unknown = rawEntries;
const sourceSupplements: unknown = rawSupplements;
const sourceGuides: unknown = rawGuides;

if (!Array.isArray(sourceEntries) || !sourceEntries.every(isEntry)) {
  throw new Error('百科数据格式不符合条目契约。');
}

const supplements = Array.isArray(sourceSupplements)
  ? sourceSupplements.filter(isSupplement)
  : [];
const supplementByName = new Map(
  supplements.map((entry) => [normalizeSearch(entry.name), entry]),
);
const supplementByEnglishName = new Map(
  supplements
    .filter((entry) => entry.englishName)
    .map((entry) => [normalizeSearch(entry.englishName ?? ''), entry]),
);

export const WIKI_ENTRIES: WikiEntry[] = [...sourceEntries, ...validateEntries(rawCharacters)].map((entry) => {
  const supplement =
    supplementByName.get(normalizeSearch(entry.name)) ??
    supplementByEnglishName.get(normalizeSearch(entry.englishName ?? ''));
  if (!supplement) return entry;

  return {
    ...entry,
    englishName: entry.englishName ?? supplement.englishName,
    acquisition: supplement.acquisition ?? entry.acquisition,
    specialAcquisition:
      supplement.specialAcquisition ?? entry.specialAcquisition,
    notes: [...new Set([...(entry.notes ?? []), ...(supplement.notes ?? [])])],
    tags: [...new Set([...entry.tags, ...(supplement.tags ?? [])])],
    sources: [...(entry.sources ?? []), ...supplement.sources],
  };
});

/** 校验每个游戏的完整数据集，避免静默丢弃错误词条。 */
function validateEntries(value: unknown): WikiEntry[] {
  if (!Array.isArray(value) || !value.every(isEntry)) {
    throw new Error('百科数据格式不符合条目契约。');
  }
  return value;
}

export const HADES_ENTRIES = validateEntries(rawHadesEntries);

/** 获取当前游戏的图鉴，用于目录、统计及收藏。 */
export function getEntriesByGame(gameId: string): WikiEntry[] {
  return gameId === 'hades' ? HADES_ENTRIES : WIKI_ENTRIES;
}

export const WIKI_GUIDES: WikiGuide[] = Array.isArray(sourceGuides)
  ? sourceGuides.filter(isGuide)
  : [];

/** 按词条名称、效果、获取方式和标签匹配全部查询片段。 */
export function matchesEntry(entry: WikiEntry, query: string): boolean {
  const haystack = normalizeSearch(
    [
      entry.name,
      entry.englishName,
      entry.description,
      ...entry.tags,
      ...(entry.notes ?? []),
      entry.acquisition,
      entry.specialAcquisition,
      ...(entry.stats ?? []).flatMap((stat) => [stat.label, stat.value]),
      ...(entry.aspects ?? []).flatMap((aspect) => [aspect.name, aspect.description, aspect.acquisition, aspect.upgradeLabel]),
    ]
      .filter(Boolean)
      .join(' '),
  );
  return query
    .trim()
    .split(/\s+/)
    .every((part) => haystack.includes(normalizeSearch(part)));
}
