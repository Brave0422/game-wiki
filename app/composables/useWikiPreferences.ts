/**
 * @author Brave
 * @date 2026-10-04T17:35:49+08:00
 * @description 在浏览器本地保存收藏与主题，供导航、卡片和详情共用。
 */
const FAVORITES_KEY = 'game-wiki:neon-abyss:favorites';
const THEME_KEY = 'game-wiki:theme';

/** 返回当前浏览器的收藏及主题；存储不可用时保留本次会话的交互。 */
export function useWikiPreferences() {
  const favoriteIds = useState<string[]>('wiki-favorite-ids', () => []);
  const isLightTheme = useState('wiki-light-theme', () => false);
  const isInitialized = useState('wiki-preferences-initialized', () => false);

  function persistFavorites(): void {
    try {
      localStorage.setItem(FAVORITES_KEY, JSON.stringify(favoriteIds.value));
    } catch {
      /* 浏览器阻止持久化时仍允许当前会话使用收藏。 */
    }
  }

  function toggleFavorite(id: string): void {
    favoriteIds.value = favoriteIds.value.includes(id)
      ? favoriteIds.value.filter((entryId) => entryId !== id)
      : [...favoriteIds.value, id];
    persistFavorites();
  }

  function applyTheme(): void {
    document.documentElement.dataset.theme = isLightTheme.value
      ? 'light'
      : 'dark';
  }

  function toggleTheme(): void {
    isLightTheme.value = !isLightTheme.value;
    applyTheme();
    try {
      localStorage.setItem(THEME_KEY, isLightTheme.value ? 'light' : 'dark');
    } catch {
      /* 主题选择可在禁用本地存储的环境中继续生效。 */
    }
  }

  onMounted(() => {
    if (isInitialized.value) return;
    try {
      const storedFavorites: unknown = JSON.parse(
        localStorage.getItem(FAVORITES_KEY) ?? '[]',
      );
      if (
        Array.isArray(storedFavorites) &&
        storedFavorites.every((id) => typeof id === 'string')
      ) {
        favoriteIds.value = storedFavorites;
      }
      isLightTheme.value = localStorage.getItem(THEME_KEY) === 'light';
    } catch {
      favoriteIds.value = [];
    }
    applyTheme();
    isInitialized.value = true;
  });

  return { favoriteIds, isLightTheme, toggleFavorite, toggleTheme };
}
