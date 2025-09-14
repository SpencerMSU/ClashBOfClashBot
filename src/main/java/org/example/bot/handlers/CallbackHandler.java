package org.example.bot.handlers;

import org.example.bot.ClashBot;
import org.example.bot.Keyboards;
import org.example.bot.WarSort;
import org.example.bot.view.MessageGenerator;
import org.telegram.telegrambots.meta.api.objects.CallbackQuery;

public class CallbackHandler {
    private final ClashBot bot;
    private final MessageGenerator messageGenerator;

    public CallbackHandler(ClashBot bot, MessageGenerator messageGenerator) {
        this.bot = bot;
        this.messageGenerator = messageGenerator;
    }

    public void handle(CallbackQuery callbackQuery) {
        if ("noop".equals(callbackQuery.getData())) return;

        String[] data = callbackQuery.getData().split(":");
        if (data.length < 2) return;

        String type = data[0];
        long chatId = callbackQuery.getMessage().getChatId();
        int messageId = callbackQuery.getMessage().getMessageId();

        try {
            if (Keyboards.MEMBERS_SORT_CALLBACK.equals(type)) {
                String clanTag = data[1];
                String sortType = data[2];
                String viewType = data[3];
                int page = Integer.parseInt(data[4]);
                messageGenerator.displayMembersPage(chatId, messageId, clanTag, page, sortType, viewType);
            } else if (Keyboards.WAR_LIST_CALLBACK.equals(type)) {
                String clanTag = data[1];
                WarSort sortOrder = WarSort.valueOf(data[2]);
                int page = Integer.parseInt(data[3]);
                messageGenerator.displayWarListPage(chatId, messageId, clanTag, sortOrder, page);
            } else if (Keyboards.WAR_INFO_CALLBACK.equals(type)) {
                String clanTag = data[1];
                String warEndTime = data[2];
                messageGenerator.displaySingleWarDetails(chatId, messageId, clanTag, warEndTime);
            } else if (Keyboards.PROFILE_CALLBACK.equals(type)) {
                String playerTag = data[1];
                messageGenerator.displayPlayerInfo(chatId, playerTag, Keyboards.clanInspectionMenu());
            } else if (Keyboards.NOTIFY_TOGGLE_CALLBACK.equals(type)) {
                messageGenerator.handleNotificationToggle(chatId, messageId);
            } else if (Keyboards.CWL_BONUS_CALLBACK.equals(type)) {
                String yearMonth = data[1];
                messageGenerator.handleCwlBonusRequest(chatId, messageId, yearMonth);
            }
        } catch (Exception e) {
            System.err.println("Ошибка обработки callback: " + callbackQuery.getData());
            e.printStackTrace();
        }
    }
}