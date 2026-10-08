/**
 * @author Brave
 * @date 2026-10-04T17:35:49+08:00
 * @description 维护各游戏百科分类、分页及专区路径常量。
 */
import type { WikiCategoryDefinition } from "~/types/wiki.types";

export const GAME_BASE_PATH = "/games/neon-abyss";
export const PAGE_SIZE = 24;

export const WIKI_CATEGORIES: WikiCategoryDefinition[] = [
  {
    id: "items",
    label: "道具",
    singular: "件道具",
    caption: "被动效果与道具联动",
  },
  {
    id: "weapons",
    label: "武器",
    singular: "把武器",
    caption: "射击方式与主动能力",
  },
  {
    id: "pets",
    label: "宠物",
    singular: "种宠物",
    caption: "跟随效果与成长能力",
  },
  {
    id: "characters",
    label: "角色",
    singular: "位角色",
    caption: "初始属性、专属特性与异装能力",
  },
];

export const HADES_CATEGORIES: WikiCategoryDefinition[] = [
  { id: "boons", label: "祝福", singular: "种祝福", caption: "众神赐予的能力与前置获取条件" },
  { id: "weapons", label: "武器", singular: "把武器", caption: "六种冥界武器、二十四种形态与逐级升级效果" },
];

export const CIVILIZATION_CATEGORIES: WikiCategoryDefinition[] = [
  { id: "civilizations", label: "文明", singular: "个文明", caption: "文明特色、专属能力与独特单位" },
  { id: "leaders", label: "领袖", singular: "位领袖", caption: "领袖能力、所属文明与历史背景" },
  { id: "units", label: "单位", singular: "种单位", caption: "战斗力、移动力、生产成本与解锁条件" },
  { id: "districts", label: "区域", singular: "种区域", caption: "城市规划、区域特色与解锁条件" },
  { id: "buildings", label: "建筑", singular: "座建筑", caption: "城市发展、建筑产出与建造条件" },
  { id: "wonders", label: "奇观", singular: "座奇观", caption: "世界奇观的独特效果与建造条件" },
  { id: "technologies", label: "科技", singular: "项科技", caption: "科技发展、尤里卡与前置研究" },
  { id: "civics", label: "市政", singular: "项市政", caption: "文化发展、鼓舞与前置市政" },
  { id: "resources", label: "资源", singular: "种资源", caption: "加成、奢侈与战略资源的用途与产出" },
  { id: "concepts", label: "游戏机制", singular: "项机制", caption: "从城市建设到胜利条件，理解文明的运转" },
];
