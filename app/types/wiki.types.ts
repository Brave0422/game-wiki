/**
 * @author Brave
 * @date 2026-10-04T17:35:49+08:00
 * @description 定义游戏百科条目、内容来源及攻略的展示契约。
 */
export type WikiCategory = "items" | "weapons" | "pets";

export interface WikiSource {
  label: string;
  url: string;
}

export interface WikiEntry {
  id: string;
  category: WikiCategory;
  name: string;
  englishName?: string;
  description: string;
  image: string;
  tags: string[];
  notes?: string[];
  acquisition?: string;
  specialAcquisition?: string;
  sources?: WikiSource[];
}

export interface WikiSupplement {
  name: string;
  englishName?: string;
  acquisition?: string;
  specialAcquisition?: string;
  notes?: string[];
  tags?: string[];
  sources: WikiSource[];
}

export interface WikiGuide {
  id: string;
  title: string;
  summary: string;
  paragraphs: string[];
  sources: WikiSource[];
}
