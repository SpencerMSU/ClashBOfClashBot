package org.example.cocapi.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class WarLog {
    private List<War> items;

    public List<War> getItems() { return items; }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class War {
        private String result; // "win", "lose", "tie"
        private String endTime;
        private int teamSize;
        private ClanDetails clan;
        private ClanDetails opponent;

        // Getters
        public String getResult() { return result; }
        public String getEndTime() { return endTime; }
        public int getTeamSize() { return teamSize; }
        public ClanDetails getClan() { return clan; }
        public ClanDetails getOpponent() { return opponent; }
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ClanDetails {
        private String tag;
        private String name;
        private int stars;
        private double destructionPercentage;

        // Getters
        public String getTag() { return tag; }
        public String getName() { return name; }
        public int getStars() { return stars; }
        public double getDestructionPercentage() { return destructionPercentage; }
    }
}