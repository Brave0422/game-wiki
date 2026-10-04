/**
 * @author Brave
 * @date 2026-10-04T17:47:59+08:00
 * @description 检查图鉴唯一标识、效果文本和本地 PNG 图标，防止缺图或空词条进入发布包。
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const entries = JSON.parse(
  fs.readFileSync(path.join(root, 'app/data/neon-abyss.entries.json'), 'utf8'),
);
const ids = new Set();
const counts = { items: 0, weapons: 0, pets: 0 };
const errors = [];
const pngSignature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

for (const entry of entries) {
  if (ids.has(entry.id)) errors.push(`重复标识：${entry.id}`);
  ids.add(entry.id);
  if (!Object.hasOwn(counts, entry.category))
    errors.push(`非法分类：${entry.id}`);
  else counts[entry.category]++;
  if (
    !entry.name?.trim() ||
    !entry.description?.trim() ||
    /^[.。…\s]+$/.test(entry.description)
  )
    errors.push(`名称或作用缺失：${entry.id}`);
  if (/<\/?(?:color|size|b|i)(?:[=>\s]|$)/i.test(entry.description))
    errors.push(`未清理游戏富文本：${entry.id}`);
  if (
    typeof entry.image !== 'string' ||
    !entry.image.startsWith('/images/neon-abyss/')
  ) {
    errors.push(`非法图片路径：${entry.id}`);
    continue;
  }
  const imagePath = path.join(root, 'public', entry.image.slice(1));
  if (!fs.existsSync(imagePath))
    errors.push(`图标不存在：${entry.name} / ${entry.image}`);
  else if (!fs.readFileSync(imagePath).subarray(0, 8).equals(pngSignature))
    errors.push(`无效 PNG：${entry.name}`);
}

if (errors.length) {
  console.error(errors.join('\n'));
  process.exitCode = 1;
} else {
  console.log(
    `图鉴校验通过：${entries.length} 条，${counts.items} 件道具、${counts.weapons} 把武器、${counts.pets} 种宠物形态；全部图片可用。`,
  );
}
