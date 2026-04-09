import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'

export type AppLocale = 'zh-CN' | 'en-US'

const elementLocaleMap: Record<AppLocale, any> = {
  'zh-CN': zhCn,
  'en-US': en,
}

export const useLocaleStore = defineStore('locale', () => {
  const currentLocale = ref<AppLocale>((localStorage.getItem('locale') as AppLocale) || 'zh-CN')
  const elementLocale = computed(() => elementLocaleMap[currentLocale.value])

  function setLocale(locale: AppLocale) {
    currentLocale.value = locale
    localStorage.setItem('locale', locale)
    document.documentElement.setAttribute('lang', locale === 'zh-CN' ? 'zh' : 'en')
  }

  // init lang attribute
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('lang', currentLocale.value === 'zh-CN' ? 'zh' : 'en')
  }

  return {
    currentLocale,
    elementLocale,
    setLocale,
  }
})
