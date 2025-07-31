package org.example;

import org.example.bot.ClashBot;
import org.example.cocapi.CocApiClient;
import org.example.database.DatabaseService;
import org.telegram.telegrambots.meta.TelegramBotsApi;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.updatesreceivers.DefaultBotSession;

public class Main {
    private static final String OUR_CLAN_TAG = "#2PQU0PLJ2";

    public static void main(String[] args) {
        try {
            DatabaseService dbService = new DatabaseService();
            dbService.initDb();
            CocApiClient apiClient = new CocApiClient();

            ClashBot bot = new ClashBot();

            WarArchiver archiver = new WarArchiver(OUR_CLAN_TAG, apiClient, dbService, bot);
            archiver.start();

            TelegramBotsApi botsApi = new TelegramBotsApi(DefaultBotSession.class);
            botsApi.registerBot(bot);

            System.out.println("Бот успешно запущен!");

        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }
}