package org.example.bot.view;

import org.example.bot.ClashBot;
import org.example.bot.Keyboards;
import org.example.bot.WarSort;
import org.example.cocapi.CocApiClient;
import org.example.cocapi.dto.Clan;
import org.example.cocapi.dto.Player;
import org.example.cocapi.dto.currentwar.CurrentWar;
import org.example.cocapi.dto.importer.WarData;
import org.example.database.DatabaseService;
import org.example.database.model.AttackData;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.ReplyKeyboard;
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardButton;

import java.time.LocalDate;
import java.time.YearMonth;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

public class MessageGenerator {

    private final ClashBot bot;
    private final DatabaseService dbService;
    private final CocApiClient cocApiClient;
    private static final int MEMBERS_PER_PAGE = 10;
    private static final int WARS_PER_PAGE = 10;
    private static final Map<String, String> ROLE_TRANSLATIONS = Map.of(
            "leader", "👑 Глава", "coLeader", "⚜️ Соруководитель",
            "admin", "🔰 Старейшина", "member", "👤 Участник"
    );
    private static final DateTimeFormatter COC_DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss.SSS'Z'").withZone(ZoneOffset.UTC);

    public MessageGenerator(ClashBot bot, DatabaseService dbService, CocApiClient cocApiClient) {
        this.bot = bot;
        this.dbService = dbService;
        this.cocApiClient = cocApiClient;
    }

    public void handleProfileMenuRequest(long chatId) {
        dbService.findUser(chatId).ifPresentOrElse(
                user -> cocApiClient.getPlayerInfo(user.getPlayerTag()).ifPresentOrElse(
                        player -> bot.sendMessage(chatId, "Меню профиля:", Keyboards.profileMenu(player.getName())),
                        () -> bot.sendMessage(chatId, "Меню профиля:", Keyboards.profileMenu(null))
                ),
                () -> bot.sendMessage(chatId, "Меню профиля:", Keyboards.profileMenu(null))
        );
    }

    public void handleMyProfileRequest(long chatId) {
        dbService.findUser(chatId).ifPresentOrElse(
                user -> displayPlayerInfo(chatId, user.getPlayerTag(), Keyboards.profileMenu(null)),
                () -> handleProfileMenuRequest(chatId)
        );
    }

    public void handleLinkAccount(long chatId, String playerTag) {
        if (dbService.isTagLinked(playerTag)) {
            bot.sendMessage(chatId, "Этот тег уже привязан к другому аккаунту Telegram.");
            return;
        }
        Optional<Player> playerOpt = cocApiClient.getPlayerInfo(playerTag);
        if (playerOpt.isPresent()) {
            dbService.linkUser(chatId, playerTag);
            Player player = playerOpt.get();
            bot.sendMessage(chatId, "✅ Аккаунт " + player.getName() + " успешно привязан!", Keyboards.profileMenu(player.getName()));
        } else {
            bot.sendMessage(chatId, "❌ Игрок с тегом " + playerTag + " не найден.", Keyboards.profileMenu(null));
        }
    }

    public void handleMyClanRequest(long chatId) {
        Optional<org.example.database.model.User> userOpt = dbService.findUser(chatId);
        if (userOpt.isEmpty()) {
            bot.sendMessage(chatId, "Ваш аккаунт не привязан.", Keyboards.clanMenu());
            return;
        }
        cocApiClient.getPlayerInfo(userOpt.get().getPlayerTag()).ifPresentOrElse(
                player -> {
                    Player.ClanInfo clanInfo = player.getClan();
                    if (clanInfo != null && clanInfo.getTag() != null) {
                        displayClanInfo(chatId, clanInfo.getTag());
                    } else {
                        bot.sendMessage(chatId, "Вы не состоите в клане.", Keyboards.clanMenu());
                    }
                },
                () -> bot.sendMessage(chatId, "Не удалось получить информацию о вашем профиле.", Keyboards.clanMenu())
        );
    }

