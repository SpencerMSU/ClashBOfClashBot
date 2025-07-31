package org.example.config;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class BotConfig {
    public static final String BOT_TOKEN;
    public static final String BOT_USERNAME;
    public static final String COC_API_TOKEN;

    static {
        Properties props = new Properties();
        try (InputStream input = BotConfig.class.getClassLoader().getResourceAsStream("config.properties")) {
            if (input == null) throw new RuntimeException("Файл config.properties не найден в /resources");
            props.load(input);
            BOT_TOKEN = props.getProperty("bot.token");
            BOT_USERNAME = props.getProperty("bot.username");
            COC_API_TOKEN = props.getProperty("coc.api.token");
        } catch (IOException ex) {
            throw new RuntimeException("Ошибка при загрузке конфигурации", ex);
        }
    }
}