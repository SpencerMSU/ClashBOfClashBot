package org.example.config;

public class BotConfigTest {
    
    public static void main(String[] args) {
        // Простая проверка что конфигурация загружается без ошибок
        System.out.println("Тестирование конфигурации...");
        
        try {
            // Устанавливаем тестовые значения для обязательных параметров
            System.setProperty("bot.token", "test_token");
            System.setProperty("bot.username", "test_username");
            System.setProperty("coc.api.token", "test_coc_token");
            
            // Тестируем загрузку конфигурации с переменными окружения
            System.setProperty("app.clan.tag", "#TEST123");
            System.setProperty("app.htmls.directory", "test/htmls");
            
            // Проверяем что конфигурация работает
            String clanTag = BotConfig.CLAN_TAG;
            String htmlsDir = BotConfig.HTMLS_DIRECTORY;
            
            System.out.println("✓ Клан тег: " + clanTag);
            System.out.println("✓ Директория HTML: " + htmlsDir);
            
            // Проверяем значения по умолчанию
            if ("#TEST123".equals(clanTag) && "test/htmls".equals(htmlsDir)) {
                System.out.println("✓ Конфигурация работает корректно!");
            } else {
                System.err.println("✗ Ошибка в конфигурации");
                System.exit(1);
            }
            
        } catch (Exception e) {
            System.err.println("✗ Ошибка при тестировании конфигурации: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}