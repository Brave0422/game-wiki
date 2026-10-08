/**
 * @author Brave
 * @date 2026-10-04T17:47:59+08:00
 * @description 检查多游戏词条、图片、获取条件、武器形态及文明百科提取记录的完整性。
 */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const readData = (name) => JSON.parse(fs.readFileSync(path.join(root, `app/data/${name}.json`), 'utf8'));
const neonEntries = [...readData('neon-abyss.entries'), ...readData('neon-abyss.characters')];
const hadesEntries = readData('hades.entries');
const civilizationEntries = readData('civilization-vi.entries');
const civilizationSource = readData('civilization-vi.source');
const civilizationCategories = [
  'civilizations', 'leaders', 'units', 'buildings', 'wonders', 'districts',
  'technologies', 'civics', 'resources', 'concepts',
];
const ids = new Set();
const errors = [];
const pngSignature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

function checkImage(image, label, prefix) {
  if (typeof image !== 'string' || !image.startsWith(prefix)) {
    errors.push(`非法图片路径：${label}`);
    return;
  }
  const imagePath = path.resolve(root, 'public', image.slice(1));
  const imageDirectory = path.resolve(root, 'public', prefix.slice(1));
  if (!imagePath.startsWith(`${imageDirectory}${path.sep}`) || !image.endsWith('.png')) {
    errors.push(`图片路径越界或格式错误：${label} / ${image}`);
    return;
  }
  if (!fs.existsSync(imagePath)) errors.push(`图片不存在：${label} / ${image}`);
  else {
    const bytes = fs.readFileSync(imagePath);
    if (bytes.length < 45 || !bytes.subarray(0, 8).equals(pngSignature) || bytes.toString('ascii', 12, 16) !== 'IHDR' || bytes.toString('ascii', bytes.length - 8, bytes.length - 4) !== 'IEND') {
      errors.push(`无效 PNG：${label}`);
    } else if (bytes.readUInt32BE(16) < 1 || bytes.readUInt32BE(20) < 1) {
      errors.push(`图片尺寸无效：${label}`);
    }
  }
}

/** 核对玩家可见的正文，源文件中的本地化键可以保留在提取记录中。 */
function checkCivilizationText(value, label) {
  if (typeof value !== 'string' || !value.trim()) {
    errors.push(`文明百科文本缺失：${label}`);
    return;
  }
  if (/\[(?:ICON_[^\]]+|NEWLINE|TAB|ENDCOLOR|COLOR_[^\]]+|BULLET|[A-Z][A-Z0-9_]+)\]|\bLOC_[A-Z0-9_]+\b|\{[^{}]*\}|<\/?[A-Za-z][^>]*>|\b(?:undefined|null|NaN)\b/.test(value)) {
    errors.push(`文明百科未解析文本：${label}`);
  }
}

function checkCivilizationEntry(entry) {
  if (!entry.id.startsWith('civ6-')) errors.push(`文明百科标识缺少前缀：${entry.id}`);
  for (const field of ['name', 'description', 'acquisition']) {
    checkCivilizationText(entry[field], `${entry.id} / ${field}`);
  }
  for (const field of ['englishName', 'specialAcquisition']) {
    if (entry[field] !== undefined) checkCivilizationText(entry[field], `${entry.id} / ${field}`);
  }
  if (!Array.isArray(entry.tags) || !entry.tags.length) errors.push(`文明百科缺少标签：${entry.id}`);
  else {
    entry.tags.forEach((tag, index) => checkCivilizationText(tag, `${entry.id} / 标签 ${index + 1}`));
    if (new Set(entry.tags).size !== entry.tags.length) errors.push(`文明百科标签重复：${entry.id}`);
  }
  if (entry.notes !== undefined && !Array.isArray(entry.notes)) errors.push(`文明百科备注格式错误：${entry.id}`);
  else entry.notes?.forEach((note, index) => checkCivilizationText(note, `${entry.id} / 备注 ${index + 1}`));
  if (entry.category !== 'concepts' && (!Array.isArray(entry.stats) || !entry.stats.length)) {
    errors.push(`文明百科缺少属性：${entry.id}`);
  }
  if (entry.stats !== undefined && !Array.isArray(entry.stats)) errors.push(`文明百科属性格式错误：${entry.id}`);
  else if (entry.stats) {
    const statLabels = new Set();
    entry.stats.forEach((stat, index) => {
      checkCivilizationText(stat?.label, `${entry.id} / 属性 ${index + 1} 名称`);
      checkCivilizationText(stat?.value, `${entry.id} / 属性 ${index + 1} 数值`);
      if (statLabels.has(stat?.label)) errors.push(`文明百科属性名称重复：${entry.id} / ${stat?.label}`);
      statLabels.add(stat?.label);
    });
  }
  if (!Array.isArray(entry.sources) || !entry.sources.length) errors.push(`文明百科缺少来源：${entry.id}`);
  else entry.sources.forEach((source, index) => {
    checkCivilizationText(source?.label, `${entry.id} / 来源 ${index + 1}`);
    try {
      if (!['https:', 'http:'].includes(new URL(source?.url).protocol)) throw new Error('不支持的来源协议');
    } catch {
      errors.push(`文明百科来源链接错误：${entry.id} / ${source?.url}`);
    }
  });
}

