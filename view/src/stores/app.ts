import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { i18n, readStoredLocale, LOCALE_STORAGE_KEY, type AppLocale } from '@/i18n'

const THEME_STORAGE_KEY = 'networth-theme'
const FONT_SCALE_STORAGE_KEY = 'networth-font-scale'

type Theme = 'dark' | 'light'
export type FontScale = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

const FONT_SCALE_MAP: Record<FontScale, number> = {
  xs: 0.85,
  sm: 0.92,
  md: 1.0,
  lg: 1.1,
  xl: 1.2,
}

function readStoredTheme(): Theme {
  if (typeof window === 'undefined') return 'dark'
  const saved = window.localStorage.getItem(THEME_STORAGE_KEY)
  return saved === 'light' || saved === 'dark' ? saved : 'dark'
}

function applyThemeClass(theme: Theme) {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  if (theme === 'dark') {
    root.classList.add('dark')
    root.classList.remove('light')
  } else {
    root.classList.remove('dark')
    root.classList.add('light')
  }
}

function readStoredFontScale(): FontScale {
  if (typeof window === 'undefined') return 'md'
  const saved = window.localStorage.getItem(FONT_SCALE_STORAGE_KEY)
  return saved && saved in FONT_SCALE_MAP ? (saved as FontScale) : 'md'
}

function applyFontScale(scale: FontScale) {
  if (typeof document === 'undefined') return
  document.documentElement.style.setProperty(
    '--app-font-scale',
    String(FONT_SCALE_MAP[scale]),
  )
}

function applyHtmlLang(locale: AppLocale) {
  if (typeof document === 'undefined') return
  document.documentElement.lang = locale
}

export const useAppStore = defineStore('app', () => {
  // Sidebar state
  const sidebarCollapsed = ref(false)
  const isMobile = ref(false)
  const sidebarDrawerVisible = ref(false)

  // Language — store is authoritative: it persists and drives vue-i18n.
  const locale = ref<AppLocale>(readStoredLocale())
  if (i18n.global.locale.value !== locale.value) {
    i18n.global.locale.value = locale.value
  }
  applyHtmlLang(locale.value)

  watch(locale, (next) => {
    i18n.global.locale.value = next
    applyHtmlLang(next)
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(LOCALE_STORAGE_KEY, next)
    }
  })

  // Theme
  const theme = ref<Theme>(readStoredTheme())
  applyThemeClass(theme.value)

  watch(theme, (next) => {
    applyThemeClass(next)
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(THEME_STORAGE_KEY, next)
    }
  })

  // Font scale
  const fontScale = ref<FontScale>(readStoredFontScale())
  applyFontScale(fontScale.value)

  watch(fontScale, (next) => {
    applyFontScale(next)
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(FONT_SCALE_STORAGE_KEY, next)
    }
  })

  const toggleSidebar = () => {
    if (isMobile.value) {
      sidebarDrawerVisible.value = !sidebarDrawerVisible.value
    } else {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }
  }

  const closeSidebarDrawer = () => {
    sidebarDrawerVisible.value = false
  }

  const setMobile = (val: boolean) => {
    isMobile.value = val
  }

  const setLocale = (lang: AppLocale) => {
    locale.value = lang
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  const setFontScale = (s: FontScale) => {
    fontScale.value = s
  }

  const contentClass = computed(() =>
    sidebarCollapsed.value ? 'ml-[64px]' : 'ml-[220px]',
  )

  return {
    sidebarCollapsed,
    isMobile,
    sidebarDrawerVisible,
    locale,
    theme,
    fontScale,
    contentClass,
    toggleSidebar,
    closeSidebarDrawer,
    setMobile,
    setLocale,
    toggleTheme,
    setFontScale,
  }
})
