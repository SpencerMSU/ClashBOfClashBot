package utils

import (
	"fmt"
	"time"
)

// PolicyText contains the full policy text - exact copy from Python policy.py
const PolicyText = `
📋 ПОЛИТИКА ИСПОЛЬЗОВАНИЯ, ОПЛАТЫ И ВОЗВРАТОВ

🤖 Наш бот предоставляет услуги по анализу данных Clash of Clans и дополнительные премиум-функции.

💳 УСЛОВИЯ ОПЛАТЫ:
• Оплата производится через YooKassa (Яндекс.Касса)
• Поддерживаются карты Visa, MasterCard, МИР
• Подписка активируется автоматически после успешной оплаты
• Стоимость указана в российских рублях (RUB)

📅 ТИПЫ ПОДПИСОК:
• 1 месяц - полный доступ ко всем функциям на 30 дней
• 3 месяца - экономия по сравнению с ежемесячной оплатой
• 6 месяцев - максимальная экономия для долгосрочного использования

⚡ ПРЕМИУМ ФУНКЦИИ:
• Отслеживание улучшений зданий с уведомлениями
• Расширенная статистика войн и участников
• Множественные профили (до 5 аккаунтов Clash of Clans)
• Приоритетная поддержка

🔄 ПОЛИТИКА ВОЗВРАТОВ:
• Возврат возможен в течение 14 дней с момента покупки
• Возврат производится только при технических проблемах
• Сумма возврата составляет полную стоимость подписки
• Для возврата обратитесь к администратору бота

❌ ОСНОВАНИЯ ДЛЯ ОТКАЗА В ВОЗВРАТЕ:
• Изменение мнения о необходимости подписки
• Нарушение правил использования бота
• Попытка мошенничества или злоупотребления

📞 ПОДДЕРЖКА:
• При возникновении проблем обращайтесь в поддержку
• Техническая поддержка предоставляется бесплатно
• Среднее время ответа: 24 часа

🔒 КОНФИДЕНЦИАЛЬНОСТЬ:
• Мы не передаем ваши данные третьим лицам
• Платежные данные обрабатываются через защищенные каналы YooKassa
• Игровые данные используется только для предоставления услуг

⚖️ ОТВЕТСТВЕННОСТЬ:
• Мы не несем ответственности за временные сбои Clash of Clans API
• Сервис предоставляется "как есть"
• Мы стремимся обеспечить максимальную надежность работы

📜 ИЗМЕНЕНИЯ ПОЛИТИКИ:
• Мы оставляем за собой право изменять данную политику
• О существенных изменениях пользователи будут уведомлены заранее
• Продолжение использования после изменений означает согласие с новыми условиями

📅 Дата последнего обновления: {date}

При использовании Бота вы подтверждаете, что ознакомились и согласны с данной политикой.
`

// GetPolicyText returns the policy text with current date - exact copy from Python get_policy_text()
func GetPolicyText() string {
	currentDate := time.Now().Format("02.01.2006")
	return fmt.Sprintf(PolicyText, currentDate)
}

// GetPolicyURL returns the policy URL - exact copy from Python get_policy_url()  
func GetPolicyURL() string {
	// TODO: Upload to Telegraph and return real URL
	return "https://telegra.ph/POLITIKA-ISPOLZOVANIYA-OPLATY-I-VOZVRATOV-09-27"
}

// GetTermsURL returns the terms of service URL
func GetTermsURL() string {
	// TODO: Upload to Telegraph and return real URL
	return "https://telegra.ph/POLZOVATELSKOE-SOGLASHENIE-09-27"
}

// GetSupportContact returns the support contact information
func GetSupportContact() string {
	return "@ClashBotSupport"
}

// GetRefundPeriodDays returns the refund period in days
func GetRefundPeriodDays() int {
	return 14
}

// IsRefundEligible checks if a subscription is eligible for refund
func IsRefundEligible(purchaseDate time.Time) bool {
	now := time.Now()
	daysSincePurchase := int(now.Sub(purchaseDate).Hours() / 24)
	return daysSincePurchase <= GetRefundPeriodDays()
}

// GetMaxProfilesForSubscription returns max profiles allowed for subscription type
func GetMaxProfilesForSubscription(subscriptionType string) int {
	switch subscriptionType {
	case "premium_1month", "premium_3months", "premium_6months", "premium_1year":
		return 3 // Premium allows 3 profiles
	case "proplus_1month", "proplus_3months", "proplus_6months", "proplus_1year", "proplus_permanent":
		return 5 // PRO PLUS allows 5 profiles
	default:
		return 1 // Free users get 1 profile
	}
}