package org.example.database;

import org.example.bot.WarSort;
import org.example.cocapi.dto.Clan;
import org.example.cocapi.dto.importer.WarData;
import org.example.database.model.AttackData;
import org.example.database.model.User;
import org.example.database.model.WarToSave;

import java.sql.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class DatabaseService {
    private static final String DB_URL = "jdbc:sqlite:clashbot.db";

    private Connection connect() throws SQLException {
        return DriverManager.getConnection(DB_URL);
    }

    public void initDb() {
        String createUserTable = "CREATE TABLE IF NOT EXISTS users (" +
                "  telegram_id INTEGER PRIMARY KEY," +
                "  player_tag TEXT NOT NULL UNIQUE" +
                ");";
        String createWarsTable = "CREATE TABLE IF NOT EXISTS wars (" +
                "  end_time TEXT PRIMARY KEY," +
                "  opponent_name TEXT NOT NULL," +
                "  team_size INTEGER NOT NULL," +
                "  clan_stars INTEGER NOT NULL," +
                "  opponent_stars INTEGER NOT NULL," +
                "  clan_destruction REAL NOT NULL," +
                "  opponent_destruction REAL NOT NULL," +
                "  clan_attacks_used INTEGER NOT NULL," +
                "  result TEXT NOT NULL," +
                "  is_cwl_war INTEGER NOT NULL DEFAULT 0," +
                "  total_violations INTEGER DEFAULT 0" +
                ");";
        String createAttacksTable = "CREATE TABLE IF NOT EXISTS attacks (" +
                "  id INTEGER PRIMARY KEY AUTOINCREMENT," +
                "  war_id TEXT NOT NULL," +
                "  attacker_tag TEXT," +
                "  attacker_name TEXT NOT NULL," +
                "  defender_tag TEXT," +
                "  stars INTEGER NOT NULL," +
                "  destruction REAL NOT NULL," +
                "  attack_order INTEGER," +
                "  attack_timestamp INTEGER," +
                "  is_rule_violation INTEGER," +
                "  FOREIGN KEY (war_id) REFERENCES wars(end_time)" +
                ");";
        String createCwlSeasonsTable = "CREATE TABLE IF NOT EXISTS cwl_seasons (" +
                "  season_date TEXT PRIMARY KEY," +
                "  participants_json TEXT," +
                "  bonus_results_json TEXT" +
                ");";
        String createPlayerStatsSnapshotsTable = "CREATE TABLE IF NOT EXISTS player_stats_snapshots (" +
                "  snapshot_time TEXT NOT NULL," +
                "  player_tag TEXT NOT NULL," +
                "  donations INTEGER NOT NULL," +
                "  PRIMARY KEY (snapshot_time, player_tag)" +
                ");";
        String createNotificationsTable = "CREATE TABLE IF NOT EXISTS notifications (" +
                "  telegram_id INTEGER PRIMARY KEY" +
                ");";

        try (Connection conn = this.connect(); Statement stmt = conn.createStatement()) {
            stmt.execute(createUserTable);
            stmt.execute(createWarsTable);
            stmt.execute(createAttacksTable);
            stmt.execute(createCwlSeasonsTable);
            stmt.execute(createPlayerStatsSnapshotsTable);
            stmt.execute(createNotificationsTable);
            System.out.println("База данных успешно инициализирована.");
        } catch (SQLException e) {
            System.out.println("Ошибка при инициализации БД: " + e.getMessage());
        }
    }

    public Optional<User> findUser(long telegramId) {
        String sql = "SELECT telegram_id, player_tag FROM users WHERE telegram_id = ?";
        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setLong(1, telegramId);
            ResultSet rs = pstmt.executeQuery();
            if (rs.next()) {
                User user = new User();
                user.setTelegramId(rs.getLong("telegram_id"));
                user.setPlayerTag(rs.getString("player_tag"));
                return Optional.of(user);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return Optional.empty();
    }

    public boolean isTagLinked(String playerTag) {
        String sql = "SELECT 1 FROM users WHERE player_tag = ?";
        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, playerTag);
            return pstmt.executeQuery().next();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return false;
    }

    public void linkUser(long telegramId, String playerTag) {
        String sql = "INSERT INTO users(telegram_id, player_tag) VALUES(?, ?) ON CONFLICT(telegram_id) DO UPDATE SET player_tag = ?;";
        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setLong(1, telegramId);
            pstmt.setString(2, playerTag);
            pstmt.setString(3, playerTag);
            pstmt.executeUpdate();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public List<WarData> getWars(WarSort sortOrder) {
        StringBuilder sql = new StringBuilder("SELECT end_time, opponent_name, team_size, result FROM wars");
        List<String> params = new ArrayList<>();
        if (sortOrder == WarSort.CWL_ONLY) {
            LocalDate today = LocalDate.now();
            LocalDate startDate;
            LocalDate endDate;
            if (today.getDayOfMonth() < 5) {
                endDate = today.withDayOfMonth(5);
                startDate = today.minusMonths(1).withDayOfMonth(5);
            } else {
                startDate = today.withDayOfMonth(5);
                endDate = today.plusMonths(1).withDayOfMonth(5);
            }
            sql.append(" WHERE date(substr(end_time, 1, 4) || '-' || substr(end_time, 5, 2) || '-' || substr(end_time, 7, 2)) BETWEEN date(?) AND date(?)");
            params.add(startDate.toString());
            params.add(endDate.toString());
        }
        switch (sortOrder) {
            case DATE_DESC:
            case CWL_ONLY:
                sql.append(" ORDER BY end_time DESC");
                break;
            case DATE_ASC:
                sql.append(" ORDER BY end_time ASC");
                break;
        }
        List<WarData> wars = new ArrayList<>();
        try (Connection conn = this.connect();
             PreparedStatement pstmt = conn.prepareStatement(sql.toString())) {
            for (int i = 0; i < params.size(); i++) {
                pstmt.setString(i + 1, params.get(i));
            }
            ResultSet rs = pstmt.executeQuery();
            while (rs.next()) {
                WarData war = new WarData(
                        rs.getString("end_time"),
                        rs.getString("opponent_name"),
                        rs.getInt("team_size") + " vs " + rs.getInt("team_size"),
                        rs.getString("result")
                );
                wars.add(war);
            }
        } catch (SQLException e) {
            System.out.println("Ошибка при получении войн: " + e.getMessage());
        }
        return wars;
    }

    public Optional<WarData> getSingleWarFromDb(String endTime) {
        String sql = "SELECT * FROM wars WHERE end_time = ?";
        try (Connection conn = this.connect();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, endTime);
            ResultSet rs = pstmt.executeQuery();
            if (rs.next()) {
                WarData warData = new WarData(
                        rs.getString("end_time"),
                        rs.getString("opponent_name"),
                        rs.getInt("team_size") + " vs " + rs.getInt("team_size"),
                        rs.getString("result"),
                        rs.getInt("clan_stars"),
                        rs.getDouble("clan_destruction"),
                        rs.getInt("clan_attacks_used"),
                        rs.getInt("opponent_stars"),
                        rs.getDouble("opponent_destruction")
                );
                return Optional.of(warData);
            }
        } catch (SQLException e) {
            System.out.println(e.getMessage());
        }
        return Optional.empty();
    }

    public List<AttackData> getAttacksForWar(String warEndTime) {
        List<AttackData> attacks = new ArrayList<>();
        String sql = "SELECT attacker_name, stars, destruction FROM attacks WHERE war_id = ? ORDER BY id";
        try (Connection conn = this.connect();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, warEndTime);
            ResultSet rs = pstmt.executeQuery();
            while (rs.next()) {
                attacks.add(new AttackData(
                        rs.getString("attacker_name"),
                        rs.getInt("stars"),
                        rs.getDouble("destruction")
                ));
            }
        } catch (SQLException e) {
            System.out.println("Ошибка при получении атак: " + e.getMessage());
        }
        return attacks;
    }

    public void deleteAttacksForWar(String warEndTime) {
        String sql = "DELETE FROM attacks WHERE war_id = ?";
        try (Connection conn = this.connect();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, warEndTime);
            pstmt.executeUpdate();
        } catch (SQLException e) {
            System.out.println("Ошибка при удалении старых атак: " + e.getMessage());
        }
    }

    public boolean warExists(String warEndTime) {
        String sql = "SELECT 1 FROM wars WHERE end_time = ?";
        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, warEndTime);
            return pstmt.executeQuery().next();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return false;
    }

    public void saveWar(WarToSave war) {
        String sql = "INSERT OR REPLACE INTO wars(end_time, opponent_name, team_size, clan_stars, opponent_stars, clan_destruction, opponent_destruction, clan_attacks_used, result, is_cwl_war, total_violations) VALUES(?,?,?,?,?,?,?,?,?,?,?)";
        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, war.getEndTime());
            pstmt.setString(2, war.getOpponentName());
            pstmt.setInt(3, war.getTeamSize());
            pstmt.setInt(4, war.getClanStars());
            pstmt.setInt(5, war.getOpponentStars());
            pstmt.setDouble(6, war.getClanDestruction());
            pstmt.setDouble(7, war.getOpponentDestruction());
            pstmt.setInt(8, war.getClanAttacksUsed());
            pstmt.setString(9, war.getResult());
            pstmt.setInt(10, war.isCwlWar() ? 1 : 0);
            pstmt.setInt(11, war.getTotalViolations());
            pstmt.executeUpdate();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void saveAttack(String warId, String attackerTag, String attackerName, String defenderTag, int stars, double destruction, int order, long timestamp, int violation) {
        String sql = "INSERT INTO attacks(war_id, attacker_tag, attacker_name, defender_tag, stars, destruction, attack_order, attack_timestamp, is_rule_violation) VALUES(?,?,?,?,?,?,?,?,?)";
        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, warId);
            pstmt.setString(2, attackerTag);
            pstmt.setString(3, attackerName);
            pstmt.setString(4, defenderTag);
            pstmt.setInt(5, stars);
            pstmt.setDouble(6, destruction);
            pstmt.setInt(7, order);
            pstmt.setLong(8, timestamp);
            pstmt.setInt(9, violation);
            pstmt.executeUpdate();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void saveDonationSnapshot(List<Clan.ClanMember> members) {
        String sql = "INSERT OR REPLACE INTO player_stats_snapshots(snapshot_time, player_tag, donations) VALUES(strftime('%Y-%m-%d %H:%M:%S', 'now'),?,?)";
        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            for (Clan.ClanMember member : members) {
                pstmt.setString(1, member.getTag());
                pstmt.setInt(2, member.getDonations());
                pstmt.addBatch();
            }
            pstmt.executeBatch();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void subscribeUserToNotifications(long telegramId) {
        String sql = "INSERT OR IGNORE INTO notifications(telegram_id) VALUES(?)";
        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setLong(1, telegramId);
            pstmt.executeUpdate();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void unsubscribeUserFromNotifications(long telegramId) {
        String sql = "DELETE FROM notifications WHERE telegram_id = ?";
        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setLong(1, telegramId);
            pstmt.executeUpdate();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public boolean isUserSubscribed(long telegramId) {
        String sql = "SELECT 1 FROM notifications WHERE telegram_id = ?";
        try (Connection conn = connect(); PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setLong(1, telegramId);
            return pstmt.executeQuery().next();
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return false;
    }

    public List<Long> getSubscribedUsers() {
        List<Long> userIds = new ArrayList<>();
        String sql = "SELECT telegram_id FROM notifications";
        try (Connection conn = connect(); Statement stmt = conn.createStatement(); ResultSet rs = stmt.executeQuery(sql)) {
            while (rs.next()) {
                userIds.add(rs.getLong("telegram_id"));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return userIds;
    }

    public Map<String, Integer> countPlayerAttacksInPeriod(String startDate, String endDate) {
        Map<String, Integer> attackCounts = new HashMap<>();
        String sql = "SELECT a.attacker_name, COUNT(a.id) as attack_count " +
                "FROM attacks a JOIN wars w ON a.war_id = w.end_time " +
                "WHERE w.is_cwl_war = 0 AND date(substr(w.end_time, 1, 4) || '-' || substr(w.end_time, 5, 2) || '-' || substr(w.end_time, 7, 2)) BETWEEN date(?) AND date(?) " +
                "GROUP BY a.attacker_name " +
                "ORDER BY attack_count DESC";
        try (Connection conn = this.connect();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, startDate);
            pstmt.setString(2, endDate);
            ResultSet rs = pstmt.executeQuery();
            while (rs.next()) {
                attackCounts.put(rs.getString("attacker_name"), rs.getInt("attack_count"));
            }
        } catch (SQLException e) {
            System.out.println("Ошибка при подсчете атак: " + e.getMessage());
        }
        return attackCounts;
    }
}