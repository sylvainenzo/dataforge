import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useUiStore } from '@/stores/uiStore'

export function LanguageSync() {
  const language = useUiStore((s) => s.language)
  const { i18n } = useTranslation()

  useEffect(() => {
    if (i18n.language !== language) {
      i18n.changeLanguage(language)
    }
    document.documentElement.setAttribute('lang', language)
  }, [language, i18n])

  return null
}
