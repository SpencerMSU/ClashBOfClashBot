package org.example.bot;

import org.example.cocapi.CocApiClient;
import org.example.cocapi.dto.Clan;
import org.example.cocapi.dto.Player;
import org.example.cocapi.dto.currentwar.CurrentWar;
import org.example.cocapi.dto.importer.WarData;
import org.example.config.BotConfig;
import org.example.database.DatabaseService;
import org.example.database.model.AttackData;
import org.telegram.telegrambots.bots.TelegramLongPollingBot;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.methods.updatingmessages.EditMessageText;
import org.telegram.telegrambots.meta.api.objects.CallbackQuery;
import org.telegram.telegrambots.meta.api.objects.Message;
import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.ReplyKeyboard;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardButton;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;

import java.time.LocalDate;
import java.time.YearMonth;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class ClashBot extends TelegramLongPollingBot {

    private final Map<Long, UserState> userStates = new ConcurrentHashMap<>();
    private final Map<Long, String> userInspectingClan = new ConcurrentHashMap<>();
    private final DatabaseService dbService = new DatabaseService();
    private final CocApiClient cocApiClient = new CocApiClient();
    private static final int MEMBERS_PER_PAGE = 10;
    private static final int WARS_PER_PAGE = 10;
    private static final Map<String, String> ROLE_TRANSLATIONS = Map.of(
            "leader", "👑 Глава", "coLeader", "⚜️ Соруководитель",
            "admin", "🔰 Старейшина", "member", "👤 Участник"
    );
    private static final DateTimeFormatter COC_DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss.SSS'Z'").withZone(ZoneOffset.UTC);

    public ClashBot() { super(BotConfig.BOT_TOKEN); }

    @Override
    public void onUpdateReceived(Update update) {
        if (update.hasMessage() && update.getMessage().hasText()) {
            handleTextMessage(update.getMessage());
        } else if (update.hasCallbackQuery()) {
            handleCallbackQuery(update.getCallbackQuery());
        }
    }

    private void handleCallbackQuery(CallbackQuery callbackQuery) {
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
                displayMembersPage(chatId, messageId, clanTag, page, sortType, viewType);
            }
            else if (Keyboards.WAR_LIST_CALLBACK.equals(type)) {
                String clanTag = data[1];
                WarSort sortOrder = WarSort.valueOf(data[2]);
                int page = Integer.parseInt(data[3]);
                displayWarListPage(chatId, messageId, clanTag, sortOrder, page);
            } else if (Keyboards.WAR_INFO_CALLBACK.equals(type)) {
                String clanTag = data[1];
                String warEndTime = data[2];
                displaySingleWarDetails(chatId, messageId, clanTag, warEndTime);
            } else if (Keyboards.PROFILE_CALLBACK.equals(type)) {
                String playerTag = data[1];
                displayPlayerInfo(chatId, playerTag, Keyboards.clanInspectionMenu());
            } else if (Keyboards.NOTIFY_TOGGLE_CALLBACK.equals(type)) {
                handleNotificationToggle(chatId, messageId);
            } else if (Keyboards.CWL_BONUS_CALLBACK.equals(type)) {
                String yearMonth = data[1];
                handleCwlBonusRequest(chatId, messageId, yearMonth);
            }
        } catch (Exception e) {
            System.err.println("Ошибка обработки callback: " + callbackQuery.getData());
            e.printStackTrace();
        }
    }

    private void handleTextMessage(Message message) {
        long chatId = message.getChatId();
        String text = message.getText();
        UserState state = userStates.get(chatId);

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
                handleLinkAccount(chatId, tag);
                break;
            case AWAITING_PLAYER_TAG_TO_SEARCH:
                displayPlayerInfo(chatId, tag, Keyboards.profileMenu(null));
                break;
            case AWAITING_CLAN_TAG_TO_SEARCH:
                displayClanInfo(chatId, tag);
                break;
        }
        userStates.remove(chatId);
    }

    private void handleMenuCommands(long chatId, String text) {
        if (text.startsWith(Keyboards.MY_PROFILE_PREFIX)) {
            handleMyProfileRequest(chatId);
            return;
        }

        switch (text) {
            case "/start":
                userInspectingClan.remove(chatId);
                sendMessage(chatId, "Добро пожаловать!", Keyboards.mainMenu());
                break;
            case Keyboards.PROFILE_BTN:
                handleProfileMenuRequest(chatId);
                break;
            case Keyboards.CLAN_BTN:
            case Keyboards.BACK_TO_CLAN_MENU_BTN:
                userInspectingClan.remove(chatId);
                sendMessage(chatId, "Меню клана:", Keyboards.clanMenu());
                break;
            case Keyboards.MY_CLAN_BTN:
                handleMyClanRequest(chatId);
                break;
            case Keyboards.CLAN_MEMBERS_BTN:
                userInspectingClan.computeIfPresent(chatId, (id, clanTag) -> {
                    displayMembersPage(chatId, null, clanTag, 0, "rank", "home");
                    return clanTag;
                });
                break;
            case Keyboards.CLAN_WARLOG_BTN:
                userInspectingClan.computeIfPresent(chatId, (id, clanTag) -> {
                    sendMessage(chatId, "Выберите, как отобразить историю войн:", Keyboards.warHistorySortMenu(clanTag));
                    return clanTag;
                });
                break;
            case Keyboards.CLAN_CURRENT_WAR_BTN:
                userInspectingClan.computeIfPresent(chatId, (id, clanTag) -> {
                    handleCurrentWarRequest(chatId, clanTag);
                    return clanTag;
                });
                break;
            case Keyboards.CLAN_CURRENT_CWL_BTN:
                userInspectingClan.computeIfPresent(chatId, (id, clanTag) -> {
                    handleCurrentCwlRequest(chatId, clanTag);
                    return clanTag;
                });
                break;
            case Keyboards.CLAN_CWL_BONUS_BTN:
                sendMessage(chatId, "🏆 Выберите месяц для подсчета бонусов ЛВК:", Keyboards.cwlBonusMonthMenu());
                break;
            case Keyboards.NOTIFICATIONS_BTN:
                handleNotificationMenu(chatId);
                break;
            case Keyboards.LINK_ACC_BTN:
                userStates.put(chatId, UserState.AWAITING_PLAYER_TAG_TO_LINK);
                sendMessage(chatId, "Отправьте мне ваш тег игрока (например, 2V99V8J0).");
                break;
            case Keyboards.SEARCH_PROFILE_BTN:
                userStates.put(chatId, UserState.AWAITING_PLAYER_TAG_TO_SEARCH);
                sendMessage(chatId, "Отправьте тег игрока для поиска.");
                break;
            case Keyboards.SEARCH_CLAN_BTN:
                userStates.put(chatId, UserState.AWAITING_CLAN_TAG_TO_SEARCH);
                sendMessage(chatId, "Отправьте тег клана для поиска.");
                break;
            case Keyboards.BACK_BTN:
                userInspectingClan.remove(chatId);
                sendMessage(chatId, "Добро пожаловать!", Keyboards.mainMenu());
                break;
        }
    }

    private void handleProfileMenuRequest(long chatId) {
        dbService.findUser(chatId).ifPresentOrElse(
                user -> cocApiClient.getPlayerInfo(user.getPlayerTag()).ifPresentOrElse(
                        player -> sendMessage(chatId, "Меню профиля:", Keyboards.profileMenu(player.getName())),
                        () -> sendMessage(chatId, "Меню профиля:", Keyboards.profileMenu(null))
                ),
                () -> sendMessage(chatId, "Меню профиля:", Keyboards.profileMenu(null))
        );
    }

    private void handleMyProfileRequest(long chatId) {
        dbService.findUser(chatId).ifPresentOrElse(
                this::displayPlayerInfo,
                () -> handleProfileMenuRequest(chatId)
        );
    }

    private void displayPlayerInfo(org.example.database.model.User user) {
        displayPlayerInfo(user.getTelegramId(), user.getPlayerTag(), Keyboards.profileMenu(null));
    }

    private void handleLinkAccount(long chatId, String playerTag) {
        if (dbService.isTagLinked(playerTag)) {
            sendMessage(chatId, "Этот тег уже привязан к другому аккаунту Telegram.", Keyboards.profileMenu(null));
            return;
        }
        Optional<Player> playerOpt = cocApiClient.getPlayerInfo(playerTag);
        if (playerOpt.isPresent()) {
            dbService.linkUser(chatId, playerTag);
            Player player = playerOpt.get();
            sendMessage(chatId, "✅ Аккаунт " + player.getName() + " успешно привязан!", Keyboards.profileMenu(player.getName()));
        } else {
            sendMessage(chatId, "❌ Игрок с тегом " + playerTag + " не найден.", Keyboards.profileMenu(null));
        }
    }

    private void handleMyClanRequest(long chatId) {
        Optional<org.example.database.model.User> userOpt = dbService.findUser(chatId);
        if (userOpt.isEmpty()) {
            sendMessage(chatId, "Ваш аккаунт не привязан.", Keyboards.clanMenu());
            return;
        }
        cocApiClient.getPlayerInfo(userOpt.get().getPlayerTag()).ifPresentOrElse(
                player -> {
                    Player.ClanInfo clanInfo = player.getClan();
                    if (clanInfo != null && clanInfo.getTag() != null) {
                        displayClanInfo(chatId, clanInfo.getTag());
                    } else {
                        sendMessage(chatId, "Вы не состоите в клане.", Keyboards.clanMenu());
                    }
                },
                () -> sendMessage(chatId, "Не удалось получить информацию о вашем профиле.", Keyboards.clanMenu())
        );
    }

    private void handleCurrentCwlRequest(long chatId, String clanTag) {
        cocApiClient.getClanWarLeagueGroup(clanTag).ifPresentOrElse(
                leagueGroup -> {
                    if ("inWar".equals(leagueGroup.getState()) || "preparation".equals(leagueGroup.getState())) {
                        sendMessage(chatId, "⚔️ Идет Лига Клановых Войн!\n\nФункция детального просмотра текущего раунда в разработке.");
                    } else {
                        sendMessage(chatId, "✅ Лига Клановых Войн завершена или еще не началась.");
                    }
                },
                () -> sendMessage(chatId, "Клан в данный момент не участвует в Лиге Клановых Войн.")
        );
    }

    private void handleNotificationMenu(long chatId) {
        boolean isSubscribed = dbService.isUserSubscribed(chatId);
        String text = isSubscribed
                ? "Вы подписаны на уведомления о начале клановых войн."
                : "Вы не подписаны на уведомления. Хотите получать сообщение за час до начала КВ?";
        sendMessage(chatId, text, Keyboards.notificationMenu(isSubscribed));
    }

    private void handleNotificationToggle(long chatId, int messageId) {
        boolean isSubscribed = dbService.isUserSubscribed(chatId);
        String notificationText;
        if (isSubscribed) {
            dbService.unsubscribeUserFromNotifications(chatId);
            notificationText = "✅ Вы успешно отписались от уведомлений.";
        } else {
            dbService.subscribeUserToNotifications(chatId);
            notificationText = "✅ Вы успешно подписались на уведомления о начале КВ!";
        }
        editMessage(chatId, messageId, notificationText, null);
    }

    private void handleCurrentWarRequest(long chatId, String clanTag) {
        cocApiClient.getClanCurrentWar(clanTag).ifPresentOrElse(
                war -> {
                    DateTimeFormatter userFriendlyFormatter = DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm");

                    StringBuilder sb = new StringBuilder();
                    sb.append(String.format("*⚔️ Текущая война против: %s*\n\n", war.getOpponent().getName()));
                    sb.append(String.format("*Счёт:* ⭐`%d` (%.2f%%) - ⭐`%d` (%.2f%%)\n",
                            war.getClan().getStars(), war.getClan().getDestructionPercentage(),
                            war.getOpponent().getStars(), war.getOpponent().getDestructionPercentage()
                    ));

                    if ("preparation".equals(war.getState())) {
                        ZonedDateTime startTime = ZonedDateTime.parse(war.getStartTime(), COC_DATE_FORMATTER);
                        sb.append(String.format("*Состояние:* День подготовки\n*Начало битвы:* %s\n", startTime.format(userFriendlyFormatter)));
                    } else {
                        ZonedDateTime endTime = ZonedDateTime.parse(war.getEndTime(), COC_DATE_FORMATTER);
                        sb.append(String.format("*Состояние:* День битвы\n*Окончание:* %s\n", endTime.format(userFriendlyFormatter)));
                    }

                    int attacksPerMember = war.getClan().getAttacksPerMember();
                    List<String> slackers = war.getClan().getMembers().stream()
                            .filter(m -> m.getAttacks() == null || m.getAttacks().size() < attacksPerMember)
                            .map(m -> String.format("- %s (%d/%d)", m.getName(), m.getAttacks() == null ? 0 : m.getAttacks().size(), attacksPerMember))
                            .collect(Collectors.toList());

                    if (!slackers.isEmpty()) {
                        sb.append("\n*Не провели все атаки:*\n");
                        sb.append(String.join("\n", slackers));
                    } else {
                        sb.append("\n*Все участники провели свои атаки!*");
                    }

                    sendMessage(chatId, sb.toString());
                },
                () -> sendMessage(chatId, "✅ Клан сейчас не участвует в обычной войне.")
        );
    }

    private void handleCwlBonusRequest(long chatId, int messageId, String yearMonth) {
        YearMonth selectedMonth = YearMonth.parse(yearMonth);
        LocalDate endDate = selectedMonth.atDay(5);
        LocalDate startDate = endDate.minusMonths(1);

        DateTimeFormatter dbFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
        Map<String, Integer> attackCounts = dbService.countPlayerAttacksInPeriod(startDate.format(dbFormatter), endDate.format(dbFormatter));

        if (attackCounts.isEmpty()) {
            editMessage(chatId, messageId, "Не найдено данных об атаках в КВ за этот период.", null);
            return;
        }

        StringBuilder sb = new StringBuilder();
        sb.append(String.format("*🏆 Рейтинг по атакам в КВ для ЛВК %s*\n", selectedMonth.format(DateTimeFormatter.ofPattern("LLLL yyyy", new Locale("ru")))));
        sb.append(String.format("_(учитываются атаки в обычных КВ с %s по %s)_\n\n", startDate.format(DateTimeFormatter.ofPattern("dd.MM.yy")), endDate.format(DateTimeFormatter.ofPattern("dd.MM.yy"))));

        final int[] rank = {1};
        attackCounts.entrySet().stream()
                .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
                .forEach(entry -> {
                    String medal = "";
                    if (rank[0] == 1) medal = "🥇 ";
                    if (rank[0] == 2) medal = "🥈 ";
                    if (rank[0] == 3) medal = "🥉 ";
                    sb.append(String.format("%s*%s*: %d атак\n", medal, entry.getKey(), entry.getValue()));
                    rank[0]++;
                });

        editMessage(chatId, messageId, sb.toString(), null);
    }

    private void displayPlayerInfo(long chatId, String playerTag, ReplyKeyboard keyboardOnSuccess) {
        Optional<Player> playerOpt = cocApiClient.getPlayerInfo(playerTag);
        if (playerOpt.isPresent()) {
            Player player = playerOpt.get();
            String clanName = (player.getClan() != null && player.getClan().getName() != null) ? player.getClan().getName() : "Нет клана";
            String text = String.format(
                    "👤 *Профиль игрока: %s*\n" +
                            "🏷 Тег: `%s`\n\n" +
                            "--- *Основная деревня* ---\n" +
                            "🏰 Ратуша: %d уровня\n" +
                            "🎖 Уровень: %d\n" +
                            "🏆 Трофеи: %d\n" +
                            "⭐ Звёзды войны: %d\n" +
                            "🛡 Клан: %s\n\n" +
                            "--- *Деревня строителя* ---\n" +
                            "🛖 Дом строителя: %d уровня\n" +
                            "🏆 Трофеи (ДС): %d",
                    player.getName(), player.getTag(),
                    player.getTownHallLevel(), player.getExpLevel(),
                    player.getTrophies(), player.getWarStars(), clanName,
                    player.getBuilderHallLevel(), player.getVersusTrophies()
            );
            sendMessage(chatId, text, keyboardOnSuccess);
        } else {
            sendMessage(chatId, "❌ Игрок с тегом " + playerTag + " не найден.", keyboardOnSuccess);
        }
    }

    private void displayClanInfo(long chatId, String clanTag) {
        cocApiClient.getClanInfo(clanTag).ifPresentOrElse(
                clan -> {
                    userInspectingClan.put(chatId, clan.getTag());
                    String text = String.format("🛡️ *Вы просматриваете клан: %s*\n\nВыберите действие из меню ниже.", clan.getName());
                    sendMessage(chatId, text, Keyboards.clanInspectionMenu());
                },
                () -> sendMessage(chatId, "❌ Клан с тегом " + clanTag + " не найден.", Keyboards.clanMenu())
        );
    }

    private void displayMembersPage(long chatId, Integer messageId, String clanTag, int page, String sortType, String viewType) {
        cocApiClient.getClanInfo(clanTag).ifPresent(clan -> {
            List<Clan.ClanMember> members = new ArrayList<>(clan.getMemberList());

            Comparator<Clan.ClanMember> comparator;
            switch (sortType) {
                case "trophies_asc":
                    comparator = Comparator.comparingInt(Clan.ClanMember::getTrophies);
                    break;
                case "trophies_desc":
                    comparator = Comparator.comparingInt(Clan.ClanMember::getTrophies).reversed();
                    break;
                case "th_asc":
                    comparator = Comparator.comparingInt(Clan.ClanMember::getTownHallLevel);
                    break;
                case "th_desc":
                    comparator = Comparator.comparingInt(Clan.ClanMember::getTownHallLevel).reversed();
                    break;
                case "rank":
                default:
                    Map<String, Integer> roleOrder = Map.of("leader", 4, "coLeader", 3, "admin", 2, "member", 1);
                    comparator = (m1, m2) -> roleOrder.getOrDefault(m2.getRole(), 0)
                            .compareTo(roleOrder.getOrDefault(m1.getRole(), 0));
                    break;
            }
            members.sort(comparator);

            int totalMembers = members.size();
            int maxPage = (totalMembers - 1) / MEMBERS_PER_PAGE;
            int start = page * MEMBERS_PER_PAGE;
            int end = Math.min(start + MEMBERS_PER_PAGE, totalMembers);
            List<Clan.ClanMember> pageMembers = members.subList(start, end);

            String text = String.format("👥 *Участники клана %s (%d/%d):*", clan.getName(), page + 1, maxPage + 1);

            List<List<InlineKeyboardButton>> keyboardRows = new ArrayList<>();
            for (Clan.ClanMember member : pageMembers) {
                String buttonText;
                if ("builder".equals(viewType)) {
                    buttonText = String.format("🛖%d %s | 🏆%d", member.getBuilderHallLevel(), member.getName(), member.getVersusTrophies());
                } else {
                    String translatedRole = ROLE_TRANSLATIONS.getOrDefault(member.getRole(), member.getRole());
                    buttonText = String.format("🏰%d %s (%s) | 🏆%d", member.getTownHallLevel(), member.getName(), translatedRole, member.getTrophies());
                }
                keyboardRows.add(List.of(
                        InlineKeyboardButton.builder().text(buttonText).callbackData(Keyboards.PROFILE_CALLBACK + ":" + member.getTag()).build()
                ));
            }

            InlineKeyboardMarkup managementMarkup = Keyboards.memberListManagementMenu(clanTag, sortType, viewType);
            keyboardRows.addAll(managementMarkup.getKeyboard());

            String paginationCallbackPrefix = String.join(":", Keyboards.MEMBERS_SORT_CALLBACK, clanTag, sortType, viewType);
            InlineKeyboardMarkup paginationMarkup = Keyboards.paginationMenu(paginationCallbackPrefix, page, maxPage);
            keyboardRows.addAll(paginationMarkup.getKeyboard());

            InlineKeyboardMarkup finalKeyboard = InlineKeyboardMarkup.builder().keyboard(keyboardRows).build();

            if (messageId != null) {
                editMessage(chatId, messageId, text, finalKeyboard);
            } else {
                sendMessage(chatId, text, finalKeyboard);
            }
        });
    }

    private void displayWarListPage(long chatId, Integer messageId, String clanTag, WarSort sortOrder, int page) {
        List<WarData> allWars = dbService.getWars(sortOrder);

        if (allWars.isEmpty()) {
            String text = "По вашему запросу войн не найдено.";
            if (messageId != null) editMessage(chatId, messageId, text, null); else sendMessage(chatId, text, Keyboards.clanInspectionMenu());
            return;
        }

        int maxPage = (allWars.size() - 1) / WARS_PER_PAGE;
        int start = page * WARS_PER_PAGE;
        int end = Math.min(start + WARS_PER_PAGE, allWars.size());
        List<WarData> pageWars = allWars.subList(start, end);

        String title;
        if (sortOrder == WarSort.CWL_ONLY) {
            title = String.format("⚔️ *Войны ЛВК (%d/%d):*", page + 1, maxPage + 1);
        } else {
            title = String.format("⚔️ *История войн (%d/%d):*", page + 1, maxPage + 1);
        }
        String text = title + "\nВыберите войну для просмотра деталей.";

        List<List<InlineKeyboardButton>> keyboardRows = new ArrayList<>();
        DateTimeFormatter userFriendlyFormatter = DateTimeFormatter.ofPattern("dd.MM.yyyy");

        for (WarData war : pageWars) {
            ZonedDateTime endTime = ZonedDateTime.parse(war.getDateEnd(), COC_DATE_FORMATTER);

            String resultEmoji = "";
            if (war.getResult() != null) {
                switch (war.getResult().toLowerCase()) {
                    case "victory": case "win": resultEmoji = "✅ "; break;
                    case "defeat": case "lose": resultEmoji = "❌ "; break;
                    case "tie": resultEmoji = "➖ "; break;
                }
            }

            String buttonText = String.format("%sВойна от %s", resultEmoji, endTime.format(userFriendlyFormatter));
            keyboardRows.add(List.of(
                    InlineKeyboardButton.builder().text(buttonText).callbackData(String.join(":", Keyboards.WAR_INFO_CALLBACK, clanTag, war.getDateEnd())).build()
            ));
        }

        InlineKeyboardMarkup paginationMarkup = Keyboards.paginationMenu(Keyboards.WAR_LIST_CALLBACK, clanTag, sortOrder, page, maxPage);
        keyboardRows.addAll(paginationMarkup.getKeyboard());

        InlineKeyboardMarkup keyboard = InlineKeyboardMarkup.builder().keyboard(keyboardRows).build();

        if (messageId != null) {
            editMessage(chatId, messageId, text, keyboard);
        } else {
            sendMessage(chatId, text, keyboard);
        }
    }

    private void displaySingleWarDetails(long chatId, int messageId, String clanTag, String warEndTime) {
        dbService.getSingleWarFromDb(warEndTime).ifPresentOrElse(war -> {
            List<AttackData> attacks = dbService.getAttacksForWar(warEndTime);
            DateTimeFormatter userFriendlyFormatter = DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm");
            ZonedDateTime endTime = ZonedDateTime.parse(war.getDateEnd(), COC_DATE_FORMATTER);

            String resultText = "win".equalsIgnoreCase(war.getResult()) || "victory".equalsIgnoreCase(war.getResult()) ? "Победа" : ("lose".equalsIgnoreCase(war.getResult()) || "defeat".equalsIgnoreCase(war.getResult()) ? "Поражение" : "Ничья");

            String text = String.format(
                    "*🛡️ Детали войны от %s*\n\n" +
                            "*Противник:* %s\n" +
                            "*Результат:* %s\n" +
                            "*Размер:* %s\n" +
                            "*Счёт:* ⭐`%d` (%.2f%%) - ⭐`%d` (%.2f%%)\n" +
                            "*Атаки:* %d/%d",
                    endTime.format(userFriendlyFormatter),
                    war.getClan1().getName(),
                    resultText,
                    war.getSize(),
                    war.getClan1().getStars(), war.getClan1().getDestructionPercentage(),
                    war.getClan2().getStars(), war.getClan2().getDestructionPercentage(),
                    war.getClan1().getAttacksUsed(), Integer.parseInt(war.getSize().split(" ")[0]) * 2
            );

            StringBuilder sb = new StringBuilder(text);

            if (!attacks.isEmpty()) {
                sb.append("\n\n*-- Атаки нашего клана --*\n");
                Map<String, List<AttackData>> attacksByPlayer = attacks.stream()
                        .collect(Collectors.groupingBy(AttackData::getAttackerName));

                for (Map.Entry<String, List<AttackData>> entry : attacksByPlayer.entrySet()) {
                    sb.append(String.format("*%s*:\n", entry.getKey()));
                    for (AttackData attack : entry.getValue()) {
                        sb.append(String.format("  - ⭐`%d` (%s%%)\n", attack.getStars(), String.format("%.0f", attack.getDestruction())));
                    }
                }
            } else {
                sb.append("\n\n_Для этой войны не найдено данных об атаках в базе._");
            }

            String backCallback = String.join(":", Keyboards.WAR_LIST_CALLBACK, clanTag, WarSort.DATE_DESC.toString(), "0");
            InlineKeyboardButton backButton = InlineKeyboardButton.builder()
                    .text("⬅️ К списку войн")
                    .callbackData(backCallback)
                    .build();
            InlineKeyboardMarkup keyboard = InlineKeyboardMarkup.builder().keyboardRow(List.of(backButton)).build();

            editMessage(chatId, messageId, sb.toString(), keyboard);

        }, () -> editMessage(chatId, messageId, "Не удалось найти информацию об этой войне в базе данных.", null));
    }

    private void editMessage(long chatId, int messageId, String text, InlineKeyboardMarkup keyboard) {
        EditMessageText message = EditMessageText.builder()
                .chatId(chatId)
                .messageId(messageId)
                .text(text)
                .parseMode("Markdown")
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

    private void sendMessage(long chatId, String text, ReplyKeyboard keyboard) {
        SendMessage message = new SendMessage(String.valueOf(chatId), text);
        message.setParseMode("Markdown");
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