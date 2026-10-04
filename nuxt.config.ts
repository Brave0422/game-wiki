/**
 * @author Brave
 * @date 2026-10-04T17:29:14+08:00
 * @description 配置纯客户端游戏百科、严格类型检查和静态站点构建。
 */
import { GAME_LIBRARY } from "./app/constants/games";

export default defineNuxtConfig({
  compatibilityDate: "2026-10-04",
  ssr: false,
  devtools: { enabled: false },
  app: {
    head: {
      htmlAttrs: { lang: "zh-CN" },
      title: "游戏图鉴 · 游戏百科",
      link: [{ rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }],
      meta: [
        {
          name: "description",
          content:
            "选择游戏，查询游戏内资料、获取方式与机制攻略，各游戏专区按内容提供独立栏目。",
        },
        { name: "theme-color", content: "#101013" },
      ],
    },
  },
  devServer: {
    host: "127.0.0.1",
    port: 3000,
  },
  nitro: {
    preset: "static",
    prerender: {
      crawlLinks: false,
      routes: [
        "/",
        ...GAME_LIBRARY.filter((game) => game.status === "available").flatMap(
          (game) =>
            game.sections.map((section) => `/games/${game.id}/${section.id}`),
        ),
      ],
    },
  },
  typescript: {
    strict: true,
  },
  vite: {
    server: {
      strictPort: true,
    },
  },
});
