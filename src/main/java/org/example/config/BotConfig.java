package org.example.config;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * Configuration class for the ClashBot application.
 * Loads configuration from config.properties file in the resources directory.
 */
public class BotConfig {
    public static final String BOT_TOKEN;
    public static final String BOT_USERNAME;
    public static final String COC_API_TOKEN;

    static {
        Properties props = new Properties();
        try (InputStream input = BotConfig.class.getClassLoader().getResourceAsStream("config.properties")) {
            if (input == null) {
                throw new RuntimeException("Файл config.properties не найден в /resources. " +
                        "Скопируйте config.properties.template в config.properties и заполните необходимые данные.");
            }
            props.load(input);
            
            BOT_TOKEN = getRequiredProperty(props, "bot.token");
            BOT_USERNAME = getRequiredProperty(props, "bot.username");
            COC_API_TOKEN = getRequiredProperty(props, "coc.api.token");
            
        } catch (IOException ex) {
            throw new RuntimeException("Ошибка при загрузке конфигурации", ex);
        }
    }
    
    /**
     * Gets a required property from the properties file.
     * Throws RuntimeException if the property is missing or empty.
     */
    private static String getRequiredProperty(Properties props, String key) {
        String value = props.getProperty(key);
        if (value == null || value.trim().isEmpty()) {
            throw new RuntimeException("Отсутствует обязательное свойство: " + key + 
                    ". Проверьте файл config.properties");
        }
        return value.trim();
    }
}