    public void handleCurrentCwlRequest(long chatId, String clanTag) {
        cocApiClient.getClanWarLeagueGroup(clanTag).ifPresentOrElse(
                leagueGroup -> {
                    if ("inWar".equals(leagueGroup.getState()) || "preparation".equals(leagueGroup.getState())) {
                        bot.sendMessage(chatId, "⚔️ Идет Лига Клановых Войн!\n\nФункция детального просмотра текущего раунда в разработке.");
                    } else {
                        bot.sendMessage(chatId, "✅ Лига Клановых Войн завершена или еще не началась.");
                    }
                },
                () -> bot.sendMessage(chatId, "Клан в данный момент не участвует в Лиге Клановых Войн.")
        );
    }

    public void handleNotificationMenu(long chatId) {
        boolean isSubscribed = dbService.isUserSubscribed(chatId);
        String text = isSubscribed
                ? "Вы подписаны на уведомления о начале клановых войн."
                : "Вы не подписаны на уведомления. Хотите получать сообщение за час до начала КВ?";
        bot.sendMessage(chatId, text, Keyboards.notificationMenu(isSubscribed));
    }

    public void handleNotificationToggle(long chatId, int messageId) {
        boolean isSubscribed = dbService.isUserSubscribed(chatId);
        String notificationText;
        if (isSubscribed) {
            dbService.unsubscribeUserFromNotifications(chatId);
            notificationText = "✅ Вы успешно отписались от уведомлений.";
        } else {
            dbService.subscribeUserToNotifications(chatId);
            notificationText = "✅ Вы успешно подписались на уведомления о начале КВ!";
        }
        bot.editMessage(chatId, messageId, notificationText, null);
    }

    public void handleCurrentWarRequest(long chatId, String clanTag) {
        cocApiClient.getClanCurrentWar(clanTag).ifPresentOrElse(
                war -> {
                    DateTimeFormatter userFriendlyFormatter = DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm");

                    StringBuilder sb = new StringBuilder();
                    sb.append(String.format("⚔️ Текущая война против: %s\n\n", war.getOpponent().getName()));
                    sb.append(String.format("Счёт: ⭐%d (%.2f%%) - ⭐%d (%.2f%%)\n",
                            war.getClan().getStars(), war.getClan().getDestructionPercentage(),
                            war.getOpponent().getStars(), war.getOpponent().getDestructionPercentage()
                    ));

                    if ("preparation".equals(war.getState())) {
                        ZonedDateTime startTime = ZonedDateTime.parse(war.getStartTime(), COC_DATE_FORMATTER);
                        sb.append(String.format("Состояние: День подготовки\nНачало битвы: %s\n", startTime.format(userFriendlyFormatter)));
                    } else {
                        ZonedDateTime endTime = ZonedDateTime.parse(war.getEndTime(), COC_DATE_FORMATTER);
                        sb.append(String.format("Состояние: День битвы\nОкончание: %s\n", endTime.format(userFriendlyFormatter)));
                    }

                    int attacksPerMember = war.getAttacksPerMember();
                    List<String> slackers = war.getClan().getMembers().stream()
                            .filter(m -> m.getAttacks() == null || m.getAttacks().size() < attacksPerMember)
                            .map(m -> String.format("- %s (%d/%d)", m.getName(), m.getAttacks() == null ? 0 : m.getAttacks().size(), attacksPerMember))
                            .collect(Collectors.toList());

                    if (!slackers.isEmpty()) {
                        sb.append("\nНе провели все атаки:\n");
                        sb.append(String.join("\n", slackers));
                    } else {
                        sb.append("\nВсе участники провели свои атаки!");
                    }

                    bot.sendMessage(chatId, sb.toString());
                },
                () -> bot.sendMessage(chatId, "✅ Клан сейчас не участвует в обычной войне.")
        );
    }

