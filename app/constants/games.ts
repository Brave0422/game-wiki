/**
 * @author Brave
 * @date 2026-10-04T19:06:04+08:00
 * @description 维护游戏目录、各游戏栏目及可访问的专区入口。
 */
import type { GameDefinition } from "../types/game.types";

export const NEON_ABYSS_GAME: GameDefinition = {
  id: "neon-abyss",
  name: "霓虹深渊",
  englishName: "Neon Abyss",
  shortName: "深渊",
  genres: ["动作", "Roguelike"],
  status: "available",
  cover: "/images/neon-abyss/steam-header.jpg",
  accent: "#f36fa6",
  description: "道具效果、武器能力、宠物进化、角色特性，一处查阅。",
  sections: [
    { id: "encyclopedia", label: "百科", icon: "book-open" },
    { id: "guides", label: "攻略", icon: "map" },
  ],
};

export const HADES_GAME: GameDefinition = {
  id: "hades",
  name: "哈迪斯",
  englishName: "Hades",
  shortName: "哈迪斯",
  genres: ["动作", "Roguelike"],
  status: "available",
  cover: "/images/games/hades-header.jpg",
  accent: "#e88879",
  description: "众神祝福、获取条件、冥界武器与形态成长，一处查阅。",
  sections: [
    { id: "boons", label: "祝福", icon: "sparkles" },
    { id: "weapons", label: "武器", icon: "swords" },
  ],
};

export const CIVILIZATION_GAME: GameDefinition = {
  id: "civilization-vi",
  name: "文明 VI",
  englishName: "Sid Meier's Civilization VI",
  shortName: "文明6",
  genres: ["策略", "回合制"],
  status: "available",
  cover: "/images/games/civilization-vi-header.jpg",
  accent: "#bd9959",
  description: "文明与领袖、城市与奇观、科技与市政，书写你的文明史。",
  sections: [{ id: "encyclopedia", label: "百科", icon: "book-open" }],
};

export const GAME_LIBRARY: GameDefinition[] = [
  NEON_ABYSS_GAME,
  {
    id: "dont-starve",
    name: "饥荒",
    englishName: "Don't Starve",
    shortName: "饥荒",
    genres: ["生存", "沙盒"],
    status: "planned",
    cover: "/images/games/dont-starve-header.jpg",
    accent: "#d4b37c",
    sections: [],
  },
  CIVILIZATION_GAME,
  HADES_GAME,
];

/**
 * 按路由使用的游戏标识查找目录定义。
 * @param gameId - 游戏路由标识
 * @returns 对应游戏，未收录时返回 undefined
 */
export function getGameById(gameId: string): GameDefinition | undefined {
  return GAME_LIBRARY.find((game) => game.id === gameId);
}

/**
 * 获取已开放游戏的默认栏目入口，避免为筹备游戏生成无内容链接。
 * @param game - 游戏目录定义
 * @returns 首栏目路由，未开放或无栏目时返回 null
 */
export function getGameEntryPath(game: GameDefinition): string | null {
  const firstSection = game.sections[0];
  if (game.status !== "available" || !firstSection) return null;
  return `/games/${game.id}/${firstSection.id}`;
}
