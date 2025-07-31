package org.example;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.example.cocapi.dto.importer.Participant;
import org.example.cocapi.dto.importer.WarData;
import org.example.cocapi.dto.importer.WarJson;
import org.example.database.DatabaseService;

import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.util.List;
import java.util.Locale;

public class OneTimeImporter {

    private static final String DB_URL = "jdbc:sqlite:clashbot.db";
    private static final String JSON_FILE_PATH = "/war_data.json";

    public static void main(String[] args) {
        System.out.println("Запуск импорта данных о войнах из JSON-файла...");
        ObjectMapper mapper = new ObjectMapper();
        DatabaseService dbService = new DatabaseService();

        try (Connection conn = DriverManager.getConnection(DB_URL);
             InputStream jsonStream = OneTimeImporter.class.getResourceAsStream(JSON_FILE_PATH)) {

            if (jsonStream == null) {
                System.err.println("Ошибка: не удалось найти файл " + JSON_FILE_PATH);
                return;
            }

            WarJson warJson = mapper.readValue(jsonStream, WarJson.class);
            List<WarData> wars = warJson.getWars();
            System.out.println("Найдено войн в файле: " + wars.size());

            String sqlWar = "INSERT OR REPLACE INTO wars(end_time, opponent_name, team_size, clan_stars, opponent_stars, clan_destruction, opponent_destruction, clan_attacks_used, result) VALUES(?,?,?,?,?,?,?,?,?)";
            String sqlAttack = "INSERT INTO attacks(war_id, attacker_name, defender_tag, stars, destruction, is_rule_violation) VALUES(?,?,?,?,?,?)";

            for (WarData war : wars) {
                if (war.getClan1() == null || war.getClan1().getParticipants() == null) continue;

                String warEndTimeForDb = convertDate(war.getDateEnd());
                if (warEndTimeForDb == null) {
                    System.err.println("  Пропускаем войну с нераспознанной датой: " + war.getDateEnd());
                    continue;
                }

                int teamSize = Integer.parseInt(war.getSize().split(" ")[0]);
                int clanStars = war.getTotalStars();
                double clanDestruction = Double.parseDouble(war.getDestructionPercentage().replace("%", ""));
                int clanAttacksUsed = Integer.parseInt(war.getAttacksUsed().split("/")[0].trim());
                String result = war.getResult() != null ? war.getResult() : "Tie";

                try (PreparedStatement pstmt = conn.prepareStatement(sqlWar)) {
                    pstmt.setString(1, warEndTimeForDb);
                    pstmt.setString(2, "Неизвестный противник"); // В JSON нет имени оппонента
                    pstmt.setInt(3, teamSize);
                    pstmt.setInt(4, clanStars);
                    pstmt.setInt(5, 0); // В JSON нет звезд оппонента
                    pstmt.setDouble(6, clanDestruction);
                    pstmt.setDouble(7, 0.0); // В JSON нет разрушения оппонента
                    pstmt.setInt(8, clanAttacksUsed);
                    pstmt.setString(9, result);
                    pstmt.executeUpdate();
                }

                dbService.deleteAttacksForWar(warEndTimeForDb);

                for (Participant participant : war.getClan1().getParticipants()) {
                    if (participant.getAttacks() == null) continue;
                    for (org.example.cocapi.dto.importer.Attack attack : participant.getAttacks()) {
                        try (PreparedStatement pstmt = conn.prepareStatement(sqlAttack)) {
                            pstmt.setString(1, warEndTimeForDb);
                            pstmt.setString(2, participant.getName());
                            pstmt.setString(3, "#" + attack.getOpponentNumber());
                            pstmt.setInt(4, attack.getStars());
                            double destruction = Double.parseDouble(attack.getDestructionPercentage().replace("%", ""));
                            pstmt.setDouble(5, destruction);
                            pstmt.setInt(6, -1);
                            pstmt.executeUpdate();
                        }
                    }
                }
                System.out.println("  Война, закончившаяся " + war.getDateEnd() + ", успешно обработана.");
            }
            System.out.println("Импорт из JSON успешно завершен.");

        } catch (Exception e) {
            System.err.println("Критическая ошибка во время импорта: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static String convertDate(String dateStr) {
        try {
            DateTimeFormatter formatter = new DateTimeFormatterBuilder()
                    .parseCaseInsensitive()
                    .appendPattern("M/d/yy, h:mm a")
                    .toFormatter(Locale.ENGLISH);
            LocalDateTime ldt = LocalDateTime.parse(dateStr, formatter);
            return ldt.atZone(ZoneId.of("Europe/Moscow"))
                    .withZoneSameInstant(java.time.ZoneOffset.UTC)
                    .format(DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss.SSS'Z'"));
        } catch (Exception e) {
            return null;
        }
    }
}