    public void handleCwlBonusRequest(long chatId, int messageId, String yearMonth) {
        YearMonth selectedMonth = YearMonth.parse(yearMonth);
        LocalDate endDate = selectedMonth.atDay(5);
        LocalDate startDate = endDate.minusMonths(1);

        DateTimeFormatter dbFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
        Map<String, Integer> attackCounts = dbService.countPlayerAttacksInPeriod(startDate.format(dbFormatter), endDate.format(dbFormatter));

        if (attackCounts.isEmpty()) {
            bot.editMessage(chatId, messageId, "Не найдено данных об атаках в КВ за этот период.", null);
            return;
        }

        DateTimeFormatter userFriendlyFormatter = DateTimeFormatter.ofPattern("dd.MM.yy");
        String period = String.format("(учитываются атаки в обычных КВ с %s по %s)",
                startDate.format(userFriendlyFormatter),
                endDate.format(userFriendlyFormatter));

        StringBuilder sb = new StringBuilder();
        sb.append(String.format("🏆 Рейтинг по атакам для ЛВК %s\n", selectedMonth.format(DateTimeFormatter.ofPattern("LLLL yyyy", new Locale("ru")))));
        sb.append(period).append("\n\n");

        final int[] rank = {1};
        attackCounts.entrySet().stream()
                .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
                .forEach(entry -> {
                    String medal = "";
                    if (rank[0] == 1) medal = "🥇 ";
                    if (rank[0] == 2) medal = "🥈 ";
                    if (rank[0] == 3) medal = "🥉 ";
                    sb.append(String.format("%s%s: %d атак\n", medal, entry.getKey(), entry.getValue()));
                    rank[0]++;
                });

        bot.editMessage(chatId, messageId, sb.toString(), null);
    }

    public void displayPlayerInfo(long chatId, String playerTag, ReplyKeyboard keyboardOnSuccess) {
        Optional<Player> playerOpt = cocApiClient.getPlayerInfo(playerTag);
        if (playerOpt.isPresent()) {
            Player player = playerOpt.get();
            String clanName = (player.getClan() != null && player.getClan().getName() != null) ? player.getClan().getName() : "Нет клана";
            String text = String.format(
                    "👤 Профиль игрока: %s\n" +
                            "🏷 Тег: %s\n\n" +
                            "--- Основная деревня ---\n" +
                            "🏰 Ратуша: %d уровня\n" +
                            "🎖 Уровень: %d\n" +
                            "🏆 Трофеи: %d\n" +
                            "⭐ Звёзды войны: %d\n" +
                            "🛡 Клан: %s\n\n" +
                            "--- Деревня строителя ---\n" +
                            "🛖 Дом строителя: %d уровня\n" +
                            "🏆 Трофеи (ДС): %d",
                    player.getName(), player.getTag(),
                    player.getTownHallLevel(), player.getExpLevel(),
                    player.getTrophies(), player.getWarStars(), clanName,
                    player.getBuilderHallLevel(), player.getVersusTrophies()
            );
            bot.sendMessage(chatId, text, keyboardOnSuccess);
        } else {
            bot.sendMessage(chatId, "❌ Игрок с тегом " + playerTag + " не найден.", keyboardOnSuccess);
        }
    }

    public void displayClanInfo(long chatId, String clanTag) {
        cocApiClient.getClanInfo(clanTag).ifPresentOrElse(
                clan -> {
                    bot.getUserInspectingClan().put(chatId, clan.getTag());
                    String text = String.format("🛡️ Вы просматриваете клан: %s\n\nВыберите действие из меню ниже.", clan.getName());
                    bot.sendMessage(chatId, text, Keyboards.clanInspectionMenu());
                },
                () -> bot.sendMessage(chatId, "❌ Клан с тегом " + clanTag + " не найден.", Keyboards.clanMenu())
        );
    }

