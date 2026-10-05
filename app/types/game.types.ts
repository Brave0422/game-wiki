/**
 * @author Brave
 * @date 2026-10-04T19:06:04+08:00
 * @description 定义游戏目录及各游戏独立配置的内容栏目契约。
 */

/** 栏目图标仅约束视觉选择，栏目 ID 可按游戏内容自由扩展。 */
export type GameSectionIcon =
  "book-open" | "map" | "puzzle" | "layers" | "trophy" | "sparkles" | "swords";

export interface GameSectionDefinition {
  id: string;
  label: string;
  icon: GameSectionIcon;
}

export interface GameDefinition {
  id: string;
  name: string;
  englishName: string;
  shortName: string;
  genres: string[];
  /** available 游戏可进入专区，planned 游戏仅在目录展示建设状态。 */
  status: "available" | "planned";
  cover?: string;
  accent?: string;
  /** 按导航顺序排列，首栏目作为专区默认入口。 */
  sections: GameSectionDefinition[];
  description?: string;
}
