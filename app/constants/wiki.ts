/**
 * @author Brave
 * @date 2026-10-04T17:35:49+08:00
 * @description 维护霓虹深渊百科分类、分页及专区路径常量。
 */
import type { WikiCategory } from "~/types/wiki.types";

export const GAME_BASE_PATH = "/games/neon-abyss";
export const PAGE_SIZE = 24;

export const WIKI_CATEGORIES: {
  id: WikiCategory;
  label: string;
  singular: string;
  caption: string;
}[] = [
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
];