    public void displayMembersPage(long chatId, Integer messageId, String clanTag, int page, String sortType, String viewType) {
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

            String text = String.format("👥 Участники клана %s (%d/%d):", clan.getName(), page + 1, maxPage + 1);

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
                bot.editMessage(chatId, messageId, text, finalKeyboard);
            } else {
                bot.sendMessage(chatId, text, finalKeyboard);
            }
        });
    }

    public void displayWarListPage(long chatId, Integer messageId, String clanTag, WarSort sortOrder, int page) {
        List<WarData> allWars = dbService.getWars(sortOrder);

        if (allWars.isEmpty()) {
            String text = "По вашему запросу войн не найдено.";
            if (messageId != null) bot.editMessage(chatId, messageId, text, null); else bot.sendMessage(chatId, text, Keyboards.clanInspectionMenu());
            return;
        }

        int maxPage = (allWars.size() - 1) / WARS_PER_PAGE;
        int start = page * WARS_PER_PAGE;
        int end = Math.min(start + WARS_PER_PAGE, allWars.size());
        List<WarData> pageWars = allWars.subList(start, end);

        String title;
        if (sortOrder == WarSort.CWL_ONLY) {
            title = String.format("⚔️ Войны ЛВК (%d/%d):", page + 1, maxPage + 1);
        } else {
            title = String.format("⚔️ История войн (%d/%d):", page + 1, maxPage + 1);
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
            bot.editMessage(chatId, messageId, text, keyboard);
        } else {
            bot.sendMessage(chatId, text, keyboard);
        }
    }

    public void displaySingleWarDetails(long chatId, int messageId, String clanTag, String warEndTime) {
        dbService.getSingleWarFromDb(warEndTime).ifPresentOrElse(war -> {
            List<AttackData> attacks = dbService.getAttacksForWar(warEndTime);
            DateTimeFormatter userFriendlyFormatter = DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm");
            ZonedDateTime endTime = ZonedDateTime.parse(war.getDateEnd(), COC_DATE_FORMATTER);

            String resultText = "win".equalsIgnoreCase(war.getResult()) || "victory".equalsIgnoreCase(war.getResult()) ? "Победа" : ("lose".equalsIgnoreCase(war.getResult()) || "defeat".equalsIgnoreCase(war.getResult()) ? "Поражение" : "Ничья");

            String text = String.format(
                    "🛡️ Детали войны от %s\n\n" +
                            "Противник: %s\n" +
                            "Результат: %s\n" +
                            "Размер: %s\n" +
                            "Счёт: ⭐%d (%.2f%%) - ⭐%d (%.2f%%)\n" +
                            "Атаки: %d/%d",
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
                sb.append("\n\n-- Атаки нашего клана --\n");
                Map<String, List<AttackData>> attacksByPlayer = attacks.stream()
                        .collect(Collectors.groupingBy(AttackData::getAttackerName));

                for (Map.Entry<String, List<AttackData>> entry : attacksByPlayer.entrySet()) {
                    sb.append(String.format("\n%s:\n", entry.getKey()));
                    for (AttackData attack : entry.getValue()) {
                        sb.append(String.format("  - ⭐%d (%s%%)\n", attack.getStars(), String.format("%.0f", attack.getDestruction())));
                    }
                }
            } else {
                sb.append("\n\nДля этой войны не найдено данных об атаках в базе.");
            }

            String backCallback = String.join(":", Keyboards.WAR_LIST_CALLBACK, clanTag, WarSort.DATE_DESC.toString(), "0");
            InlineKeyboardButton backButton = InlineKeyboardButton.builder()
                    .text("⬅️ К списку войн")
                    .callbackData(backCallback)
                    .build();
            InlineKeyboardMarkup keyboard = InlineKeyboardMarkup.builder().keyboardRow(List.of(backButton)).build();

            bot.editMessage(chatId, messageId, sb.toString(), keyboard);

        }, () -> bot.editMessage(chatId, messageId, "Не удалось найти информацию об этой войне в базе данных.", null));
    }
}