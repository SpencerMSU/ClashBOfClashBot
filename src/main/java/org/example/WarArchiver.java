package org.example;

import org.example.bot.ClashBot;
import org.example.cocapi.CocApiClient;
import org.example.cocapi.dto.currentwar.CurrentWar;
import org.example.cocapi.dto.currentwar.WarAttack;
import org.example.cocapi.dto.currentwar.WarMember;
import org.example.database.DatabaseService;
import org.example.database.model.WarToSave;

import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

public class WarArchiver {
    private final String clanTag;
    private final CocApiClient apiClient;
    private final DatabaseService dbService;
    private final ClashBot bot;
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

    private String notifiedWarStartTime = "";
    private String lastKnownWarEndTime = "";

    public WarArchiver(String clanTag, CocApiClient apiClient, DatabaseService dbService, ClashBot bot) {
        this.clanTag = clanTag;
        this.apiClient = apiClient;
        this.dbService = dbService;
        this.bot = bot;
    }

    public void start() {
        Runnable archiveTask = () -> {
            try {
                System.out.println("[Архиватор] Проверка текущей войны для клана " + clanTag);
                apiClient.getClanCurrentWar(clanTag).ifPresent(currentWar -> {

                    if ("preparation".equals(currentWar.getState())) {
                        ZonedDateTime startTime = ZonedDateTime.parse(currentWar.getStartTime(), DateTimeFormatter.ISO_DATE_TIME);
                        if (startTime.isBefore(ZonedDateTime.now().plusHours(1)) && !currentWar.getStartTime().equals(notifiedWarStartTime)) {
                            System.out.println("[Архиватор] Скоро начнется война! Отправка уведомлений...");
                            String messageText = String.format(
                                    "⚔️ *Внимание!* Скоро начнется клановая война!\n\n" +
                                            "*Противник:* %s\n" +
                                            "*Размер:* %d на %d\n" +
                                            "*Начало примерно через:* меньше часа.",
                                    currentWar.getOpponent().getName(),
                                    currentWar.getClan().getMembers().size(),
                                    currentWar.getOpponent().getMembers().size()
                            );

                            List<Long> userIds = dbService.getSubscribedUsers();
                            for (Long userId : userIds) {
                                bot.sendMessage(userId, messageText);
                            }
                            notifiedWarStartTime = currentWar.getStartTime();
                        }
                    }

                    if ("warEnded".equals(currentWar.getState()) && !dbService.warExists(currentWar.getEndTime())) {
                        System.out.println("[Архиватор] Обнаружена новая завершенная война: " + currentWar.getEndTime());
                        boolean isCwlWar = apiClient.getClanWarLeagueGroup(clanTag)
                                .map(group -> "inWar".equals(group.getState()) || "warEnded".equals(group.getState()))
                                .orElse(false);
                        analyzeAndSaveWar(currentWar, isCwlWar);
                        lastKnownWarEndTime = currentWar.getEndTime();
                    }
                });

                if (ZonedDateTime.now().getHour() % 6 == 0) {
                    apiClient.getClanInfo(clanTag).ifPresent(clan -> {
                        if (clan.getMemberList() != null) {
                            dbService.saveDonationSnapshot(clan.getMemberList());
                            System.out.println("[Архиватор] Снимок донатов сохранен.");
                        }
                    });
                }

            } catch (Exception e) {
                System.err.println("[Архиватор] Ошибка в фоновой задаче:");
                e.printStackTrace();
            }
        };

        scheduler.scheduleAtFixedRate(archiveTask, 1, 15, TimeUnit.MINUTES);
        System.out.println("Сервис архивации войн запущен для клана " + clanTag);
    }

    private void analyzeAndSaveWar(CurrentWar war, boolean isCwlWar) {
        long warEndTimestamp = ZonedDateTime.parse(war.getEndTime(), DateTimeFormatter.ISO_DATE_TIME).toEpochSecond();
        long tenHoursBeforeEnd = warEndTimestamp - (10 * 60 * 60);

        if (war.getClan() == null || war.getClan().getMembers() == null) {
            System.err.println("[Архиватор] Ошибка: нет данных об участниках нашего клана.");
            return;
        }

        Map<String, WarMember> ourMembersMap = war.getClan().getMembers().stream()
                .collect(Collectors.toMap(WarMember::getTag, member -> member));

        Map<WarMember, List<WarAttack>> attacksByMember = new HashMap<>();
        int totalViolations = 0;

        for (WarMember member : war.getClan().getMembers()) {
            if (member.getAttacks() == null || member.getAttacks().isEmpty()) continue;

            attacksByMember.put(member, member.getAttacks());

            if (!isCwlWar) {
                for (WarAttack attack : member.getAttacks()) {
                    boolean isViolation = false;
                    WarMember defender = ourMembersMap.get(attack.getDefenderTag());
                    if (defender == null) continue;

                    if (attack.getOrder() == 1 && member.getMapPosition() != defender.getMapPosition()) {
                        isViolation = true;
                    }

                    if (attack.getOrder() == 2 && member.getMapPosition() != defender.getMapPosition()) {
                        long attackTimestamp = System.currentTimeMillis() / 1000L;
                        if (attackTimestamp < tenHoursBeforeEnd) {
                            isViolation = true;
                        }
                    }

                    if (isViolation) {
                        totalViolations++;
                    }
                    dbService.saveAttack(war.getEndTime(), member.getTag(), member.getName(), attack.getDefenderTag(), attack.getStars(), attack.getDestructionPercentage(), attack.getOrder(), System.currentTimeMillis() / 1000L, isViolation ? 1 : 0);
                }
            } else {
                for (WarAttack attack : member.getAttacks()) {
                    dbService.saveAttack(war.getEndTime(), member.getTag(), member.getName(), attack.getDefenderTag(), attack.getStars(), attack.getDestructionPercentage(), attack.getOrder(), System.currentTimeMillis() / 1000L, 0);
                }
            }
        }

        int totalAttacksUsed = war.getClan().getMembers().stream()
                .mapToInt(m -> m.getAttacks() == null ? 0 : m.getAttacks().size())
                .sum();

        WarToSave warToSave = new WarToSave(
                war.getEndTime(), war.getOpponent().getName(),
                war.getClan().getMembers().size(), war.getClan().getStars(),
                war.getOpponent().getStars(), war.getClan().getDestructionPercentage(),
                war.getOpponent().getDestructionPercentage(), totalAttacksUsed,
                determineResult(war.getClan().getStars(), war.getOpponent().getStars()),
                isCwlWar, totalViolations, attacksByMember
        );

        dbService.saveWar(warToSave);
        System.out.println("[Архиватор] Война против " + warToSave.getOpponentName() + " сохранена. Является ЛВК: " + isCwlWar);
    }

    private String determineResult(int clanStars, int opponentStars) {
        if (clanStars > opponentStars) return "win";
        if (clanStars < opponentStars) return "lose";
        return "tie";
    }

    public void stop() {
        scheduler.shutdown();
    }
}