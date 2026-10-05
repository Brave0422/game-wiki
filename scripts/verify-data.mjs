/**
 * @author Brave
 * @date 2026-10-04T17:47:59+08:00
 * @description 检查多游戏词条、图片、祝福前置条件和武器形态逐级数据完整性。
 */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const readData = (name) => JSON.parse(fs.readFileSync(path.join(root, `app/data/${name}.json`), 'utf8'));
const neonEntries = [...readData('neon-abyss.entries'), ...readData('neon-abyss.characters')];
const hadesEntries = readData('hades.entries');
const ids = new Set();
const errors = [];
const pngSignature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

function checkImage(image, label, prefix) {
  if (typeof image !== 'string' || !image.startsWith(prefix)) {
    errors.push(`非法图片路径：${label}`);
    return;
  }
  const imagePath = path.join(root, 'public', image.slice(1));
  if (!fs.existsSync(imagePath)) errors.push(`图片不存在：${label} / ${image}`);
  else if (!fs.readFileSync(imagePath).subarray(0, 8).equals(pngSignature)) errors.push(`无效 PNG：${label}`);
}

for (const [entries, categories, prefix] of [
  [neonEntries, ['items', 'weapons', 'pets', 'characters'], '/images/neon-abyss/'],
  [hadesEntries, ['boons', 'weapons'], '/images/hades/'],
]) {
  for (const entry of entries) {
    if (ids.has(entry.id)) errors.push(`重复标识：${entry.id}`);
    ids.add(entry.id);
    if (!categories.includes(entry.category)) errors.push(`非法分类：${entry.id}`);
    if (!entry.name?.trim() || !entry.description?.trim() || /^[.。…\s]+$/.test(entry.description)) errors.push(`名称或作用缺失：${entry.id}`);
    if (/\{\$|\{#|\{!|〔数值〕|<\/?(?:color|size|b|i)(?:[=>\s]|$)/i.test(entry.description)) errors.push(`未解析文本：${entry.id}`);
    checkImage(entry.image, entry.name, prefix);
    if (entry.category === 'characters') {
      for (const label of ['生命容器', '护盾', '钥匙', '手雷', '金币']) {
        if (!entry.stats?.some((stat) => stat.label === label && stat.value)) errors.push(`缺少角色属性：${entry.name} / ${label}`);
      }
    }
    if (entry.category === 'boons') {
      if (!entry.acquisition?.trim()) errors.push(`祝福缺少获取方式：${entry.name}`);
      if (entry.tags.includes('双重祝福') && !entry.specialAcquisition) errors.push(`双重祝福缺少前置条件：${entry.name}`);
    }
    if (entry.id.startsWith('hades-') && entry.category === 'weapons') {
      if (entry.aspects?.length !== 4) errors.push(`武器缺少形态：${entry.name}`);
      for (const aspect of entry.aspects ?? []) {
        checkImage(aspect.image, aspect.name, prefix);
        if (!aspect.description || !aspect.acquisition || !aspect.upgradeLabel || aspect.levels.length !== 5) errors.push(`形态数据不完整：${aspect.id}`);
        aspect.levels.forEach((level, index) => {
          if (level.level !== index + 1 || !level.value || !level.delta || !Number.isInteger(level.cost) || level.cost < 1) errors.push(`升级数据不完整：${aspect.id} / ${index + 1}`);
        });
      }
    }
  }
}

assert.equal(neonEntries.filter((entry) => entry.category === 'characters').length, 21);
assert.equal(hadesEntries.filter((entry) => entry.category === 'weapons').length, 6);
assert.equal(hadesEntries.flatMap((entry) => entry.aspects ?? []).length, 24);
assert.equal(readData('hades.source').unresolvedTokens.length, 0);
// 核对需要读取基础值或自定义倍率的三种形态，防止将内部倍率直接展示。
const aspects = new Map(hadesEntries.flatMap((entry) => entry.aspects ?? []).map((aspect) => [aspect.id, aspect]));
assert.deepEqual(aspects.get('BowMarkHomingTrait').levels.map((level) => level.value), ['4', '5', '6', '7', '8']);
assert.deepEqual(aspects.get('ShieldTwoShieldTrait').levels.map((level) => level.value), ['8', '13', '19', '24', '30']);
assert.deepEqual(aspects.get('BowLoadAmmoTrait').levels.map((level) => level.value), ['10 秒', '8 秒', '6.67 秒', '6.15 秒', '5 秒']);

if (errors.length) {
  console.error(errors.join('\n'));
  process.exitCode = 1;
} else {
  console.log(`图鉴校验通过：霓虹深渊 ${neonEntries.length} 条（21 个角色），哈迪斯 ${hadesEntries.length} 条（172 个祝福、6 把武器、24 种形态）；全部图片和升级表完整。`);
}