for (const [entries, categories, prefix] of [
  [neonEntries, ['items', 'weapons', 'pets', 'characters'], '/images/neon-abyss/'],
  [hadesEntries, ['boons', 'weapons'], '/images/hades/'],
  [civilizationEntries, civilizationCategories, '/images/civilization-vi/'],
]) {
  for (const entry of entries) {
    if (ids.has(entry.id)) errors.push(`重复标识：${entry.id}`);
    ids.add(entry.id);
    if (!categories.includes(entry.category)) errors.push(`非法分类：${entry.id}`);
    if (!entry.name?.trim() || !entry.description?.trim() || /^[.。…\s]+$/.test(entry.description)) errors.push(`名称或作用缺失：${entry.id}`);
    if (/\{\$|\{#|\{!|〔数值〕|<\/?(?:color|size|b|i)(?:[=>\s]|$)/i.test(entry.description)) errors.push(`未解析文本：${entry.id}`);
    checkImage(entry.image, entry.name, prefix);
    if (prefix === '/images/civilization-vi/') checkCivilizationEntry(entry);
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

// 提取记录与可见词条必须一一对应，避免漏掉分类、图像或资料来源。
for (const category of civilizationCategories) {
  const count = civilizationEntries.filter((entry) => entry.category === category).length;
  if (count === 0) errors.push(`文明百科分类为空：${category}`);
  if (civilizationSource.categoryCounts?.[category] !== count) errors.push(`文明百科分类统计不一致：${category}`);
}
if (civilizationSource.entryCount !== civilizationEntries.length) errors.push('文明百科总数与提取记录不一致');
if (!Array.isArray(civilizationSource.unresolvedTokens) || civilizationSource.unresolvedTokens.length) {
  errors.push('文明百科提取记录含未解析文本');
}
if (!civilizationSource.ruleset?.trim()) errors.push('文明百科提取记录缺少规则集');
const civilizationRecords = Array.isArray(civilizationSource.entries) ? civilizationSource.entries : [];
const recordIds = new Set();
const entriesById = new Map(civilizationEntries.map((entry) => [entry.id, entry]));
for (const record of civilizationRecords) {
  if (recordIds.has(record.id)) errors.push(`文明百科提取记录重复：${record.id}`);
  recordIds.add(record.id);
  const entry = entriesById.get(record.id);
  if (!entry || entry.category !== record.category) errors.push(`文明百科提取记录无法匹配词条：${record.id}`);
  if (typeof record.sourceType !== 'string' || !record.sourceType.trim()) errors.push(`文明百科缺少原始类型：${record.id}`);
  if (typeof record.iconName !== 'string' || !record.iconName.startsWith('ICON_')) errors.push(`文明百科缺少图标记录：${record.id}`);
  if (!Array.isArray(record.sourceFiles) || !record.sourceFiles.length) errors.push(`文明百科词条缺少源文件记录：${record.id}`);
}
for (const entry of civilizationEntries) {
  if (!recordIds.has(entry.id)) errors.push(`文明百科缺少提取记录：${entry.id}`);
}

/** 对游戏配置中容易被原版字段或内部倍率覆盖的值保留回归检查。 */
function checkCivilizationStats(id, expected) {
  const entry = entriesById.get(id);
  if (!entry) {
    errors.push(`文明百科缺少基础词条：${id}`);
    return;
  }
  const stats = new Map((entry.stats ?? []).map((stat) => [stat.label, stat.value]));
  for (const [label, value] of Object.entries(expected)) {
    if (stats.get(label) !== value) errors.push(`文明百科属性与风云变幻规则不一致：${id} / ${label} / 预期 ${value}`);
  }
}
checkCivilizationStats('civ6-UNIT_WARRIOR', { '基础生产力成本': '40', '移动力': '2', '近战战斗力': '20' });
checkCivilizationStats('civ6-UNIT_MODERN_ARMOR', { '每回合消耗资源': '石油 1' });
checkCivilizationStats('civ6-UNIT_GIANT_DEATH_ROBOT', { '每回合消耗资源': '铀 3' });
checkCivilizationStats('civ6-RESOURCE_URANIUM', { '改良后每回合积累': '3', '每单位资源供电量': '16' });
checkCivilizationStats('civ6-TECH_POTTERY', { '所需科技值': '25' });
checkCivilizationStats('civ6-TECH_STEAM_POWER', { '尤里卡加速比例': '40%' });
for (const [id, cost, prerequisite] of [
  ['civ6-UNIT_APOSTLE', '400', '寺庙'],
  ['civ6-UNIT_MISSIONARY', '150', '神社'],
]) {
  checkCivilizationStats(id, { '基础信仰购买成本': cost });
  const entry = entriesById.get(id);
  if (entry?.stats?.some((stat) => stat.label === '基础生产力成本')) errors.push(`信仰购买单位误标生产力成本：${id}`);
  if (!entry?.acquisition.includes(prerequisite)) errors.push(`单位缺少前置建筑：${id} / ${prerequisite}`);
}
for (const [id, prerequisite] of [
  ['civ6-UNIT_MILITARY_ENGINEER', '兵工厂'],
  ['civ6-UNIT_ARCHAEOLOGIST', '考古博物馆'],
  ['civ6-DISTRICT_CAMPUS', '写作'],
]) {
  if (!entriesById.get(id)?.acquisition.includes(prerequisite)) errors.push(`文明百科缺少前置条件：${id} / ${prerequisite}`);
}
if (!entriesById.get('civ6-TECH_STEAM_POWER')?.stats?.some((stat) => stat.label === '解锁内容' && stat.value.includes('铁路'))) {
  errors.push('蒸汽动力缺少风云变幻的铁路解锁内容');
}
const scienceVictory = entriesById.get('civ6-CONCEPT_VICTORY_3')?.description ?? '';
if (!scienceVictory.includes('系外行星') || !scienceVictory.includes('激光站') || /火星反应堆|火星水耕|火星居住舱/.test(scienceVictory)) {
  errors.push('科技胜利未使用完整的风云变幻流程，或残留已删除的原版任务');
}
if (!Array.isArray(civilizationSource.files) || !civilizationSource.files.length) {
  errors.push('文明百科缺少源文件校验记录');
} else {
  const sourcePaths = new Set(civilizationSource.files.map((file) => file.path));
  for (const file of civilizationSource.files) {
    if (typeof file.path !== 'string' || !file.path.trim() || !/^[a-f0-9]{64}$/i.test(file.sha256 ?? '')) {
      errors.push(`文明百科源文件校验记录错误：${file.path}`);
    }
  }
  for (const record of civilizationRecords) {
    for (const sourceFile of record.sourceFiles ?? []) {
      if (!sourcePaths.has(sourceFile)) errors.push(`文明百科源文件未登记：${record.id} / ${sourceFile}`);
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
  console.log(`图鉴校验通过：霓虹深渊 ${neonEntries.length} 条（21 个角色），哈迪斯 ${hadesEntries.length} 条（172 个祝福、6 把武器、24 种形态），文明 VI ${civilizationEntries.length} 条（${civilizationCategories.length} 类）；全部图片、获取条件、升级表和提取记录完整。`);
}
