/**
 * @author Brave
 * @date 2026-10-04T17:35:49+08:00
 * @description 维护霓虹深渊百科分类、分页及专区路径常量。
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
