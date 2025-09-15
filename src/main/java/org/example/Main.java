package org.example;

import org.example.bot.ClashBot;
import org.example.cocapi.CocApiClient;
import org.example.config.BotConfig;
import org.example.database.DatabaseService;
import org.telegram.telegrambots.meta.TelegramBotsApi;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.updatesreceivers.DefaultBotSession;

public class Main {
    public static void main(String[] args) {
        try {
            System.out.println("Запуск Clash of Clans Telegram Bot...");
            
            DatabaseService dbService = new DatabaseService();
            dbService.initDb();
            System.out.println("База данных инициализирована");
            
            CocApiClient apiClient = new CocApiClient();
            System.out.println("API клиент создан");

            ClashBot bot = new ClashBot();
            System.out.println("Бот создан");

            // Используем клан-тег из конфигурации
            WarArchiver archiver = new WarArchiver(BotConfig.CLAN_TAG, apiClient, dbService, bot);
            archiver.start();
            System.out.println("Архиватор войн запущен для клана: " + BotConfig.CLAN_TAG);

            TelegramBotsApi botsApi = new TelegramBotsApi(DefaultBotSession.class);
            botsApi.registerBot(bot);

            System.out.println("Бот успешно запущен!");

        } catch (TelegramApiException e) {
            System.err.println("Ошибка при запуске Telegram API: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("Неожиданная ошибка при запуске: " + e.getMessage());
            e.printStackTrace();
        }
    }
}