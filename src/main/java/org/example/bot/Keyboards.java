package org.example.bot;

import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.ReplyKeyboardMarkup;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardButton;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.KeyboardButton;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.KeyboardRow;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class Keyboards {

    // Константы для кнопок
    public static final String PROFILE_BTN = "👤 Профиль";
    public static final String CLAN_BTN = "🛡 Клан";
    public static final String LINK_ACC_BTN = "🔗 Привязать аккаунт";
    public static final String SEARCH_PROFILE_BTN = "🔍 Найти профиль по тегу";
    public static final String MY_CLAN_BTN = "🛡 Мой клан (из профиля)";
    public static final String SEARCH_CLAN_BTN = "🔍 Найти клан по тегу";
    public static final String BACK_BTN = "⬅️ Назад в главное меню";
    public static final String MY_PROFILE_PREFIX = "👤 Мой профиль";
    public static final String CLAN_MEMBERS_BTN = "👥 Список участников";
    public static final String CLAN_WARLOG_BTN = "⚔️ Последние войны";
    public static final String BACK_TO_CLAN_MENU_BTN = "⬅️ Назад в меню кланов";
    public static final String CLAN_CURRENT_CWL_BTN = "⚔️ Текущее ЛВК";
    public static final String CLAN_CWL_BONUS_BTN = "🏆 Бонусы ЛВК";
    public static final String NOTIFICATIONS_BTN = "🔔 Уведомления о КВ";
    public static final String CLAN_CURRENT_WAR_BTN = "⚔️ Текущая КВ";

    // Константы для callback-данных
    public static final String MEMBERS_CALLBACK = "members";
    public static final String WAR_LIST_CALLBACK = "warlist";
    public static final String WAR_INFO_CALLBACK = "warinfo";
    public static final String PROFILE_CALLBACK = "profile";
    public static final String NOTIFY_TOGGLE_CALLBACK = "notify_toggle";
    public static final String CWL_BONUS_CALLBACK = "cwlbonus";
    public static final String MEMBERS_SORT_CALLBACK = "members_sort";
    public static final String MEMBERS_VIEW_CALLBACK = "members_view";

    public static ReplyKeyboardMarkup mainMenu() {
        KeyboardRow row1 = new KeyboardRow();
        row1.add(new KeyboardButton(PROFILE_BTN));
        row1.add(new KeyboardButton(CLAN_BTN));

        KeyboardRow row2 = new KeyboardRow();
        row2.add(new KeyboardButton(NOTIFICATIONS_BTN));

        return ReplyKeyboardMarkup.builder().keyboard(List.of(row1, row2)).resizeKeyboard(true).build();
    }

    public static ReplyKeyboardMarkup profileMenu(String playerName) {
        List<KeyboardRow> keyboard = new ArrayList<>();
        if (playerName != null && !playerName.isEmpty()) {
            KeyboardRow myProfileRow = new KeyboardRow();
            myProfileRow.add(new KeyboardButton(MY_PROFILE_PREFIX + " (" + playerName + ")"));
            keyboard.add(myProfileRow);
        }
        KeyboardRow actionsRow = new KeyboardRow();
        actionsRow.add(new KeyboardButton(LINK_ACC_BTN));
        actionsRow.add(new KeyboardButton(SEARCH_PROFILE_BTN));
        keyboard.add(actionsRow);
        KeyboardRow backRow = new KeyboardRow();
        backRow.add(new KeyboardButton(BACK_BTN));
        keyboard.add(backRow);
        return ReplyKeyboardMarkup.builder().keyboard(keyboard).resizeKeyboard(true).build();
    }

    public static ReplyKeyboardMarkup clanMenu() {
        KeyboardRow row1 = new KeyboardRow();
        row1.add(new KeyboardButton(MY_CLAN_BTN));
        row1.add(new KeyboardButton(SEARCH_CLAN_BTN));
        KeyboardRow row2 = new KeyboardRow();
        row2.add(new KeyboardButton(BACK_BTN));
        return ReplyKeyboardMarkup.builder().keyboard(List.of(row1, row2)).resizeKeyboard(true).build();
    }

    public static ReplyKeyboardMarkup clanInspectionMenu() {
        KeyboardRow row1 = new KeyboardRow();
        row1.add(new KeyboardButton(CLAN_MEMBERS_BTN));
        row1.add(new KeyboardButton(CLAN_WARLOG_BTN));
        KeyboardRow row2 = new KeyboardRow();
        row2.add(new KeyboardButton(CLAN_CURRENT_WAR_BTN));
        row2.add(new KeyboardButton(CLAN_CURRENT_CWL_BTN));
        row2.add(new KeyboardButton(CLAN_CWL_BONUS_BTN));
        KeyboardRow row3 = new KeyboardRow();
        row3.add(new KeyboardButton(BACK_TO_CLAN_MENU_BTN));
        return ReplyKeyboardMarkup.builder().keyboard(List.of(row1, row2, row3)).resizeKeyboard(true).build();
    }

    public static InlineKeyboardMarkup warHistorySortMenu(String clanTag) {
        List<List<InlineKeyboardButton>> rows = new ArrayList<>();
        rows.add(List.of(
                InlineKeyboardButton.builder().text("📅 Сначала новые").callbackData(String.join(":", WAR_LIST_CALLBACK, clanTag, WarSort.DATE_DESC.toString(), "0")).build()
        ));
        rows.add(List.of(
                InlineKeyboardButton.builder().text("📅 Сначала старые").callbackData(String.join(":", WAR_LIST_CALLBACK, clanTag, WarSort.DATE_ASC.toString(), "0")).build()
        ));
        rows.add(List.of(
                InlineKeyboardButton.builder().text("🏆 Только ЛВК (текущий сезон)").callbackData(String.join(":", WAR_LIST_CALLBACK, clanTag, WarSort.CWL_ONLY.toString(), "0")).build()
        ));
        return InlineKeyboardMarkup.builder().keyboard(rows).build();
    }

    public static InlineKeyboardMarkup cwlBonusMonthMenu() {
        List<List<InlineKeyboardButton>> rows = new ArrayList<>();
        LocalDate today = LocalDate.now();
        for (int i = 0; i < 4; i++) {
            LocalDate date = today.minusMonths(i);
            String monthName = date.format(DateTimeFormatter.ofPattern("LLLL yyyy", new Locale("ru")));
            String callbackData = String.join(":", CWL_BONUS_CALLBACK, date.format(DateTimeFormatter.ofPattern("yyyy-MM")));
            rows.add(List.of(
                    InlineKeyboardButton.builder().text(monthName).callbackData(callbackData).build()
            ));
        }
        return InlineKeyboardMarkup.builder().keyboard(rows).build();
    }

    public static InlineKeyboardMarkup memberListManagementMenu(String clanTag, String currentSort, String currentView) {
        List<List<InlineKeyboardButton>> rows = new ArrayList<>();

        List<InlineKeyboardButton> sortRow = new ArrayList<>();
        sortRow.add(InlineKeyboardButton.builder().text("🏆⬆️").callbackData(String.join(":", MEMBERS_SORT_CALLBACK, clanTag, "trophies_asc", currentView, "0")).build());
        sortRow.add(InlineKeyboardButton.builder().text("🏆⬇️").callbackData(String.join(":", MEMBERS_SORT_CALLBACK, clanTag, "trophies_desc", currentView, "0")).build());
        sortRow.add(InlineKeyboardButton.builder().text("🏰⬆️").callbackData(String.join(":", MEMBERS_SORT_CALLBACK, clanTag, "th_asc", currentView, "0")).build());
        sortRow.add(InlineKeyboardButton.builder().text("🏰⬇️").callbackData(String.join(":", MEMBERS_SORT_CALLBACK, clanTag, "th_desc", currentView, "0")).build());
        sortRow.add(InlineKeyboardButton.builder().text("🔰Ранг").callbackData(String.join(":", MEMBERS_SORT_CALLBACK, clanTag, "rank", currentView, "0")).build());
        rows.add(sortRow);

        String switchButtonText = "home".equals(currentView) ? "🏠 ➡️  строителя" : "строителя ➡️ 🏠";
        String newView = "home".equals(currentView) ? "builder" : "home";
        rows.add(List.of(
                InlineKeyboardButton.builder().text(switchButtonText).callbackData(String.join(":", MEMBERS_SORT_CALLBACK, clanTag, currentSort, newView, "0")).build()
        ));

        return InlineKeyboardMarkup.builder().keyboard(rows).build();
    }

    public static InlineKeyboardMarkup notificationMenu(boolean isSubscribed) {
        String buttonText = isSubscribed ? "✅ Отписаться от уведомлений" : "🔔 Подписаться на уведомления";
        InlineKeyboardButton button = InlineKeyboardButton.builder()
                .text(buttonText)
                .callbackData(NOTIFY_TOGGLE_CALLBACK)
                .build();
        return InlineKeyboardMarkup.builder().keyboardRow(List.of(button)).build();
    }

    public static InlineKeyboardMarkup paginationMenu(String callbackPrefix, String clanTag, WarSort sortOrder, int currentPage, int maxPage) {
        List<InlineKeyboardButton> row = new ArrayList<>();
        if (currentPage > 0) {
            row.add(InlineKeyboardButton.builder().text("⬅️ Назад").callbackData(String.join(":", callbackPrefix, clanTag, sortOrder.toString(), String.valueOf(currentPage - 1))).build());
        }
        row.add(InlineKeyboardButton.builder().text((currentPage + 1) + "/" + (maxPage + 1)).callbackData("noop").build());
        if (currentPage < maxPage) {
            row.add(InlineKeyboardButton.builder().text("Вперёд ➡️").callbackData(String.join(":", callbackPrefix, clanTag, sortOrder.toString(), String.valueOf(currentPage + 1))).build());
        }
        return InlineKeyboardMarkup.builder().keyboardRow(row).build();
    }

    public static InlineKeyboardMarkup paginationMenu(String callbackPrefix, String clanTag, int currentPage, int maxPage) {
        List<InlineKeyboardButton> row = new ArrayList<>();
        if (currentPage > 0) {
            row.add(InlineKeyboardButton.builder().text("⬅️ Назад").callbackData(String.join(":", callbackPrefix, clanTag, String.valueOf(currentPage - 1))).build());
        }
        row.add(InlineKeyboardButton.builder().text((currentPage + 1) + "/" + (maxPage + 1)).callbackData("noop").build());
        if (currentPage < maxPage) {
            row.add(InlineKeyboardButton.builder().text("Вперёд ➡️").callbackData(String.join(":", callbackPrefix, clanTag, String.valueOf(currentPage + 1))).build());
        }
        return InlineKeyboardMarkup.builder().keyboardRow(row).build();
    }

    // Универсальная пагинация для списка участников, которая принимает полный префикс
    public static InlineKeyboardMarkup paginationMenu(String callbackPrefix, int currentPage, int maxPage) {
        List<InlineKeyboardButton> row = new ArrayList<>();
        if (currentPage > 0) {
            row.add(InlineKeyboardButton.builder().text("⬅️ Назад").callbackData(callbackPrefix + ":" + (currentPage - 1)).build());
        }
        row.add(InlineKeyboardButton.builder().text((currentPage + 1) + "/" + (maxPage + 1)).callbackData("noop").build());
        if (currentPage < maxPage) {
            row.add(InlineKeyboardButton.builder().text("Вперёд ➡️").callbackData(callbackPrefix + ":" + (currentPage + 1)).build());
        }
        return InlineKeyboardMarkup.builder().keyboardRow(row).build();
    }
}