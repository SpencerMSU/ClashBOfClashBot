package org.example.bot;

import org.example.bot.handlers.CallbackHandler;
import org.example.bot.handlers.MessageHandler;
import org.example.bot.view.MessageGenerator;
import org.example.cocapi.CocApiClient;
import org.example.config.BotConfig;
import org.example.database.DatabaseService;
import org.telegram.telegrambots.bots.TelegramLongPollingBot;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.methods.updatingmessages.EditMessageText;
import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.ReplyKeyboard;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class ClashBot extends TelegramLongPollingBot {

    private final Map<Long, UserState> userStates = new ConcurrentHashMap<>();
    private final Map<Long, String> userInspectingClan = new ConcurrentHashMap<>();

    private final DatabaseService dbService = new DatabaseService();
    private final CocApiClient cocApiClient = new CocApiClient();

    private final MessageHandler messageHandler;
    private final CallbackHandler callbackHandler;

    public ClashBot() {
        super(BotConfig.BOT_TOKEN);
        MessageGenerator messageGenerator = new MessageGenerator(this, dbService, cocApiClient);
        this.messageHandler = new MessageHandler(this, messageGenerator);
        this.callbackHandler = new CallbackHandler(this, messageGenerator);
    }

    @Override
    public void onUpdateReceived(Update update) {
        if (update.hasMessage() && update.getMessage().hasText()) {
            messageHandler.handle(update.getMessage());
        } else if (update.hasCallbackQuery()) {
            callbackHandler.handle(update.getCallbackQuery());
        }
    }

    public Map<Long, UserState> getUserStates() { return userStates; }
    public Map<Long, String> getUserInspectingClan() { return userInspectingClan; }

    public void editMessage(long chatId, int messageId, String text, InlineKeyboardMarkup keyboard) {
        EditMessageText message = EditMessageText.builder()
                .chatId(chatId)
                .messageId(messageId)
                .text(text)
                .replyMarkup(keyboard)
                .build();
        try {
            execute(message);
        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }

    public void sendMessage(long chatId, String text) {
        sendMessage(chatId, text, null);
    }

    public void sendMessage(long chatId, String text, ReplyKeyboard keyboard) {
        SendMessage message = new SendMessage(String.valueOf(chatId), text);
        if (keyboard != null) {
            message.setReplyMarkup(keyboard);
        }
        try {
            execute(message);
        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }

    @Override
    public String getBotUsername() {
        return BotConfig.BOT_USERNAME;
    }
}