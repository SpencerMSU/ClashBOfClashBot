package org.example.bot.handlers;

import org.example.bot.ClashBot;
import org.example.bot.Keyboards;
import org.example.bot.UserState;
import org.example.bot.view.MessageGenerator;
import org.telegram.telegrambots.meta.api.objects.Message;

public class MessageHandler {
    private final ClashBot bot;
    private final MessageGenerator messageGenerator;

    public MessageHandler(ClashBot bot, MessageGenerator messageGenerator) {
        this.bot = bot;
        this.messageGenerator = messageGenerator;
    }

    public void handle(Message message) {
        long chatId = message.getChatId();
        String text = message.getText();
        UserState state = bot.getUserStates().get(chatId);

        if (state == null) {
            handleMenuCommands(chatId, text);
            return;
        }

        String tag = text.replaceAll("\\s+", "").toUpperCase().replace('O', '0');
        if (!tag.startsWith("#")) {
            tag = "#" + tag;
        }

        switch (state) {
            case AWAITING_PLAYER_TAG_TO_LINK:
                messageGenerator.handleLinkAccount(chatId, tag);
                break;
            case AWAITING_PLAYER_TAG_TO_SEARCH:
                messageGenerator.displayPlayerInfo(chatId, tag, Keyboards.profileMenu(null));
                break;
            case AWAITING_CLAN_TAG_TO_SEARCH:
                messageGenerator.displayClanInfo(chatId, tag);
                break;
        }
        bot.getUserStates().remove(chatId);
    }

    private void handleMenuCommands(long chatId, String text) {
        if (text.startsWith(Keyboards.MY_PROFILE_PREFIX)) {
            messageGenerator.handleMyProfileRequest(chatId);
            return;
        }

        switch (text) {
            case "/start":
                bot.getUserInspectingClan().remove(chatId);
                bot.sendMessage(chatId, "Добро пожаловать!", Keyboards.mainMenu());
                break;
            case Keyboards.PROFILE_BTN:
                messageGenerator.handleProfileMenuRequest(chatId);
                break;
            case Keyboards.CLAN_BTN:
            case Keyboards.BACK_TO_CLAN_MENU_BTN:
                bot.getUserInspectingClan().remove(chatId);
                bot.sendMessage(chatId, "Меню клана:", Keyboards.clanMenu());
                break;
            case Keyboards.MY_CLAN_BTN:
                messageGenerator.handleMyClanRequest(chatId);
                break;
            case Keyboards.CLAN_MEMBERS_BTN:
                bot.getUserInspectingClan().computeIfPresent(chatId, (id, clanTag) -> {
                    messageGenerator.displayMembersPage(chatId, null, clanTag, 0, "rank", "home");
                    return clanTag;
                });
                break;
            case Keyboards.CLAN_WARLOG_BTN:
                bot.getUserInspectingClan().computeIfPresent(chatId, (id, clanTag) -> {
                    bot.sendMessage(chatId, "Выберите, как отобразить историю войн:", Keyboards.warHistorySortMenu(clanTag));
                    return clanTag;
                });
                break;
            case Keyboards.CLAN_CURRENT_WAR_BTN:
                bot.getUserInspectingClan().computeIfPresent(chatId, (id, clanTag) -> {
                    messageGenerator.handleCurrentWarRequest(chatId, clanTag);
                    return clanTag;
                });
                break;
            case Keyboards.CLAN_CURRENT_CWL_BTN:
                bot.getUserInspectingClan().computeIfPresent(chatId, (id, clanTag) -> {
                    messageGenerator.handleCurrentCwlRequest(chatId, clanTag);
                    return clanTag;
                });
                break;
            case Keyboards.CLAN_CWL_BONUS_BTN:
                bot.sendMessage(chatId, "🏆 Выберите месяц для подсчета бонусов ЛВК:", Keyboards.cwlBonusMonthMenu());
                break;
            case Keyboards.NOTIFICATIONS_BTN:
                messageGenerator.handleNotificationMenu(chatId);
                break;
            case Keyboards.LINK_ACC_BTN:
                bot.getUserStates().put(chatId, UserState.AWAITING_PLAYER_TAG_TO_LINK);
                bot.sendMessage(chatId, "Отправьте мне ваш тег игрока (например, 2V99V8J0).");
                break;
            case Keyboards.SEARCH_PROFILE_BTN:
                bot.getUserStates().put(chatId, UserState.AWAITING_PLAYER_TAG_TO_SEARCH);
                bot.sendMessage(chatId, "Отправьте тег игрока для поиска.");
                break;
            case Keyboards.SEARCH_CLAN_BTN:
                bot.getUserStates().put(chatId, UserState.AWAITING_CLAN_TAG_TO_SEARCH);
                bot.sendMessage(chatId, "Отправьте тег клана для поиска.");
                break;
            case Keyboards.BACK_BTN:
                bot.getUserInspectingClan().remove(chatId);
                bot.sendMessage(chatId, "Добро пожаловать!", Keyboards.mainMenu());
                break;
        }
    }
}