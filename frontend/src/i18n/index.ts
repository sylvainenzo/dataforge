import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from './locales/en.json'
import fr from './locales/fr.json'

function initialLanguage(): 'en' | 'fr' {
  try {
    const raw = localStorage.getItem('dataforge-ui')
    if (!raw) return 'en'
    const parsed = JSON.parse(raw)
    return parsed?.state?.language === 'fr' ? 'fr' : 'en'
  } catch {
    return 'en'
  }
}

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    fr: { translation: fr },
  },
  lng: initialLanguage(),
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n
