package org.example.cocapi.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Clan {
    private String tag;
    private String name;
    private String type;
    private boolean isWarLogPublic;
    private int clanLevel;
    private int clanPoints;
    private int requiredTrophies;
    private int warWins;
    private int warWinStreak;
    private int members;
    private String description;
    private List<ClanMember> memberList;
    private List<Label> labels;
    private ClanCapital clanCapital;

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ClanMember {
        private String tag;
        private String name;
        private String role;
        private int townHallLevel; // Добавлено для сортировки
        private int trophies;
        private int donations;
        private int donationsReceived;
        // Новые поля для Деревни Строителя
        private int builderHallLevel;
        private int versusTrophies;

        // Getters
        public String getTag() { return tag; }
        public String getName() { return name; }
        public String getRole() { return role; }
        public int getTownHallLevel() { return townHallLevel; }
        public int getTrophies() { return trophies; }
        public int getDonations() { return donations; }
        public int getDonationsReceived() { return donationsReceived; }
        public int getBuilderHallLevel() { return builderHallLevel; }
        public int getVersusTrophies() { return versusTrophies; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Label {
        private String name;
        public String getName() { return name; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ClanCapital {
        private int capitalHallLevel;
        public int getCapitalHallLevel() { return capitalHallLevel; }
    }

    // Getters for Clan
    public String getTag() { return tag; }
    public String getName() { return name; }
    public String getType() { return type; }
    public boolean isWarLogPublic() { return isWarLogPublic; }
    public int getClanLevel() { return clanLevel; }
    public int getClanPoints() { return clanPoints; }
    public int getRequiredTrophies() { return requiredTrophies; }
    public int getWarWins() { return warWins; }
    public int getWarWinStreak() { return warWinStreak; }
    public int getMembers() { return members; }
    public String getDescription() { return description; }
    public List<ClanMember> getMemberList() { return memberList; }
    public List<Label> getLabels() { return labels; }
    public ClanCapital getClanCapital() { return clanCapital; }
}