package org.example.config;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class BotConfig {
    public static final String BOT_TOKEN;
    public static final String BOT_USERNAME;
    public static final String COC_API_TOKEN;
    public static final String HTMLS_DIRECTORY;
    public static final String OUTPUT_JSON;
    public static final String CLAN_TAG;

    static {
        Properties props = new Properties();
        try (InputStream input = BotConfig.class.getClassLoader().getResourceAsStream("config.properties")) {
            if (input == null) {
                System.err.println("Файл config.properties не найден в /resources. Используются переменные окружения или значения по умолчанию.");
                props = new Properties();
            } else {
                props.load(input);
            }
            
            // Основные настройки бота
            BOT_TOKEN = getConfigValue(props, "bot.token", "BOT_TOKEN", null);
            BOT_USERNAME = getConfigValue(props, "bot.username", "BOT_USERNAME", null);
            COC_API_TOKEN = getConfigValue(props, "coc.api.token", "COC_API_TOKEN", null);
            
            // Настройки приложения
            HTMLS_DIRECTORY = getConfigValue(props, "app.htmls.directory", "HTMLS_DIRECTORY", "data/htmls");
            OUTPUT_JSON = getConfigValue(props, "app.output.json", "OUTPUT_JSON", "data/war_data.json");
            CLAN_TAG = getConfigValue(props, "app.clan.tag", "CLAN_TAG", "#2PQU0PLJ2");
            
        } catch (IOException ex) {
            throw new RuntimeException("Ошибка при загрузке конфигурации", ex);
        }
    }
    
    /**
     * Получает значение конфигурации из properties файла, переменных окружения или использует значение по умолчанию
     * @param props объект Properties
     * @param propertyKey ключ в properties файле
     * @param envKey ключ переменной окружения
     * @param defaultValue значение по умолчанию
     * @return найденное значение
     */
    private static String getConfigValue(Properties props, String propertyKey, String envKey, String defaultValue) {
        // Сначала проверяем system properties
        String value = System.getProperty(propertyKey);
        if (value != null && !value.trim().isEmpty()) {
            return value.trim();
        }
        
        // Затем проверяем переменные окружения
        value = System.getenv(envKey);
        if (value != null && !value.trim().isEmpty()) {
            return value.trim();
        }
        
        // Затем проверяем properties файл
        value = props.getProperty(propertyKey);
        if (value != null && !value.trim().isEmpty()) {
            return value.trim();
        }
        
        // Возвращаем значение по умолчанию
        if (defaultValue == null) {
            throw new RuntimeException("Не найдено значение для конфигурации: " + propertyKey + " (env: " + envKey + ")");
        }
        
        return defaultValue;
    }
}