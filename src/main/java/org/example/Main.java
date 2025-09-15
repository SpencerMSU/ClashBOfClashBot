package org.example;

import org.example.bot.ClashBot;
import org.example.cocapi.CocApiClient;
import org.example.database.DatabaseService;
import org.telegram.telegrambots.meta.TelegramBotsApi;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.updatesreceivers.DefaultBotSession;

import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * Main entry point for the ClashBot application.
 * Initializes the database, API client, and Telegram bot.
 */
public class Main {
    private static final Logger LOGGER = Logger.getLogger(Main.class.getName());
    private static final String OUR_CLAN_TAG = "#2PQU0PLJ2";

    public static void main(String[] args) {
        try {
            LOGGER.info("Starting ClashBot application...");
            
            // Initialize database
            DatabaseService dbService = new DatabaseService();
            dbService.initDb();
            LOGGER.info("Database initialized successfully");

            // Initialize API client
            CocApiClient apiClient = new CocApiClient();
            LOGGER.info("Clash of Clans API client initialized");

            // Initialize bot
            ClashBot bot = new ClashBot();

            // Start war archiver
            WarArchiver archiver = new WarArchiver(OUR_CLAN_TAG, apiClient, dbService, bot);
            archiver.start();
            LOGGER.info("War archiver started");

            // Register bot with Telegram
            TelegramBotsApi botsApi = new TelegramBotsApi(DefaultBotSession.class);
            botsApi.registerBot(bot);

            LOGGER.info("ClashBot successfully started and ready to handle messages!");

        } catch (TelegramApiException e) {
            LOGGER.log(Level.SEVERE, "Failed to start Telegram bot", e);
            System.exit(1);
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Failed to start ClashBot application", e);
            System.exit(1);
        }
    }
}