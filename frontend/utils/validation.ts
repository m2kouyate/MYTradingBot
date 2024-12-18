// utils/validation.ts
import { defineRule, configure } from 'vee-validate'
import * as rules from '@vee-validate/rules'
import { localize } from '@vee-validate/i18n'

export function setupValidation(): void {
  // Регистрируем базовые правила
  Object.keys(rules).forEach(rule => {
    defineRule(rule, rules[rule])
  })

  // Пользовательские правила
  defineRule('positive', (value: number | undefined): boolean | string => {
    if (!value || value <= 0) {
      return 'Значение должно быть больше 0'
    }
    return true
  })

  defineRule('percentage', (value: number | undefined): boolean | string => {
    if (value === undefined || value < 0 || value > 100) {
      return 'Значение должно быть от 0 до 100'
    }
    return true
  })

  // Конфигурация с русской локализацией
  configure({
    generateMessage: localize('ru', {
      messages: {
        required: 'Поле обязательно для заполнения',
        min: 'Минимальное значение: {min}',
        max: 'Максимальное значение: {max}',
        numeric: 'Значение должно быть числом',
        email: 'Некорректный email адрес',
        positive: 'Значение должно быть больше 0',
        percentage: 'Значение должно быть от 0 до 100'
      }
    })
  })
}